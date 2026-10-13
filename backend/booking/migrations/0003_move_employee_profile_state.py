from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0001_move_employee_profile'),
        ('booking', '0002_alter_employeeprofile_user'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[migrations.DeleteModel(name='EmployeeProfile')],
        ),
    ]
