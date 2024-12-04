from django.db.models import Avg, Max, Min, Count
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from ..models import Location, Metric, Trend

class TrendService:
    @staticmethod
    def generate_trends(location, days=30):
        """Generate trends for a location over specified period"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        metrics = Metric.objects.filter(
            location=location,
            timestamp__range=(start_date, end_date)
        )

        metric_fields = ['pm25', 'pm10', 'o3', 'no2', 'so2']

        for metric_type in metric_fields:
            daily_metrics = metrics.values('timestamp__date').annotate(
                avg_value=Avg(metric_type),
                max_value=Max(metric_type),
                min_value=Min(metric_type),
                count=Count('id')
            ).order_by('timestamp__date')

            for daily_metric in daily_metrics:
                if daily_metric['count'] > 0:  
                    Trend.objects.update_or_create(
                        location=location,
                        metric_type=metric_type.upper(),
                        start_date=daily_metric['timestamp__date'],
                        end_date=daily_metric['timestamp__date'],
                        defaults={
                            'average_value': Decimal(str(daily_metric['avg_value'] or 0)),
                            'max_value': Decimal(str(daily_metric['max_value'] or 0)),
                            'min_value': Decimal(str(daily_metric['min_value'] or 0))
                        }
                    )

    @staticmethod
    def get_location_trends(location, days=30, metric_type=None):
        """Get trends for a location"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        trends = Trend.objects.filter(
            location=location,
            start_date__gte=start_date,
            end_date__lte=end_date
        )

        if metric_type:
            trends = trends.filter(metric_type=metric_type)

        return trends.order_by('start_date')

    @staticmethod
    def get_trend_summary(location, days=30):
        """Get summary of trends for all metrics"""
        trends = TrendService.get_location_trends(location, days)
        
        summary = {}
        for trend in trends:
            metric_type = trend.metric_type
            if metric_type not in summary:
                summary[metric_type] = {
                    'avg_values': [],
                    'max_values': [],
                    'min_values': [],
                    'dates': []
                }
            
            summary[metric_type]['avg_values'].append(float(trend.average_value))
            summary[metric_type]['max_values'].append(float(trend.max_value))
            summary[metric_type]['min_values'].append(float(trend.min_value))
            summary[metric_type]['dates'].append(trend.start_date)

        return summary