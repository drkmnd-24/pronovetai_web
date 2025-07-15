from django.contrib.auth.hashers import identify_hasher, make_password
from django.db import migrations


def forward(apps, schema_editor):
    User = apps.get_model('pronovetai_app', 'User')
    updated = 0

    for user in User.objects.all().iterator():
        try:
            identify_hasher(user.password)
            continue
        except ValueError:
            pass

        user.password = make_password(user.password)
        user.save(update_fields=['password'])
        updated += 1

    if updated:
        print(f'✓ Converted {updated} clear-text password(s) to pbkdf2_sha256')
    else:
        print(f'✓ No clear-text passwords found; nothing to convert')


def backward(apps, schema_editor):
    raise RuntimeError('Cannot reverse password-hashing migration')


class Migration(migrations.Migration):
    dependencies = [
        ('pronovetai_app', '0008_create_user_logs_table'),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
