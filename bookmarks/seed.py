import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmarks.settings')
django.setup()

from django.contrib.auth import get_user_model
from account.models import Profile

User = get_user_model()

# Create superuser
if not User.objects.filter(username='admin').exists():
    admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword123')
    Profile.objects.get_or_create(user=admin_user)
    print("Superuser 'admin' created with password 'adminpassword123'")
else:
    print("Superuser 'admin' already exists")

# Create test regular user
if not User.objects.filter(username='testuser').exists():
    user = User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpassword123',
        first_name='Alex',
        last_name='Morgan'
    )
    Profile.objects.create(
        user=user,
        date_of_birth='1998-04-12'
    )
    print("Regular user 'testuser' created with password 'testpassword123'")
else:
    print("Regular user 'testuser' already exists")

# Seed sample images
from images.models import Image
from django.core.files.base import ContentFile
from PIL import Image as PILImage
import io

colors = [
    ('Cyberpunk Cityscape', '#3b82f6', 'Futuristic neon lights in high density metropolis.'),
    ('Nordic Forest Sunset', '#10b981', 'Serene pine forest glowing in golden hour sun.'),
    ('Minimalist Architecture', '#f59e0b', 'Clean geometric lines and glass facade design.'),
    ('Deep Ocean Coral Reef', '#ec4899', 'Vibrant underwater ecosystem with coral formation.')
]

test_user = User.objects.get(username='testuser')
admin_user = User.objects.get(username='admin')

for title, hex_color, desc in colors:
    if not Image.objects.filter(title=title).exists():
        img = PILImage.new('RGB', (600, 400), color=hex_color)
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        buf.seek(0)

        slug_name = title.lower().replace(' ', '-')
        new_img = Image.objects.create(
            user=test_user,
            title=title,
            url=f'https://example.com/{slug_name}.jpg',
            description=desc
        )
        new_img.image.save(f'{slug_name}.jpg', ContentFile(buf.read()), save=True)
        new_img.users_like.add(admin_user)
        print(f"Created sample image: '{title}'")
