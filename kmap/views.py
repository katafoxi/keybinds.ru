import io
from typing import Dict

from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.http import FileResponse, HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from mypy.types import NoneType

from kmap.forms import (AddProgForm, LoginUserForm, RegisterForm)
from kmap.keyboard import Keyboard
from kmap.models import *
from kmap.keymap_handlers.pycharm import parse_keymap, get_keymap_xml_tree
from kmap.utils import DataMixin
from json import loads


class Index(DataMixin, ListView):
    model = Action
    template_name = "kmap/main.html"

    def get_context_data(self, **kwargs) -> Dict[str, NoneType]:
        context = super().get_context_data(**kwargs)
        context["k_buttons"] = Keyboard.get_empty_buttons()
        title = "Выбор программы для редактора"
        context.update(self.get_user_context(title=title))
        return context


class ShowProgActions(DataMixin, ListView):
    model = Action
    template_name = "kmap/main.html"
    allow_empty = True

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs) -> Dict[str, NoneType]:
        context = super().get_context_data(**kwargs)
        slug = self.kwargs["slug"]
        prog = Prog.objects.get(slug=slug)
        keymaps = Keymap.objects.filter(prog=slug)
        if prog.is_bounded:
            context['bouded_buttons'] = Keyboard.bounded_buttons

        if len(keymaps) != 0:
            context["keymaps"] = keymaps
            if self.request.method == "POST":
                standart_keymap = Keymap.objects.get(prog=slug, id=1).file.path
                acts_with_combs = parse_keymap(standart_keymap)
                user_keymap_file = self.request.FILES["file"]
                user_keymap_name = user_keymap_file.name.split(".")[0]
                acts_with_combs.update(parse_keymap(user_keymap_file))
                context["analyzed_keymap"] = user_keymap_name

            else:
                keymap_id = self.kwargs.get("id", 0)
                context["current_keymap"] = keymap_id
                path = Keymap.objects.get(prog=slug, id=keymap_id).file.path
                acts_with_combs = parse_keymap(keymap=path)

            without = [act for act in Action.objects.filter(prog=slug) if
                act.name not in acts_with_combs.keys()]
            context["acts_wo_combs"] = without
            k_buttons = Keyboard.get_filled_buttons(acts_with_combs, slug=slug)
            context["k_buttons"] = k_buttons
        else:
            err = f"Поддержка программы {prog.name} пока отсутствует."
            context["error_message"] = err
            context["k_buttons"] = Keyboard.get_empty_buttons()

        context.update(
            self.get_user_context(title=prog.name, prog_selected=slug))
        return context


class RegisterUser(DataMixin, CreateView):
    form_class = RegisterForm
    template_name = "kmap/register.html"
    success_url = reverse_lazy("login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_user_context(title="Регистрация"))
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user=user)
        return redirect("main")


class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = "kmap/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_user_context(title="Авторизация"))
        return context

    def get_success_url(self):
        return reverse("main")


def logout_user(request):
    logout(request)
    return redirect("main")


class AddProgram(DataMixin, CreateView):
    form_class = AddProgForm
    template_name = "kmap/add_prog.html"
    success_url = reverse_lazy("main")

    def get_context_data(self, **kwargs):
        if self.request.method == "POST":
            form = AddProgForm(self.request.POST, self.request.FILES)
        else:
            form = AddProgForm()
        context = super().get_context_data(**kwargs)
        context["form"] = form
        context.update(self.get_user_context(title="Добавление программы"))
        return context

    def form_valid(self, form):
        form.save()
        return redirect("main")


def contact(request):
    return HttpResponse("<html><name>Обратная связь</name></html>")


def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Такой страницы пока нет</h1>")


def keymap_saver(request, slug):
    if request.method == 'POST':
        body = loads(request.body)
        if body:
            keymap = get_keymap_xml_tree(keymap_name='vasya', **body)
            buffer = io.BytesIO()
            keymap.write(buffer, encoding="utf-8")
            buffer.seek(0)
            return FileResponse(buffer, as_attachment=True, filename='test.xml')