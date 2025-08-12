from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.hashers import make_password

from .models import User, UserType, Company, ODForm


def _default_usertype():
    ut = UserType.objects.first()
    if ut:
        return ut
    return UserType.objects.create(description='System', created_at=timezone.now())


def get_sentinel_user():
    user, created = User.objects.get_or_create(
        username='[deleted]',
        defaults={
            'password': make_password(None),
            'email': '',
            'first_name': '',
            'last_name': '',
            'is_active': False,
            'is_staff': False,
            'is_superuser': False,
            'user_type': _default_usertype(),
            'date_joined': timezone.now(),
        },
    )
    return user


@receiver(pre_delete, sender=User)
def reassign_user_fks(sender, instance: User, **kwargs):
    sentinel = get_sentinel_user()

    Company.objects.filter(created_by=instance).update(created_by=sentinel)
    Company.objects.filter(edited_by=instance).update(edited_by=sentinel)

    ODForm.objects.filter(created_by=instance).update(created_by=sentinel)
    ODForm.objects.filter(edited_by=instance).update(edited_by=sentinel)
    ODForm.objects.filter(account_manager=instance).update(account_manager=sentinel)
