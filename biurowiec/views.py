from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from biurowiec.models import Room

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
            return HttpResponse("Sory nie wypełniłeś w całości formularza")
        room = Room()
        room.name= name
        room.capacity = int(capacity)
        if has_projector == '1':
            room.has_projector = True
        else:
            room.has_projector = False
        room.save()
        return HttpResponse("Sala została dodana")


def index(reqest):
    rooms = Room.objects.all()
    rows = ""
    for room in rooms:
        rows += """
        <tr>
            <td><a href="/room/{}">{}</a></td>
            <td><a href="#">Edytuj</a></td>
            <td><a href="#">Usuń</a></td>
        </tr>
        """.format(room.id, room.name)
    table = room_list_table.format(rows)
    return HttpResponse(szablon.format(table))


def room_detail(request, id):
    try:
        room = Room.objects.get(id=id)
        has_projector = 'TAK' if room.has_projector else 'NIE'
        room_result = szablon_room.format(room.name, room.capacity, has_projector)

        return HttpResponse(szablon.format(room_result))
    except ObjectDoesNotExist:
        return HttpResponse("Nie ma takiej sali.")

