from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render
from .models import *


menu = [{'title': 'О сайте', 'url_name': 'about'},
        {'title': 'Добавить программу', 'url_name': 'add_program'},
        {'title': 'Обратная связь', 'url_name': 'contact'},
        {'title': 'Войти', 'url_name': 'login'}
        ]

def index(request):
    programs = Program.objects.all()
    program_commands = ProgramCommand.objects.all()
    context = {
        'menu': menu,
        'title': 'Редактор комбинаций',
        'programs': programs,
        # 'program_commands': program_commands,
        'prog_selected':0
    }
    res = render(request, 'shortcutEditor/index.html', context=context)
    return res


def about(request):
    return render(request, 'shortcutEditor/about.html', {'title':'О сайте'})


def add_program(request):
    return HttpResponse('Добавление программы')


def contact(request):
    return HttpResponse('Обратная связь')


def login(request):
    return HttpResponse('Авторизация')


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Такой страницы пока нет</h1>')

def show_program_commands(request, program_id):
    programs = Program.objects.all()
    program_commands = ProgramCommand.objects.filter(program_id=program_id)
    if len(program_commands) == 0:
        raise Http404()
    context = {
        'menu': menu,
        'title': 'Редактор комбинаций',
        'programs': programs,
        'program_commands': program_commands,
        'prog_selected':program_id
    }
    return render(request, 'shortcutEditor/index.html', context=context)

def show_command(request, command_id):
    return HttpResponse('Команда какая-то')