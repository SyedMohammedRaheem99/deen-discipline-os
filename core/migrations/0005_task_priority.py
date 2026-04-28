from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_healthlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='priority',
            field=models.CharField(
                choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')],
                default='medium',
                max_length=6,
            ),
        ),
    ]
