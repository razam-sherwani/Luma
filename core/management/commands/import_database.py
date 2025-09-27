from django.core.management.base import BaseCommand
from django.core import serializers
from django.db import transaction
import os
import glob

class Command(BaseCommand):
    help = 'Import database data from JSON files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data-dir',
            type=str,
            default='shared_data',
            help='Directory containing the JSON data files'
        )

    def handle(self, *args, **options):
        data_dir = options['data_dir']
        
        if not os.path.exists(data_dir):
            self.stdout.write(
                self.style.ERROR(f'Data directory {data_dir} not found!')
            )
            return
        
        self.stdout.write(f'Importing database data from {data_dir}...')
        
        with transaction.atomic():
            # Get all JSON files in the data directory
            json_files = glob.glob(os.path.join(data_dir, '*.json'))
            
            # Filter out summary.json and README.md
            data_files = [f for f in json_files if not f.endswith('summary.json')]
            
            if not data_files:
                self.stdout.write(
                    self.style.ERROR('No JSON data files found!')
                )
                return
            
            # Import each file
            for json_file in sorted(data_files):
                self.import_file(json_file)
        
        self.stdout.write(
            self.style.SUCCESS('Database import completed successfully!')
        )
        self.stdout.write('You can now run: python manage.py runserver')

    def import_file(self, json_file):
        """Import data from a single JSON file"""
        try:
            with open(json_file, 'r') as f:
                data = f.read()
            
            # Deserialize and save the data
            objects = serializers.deserialize('json', data)
            count = 0
            for obj in objects:
                obj.save()
                count += 1
            
            filename = os.path.basename(json_file)
            self.stdout.write(f'Imported {count} records from {filename}')
            
        except Exception as e:
            filename = os.path.basename(json_file)
            self.stdout.write(
                self.style.ERROR(f'Error importing {filename}: {e}')
            )
