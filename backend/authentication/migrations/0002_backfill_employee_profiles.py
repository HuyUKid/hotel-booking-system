from django.conf import settings
from django.db import migrations


def create_missing_profiles(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    EmployeeProfile = apps.get_model('authentication', 'EmployeeProfile')

    existing_user_ids = EmployeeProfile.objects.values_list('user_id', flat=True)
    missing_users = User.objects.exclude(pk__in=existing_user_ids)
    EmployeeProfile.objects.bulk_create([
        EmployeeProfile(
            user_id=user.pk,
            must_change_password=not user.is_superuser,
        )
        for user in missing_users.iterator()
    ])


class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0001_move_employee_profile'),
    ]

    operations = [
        migrations.RunPython(create_missing_profiles, migrations.RunPython.noop),
    ]
