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
    def trends_with_location():
        """
        Fetch trends data along with location information.
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    l.city,
                    l.country,
                    t.trend_name,
                    t.trend_value,
                    t.timestamp
                FROM dashboard_location l
                JOIN dashboard_trend t ON l.id = t.location_id
                WHERE t.timestamp >= DATE('now', '-30 days')
                ORDER BY t.timestamp DESC;
            """)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        
    @staticmethod
    def searching_location(search_term):
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT 
            l.city,
            l.country,
            l.latitude,
            l.longitude
            FROM dashboard_location l
            WHERE l.city LIKE ?
        """,(f'%{search_term}%',))
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
         
