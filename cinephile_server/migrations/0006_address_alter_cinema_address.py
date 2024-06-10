# Generated by Django 5.0.3 on 2024-06-10 08:10

import cinephile_server.models
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cinephile_server', '0005_remove_ticket_price_alter_film_cinemas_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.UUIDField(blank=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('city_name', models.TextField(max_length=256)),
                ('street_name', models.TextField(max_length=256)),
                ('house_number', models.IntegerField(validators=[cinephile_server.models.check_positive])),
                ('apartment_number', models.IntegerField(blank=True, null=True, validators=[cinephile_server.models.check_positive])),
                ('body', models.TextField(blank=True, null=True, validators=[cinephile_server.models.check_body])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='cinema',
            name='address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cinephile_server.address', verbose_name='address'),
        ),
    ]
