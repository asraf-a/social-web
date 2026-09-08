import urllib.parse
import requests
from django import forms
from django.core.files.base import ContentFile
from django.utils.text import slugify
from .models import Image


class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('title', 'url', 'description')
        widgets = {
            'url': forms.TextInput(attrs={'placeholder': 'Image URL (e.g. https://example.com/photo.jpg)'}),
            'title': forms.TextInput(attrs={'placeholder': 'Image Title'}),
            'description': forms.Textarea(attrs={'placeholder': 'Optional description...', 'rows': 4}),
        }

    def clean_url(self):
        url = self.cleaned_data['url'].strip()
        # Automatically transform Wikimedia thumbnail URLs to high-res original URLs to avoid 400 errors
        if '/wikipedia/commons/thumb/' in url:
            parts = url.replace('/wikipedia/commons/thumb/', '/wikipedia/commons/').split('/')
            if len(parts) > 1 and 'px-' in parts[-1]:
                url = '/'.join(parts[:-1])

        valid_extensions = ['jpg', 'jpeg', 'png', 'webp']
        # Parse URL path cleanly to ignore any query strings (e.g. ?w=600&auto=format)
        path = urllib.parse.urlsplit(url).path
        try:
            extension = path.rsplit('.', 1)[1].lower()
        except IndexError:
            raise forms.ValidationError('The given URL does not have a valid image file extension.')

        if extension not in valid_extensions:
            raise forms.ValidationError(
                'The given URL does not match valid image extensions (JPEG/JPG/PNG/WEBP).'
            )
        return url

    def save(self, force_insert=False, force_update=False, commit=True):
        image = super().save(commit=False)
        image_url = self.cleaned_data['url']
        name = slugify(image.title) or 'image'
        path = urllib.parse.urlsplit(image_url).path
        try:
            extension = path.rsplit('.', 1)[1].lower()
        except IndexError:
            extension = 'jpg'
        image_name = f'{name}.{extension}'

        # Download image from the given URL using modern browser headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
        }
        res = requests.get(image_url, headers=headers, timeout=12)
        res.raise_for_status()

        image.image.save(
            image_name,
            ContentFile(res.content),
            save=False
        )

        if commit:
            image.save()
        return image
