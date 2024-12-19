from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from apps.profile.models import Profile, Promocode
from apps.auth_user.forms import UserRegistrationForm, LoginForm


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')

    def test_register_get(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_register_post_valid(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword',
            'password2': 'testpassword',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register_done.html')
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertTrue(Profile.objects.filter(user__username='testuser').exists())

    def test_register_post_invalid_password(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword',
            'password2': 'wrongpassword',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_register_post_existing_username(self):
        User.objects.create_user(username='testuser', password='testpassword')
        data = {
            'username': 'testuser',
            'password': 'testpassword',
            'password2': 'testpassword',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertEqual(User.objects.filter(username='testuser').count(), 1)


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_login_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_post_valid(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(self.login_url, data)
        self.assertRedirects(response, reverse('profile'))
        self.assertTrue(response.cookies.get('access_token').value)
        self.assertTrue(response.cookies.get('refresh_token').value)

    def test_login_post_invalid_credentials(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertFalse(response.cookies.get('access_token').value)
        self.assertFalse(response.cookies.get('refresh_token').value)


class LogoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.logout_url = reverse('logout')
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_logout(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'logout.html')
        self.assertFalse(response.cookies.get('access_token').value)
        self.assertFalse(response.cookies.get('refresh_token').value)


class GoogleLoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.google_login_url = reverse('jwtgoogle')
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')

    def test_google_login(self):
        response = self.client.get(self.google_login_url)
        self.assertEqual(response.status_code, 302)  # Redirect to profile
        self.assertTrue(response.cookies.get('access_token').value)
        self.assertTrue(response.cookies.get('refresh_token').value)
        self.assertTrue(Profile.objects.filter(user=self.user).exists())
        self.assertTrue(Promocode.objects.filter(email=self.user.email).exists())


class UserRegistrationFormTest(TestCase):
    def test_valid_form(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword',
            'password2': 'testpassword',
        }
        form = UserRegistrationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_password_mismatch(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword',
            'password2': 'wrongpassword',
        }
        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password2'], ["Passwords don't match."])


class LoginFormTest(TestCase):
    def test_valid_form(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        form = LoginForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        data = {
            'username': '',
            'password': '',
        }
        form = LoginForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['This field is required.'])
        self.assertEqual(form.errors['password'], ['This field is required.'])