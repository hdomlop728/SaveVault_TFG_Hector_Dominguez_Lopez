"""Suite basica de pruebas para SaveVault. Ejecutar con: python manage.py test"""
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.usuarios.models import Usuario
from apps.juegos.models import Plataforma, Genero, Juego
from apps.guardados.models import ArchivoGuardado
from apps.guardados.validators import validar_extension_guardado
from django.core.exceptions import ValidationError


class PlataformaTests(TestCase):
    """Pruebas del modelo Plataforma y carga de datos iniciales."""
    fixtures = ['fixtures/initial_data.json']

    def test_platforms_loaded(self):
        self.assertEqual(Plataforma.objects.count(), 23)

    def test_platform_str(self):
        p = Plataforma.objects.get(pk='NES')
        self.assertEqual(str(p), 'NES')


class GuardadoValidadorTests(TestCase):
    """Pruebas de validacion de extensiones de archivos guardados."""
    def test_valid_nes_extension(self):
        f = SimpleUploadedFile('save.sav', b'data')
        try:
            validar_extension_guardado(f, 'NES')
        except ValidationError:
            self.fail("ValidationError raised for valid NES extension")

    def test_invalid_nes_extension(self):
        f = SimpleUploadedFile('save.xyz', b'data')
        with self.assertRaises(ValidationError):
            validar_extension_guardado(f, 'NES')

    def test_valid_ps1_extension(self):
        f = SimpleUploadedFile('save.mcr', b'data')
        try:
            validar_extension_guardado(f, 'PS1')
        except ValidationError:
            self.fail("ValidationError raised for valid PS1 extension")


class RegistroUsuarioTests(TestCase):
    """Pruebas de registro e inicio de sesion de usuarios."""
    def setUp(self):
        self.client = Client()

    def test_register_user(self):
        response = self.client.post(reverse('usuarios:usuario_registro'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        self.assertEqual(Usuario.objects.filter(username='testuser').count(), 1)

    def test_login_required_for_upload(self):
        response = self.client.get(reverse('guardados:guardado_subir'))
        self.assertRedirects(response, f"{reverse('usuarios:usuario_acceder')}?next={reverse('guardados:guardado_subir')}")


class JuegoTests(TestCase):
    """Pruebas del modelo Juego y vistas relacionadas."""
    fixtures = ['fixtures/initial_data.json']

    def setUp(self):
        self.user = Usuario.objects.create_user(username='gamer', email='g@g.com', password='pass123!')
        self.client = Client()
        self.client.login(username='gamer', password='pass123!')
        self.platform = Plataforma.objects.get(pk='NES')
        self.genre = Genero.objects.create(nombre='Action')
        self.game = Juego.objects.create(
            titulo='Super Mario Bros.',
            descripcion='Classic platformer.',
            desarrollador='Nintendo',
            plataforma=self.platform,
            genero=self.genre,
            num_jugadores=2,
            creado_por=self.user,
        )

    def test_game_str(self):
        self.assertIn('Super Mario Bros.', str(self.game))

    def test_game_detail_increments_visit(self):
        initial = self.game.visitas
        self.client.get(reverse('juegos:juego_detalle', kwargs={'pk': self.game.pk}))
        self.game.refresh_from_db()
        self.assertEqual(self.game.visitas, initial + 1)

    def test_home_shows_top_games(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_platform_detail(self):
        response = self.client.get(reverse('juegos:plataforma_detalle', kwargs={'slug': 'NES'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Super Mario Bros.')
