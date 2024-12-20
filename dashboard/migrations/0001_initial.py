# Generated by Django 5.0 on 2024-12-02 13:59

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=100)),
                ('country', models.CharField(max_length=100)),
                ('latitude', models.DecimalField(decimal_places=8, max_digits=10, validators=[django.core.validators.MinValueValidator(-90), django.core.validators.MaxValueValidator(90)])),
                ('longitude', models.DecimalField(decimal_places=8, max_digits=11, validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)])),
                ('elevation', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'unique_together': {('latitude', 'longitude')},
            },
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('metric_type', models.CharField(choices=[('PM2.5', 'PM2.5'), ('PM10', 'PM10'), ('O3', 'Ozone'), ('NO2', 'Nitrogen Dioxide'), ('SO2', 'Sulfur Dioxide')], max_length=20)),
                ('threshold_value', models.DecimalField(decimal_places=2, max_digits=8)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alerts', to=settings.AUTH_USER_MODEL)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.location')),
            ],
        ),
        migrations.CreateModel(
            name='AirQualityIndex',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('aqi_value', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(500)])),
                ('category', models.CharField(choices=[('Good', 'Good'), ('Moderate', 'Moderate'), ('Unhealthy for Sensitive Groups', 'Unhealthy for Sensitive Groups'), ('Unhealthy', 'Unhealthy'), ('Very Unhealthy', 'Very Unhealthy'), ('Hazardous', 'Hazardous')], max_length=50)),
                ('dominant_pollutant', models.CharField(max_length=50)),
                ('health_implications', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aqi_records', to='dashboard.location')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Metric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('pm25', models.DecimalField(decimal_places=2, max_digits=8, null=True, verbose_name='PM2.5')),
                ('pm10', models.DecimalField(decimal_places=2, max_digits=8, null=True, verbose_name='PM10')),
                ('o3', models.DecimalField(decimal_places=2, max_digits=8, null=True, verbose_name='Ozone')),
                ('no2', models.DecimalField(decimal_places=2, max_digits=8, null=True, verbose_name='Nitrogen Dioxide')),
                ('so2', models.DecimalField(decimal_places=2, max_digits=8, null=True, verbose_name='Sulfur Dioxide')),
                ('temperature', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('humidity', models.DecimalField(decimal_places=2, max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metrics', to='dashboard.location')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Trend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('metric_type', models.CharField(choices=[('PM2.5', 'PM2.5'), ('PM10', 'PM10'), ('O3', 'Ozone'), ('NO2', 'Nitrogen Dioxide'), ('SO2', 'Sulfur Dioxide')], max_length=20)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('average_value', models.DecimalField(decimal_places=2, max_digits=8)),
                ('max_value', models.DecimalField(decimal_places=2, max_digits=8)),
                ('min_value', models.DecimalField(decimal_places=2, max_digits=8)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trends', to='dashboard.location')),
            ],
            options={
                'ordering': ['-start_date'],
                'unique_together': {('location', 'metric_type', 'start_date', 'end_date')},
            },
        ),
    ]
