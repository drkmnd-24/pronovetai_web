import hashlib
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class LegacyHashBackend(BaseBackend):
    """
    Authenticates against pt_users.user_pass that are **MD5** hashes.
    On first successful login rewrites the hash using Django's hasher.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        legacy_hash = user.password  # column is user_pass
        if len(legacy_hash) == 32 and legacy_hash == hashlib.md5(password.encode()).hexdigest():
            # ✅ Password matches the old MD5 hash → upgrade!
            user.set_password(password)   # writes PBKDF2
            user.save(update_fields=["password"])
            return user

        # either already upgraded or incorrect
        return None

    def user_can_authenticate(self, user):
        # mimic Django’s default check (is_active etc.)
        return getattr(user, "is_active", True)
