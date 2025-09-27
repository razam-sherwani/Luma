from django.core.management.base import BaseCommand
from django.core import serializers
from core.models import *
import json
from datetime import datetime

class Command(BaseCommand):
    help = 'Export database data to JSON files for sharing'

    def handle(self, *args, **options):
        self.stdout.write('Exporting database data...')
        
        # Create a data directory
        import os
        data_dir = 'shared_data'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Export all the important data
        self.export_model_data(User, f'{data_dir}/users.json')
        self.export_model_data(UserProfile, f'{data_dir}/user_profiles.json')
        self.export_model_data(HCP, f'{data_dir}/hcps.json')
        self.export_model_data(AnonymizedPatient, f'{data_dir}/patients.json')
        self.export_model_data(PatientCluster, f'{data_dir}/clusters.json')
        self.export_model_data(PatientCohort, f'{data_dir}/cohorts.json')
        self.export_model_data(EMRDataPoint, f'{data_dir}/emr_data.json')
        self.export_model_data(PatientOutcome, f'{data_dir}/outcomes.json')
        self.export_model_data(ClusterMembership, f'{data_dir}/cluster_memberships.json')
        self.export_model_data(DrugRecommendation, f'{data_dir}/drug_recommendations.json')
        self.export_model_data(ActionableInsight, f'{data_dir}/insights.json')
        
        # Create a summary file
        self.create_summary_file(data_dir)
        
        self.stdout.write(
            self.style.SUCCESS(f'Database exported to {data_dir}/ directory')
        )
        self.stdout.write('You can now commit and push these files to share the data!')

    def export_model_data(self, model, filename):
        """Export model data to JSON file"""
        try:
            data = serializers.serialize('json', model.objects.all())
            with open(filename, 'w') as f:
                f.write(data)
            count = model.objects.count()
            self.stdout.write(f'Exported {count} {model.__name__} records to {filename}')
        except Exception as e:
            self.stdout.write(f'Error exporting {model.__name__}: {e}')

    def create_summary_file(self, data_dir):
        """Create a summary of the exported data"""
        summary = {
            'export_date': datetime.now().isoformat(),
            'description': 'ProviderPulse sample database export',
            'data_files': [
                'users.json - User accounts',
                'user_profiles.json - User role profiles',
                'hcps.json - Healthcare Provider records',
                'patients.json - Patient records',
                'clusters.json - AI-discovered patient clusters',
                'cohorts.json - Clinical patient cohorts',
                'emr_data.json - EMR data points',
                'outcomes.json - Treatment outcomes',
                'cluster_memberships.json - Patient-cluster relationships',
                'drug_recommendations.json - Drug recommendations',
                'insights.json - Actionable insights'
            ],
            'import_instructions': [
                '1. Run: python manage.py migrate',
                '2. Run: python manage.py loaddata shared_data/*.json',
                '3. Run: python manage.py runserver'
            ],
            'test_credentials': {
                'hcp': {'username': 'hcp_test', 'password': 'testpass123'},
                'hcr': {'username': 'hcr_test', 'password': 'testpass123'}
            }
        }
        
        with open(f'{data_dir}/README.md', 'w') as f:
            f.write(f"# ProviderPulse Sample Data\n\n")
            f.write(f"Exported on: {summary['export_date']}\n\n")
            f.write("## Files Included\n\n")
            for file_desc in summary['data_files']:
                f.write(f"- {file_desc}\n")
            f.write("\n## Import Instructions\n\n")
            for instruction in summary['import_instructions']:
                f.write(f"{instruction}\n")
            f.write("\n## Test Credentials\n\n")
            f.write("### Healthcare Provider (HCP)\n")
            f.write(f"- Username: {summary['test_credentials']['hcp']['username']}\n")
            f.write(f"- Password: {summary['test_credentials']['hcp']['password']}\n")
            f.write("\n### Healthcare Researcher (HCR)\n")
            f.write(f"- Username: {summary['test_credentials']['hcr']['username']}\n")
            f.write(f"- Password: {summary['test_credentials']['hcr']['password']}\n")
        
        # Also create a JSON summary
        with open(f'{data_dir}/summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
