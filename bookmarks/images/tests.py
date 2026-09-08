import io
from unittest.mock import patch, MagicMock
from PIL import Image as PILImage

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from images.models import Image
from images.forms import ImageCreateForm

User = get_user_model()


def get_dummy_jpeg():
    file = io.BytesIO()
    image = PILImage.new('RGB', (120, 120), color='red')
    image.save(file, 'JPEG')
    file.seek(0)
    return file.read()


class ImageModelAndViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='photouser',
            email='photo@example.com',
            password='TestPassword123!'
        )
        self.image = Image.objects.create(
            user=self.user,
            title='Sunset at the beach',
            url='https://example.com/sunset.jpg',
            description='A beautiful sunset over the waves.'
        )
        self.image.image.save('sunset.jpg', ContentFile(get_dummy_jpeg()), save=True)

    def test_image_slug_and_absolute_url(self):
        self.assertEqual(self.image.slug, 'sunset-at-the-beach')
        expected_url = reverse('images:detail', args=[self.image.id, self.image.slug])
        self.assertEqual(self.image.get_absolute_url(), expected_url)
        self.assertEqual(str(self.image), 'Sunset at the beach')

    def test_image_detail_view(self):
        self.client.login(username='photouser', password='TestPassword123!')
        response = self.client.get(self.image.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sunset at the beach')
        self.assertContains(response, '<span class="total">0</span> likes')

    def test_image_like_ajax_required(self):
        self.client.login(username='photouser', password='TestPassword123!')
        like_url = reverse('images:like')

        # Non-AJAX POST returns 400 Bad Request
        response = self.client.post(like_url, {'id': self.image.id, 'action': 'like'})
        self.assertEqual(response.status_code, 400)

        # AJAX POST returns 200 OK with JSON status
        ajax_headers = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        response = self.client.post(
            like_url,
            {'id': self.image.id, 'action': 'like'},
            **ajax_headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})
        self.assertEqual(self.image.users_like.count(), 1)

        # Unlike via AJAX POST
        response = self.client.post(
            like_url,
            {'id': self.image.id, 'action': 'unlike'},
            **ajax_headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})
        self.assertEqual(self.image.users_like.count(), 0)

    def test_image_list_views_standard_and_ajax(self):
        self.client.login(username='photouser', password='TestPassword123!')
        list_url = reverse('images:list')

        # Standard GET returns full list template
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'images/image/list.html')
        self.assertContains(response, 'Sunset at the beach')

        # AJAX GET returns partial list_ajax template for infinite scroll
        ajax_headers = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        response_ajax = self.client.get(list_url + '?page=1', **ajax_headers)
        self.assertEqual(response_ajax.status_code, 200)
        self.assertTemplateUsed(response_ajax, 'images/image/list_ajax.html')
        self.assertTemplateNotUsed(response_ajax, 'images/image/list.html')

    @patch('requests.get')
    def test_image_create_form_and_save(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = get_dummy_jpeg()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        form_data = {
            'title': 'Mountain Peak',
            'url': 'https://example.com/mountain.jpg?width=1200',
            'description': 'Snowy alpine view',
        }
        form = ImageCreateForm(data=form_data)
        self.assertTrue(form.is_valid())

        new_image = form.save(commit=False)
        new_image.user = self.user
        new_image.save()

        self.assertEqual(new_image.title, 'Mountain Peak')
        self.assertEqual(new_image.slug, 'mountain-peak')
        self.assertTrue(bool(new_image.image))

    def test_image_create_form_invalid_extension(self):
        form_data = {
            'title': 'Document',
            'url': 'https://example.com/document.pdf',
            'description': 'Not an image',
        }
        form = ImageCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('url', form.errors)

    def test_total_likes_denormalization_signal(self):
        self.assertEqual(self.image.total_likes, 0)

        # Adding user to users_like triggers users_like_changed signal
        self.image.users_like.add(self.user)
        self.image.refresh_from_db()
        self.assertEqual(self.image.total_likes, 1)

        # Removing user decrements total_likes
        self.image.users_like.remove(self.user)
        self.image.refresh_from_db()
        self.assertEqual(self.image.total_likes, 0)

    def test_image_ranking_view(self):
        self.client.login(username='photouser', password='TestPassword123!')
        response = self.client.get(reverse('images:ranking'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'images/image/ranking.html')
        self.assertContains(response, 'Image Ranking')

