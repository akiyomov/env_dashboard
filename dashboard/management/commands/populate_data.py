from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from dashboard.models import Location, Metric, Alert, AirQualityIndex
from datetime import timedelta
import random
import decimal

class Command(BaseCommand):
    help = 'Populates the database with sample environmental data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting data population...')

        try:
            superuser = User.objects.get(username='admin')
        except User.DoesNotExist:
            superuser = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin'
            )
            self.stdout.write('Superuser created')

        locations_data = [
            {'city': 'New York', 'country': 'USA', 'lat': 40.7128, 'lon': -74.0060},
            {'city': 'London', 'country': 'UK', 'lat': 51.5074, 'lon': -0.1278},
            {'city': 'Tokyo', 'country': 'Japan', 'lat': 35.6762, 'lon': 139.6503},
            {'city': 'Paris', 'country': 'France', 'lat': 48.8566, 'lon': 2.3522},
            {'city': 'Sydney', 'country': 'Australia', 'lat': -33.8688, 'lon': 151.2093},
            {'city': 'Beijing', 'country': 'China', 'lat': 39.9042, 'lon': 116.4074},
            {'city': 'Mumbai', 'country': 'India', 'lat': 19.0760, 'lon': 72.8777},
            {'city': 'Cairo', 'country': 'Egypt', 'lat': 30.0444, 'lon': 31.2357},
        ]

        # Create locations
        locations = []
        for loc_data in locations_data:
            location, created = Location.objects.get_or_create(
                city=loc_data['city'],
                country=loc_data['country'],
                defaults={
                    'latitude': loc_data['lat'],
                    'longitude': loc_data['lon'],
                    'elevation': random.randint(0, 500)
                }
            )
            locations.append(location)
            if created:
                self.stdout.write(f'Created location: {location}')

        # Create metrics for each location
        now = timezone.now()
        for location in locations:
            # Create 60 days of historical data
            for days_ago in range(60):
                # Create 4 measurements per day
                for hour in [6, 12, 18, 23]:
                    timestamp = now - timedelta(days=days_ago, hours=now.hour-hour)
                    
                    base_temp = 20 + random.uniform(-5, 5)  # Base temperature around 20°C
                    if hour in [12, 18]:  # Higher temperatures during day
                        base_temp += 5
                    
                    metric = Metric.objects.create(
                        location=location,
                        timestamp=timestamp,
                        pm25=decimal.Decimal(random.uniform(5, 150)),
                        pm10=decimal.Decimal(random.uniform(10, 200)),
                        o3=decimal.Decimal(random.uniform(10, 100)),
                        no2=decimal.Decimal(random.uniform(10, 80)),
                        so2=decimal.Decimal(random.uniform(5, 50)),
                        temperature=decimal.Decimal(base_temp),
                        humidity=decimal.Decimal(random.uniform(30, 80))
                    )

            self.stdout.write(f'Created metrics for {location}')

            for days_ago in range(60):
                timestamp = now - timedelta(days=days_ago)
                aqi_value = random.randint(0, 500)
                
                if aqi_value <= 50:
                    category = 'Good'
                    implications = 'Air quality is satisfactory.'
                elif aqi_value <= 100:
                    category = 'Moderate'
                    implications = 'Air quality is acceptable.'
                elif aqi_value <= 150:
                    category = 'Unhealthy for Sensitive Groups'
                    implications = 'Members of sensitive groups may experience health effects.'
                elif aqi_value <= 200:
                    category = 'Unhealthy'
                    implications = 'Everyone may begin to experience health effects.'
                elif aqi_value <= 300:
                    category = 'Very Unhealthy'
                    implications = 'Health alert: everyone may experience serious health effects.'
                else:
                    category = 'Hazardous'
                    implications = 'Health warnings of emergency conditions.'

                AirQualityIndex.objects.create(
                    location=location,
                    timestamp=timestamp,
                    aqi_value=aqi_value,
                    category=category,
                    dominant_pollutant=random.choice(['PM2.5', 'PM10', 'O3']),
                    health_implications=implications
                )

            metrics = ['PM2.5', 'PM10', 'O3', 'NO2', 'SO2']
            for metric in metrics:
                Alert.objects.create(
                    user=superuser,
                    location=location,
                    metric_type=metric,
                    threshold_value=decimal.Decimal(random.uniform(50, 150)),
                    is_active=random.choice([True, False])
                )

        self.stdout.write(self.style.SUCCESS('Successfully populated the database!'))