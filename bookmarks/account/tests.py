from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model, authenticate
from django.core import mail
from account.models import Profile

User = get_user_model()


class AuthenticationAndProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='InitialPassword123!',
            first_name='Alice'
        )
        self.profile, _ = Profile.objects.get_or_create(user=self.user)
        self.profile.date_of_birth = '1995-05-15'
        self.profile.save()

    def test_email_auth_backend(self):
        # Authenticate by username (ModelBackend)
        user_by_uname = authenticate(username='alice', password='InitialPassword123!')
        self.assertIsNotNone(user_by_uname)
        self.assertEqual(user_by_uname.pk, self.user.pk)

        # Authenticate by email (EmailAuthBackend)
        user_by_email = authenticate(username='alice@example.com', password='InitialPassword123!')
        self.assertIsNotNone(user_by_email)
        self.assertEqual(user_by_email.pk, self.user.pk)

        # Case-insensitive email authentication
        user_case_insensitive = authenticate(username='ALICE@EXAMPLE.COM', password='InitialPassword123!')
        self.assertIsNotNone(user_case_insensitive)

        # Invalid password returns None
        wrong_pass = authenticate(username='alice@example.com', password='WrongPassword')
        self.assertIsNone(wrong_pass)

    def test_dashboard_login_required(self):
        # Unauthenticated access redirects to login
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/account/login/', response.url)

        # Authenticated access succeeds
        self.client.login(username='alice', password='InitialPassword123!')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome, Alice!')

    def test_user_registration(self):
        reg_data = {
            'username': 'bob',
            'first_name': 'Bob',
            'email': 'bob@example.com',
            'password': 'BobSecretPassword99!',
            'password2': 'BobSecretPassword99!',
        }
        response = self.client.post(reverse('register'), data=reg_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your account has been successfully created')

        # Check Bob exists in DB with hashed password and profile
        bob = User.objects.get(username='bob')
        self.assertTrue(bob.check_password('BobSecretPassword99!'))
        self.assertTrue(hasattr(bob, 'profile'))

    def test_user_registration_mismatched_passwords(self):
        reg_data = {
            'username': 'charlie',
            'first_name': 'Charlie',
            'email': 'charlie@example.com',
            'password': 'PasswordA123!',
            'password2': 'PasswordB456!',
        }
        response = self.client.post(reverse('register'), data=reg_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Passwords don&#x27;t match")
        self.assertFalse(User.objects.filter(username='charlie').exists())

    def test_profile_edit(self):
        self.client.login(username='alice', password='InitialPassword123!')
        edit_data = {
            'first_name': 'Alicia',
            'last_name': 'Smith',
            'email': 'alicia.smith@example.com',
            'date_of_birth': '1996-06-20',
        }
        response = self.client.post(reverse('edit'), data=edit_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profile updated successfully!')

        # Verify DB updates
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Alicia')
        self.assertEqual(self.user.last_name, 'Smith')
        self.assertEqual(self.user.email, 'alicia.smith@example.com')
        self.assertEqual(str(self.profile.date_of_birth), '1996-06-20')

    def test_password_reset_flow(self):
        # Request password reset
        response = self.client.post(
            reverse('password_reset'),
            data={'email': 'alice@example.com'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "We've sent an email")
        # Check an email was sent via Django mail outbox
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('alice@example.com', mail.outbox[0].to)

    def test_google_social_auth_url_configured(self):
        google_url = reverse('social:begin', args=['google-oauth2'])
        self.assertTrue(google_url.startswith('/social-auth/login/google-oauth2/'))


class UserFollowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='TestPassword123!'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='TestPassword123!'
        )

    def test_user_list_view(self):
        self.client.login(username='user1', password='TestPassword123!')
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'user2')

    def test_user_detail_view(self):
        self.client.login(username='user1', password='TestPassword123!')
        response = self.client.get(reverse('user_detail', args=[self.user2.username]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'user2')
        self.assertContains(response, 'Follow')

    def test_user_follow_and_unfollow_ajax(self):
        self.client.login(username='user1', password='TestPassword123!')
        follow_url = reverse('user_follow')
        ajax_headers = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}

        # Follow user2
        response = self.client.post(
            follow_url,
            {'id': self.user2.id, 'action': 'follow'},
            **ajax_headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})
        self.assertTrue(self.user1.following.filter(id=self.user2.id).exists())
        self.assertTrue(self.user2.followers.filter(id=self.user1.id).exists())

        # Unfollow user2
        response = self.client.post(
            follow_url,
            {'id': self.user2.id, 'action': 'unfollow'},
            **ajax_headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})
        self.assertFalse(self.user1.following.filter(id=self.user2.id).exists())

    def test_user_cannot_follow_self(self):
        self.client.login(username='user1', password='TestPassword123!')
        follow_url = reverse('user_follow')
        ajax_headers = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}

        response = self.client.post(
            follow_url,
            {'id': self.user1.id, 'action': 'follow'},
            **ajax_headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 'error')

    def test_user_follow_non_ajax_rejected(self):
        self.client.login(username='user1', password='TestPassword123!')
        follow_url = reverse('user_follow')
        response = self.client.post(
            follow_url,
            {'id': self.user2.id, 'action': 'follow'}
        )
        self.assertEqual(response.status_code, 400)

