# Generated by Django 5.1 on 2024-12-11 21:00

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('registration_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('full_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=20)),
                ('preferred_schedule', models.CharField(choices=[('morning', 'Morning Session (9 AM - 1 PM)'), ('evening', 'Evening Session (6 PM - 10 PM)')], max_length=10)),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('qr_code', models.ImageField(blank=True, null=True, upload_to='qr_codes/')),
                ('is_email_sent', models.BooleanField(default=False)),
            ],
        ),
    ]
