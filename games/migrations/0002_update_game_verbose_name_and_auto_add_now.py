# Generated by Django 3.2 on 2021-04-12 13:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='player_2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player_2', to=settings.AUTH_USER_MODEL, verbose_name='Opponent'),
        ),
    ]