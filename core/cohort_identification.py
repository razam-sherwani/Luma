"""
AI-Powered Cohort Identification System
This module implements intelligent cohort identification using real clinical logic
"""

from django.db.models import Q, Count, Avg, Case, When, F, Value
from django.db.models.functions import Extract
from datetime import date, timedelta
from core.models import AnonymizedPatient, PatientOutcome, EMRDataPoint, PatientCluster, ClusterInsight
import json


class CohortIdentifier:
    """
    Advanced cohort identification system that actively queries patient data
    to find high-potential, actionable patient groups
    """
    
    def __init__(self):
        self.standard_care_protocols = {
            'Type 2 Diabetes Mellitus': {
                'first_line': ['Metformin'],
                'second_line': ['Sitagliptin', 'Empagliflozin', 'Insulin Glargine'],
                'target_hba1c': 7.0,
                'required_labs': ['HbA1c', 'Glucose'],
                'monitoring_frequency': 90  # days
            },
            'Essential Hypertension': {
                'first_line': ['Lisinopril', 'Amlodipine'],
                'second_line': ['Losartan', 'Hydrochlorothiazide'],
                'target_bp_systolic': 130,
                'required_labs': ['BP_Systolic', 'Blood Pressure Systolic'],
                'monitoring_frequency': 60
            },
            'Coronary Artery Disease': {
                'first_line': ['Atorvastatin', 'Aspirin'],
                'second_line': ['Clopidogrel', 'Metoprolol'],
                'target_ldl': 70,
                'required_labs': ['LDL Cholesterol', 'Cholesterol'],
                'monitoring_frequency': 90
            },
            'Heart Failure': {
                'first_line': ['Lisinopril', 'Metoprolol'],
                'second_line': ['Furosemide', 'Spironolactone'],
                'required_labs': ['BNP', 'Creatinine'],
                'monitoring_frequency': 30
            }
        }
    
    def identify_treatment_gap_cohorts(self, hcp=None):
        """
        Identify patients who aren't receiving standard-of-care treatments
        Uses real clinical guidelines and evidence-based protocols
        """
        cohorts = []
        
        # Base queryset - filter by HCP if provided
        patients_query = AnonymizedPatient.objects.all()
        if hcp:
            patients_query = patients_query.filter(hcp=hcp)
        
        for diagnosis, protocol in self.standard_care_protocols.items():
            # Find patients with this diagnosis
            diagnosis_patients = patients_query.filter(
                primary_diagnosis__icontains=diagnosis
            )
            
            if not diagnosis_patients.exists():
                continue
            
            # Identify patients NOT on first-line therapy
            missing_first_line = []
            suboptimal_control = []
            overdue_monitoring = []
            
            for patient in diagnosis_patients:
                current_treatments = patient.current_treatments or ""
                
                # Check if on first-line therapy
                on_first_line = any(drug.lower() in current_treatments.lower() 
                                  for drug in protocol['first_line'])
                
                if not on_first_line:
                    # Check if they have contraindications or tried first-line
                    recent_outcomes = PatientOutcome.objects.filter(
                        patient=patient,
                        outcome_date__gte=date.today() - timedelta(days=365)
                    )
                    
                    # If no recent outcomes showing first-line failure, they're a candidate
                    first_line_tried = any(
                        any(drug.lower() in outcome.treatment.lower() 
                            for drug in protocol['first_line'])
                        for outcome in recent_outcomes
                    )
                    
                    if not first_line_tried:
                        missing_first_line.append({
                            'patient': patient,
                            'gap_type': 'missing_first_line',
                            'gap_type_display': 'Missing First Line',
                            'recommended_treatment': protocol['first_line'][0],
                            'evidence': f"First-line {protocol['first_line'][0]} recommended for {diagnosis}"
                        })
                
                # Check lab monitoring
                if 'monitoring_frequency' in protocol:
                    last_lab_date = self._get_last_lab_date(patient, protocol.get('required_labs', []))
                    if last_lab_date:
                        days_since_lab = (date.today() - last_lab_date).days
                        if days_since_lab > protocol['monitoring_frequency']:
                            overdue_monitoring.append({
                                'patient': patient,
                                'gap_type': 'overdue_monitoring',
                                'gap_type_display': 'Overdue Monitoring',
                                'days_overdue': days_since_lab - protocol['monitoring_frequency'],
                                'required_labs': protocol.get('required_labs', [])
                            })
                
                # Check clinical targets (if we have lab data)
                if self._check_suboptimal_control(patient, protocol):
                    suboptimal_control.append({
                        'patient': patient,
                        'gap_type': 'suboptimal_control',
                        'gap_type_display': 'Suboptimal Control',
                        'current_therapy': current_treatments,
                        'optimization_opportunity': True
                    })
            
            # Create cohort results
            if missing_first_line:
                cohorts.append({
                    'type': 'treatment_gap',
                    'type_display': 'Treatment Gap',
                    'name': f"{diagnosis} - Missing First-Line Therapy",
                    'description': f"Patients with {diagnosis} not receiving guideline-recommended first-line treatment",
                    'diagnosis': diagnosis,
                    'patients': missing_first_line,
                    'count': len(missing_first_line),
                    'clinical_impact': 'High',
                    'recommended_action': f"Consider initiating {protocol['first_line'][0]}",
                    'evidence_level': 'Grade A',
                    'priority_score': 90
                })
            
            if suboptimal_control:
                cohorts.append({
                    'type': 'optimization_opportunity',
                    'type_display': 'Optimization Opportunity',
                    'name': f"{diagnosis} - Suboptimal Control",
                    'description': f"Patients with {diagnosis} not meeting clinical targets",
                    'diagnosis': diagnosis,
                    'patients': suboptimal_control,
                    'count': len(suboptimal_control),
                    'clinical_impact': 'High',
                    'recommended_action': "Therapy intensification or optimization",
                    'evidence_level': 'Grade A',
                    'priority_score': 85
                })
            
            if overdue_monitoring:
                cohorts.append({
                    'type': 'monitoring_gap',
                    'type_display': 'Monitoring Gap',
                    'name': f"{diagnosis} - Overdue Monitoring",
                    'description': f"Patients with {diagnosis} overdue for required lab monitoring",
                    'diagnosis': diagnosis,
                    'patients': overdue_monitoring,
                    'count': len(overdue_monitoring),
                    'clinical_impact': 'Medium',
                    'recommended_action': "Schedule lab work and follow-up",
                    'evidence_level': 'Grade B',
                    'priority_score': 70
                })
        
        return sorted(cohorts, key=lambda x: x['priority_score'], reverse=True)
    
    def identify_high_risk_cohorts(self, hcp=None):
        """
        Identify high-risk patient cohorts using AI analysis
        """
        patients_query = AnonymizedPatient.objects.all()
        if hcp:
            patients_query = patients_query.filter(hcp=hcp)
        
        cohorts = []
        
        # High emergency visit cohort
        high_emergency_patients = patients_query.filter(
            emergency_visits_6m__gte=3
        ).annotate(
            risk_score=Case(
                When(emergency_visits_6m__gte=5, then=Value(0.9)),
                When(emergency_visits_6m__gte=3, then=Value(0.7)),
                default=Value(0.5)
            )
        )
        
        if high_emergency_patients.exists():
            cohorts.append({
                'type': 'high_risk',
                'type_display': 'High Risk',
                'name': 'Frequent Emergency Department Users',
                'description': 'Patients with 3+ ED visits in 6 months requiring care coordination',
                'patients': list(high_emergency_patients),
                'count': high_emergency_patients.count(),
                'clinical_impact': 'Very High',
                'recommended_action': 'Care coordination and preventive intervention',
                'ai_confidence': 0.92,
                'priority_score': 95
            })
        
        # Medication adherence issues
        poor_adherence_patients = patients_query.filter(
            medication_adherence__in=['Poor', 'Irregular']
        )
        
        if poor_adherence_patients.exists():
            cohorts.append({
                'type': 'adherence_risk',
                'type_display': 'Adherence Risk',
                'name': 'Poor Medication Adherence',
                'description': 'Patients with documented poor medication adherence',
                'patients': list(poor_adherence_patients),
                'count': poor_adherence_patients.count(),
                'clinical_impact': 'High',
                'recommended_action': 'Adherence counseling and support programs',
                'ai_confidence': 0.88,
                'priority_score': 80
            })
        
        return sorted(cohorts, key=lambda x: x['priority_score'], reverse=True)
    
    def identify_ai_discovery_cohorts(self, hcp=None):
        """
        Use AI clustering insights to identify novel patient cohorts
        """
        # Get existing AI clusters and their insights
        clusters_query = PatientCluster.objects.all()
        if hcp:
            clusters_query = clusters_query.filter(hcp=hcp)
        
        cohorts = []
        
        for cluster in clusters_query:
            # Get high-confidence insights for this cluster
            high_confidence_insights = ClusterInsight.objects.filter(
                cluster=cluster,
                confidence_score__gte=0.8,
                insight_type__in=['TREATMENT_EFFECTIVENESS', 'PATTERN_DISCOVERY']
            )
            
            for insight in high_confidence_insights:
                # Extract actionable cohorts from AI insights
                if insight.insight_type == 'TREATMENT_EFFECTIVENESS':
                    cohorts.append({
                        'type': 'ai_discovery',
                        'type_display': 'AI Discovery',
                        'name': f"AI-Discovered: {insight.title}",
                        'description': insight.description,
                        'cluster': cluster,
                        'patients': list(cluster.patients.all()),
                        'count': cluster.patient_count,
                        'clinical_impact': 'Medium-High',
                        'recommended_action': insight.actionable_recommendations,
                        'ai_confidence': insight.confidence_score,
                        'priority_score': int(insight.confidence_score * 75),
                        'supporting_data': insight.supporting_data
                    })
        
        return sorted(cohorts, key=lambda x: x['priority_score'], reverse=True)
    
    def get_all_cohorts(self, hcp=None):
        """
        Get comprehensive cohort analysis combining all identification methods
        """
        all_cohorts = []
        
        # Rule-based clinical cohorts
        treatment_gap_cohorts = self.identify_treatment_gap_cohorts(hcp)
        all_cohorts.extend(treatment_gap_cohorts)
        
        # Risk-based cohorts
        high_risk_cohorts = self.identify_high_risk_cohorts(hcp)
        all_cohorts.extend(high_risk_cohorts)
        
        # AI-discovered cohorts
        ai_cohorts = self.identify_ai_discovery_cohorts(hcp)
        all_cohorts.extend(ai_cohorts)
        
        # Sort by priority and clinical impact
        return sorted(all_cohorts, key=lambda x: x['priority_score'], reverse=True)
    
    def _get_last_lab_date(self, patient, required_labs):
        """Get the most recent lab date for required labs"""
        if not required_labs:
            return None
        
        recent_labs = EMRDataPoint.objects.filter(
            patient=patient,
            data_type='LAB_RESULT',
            metric_name__in=required_labs
        ).order_by('-date_recorded').first()
        
        return recent_labs.date_recorded if recent_labs else None
    
    def _check_suboptimal_control(self, patient, protocol):
        """Check if patient has suboptimal clinical control based on latest labs"""
        # Get most recent lab values and vital signs
        lab_data = patient.last_lab_values or {}
        vital_data = patient.vital_signs or {}
        
        if not lab_data and not vital_data:
            return False
        
        # Check diabetes control
        if 'target_hba1c' in protocol and 'HbA1c' in lab_data:
            try:
                hba1c_value = lab_data['HbA1c']
                # Handle both string ("5.8 %") and float (5.8) formats
                if isinstance(hba1c_value, str):
                    current_hba1c = float(hba1c_value.strip().rstrip('%').strip())
                else:
                    current_hba1c = float(hba1c_value)
                if current_hba1c > protocol['target_hba1c']:
                    return True
            except (ValueError, TypeError):
                pass
        
        # Check BP control - handle different field name formats
        if 'target_bp_systolic' in protocol:
            try:
                systolic = None
                # Try different field names in both lab_data and vital_data
                if 'BP_Systolic' in vital_data:
                    systolic = int(vital_data['BP_Systolic'])
                elif 'BP_Systolic' in lab_data:
                    systolic = int(lab_data['BP_Systolic'])
                elif 'Blood Pressure' in lab_data:
                    bp_reading = lab_data['Blood Pressure']
                    if isinstance(bp_reading, str) and '/' in bp_reading:
                        systolic = int(bp_reading.split('/')[0])
                elif 'Blood Pressure Systolic' in lab_data:
                    bp_value = lab_data['Blood Pressure Systolic']
                    if isinstance(bp_value, str):
                        systolic = int(bp_value.strip().split()[0])
                    else:
                        systolic = int(bp_value)
                
                if systolic and systolic > protocol['target_bp_systolic']:
                    return True
            except (ValueError, TypeError):
                pass
        
        # Check cholesterol control - handle different field names
        if 'target_ldl' in protocol:
            try:
                ldl_value = None
                # Try different field names
                if 'LDL' in lab_data:
                    ldl_value = lab_data['LDL']
                elif 'LDL Cholesterol' in lab_data:
                    ldl_value = lab_data['LDL Cholesterol']
                elif 'Cholesterol' in lab_data:
                    ldl_value = lab_data['Cholesterol']
                
                if ldl_value is not None:
                    if isinstance(ldl_value, str):
                        current_ldl = float(ldl_value.strip().split()[0])
                    else:
                        current_ldl = float(ldl_value)
                    if current_ldl > protocol['target_ldl']:
                        return True
            except (ValueError, TypeError):
                pass
        
        return False


# Global instance
cohort_identifier = CohortIdentifier()