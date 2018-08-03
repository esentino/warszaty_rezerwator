from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from biurowiec.models import Room, Reservation

szablon = """
<html>
    <body>
        <ul>
            <li>
                <a href="/room/new">Dodaj nową salę</a>
                <a href="/">Strona główna</a>
            </li>
        </ul>
        <div>
            {}
        </div>
    </body>
</html>
"""

form_room = """
        <form action="#" method="POST">
            <label>
                Nazwa sali:
                <input type="text" name="name">
            </label>
            <label>
                Pojemność sali:
                <input type="number" name="capacity" min="1">
            </label>
            <label>
                Czy posiada rzutnik:
                <input type="checkbox" name="has_projector" value="1">
            </label>
            <input type="submit" value="Dodaj salę">
        </form>
    """

form_room_edit = """
        <form action="/room/modify/{}" method="POST">
            <label>
                Nazwa sali:
                <input type="text" name="name" value="{}">
            </label>
            <label>
                Pojemność sali:
                <input type="number" name="capacity" min="1" value="{}">
            </label>
            <label>
                Czy posiada rzutnik:
                <input type="checkbox" name="has_projector" value="1" {}>
            </label>
            <input type="submit" value="Dodaj salę">
        </form>
    """

room_list_table = """
<table>
    <thead>
        <tr>
            <th>Nazwa</th>
            <th>Edycja</th>
            <th>Usuwanie</th>
        </tr>
    </thead>
    <tbody>
        {}
    </tbody>
</table>

"""

szablon_room = """
<p>
    Nazwa: {}
</p>
<p>
    Pojemność: {}
</p>
<p>
    Posiada rzutnik: {}
</p>
<p>Dodaj rezerwację:
</p>
<p>
    {}
</p>
"""

form_reservation = """
<form action="/reservation/{}" method="POST">
    <label>
        Data rezerwacji:
        <input type="date" name="date">
    </label>
    <label>
        Komentarz:
        <input type="textarea" name="comment">
    </label>
    <input type="submit" value="Dodaj rezerwację">
</form>
"""

@csrf_exempt
def room_new(request):
    if request.method == "GET":
        return HttpResponse(szablon.format(form_room))
    elif request.method == "POST":
        name = request.POST.get('name')
        capacity = request.POST.get('capacity')
        has_projector = request.POST.get('has_projector')
        if (name is None or name == '' or capacity is None
                or capacity == ''):
            return HttpResponse(szablon.format("Sory nie wypełniłeś w całości formularza"))
        room = Room()
        room.name= name
        room.capacity = int(capacity)
        if has_projector == '1':
            room.has_projector = True
        else:
            room.has_projector = False
        room.save()
        return HttpResponse(szablon.format("Sala została dodana"))


def index(reqest):
    rooms = Room.objects.all()
    rows = ""
    for room in rooms:
        rows += """
        <tr>
            <td><a href="/room/{}">{}</a></td>
            <td><a href="/room/modify/{}">Edytuj</a></td>
            <td><a href="/room/delete/{}">Usuń</a></td>
        </tr>
        """.format(room.id, room.name, room.id, room.id)
    table = room_list_table.format(rows)
    return HttpResponse(szablon.format(table))


def room_detail(request, id):
    try:
        room = Room.objects.get(id=id)
        has_projector = 'TAK' if room.has_projector else 'NIE'
        room_result = szablon_room.format(room.name, room.capacity, has_projector, form_reservation.format(room.id))

        return HttpResponse(szablon.format(room_result))
    except ObjectDoesNotExist:
        return HttpResponse(szablon.format("Nie ma takiej sali."))


@csrf_exempt
def room_modify(request, id):
    try:
        room = Room.objects.get(id=id)
    except ObjectDoesNotExist:
        return HttpResponse(szablon.format("Nie ma takiej sali."))
    if request.method == "GET":
        has_projector = "checked" if room.has_projector else ""
        edit_form = form_room_edit.format(room.id, room.name, room.capacity, has_projector)
        return HttpResponse(szablon.format(edit_form))
    elif request.method == "POST":
        name = request.POST.get('name')
        capacity = request.POST.get('capacity')
        has_projector = request.POST.get('has_projector')
        if name is None or name == '' or capacity is None or capacity == '':
            return HttpResponse(szablon.format("Sory nie wypełniłeś w całości formularza"))
        room.name = name
        room.capacity = int(capacity)
        if has_projector == '1':
            room.has_projector = True
        else:
            room.has_projector = False
        room.save()
        return HttpResponse(szablon.format("Sala została zmieniona"))


def room_delete(request, id):
    try:
        room = Room.objects.get(id=id)
        room.delete()
        return HttpResponse(szablon.format("Sala została usunięta."))
    except ObjectDoesNotExist:
        return HttpResponse(szablon.format("Nie ma takiej sali."))


@csrf_exempt
def reservation_new(request, id):
    try:
        room = Room.objects.get(id=id)
    except ObjectDoesNotExist:
        return HttpResponse(szablon.format("Nie ma takiej sali"))
    if request.method == "POST":
        comment = request.POST.get('comment')
        date_sting = request.POST.get("date")
        date = datetime.strptime(date_sting, '%Y-%m-%d').date()
        reservation_exists = (room.reservation_set.filter(date=date).count() > 0)
        today= datetime.now().date()
        if date < today or reservation_exists:
            return HttpResponse(szablon.format("Nie można zarezerwować sali w przeszłości lub sala jest zarezerowana na dany dzień"))
        reservation = Reservation()
        reservation.date = date
        reservation.room = room
        reservation.comment = comment
        reservation.save()
        return HttpResponseRedirect("/")
