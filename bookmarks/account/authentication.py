from django.contrib.auth import get_user_model

User = get_user_model()


class EmailAuthBackend:
    """
    Custom authentication backend to authenticate users using their e-mail address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # The login form passes credentials in the 'username' field, which may be an email
        email = username or kwargs.get('email')
        if not email or not password:
            return None
        try:
            user = User.objects.get(email__iexact=email)
            if user.check_password(password):
                return user
            return None
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
