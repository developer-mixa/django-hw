from django.shortcuts import render, redirect, HttpResponse
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.models import User
from .serializers import UserSerializer, CinemaSerializer, FilmSerializer, TicketSerializer, FilmCinemaSerializer
from .models import Cinema, Film, Ticket, FilmCinema
from .auth import LoginRequired, LoginAdminRequired
from .forms import RegistrationForm
from django.db.models import Prefetch
import cinephile_server.template_names as template
from rest_framework.viewsets import ModelViewSet

# viewsets

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CinemaViewSet(LoginAdminRequired, ModelViewSet):
    queryset = Cinema.objects.all()
    serializer_class = CinemaSerializer

class FilmViewSet(LoginAdminRequired, ModelViewSet):
    queryset = Film.objects.all()
    serializer_class = FilmSerializer

class FilmCinemaViewSet(LoginAdminRequired, ModelViewSet):
    queryset = FilmCinema.objects.all()
    serializer_class = FilmCinemaSerializer

class TicketViewSet(LoginRequired, ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

# helpers

def __generate_html_page(request, template_name, context=None, extension='html'):
    if context is None:
        context = {}
    return render(request, f'{template_name}.{extension}', context)

def __get_tickets_by_film_cinema(model: Film | Cinema) -> list[Ticket]:
    film_cinemas = model.filmcinema_set.all()
    all_tickets = Ticket.objects.prefetch_related(
        Prefetch('film_cinema', queryset=film_cinemas, to_attr='film_cinemas')
    )
    tickets = []
    for ticket in all_tickets:
        if model.id in (ticket.film_cinema.film.id, ticket.film_cinema.cinema.id):
            tickets.append(ticket)
    return tickets

# pages

def main_page(request):
    return __generate_html_page(request, template.INDEX)

def films_page(request: WSGIRequest):
    return __generate_html_page(request, template.FILMS, {template.FILMS: Film.objects.all()})

def cinemas_page(request: WSGIRequest):
    return __generate_html_page(request, template.CINEMAS, {template.CINEMAS: Cinema.objects.all()})

def film_detail_page(request: WSGIRequest, pk):
    film = Film.objects.get(id=pk)
    tickets = __get_tickets_by_film_cinema(film)
    return __generate_html_page(request, template.FILM_DETAILS, {'film': film, 'tickets': tickets})

def cinema_detail_page(request: WSGIRequest, pk):
    cinema = Cinema.objects.get(id=pk)
    tickets = __get_tickets_by_film_cinema(cinema)
    return __generate_html_page(request, template.CINEMA_DETAILS, {'cinema': cinema, 'tickets': tickets})

def booked_tickets_page(request: WSGIRequest):
    if request.user.is_authenticated:
        user = request.user
        tickets = Ticket.objects.filter(user=user)
        return __generate_html_page(request, template.BOOKED_TICKETS, {'tickets': tickets})
    return redirect(template.PROFILE)

def profile_page(request: WSGIRequest):
    return __generate_html_page(request, template.PROFILE, {'user': request.user})

def register_page(request: WSGIRequest):
    errors = ''
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.save()
            return redirect('')
        else:
            errors = form.errors
    else:
        form = RegistrationForm()
    return __generate_html_page(
        request,
        template.REGISTER,
        {'form': form, 'errors': errors},
    )

# queries

def book_ticket(request: WSGIRequest):
    if request.method == 'POST':
        if request.user.is_authenticated:
            ticket_id = request.GET.get('ticket_id')
            ticket = Ticket.objects.get(id=ticket_id)
            ticket.user = request.user
            ticket.save()
        else:
            return redirect(template.LOGIN)
        return booked_tickets_page(request)
    return HttpResponse('Something went wrong...')