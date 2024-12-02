from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class AirQualityIndex(models.Model):
    CATEGORY_CHOICES = [
        ('Good', 'Good'),
        ('Moderate', 'Moderate'),
        ('Unhealthy for Sensitive Groups', 'Unhealthy for Sensitive Groups'),
        ('Unhealthy', 'Unhealthy'),
        ('Very Unhealthy', 'Very Unhealthy'),
        ('Hazardous', 'Hazardous'),
    ]
    
    location = models.ForeignKey('Location', on_delete=models.CASCADE, related_name='aqi_records')
    timestamp = models.DateTimeField()
    aqi_value = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(500)]
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    dominant_pollutant = models.CharField(max_length=50)
    health_implications = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.location} - AQI: {self.aqi_value} ({self.category})"

    class Meta:
        ordering = ['-timestamp']
        
class Location(models.Model):
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=8,
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90)
        ]
    )
    longitude = models.DecimalField(
        max_digits=11, 
        decimal_places=8,
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ]
    )
    elevation = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.city}, {self.country}"

    class Meta:
        unique_together = ['latitude', 'longitude']

class Metric(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='metrics')
    timestamp = models.DateTimeField()
    pm25 = models.DecimalField(max_digits=8, decimal_places=2, null=True, verbose_name='PM2.5')
    pm10 = models.DecimalField(max_digits=8, decimal_places=2, null=True, verbose_name='PM10')
    o3 = models.DecimalField(max_digits=8, decimal_places=2, null=True, verbose_name='Ozone')
    no2 = models.DecimalField(max_digits=8, decimal_places=2, null=True, verbose_name='Nitrogen Dioxide')
    so2 = models.DecimalField(max_digits=8, decimal_places=2, null=True, verbose_name='Sulfur Dioxide')
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    humidity = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        null=True
    )

    def __str__(self):
        return f"{self.location} - {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']

class Alert(models.Model):
    METRIC_CHOICES = [
        ('PM2.5', 'PM2.5'),
        ('PM10', 'PM10'),
        ('O3', 'Ozone'),
        ('NO2', 'Nitrogen Dioxide'),
        ('SO2', 'Sulfur Dioxide'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    metric_type = models.CharField(max_length=20, choices=METRIC_CHOICES)
    threshold_value = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.location} - {self.metric_type}"

class Trend(models.Model):
    METRIC_CHOICES = [
        ('PM2.5', 'PM2.5'),
        ('PM10', 'PM10'),
        ('O3', 'Ozone'),
        ('NO2', 'Nitrogen Dioxide'),
        ('SO2', 'Sulfur Dioxide'),
    ]

    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='trends')
    metric_type = models.CharField(max_length=20, choices=METRIC_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    average_value = models.DecimalField(max_digits=8, decimal_places=2)
    max_value = models.DecimalField(max_digits=8, decimal_places=2)
    min_value = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.location} - {self.metric_type} ({self.start_date} to {self.end_date})"

    class Meta:
        unique_together = ['location', 'metric_type', 'start_date', 'end_date']
        ordering = ['-start_date']