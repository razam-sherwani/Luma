#!/usr/bin/env python
"""
Test script to verify the cohort identification fix
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'providerpulse.settings')
django.setup()

from core.cohort_identification import cohort_identifier
from core.models import AnonymizedPatient

def test_cohort_identification():
    """Test that cohort identification works without AttributeError"""
    print("Testing cohort identification system...")
    
    try:
        # Test getting all cohorts
        print("Getting all cohorts...")
        all_cohorts = cohort_identifier.get_all_cohorts()
        print(f"✓ Successfully retrieved {len(all_cohorts)} cohorts")
        
        # Print cohort types
        for cohort in all_cohorts[:5]:  # Show first 5 cohorts
            print(f"  - {cohort['name']}: {cohort['count']} patients")
        
        # Test getting treatment gap cohorts specifically  
        print("\nTesting treatment gap cohorts...")
        gap_cohorts = cohort_identifier.identify_treatment_gap_cohorts()
        print(f"✓ Successfully identified {len(gap_cohorts)} treatment gap cohorts")
        
        # Test high-risk cohorts
        print("\nTesting high-risk cohorts...")
        risk_cohorts = cohort_identifier.identify_high_risk_cohorts()
        print(f"✓ Successfully identified {len(risk_cohorts)} high-risk cohorts")
        
        print("\n✅ All tests passed! The AttributeError has been fixed.")
        return True
        
    except AttributeError as e:
        print(f"❌ AttributeError still occurs: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error occurred: {e}")
        return False

if __name__ == '__main__':
    success = test_cohort_identification()
    sys.exit(0 if success else 1)