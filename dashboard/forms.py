from django import forms
from .models import Location, Metric, Alert, AirQualityIndex

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['city', 'country', 'latitude', 'longitude', 'elevation']
        widgets = {
            'latitude': forms.NumberInput(attrs={'step': '0.00000001'}),
            'longitude': forms.NumberInput(attrs={'step': '0.00000001'}),
        }

class MetricForm(forms.ModelForm):
    class Meta:
        model = Metric
        fields = ['location', 'timestamp', 'pm25', 'pm10', 'o3', 'no2', 'so2', 
                 'temperature', 'humidity']
        widgets = {
            'timestamp': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class AlertForm(forms.ModelForm):
    class Meta:
        model = Alert
        fields = ['location', 'metric_type', 'threshold_value', 'is_active']

class AQIForm(forms.ModelForm):
    class Meta:
        model = AirQualityIndex
        fields = ['location', 'timestamp', 'aqi_value', 'category', 
                 'dominant_pollutant', 'health_implications']
        widgets = {
            'timestamp': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'health_implications': forms.Textarea(attrs={'rows': 3}),
        }