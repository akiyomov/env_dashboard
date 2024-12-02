from django.contrib import admin
from django.db.models import Avg, Count, Max, Min
from django.db import connection
from django.utils.html import format_html
from .models import Location, Metric, Alert, AirQualityIndex

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'country', 'latitude', 'longitude', 'created_at', 'get_average_pm25')
    list_filter = ('country',)
    search_fields = ('city', 'country')
    ordering = ('city',)
    date_hierarchy = 'created_at'
    
    def get_average_pm25(self, obj):
        avg = Metric.objects.filter(location=obj).aggregate(Avg('pm25'))['pm25__avg']
        return round(avg, 2) if avg else 'N/A'
    get_average_pm25.short_description = 'Avg PM2.5'

@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ('location', 'timestamp', 'pm25', 'pm10', 'temperature', 'humidity')
    list_filter = ('location', 'timestamp')
    search_fields = ('location__city',)
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    list_per_page = 50

    fieldsets = (
        ('Location Information', {
            'fields': ('location', 'timestamp')
        }),
        ('Air Quality Measurements', {
            'fields': ('pm25', 'pm10', 'o3', 'no2', 'so2')
        }),
        ('Weather Data', {
            'fields': ('temperature', 'humidity')
        }),
    )

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'metric_type', 'threshold_value', 'is_active', 'created_at')
    list_filter = ('is_active', 'metric_type', 'location')
    search_fields = ('user__username', 'location__city')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('User and Location', {
            'fields': ('user', 'location')
        }),
        ('Alert Settings', {
            'fields': ('metric_type', 'threshold_value', 'is_active')
        }),
    )

@admin.register(AirQualityIndex)
class AQIAdmin(admin.ModelAdmin):
    list_display = ('location', 'timestamp', 'aqi_value', 'category', 'dominant_pollutant')
    list_filter = ('category', 'dominant_pollutant', 'location')
    search_fields = ('location__city',)
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Location and Time', {
            'fields': ('location', 'timestamp')
        }),
        ('AQI Information', {
            'fields': ('aqi_value', 'category', 'dominant_pollutant')
        }),
        ('Health Information', {
            'fields': ('health_implications',),
            'classes': ('collapse',)
        }),
    )

admin.site.site_header = 'Environmental Data Dashboard Administration'
admin.site.site_title = 'Env Dashboard Admin'
admin.site.index_title = 'Dashboard Administration'