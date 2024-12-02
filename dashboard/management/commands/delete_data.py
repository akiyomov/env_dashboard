from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from dashboard.models import Metric, AirQualityIndex, Location
from django.db.models import Q

class Command(BaseCommand):
    help = 'Delete data based on various conditions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            choices=['metric', 'aqi', 'all'],
            help='Choose model: metric, aqi, or all'
        )
        
        parser.add_argument(
            '--city',
            type=str,
            help='Filter by city name'
        )

        parser.add_argument(
            '--country',
            type=str,
            help='Filter by country name'
        )

        parser.add_argument(
            '--future',
            action='store_true',
            help='Delete future records'
        )

        parser.add_argument(
            '--before',
            type=str,
            help='Delete records before this date (YYYY-MM-DD)'
        )

        parser.add_argument(
            '--after',
            type=str,
            help='Delete records after this date (YYYY-MM-DD)'
        )

        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt'
        )

    def handle(self, *args, **options):
        models_to_clean = []
        if options['model'] == 'metric':
            models_to_clean = [Metric]
        elif options['model'] == 'aqi':
            models_to_clean = [AirQualityIndex]
        elif options['model'] == 'all':
            models_to_clean = [Metric, AirQualityIndex]
        else:
            self.stdout.write(self.style.ERROR('Please specify a model using --model'))
            return

        conditions = Q()

        if options['city'] or options['country']:
            locations = Location.objects.all()
            if options['city']:
                locations = locations.filter(city__icontains=options['city'])
            if options['country']:
                locations = locations.filter(country__icontains=options['country'])
            conditions &= Q(location__in=locations)

        if options['future']:
            conditions &= Q(timestamp__gt=timezone.now())
        
        if options['before']:
            try:
                before_date = datetime.strptime(options['before'], '%Y-%m-%d')
                conditions &= Q(timestamp__lt=before_date)
            except ValueError:
                self.stdout.write(self.style.ERROR('Invalid date format for --before. Use YYYY-MM-DD'))
                return

        if options['after']:
            try:
                after_date = datetime.strptime(options['after'], '%Y-%m-%d')
                conditions &= Q(timestamp__gt=after_date)
            except ValueError:
                self.stdout.write(self.style.ERROR('Invalid date format for --after. Use YYYY-MM-DD'))
                return

        for model in models_to_clean:
            queryset = model.objects.filter(conditions)
            count = queryset.count()
            
            self.stdout.write(f"Will delete {count} records from {model.__name__}")
            
            if count > 0 and not options['force']:
                confirm = input(f"Are you sure you want to delete these {model.__name__} records? [y/N]: ")
                if confirm.lower() != 'y':
                    self.stdout.write(self.style.WARNING(f"Skipping deletion of {model.__name__} records"))
                    continue

            deleted_count = queryset.delete()[0]
            self.stdout.write(
                self.style.SUCCESS(f"Successfully deleted {deleted_count} {model.__name__} records")
            )