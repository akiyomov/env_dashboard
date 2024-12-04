from django.utils import timezone
from datetime import timedelta
from dashboard.models import Alert, Metric

class AlertService:
    @staticmethod
    def create_alert_with_check(user, location, metric_type, threshold_value):
        """
        Create a new alert and check existing data against the threshold
        Returns alert and any existing violations
        """
        # Create the alert
        alert = Alert.objects.create(
            user=user,
            location=location,
            metric_type=metric_type,
            threshold_value=threshold_value,
            is_active=True
        )

        # Check last 24 hours of data for violations
        end_time = timezone.now()
        start_time = end_time - timedelta(hours=24)

        violations = []
        metrics = Metric.objects.filter(
            location=location,
            timestamp__range=(start_time, end_time)
        ).order_by('-timestamp')

        for metric in metrics:
            current_value = getattr(metric, metric_type.lower().replace('.', ''), None)
            if current_value and current_value > threshold_value:
                violations.append({
                    'timestamp': metric.timestamp,
                    'value': current_value,
                    'threshold': threshold_value,
                    'location': location.city
                })

        return alert, violations