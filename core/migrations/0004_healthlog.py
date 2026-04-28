from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_journal'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HealthLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('water_count', models.IntegerField(default=0)),
                ('workout_done', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='health_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Health Log',
                'verbose_name_plural': 'Health Logs',
                'unique_together': {('user', 'date')},
            },
        ),
    ]
