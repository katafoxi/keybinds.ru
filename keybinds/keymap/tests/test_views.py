from django import forms
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from keyboard import Keyboard
from keymap.models import Program, Command
from views import AddProgram


class PagesTest(TestCase):
    small_gif = (
        b'\x47\x49\x46\x38\x39\x61\x02\x00'
        b'\x01\x00\x80\x00\x00\x00\x00\x00'
        b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
        b'\x00\x00\x00\x2C\x00\x00\x00\x00'
        b'\x02\x00\x01\x00\x00\x02\x02\x0C'
        b'\x0A\x00\x3B'
    )
    uploaded = SimpleUploadedFile(
        name='small.gif',
        content=small_gif,
        content_type='image/gif'
    )
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Keyboard.buttons_front = {'rowZX': ['Z', ]}
        Keyboard.buttons_back = {'rowZX': ['z', ]}

        prog = Program.objects.create(
            title='PyCharm',
            slug='pycharm',
            icon=PagesTest.uploaded
        )
        command = Command.objects.create(
            program=prog,
            name="Cut",
            short_name="Cut",
        )

    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username='admin')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse('main'): 'keymap/index.html',
            reverse('login'): 'keymap/login.html',
            reverse('register'): 'keymap/register.html',
            reverse('add_program'): 'keymap/add_program.html',
            reverse('program', kwargs={'slug': 'pycharm'}): 'keymap/index.html',
            reverse('settings_file', args=['pycharm', '1']): 'keymap/index.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверка словаря контекста главной страницы (в нём передаётся форма)
    def test_main_page_show_correct_context(self):
        """Шаблон main сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('main'))
        self.assertEquals(response.context['title'], 'Выбор программы для редактора')
        self.assertEquals(response.context['prog_selected'], 0)
        self.assertEquals(response.context['programs'][0].title, 'PyCharm')
        self.assertEquals(response.context['menu'], [{'title': 'Главная', 'url_name': 'main'},
                                                     {'title': 'Обратная связь', 'url_name': 'contact'}])

    def test_add_program_page_show_correct_context(self):
        """Шаблон add_program сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('add_program'))
        form_fields = {
            'title': forms.fields.CharField,
            'slug': forms.fields.SlugField,
            'icon': forms.fields.ImageField,
            'settings_file_info': forms.fields.CharField,
            'site': forms.fields.URLField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    # def test_add_program_correct_save(self):
    #     """ Представление корректно сохраняет данные валидной формы"""
    #     response = self.authorized_client.post(
    #         path=reverse('add_program'),
    #         data=self.form.fields,
    #         content_type='multipart/form-data',
    #         follow=True
    #     )
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.resolver_match.func.__name__, AddProgram.as_view().__name__)
    #     self.assertTemplateUsed(template_name='add_program.html')
    #     self.assertEqual(Program.objects.count(), program_count + 1)
    #     self.assertTrue(Program.objects.filter(pk=2).exists())
    #     self.assertEqual(Program.objects.get(pk=2).title, 'prog2')
