# dashboard/queries.py

from django.db import connection
from django.db.models import Avg, Count, F, Max, Min
from .models import Location, Metric, Alert, Trend, AirQualityIndex
from django.utils import timezone

class SampleQueries:
    @staticmethod
    def join_query_locations_with_alerts():
        """
        Sample Join Query: Gets locations with their metrics and active alerts
        Demonstrates JOIN between three tables
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    l.city,
                    l.country,
                    m.pm25,
                    m.temperature,
                    a.threshold_value,
                    a.metric_type,
                    aqi.aqi_value,
                    aqi.category
                FROM dashboard_location l
                JOIN dashboard_metric m ON l.id = m.location_id
                JOIN dashboard_alert a ON l.id = a.location_id
                JOIN dashboard_airqualityindex aqi ON l.id = aqi.location_id
                WHERE a.is_active = True
                AND m.timestamp = (
                    SELECT MAX(timestamp)
                    FROM dashboard_metric
                    WHERE location_id = l.id
                )
                ORDER BY m.timestamp DESC;
            """)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def aggregate_query_city_statistics():
        """
        Sample Aggregate Query: Calculates statistics by city using GROUP BY
        Demonstrates aggregate functions and GROUP BY
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    l.city,
                    l.country,
                    COUNT(m.id) as total_measurements,
                    AVG(m.pm25) as avg_pm25,
                    MAX(m.pm25) as max_pm25,
                    MIN(m.pm25) as min_pm25,
                    AVG(m.temperature) as avg_temperature
                FROM dashboard_location l
                JOIN dashboard_metric m ON l.id = m.location_id
                GROUP BY l.city, l.country
                HAVING AVG(m.pm25) > 20
                ORDER BY avg_pm25 DESC;
            """)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def subquery_high_pollution_locations():
        """
        Sample Subquery: Finds locations with above-average pollution
        Demonstrates use of subqueries
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT l.city, l.country, l.latitude, l.longitude
                FROM dashboard_location l
                WHERE l.id IN (
                    SELECT location_id
                    FROM dashboard_metric
                    WHERE pm25 > (
                        SELECT AVG(pm25)
                        FROM dashboard_metric
                        WHERE pm25 IS NOT NULL
                    )
                    AND timestamp >= DATE('now', '-7 days')
                )
                ORDER BY l.city;
            """)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Django ORM versions of the same queries
    @staticmethod
    def orm_locations_with_alerts():
        return Location.objects.filter(
            metrics__timestamp__in=Metric.objects.filter(
                location=F('location')
            ).values('location').annotate(
                max_timestamp=Max('timestamp')
            ).values('max_timestamp'),
            alerts__is_active=True
        ).annotate(
            current_pm25=F('metrics__pm25'),
            current_temperature=F('metrics__temperature'),
            alert_threshold=F('alerts__threshold_value'),
            alert_type=F('alerts__metric_type'),
            aqi_value=F('aqi_records__aqi_value'),
            aqi_category=F('aqi_records__category')
        )

    @staticmethod
    def orm_city_statistics():
        return Location.objects.annotate(
            total_measurements=Count('metrics'),
            avg_pm25=Avg('metrics__pm25'),
            max_pm25=Max('metrics__pm25'),
            min_pm25=Min('metrics__pm25'),
            avg_temperature=Avg('metrics__temperature')
        ).filter(
            avg_pm25__gt=20
        ).order_by('-avg_pm25')

    @staticmethod
    def orm_high_pollution_locations():
        avg_pm25 = Metric.objects.filter(
            pm25__isnull=False
        ).aggregate(avg=Avg('pm25'))['avg']
        
        return Location.objects.filter(
            metrics__pm25__gt=avg_pm25,
            metrics__timestamp__gte=timezone.now() - timezone.timedelta(days=7)
        ).distinct().order_by('city')
    
    @staticmethod
    def continuous_high_pollution_locations():
    #Identifies locations with PM2.5 consistently exceeding a threshold for the past 3 days.
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT l.city, l.country, COUNT(*) as high_pollution_days
                FROM dashboard_location l
                JOIN dashboard_metric m ON l.id = m.location_id
                WHERE m.timestamp >= DATE('now', '-3 days')
                AND m.pm25 > 50
                GROUP BY l.city, l.country
                HAVING COUNT(*) = 3
                ORDER BY l.city;
            """)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    @staticmethod
    def temperature_spike_locations():
    # Finds locations with temperature spikes greater than 10°C in the last 24 hours.
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT l.city, l.country, MAX(m.temperature) - MIN(m.temperature) as temp_change
                FROM dashboard_location l
                JOIN dashboard_metric m ON l.id = m.location_id
                WHERE m.timestamp >= DATE('now', '-1 day')
                GROUP BY l.city, l.country
                HAVING temp_change > 10
                ORDER BY temp_change DESC;
            """)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def alerts_triggered_last_week():
    # Retrieves alerts triggered in the past week with associated metrics.
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    a.metric_type,
                    a.threshold_value,
                    l.city,
                    l.country,
                    m.pm25,
                    m.temperature,
                    m.timestamp
                FROM dashboard_alert a
                JOIN dashboard_location l ON a.location_id = l.id
                JOIN dashboard_metric m ON a.location_id = m.location_id
                WHERE a.is_active = True
                AND m.timestamp >= DATE('now', '-7 days')
                ORDER BY m.timestamp DESC;
            """)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    