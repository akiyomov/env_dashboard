from django.core.management.base import BaseCommand
from dashboard.models import Location
from dashboard.services.historical_data_service import WAQIDataService, save_waqi_data
import time

class Command(BaseCommand):
    help = 'Fetch air quality data from WAQI API'

    def handle(self, *args, **kwargs):
        cities = [
            'beijing', 'shanghai', 'tokyo', 'seoul', 
            'delhi', 'london', 'paris', 'newyork'
        ]

        for city in cities:
            self.stdout.write(f"Fetching data for {city}...")
            
            location = Location.objects.filter(
                city=city.title()
            ).first()

            if not location:
                self.stdout.write(self.style.WARNING(f"Location not found for {city}, skipping..."))
                continue

            success, data = WAQIDataService.fetch_city_data(city)

            if success:
                if 'city' in data and 'geo' in data['city']:
                    location.latitude = data['city']['geo'][0]
                    location.longitude = data['city']['geo'][1]
                    location.save()

                save_success, message = save_waqi_data(location, data)
                if save_success:
                    self.stdout.write(
                        self.style.SUCCESS(f"Successfully saved data for {city}")
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"Error saving data for {city}: {message}")
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(f"Failed to fetch data for {city}: {data}")
                )

            time.sleep(3)

        self.stdout.write(self.style.SUCCESS('Data fetch completed'))