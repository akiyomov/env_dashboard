# dashboard/management/commands/populate_data.py

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

        # Create sample locations (major cities)
        locations_data = [
            {'city': 'New York', 'country': 'USA', 'lat': 40.7128, 'lon': -74.0060},
            {'city': 'London', 'country': 'UK', 'lat': 51.5074, 'lon': -0.1278},
            {'city': 'Tokyo', 'country': 'Japan', 'lat': 35.6762, 'lon': 139.6503},
            {'city': 'Beijing', 'country': 'China', 'lat': 39.9042, 'lon': 116.4074},
            {'city': 'Sydney', 'country': 'Australia', 'lat': -33.8688, 'lon': 151.2093},
            # Add more cities to reach 50+ records
        ]

        locations = []
        for loc_data in locations_data:
            location = Location.objects.create(
                city=loc_data['city'],
                country=loc_data['country'],
                latitude=loc_data['lat'],
                longitude=loc_data['lon'],
                elevation=random.randint(0, 500)
            )
            locations.append(location)
            self.stdout.write(f'Created location: {location}')

        # Create metrics for each location
        now = timezone.now()
        for location in locations:
            for days_ago in range(60):  # 60 days of historical data
                timestamp = now - timedelta(days=days_ago)
                
                # Create 4 measurements per day
                for hour in [6, 12, 18, 23]:
                    measurement_time = timestamp.replace(hour=hour)
                    
                    Metric.objects.create(
                        location=location,
                        timestamp=measurement_time,
                        pm25=decimal.Decimal(random.uniform(5, 150)),
                        pm10=decimal.Decimal(random.uniform(10, 200)),
                        o3=decimal.Decimal(random.uniform(10, 100)),
                        no2=decimal.Decimal(random.uniform(10, 80)),
                        so2=decimal.Decimal(random.uniform(5, 50)),
                        temperature=decimal.Decimal(random.uniform(15, 35)),
                        humidity=decimal.Decimal(random.uniform(30, 80))
                    )

        # Create sample users
        users = []
        for i in range(10):
            user = User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='password123'
            )
            users.append(user)

        # Create alerts
        for user in users:
            for location in random.sample(locations, 3):
                Alert.objects.create(
                    user=user,
                    location=location,
                    metric_type=random.choice(['PM2.5', 'PM10', 'O3', 'NO2', 'SO2']),
                    threshold_value=decimal.Decimal(random.uniform(50, 150)),
                    is_active=random.choice([True, False])
                )

        # Create AQI records
        for location in locations:
            for days_ago in range(60):
                timestamp = now - timedelta(days=days_ago)
                aqi_value = random.randint(0, 500)
                
                # Determine category based on AQI value
                if aqi_value <= 50:
                    category = 'Good'
                    implications = 'Air quality is satisfactory.'
                elif aqi_value <= 100:
                    category = 'Moderate'
                    implications = 'Acceptable air quality.'
                else:
                    category = 'Unhealthy'
                    implications = 'Everyone may begin to experience health effects.'

                AirQualityIndex.objects.create(
                    location=location,
                    timestamp=timestamp,
                    aqi_value=aqi_value,
                    category=category,
                    dominant_pollutant=random.choice(['PM2.5', 'PM10', 'O3']),
                    health_implications=implications
                )

        self.stdout.write(self.style.SUCCESS('Successfully populated the database!'))