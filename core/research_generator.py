"""
Simplified Medical Research Generator
Creates realistic medical research updates without external dependencies
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict
from django.utils import timezone
from .models import ResearchUpdate, HCP
from .real_research_urls import get_real_research_url
import logging

logger = logging.getLogger(__name__)

class SimplifiedResearchGenerator:
    """Generates realistic medical research updates using templates and medical knowledge"""
    
    def __init__(self):
        # Medical journal URLs for realistic linking
        self.journal_urls = {
            'CARDIOVASCULAR DISEASE (CARDIOLOGY)': [
                'https://www.ahajournals.org/doi/full/',
                'https://www.jacc.org/doi/',
                'https://academic.oup.com/eurheartj/article/',
                'https://www.onlinejacc.org/content/',
                'https://www.ahajournals.org/doi/abs/'
            ],
            'INTERNAL MEDICINE': [
                'https://www.nejm.org/doi/full/',
                'https://jamanetwork.com/journals/jamainternalmedicine/fullarticle/',
                'https://www.acpjournals.org/doi/',
                'https://www.bmj.com/content/',
                'https://www.thelancet.com/journals/lancet/article/'
            ],
            'FAMILY PRACTICE': [
                'https://www.aafp.org/pubs/afp/issues/',
                'https://www.stfm.org/familymedicine/vol/',
                'https://www.jabfm.org/content/',
                'https://link.springer.com/article/',
                'https://www.cfp.ca/content/'
            ],
            'GENERAL SURGERY': [
                'https://www.journalacs.org/article/',
                'https://journals.lww.com/annalsofsurgery/Abstract/',
                'https://www.surgery.org/article/',
                'https://www.elsevier.com/locate/surgery/article/',
                'https://link.springer.com/article/'
            ],
            'ORTHOPEDIC SURGERY': [
                'https://journals.lww.com/jbjsjournal/Abstract/',
                'https://link.springer.com/article/',
                'https://www.orthosurg.org.cn/EN/abstract/article/',
                'https://www.clinorthop.org/article/',
                'https://www.arthroscopyjournal.org/article/'
            ],
            'RADIATION ONCOLOGY': [
                'https://www.redjournal.org/article/',
                'https://ascopubs.org/doi/',
                'https://aacrjournals.org/cancerres/article/',
                'https://link.springer.com/article/',
                'https://www.thelancet.com/journals/lanonc/article/'
            ],
            'INFECTIOUS DISEASE': [
                'https://academic.oup.com/cid/article/',
                'https://www.journalofdisease.org/article/',
                'https://journals.asm.org/doi/',
                'https://www.cambridge.org/core/journals/infection-control-and-hospital-epidemiology/article/',
                'https://link.springer.com/article/'
            ],
            'UROLOGY': [
                'https://www.auajournals.org/doi/',
                'https://www.europeanurology.com/article/',
                'https://www.goldjournal.net/article/',
                'https://link.springer.com/article/',
                'https://www.elsevier.com/locate/urology/article/'
            ],
            'PAIN MANAGEMENT': [
                'https://journals.lww.com/painmedicine/Abstract/',
                'https://www.painjournalonline.com/article/',
                'https://www.springer.com/journal/12630/article/',
                'https://onlinelibrary.wiley.com/doi/',
                'https://www.anesthesia-analgesia.org/article/'
            ],
            'PHYSICAL MEDICINE AND REHABILITATION': [
                'https://www.archives-pmr.org/article/',
                'https://journals.lww.com/ajpmr/Abstract/',
                'https://www.pmrjournal.org/article/',
                'https://link.springer.com/article/',
                'https://www.elsevier.com/locate/pmr/article/'
            ]
        }
        
        # Enhanced medical specialty templates with real medical terminology
        self.research_templates = {
            'CARDIOVASCULAR DISEASE (CARDIOLOGY)': [
                {
                    'template': 'Novel {drug_class} {drug_name} Reduces {condition} Risk by {percent}% in Phase III Trial',
                    'abstract_template': 'A multicenter, randomized, double-blind trial involving {patient_count} patients demonstrated that {drug_name} significantly reduced {condition} events compared to placebo. The study showed a {percent}% relative risk reduction with excellent safety profile.',
                    'variables': {
                        'drug_class': ['ACE Inhibitor', 'Beta-Blocker', 'Calcium Channel Blocker', 'ARB', 'SGLT2 Inhibitor'],
                        'drug_name': ['Cardioplex', 'Vasculin', 'Heartguard', 'Coronex', 'Ventrimax'],
                        'condition': ['Myocardial Infarction', 'Heart Failure', 'Atrial Fibrillation', 'Coronary Artery Disease'],
                        'percent': ['25', '30', '35', '40', '45'],
                        'patient_count': ['2,847', '3,251', '4,102', '5,683', '6,924']
                    }
                },
                {
                    'template': 'Advanced {procedure} Technique Improves {outcome} in {population}',
                    'abstract_template': 'New minimally invasive {procedure} approach shows significant improvement in {outcome} outcomes. The technique reduced procedure time by {time_reduction} minutes and improved patient recovery.',
                    'variables': {
                        'procedure': ['PCI', 'CABG', 'TAVR', 'Catheter Ablation', 'Valve Replacement'],
                        'outcome': ['Survival Rate', 'Recovery Time', 'Quality of Life', 'Procedural Success'],
                        'population': ['High-Risk Patients', 'Elderly Patients', 'Diabetic Patients', 'Acute MI Patients'],
                        'time_reduction': ['15', '20', '25', '30', '35']
                    }
                }
            ],
            'INTERNAL MEDICINE': [
                {
                    'template': 'AI-Powered {diagnostic_tool} Enhances Early Detection of {condition}',
                    'abstract_template': 'Machine learning algorithm analyzing {data_type} achieved {accuracy}% accuracy in detecting {condition}, potentially enabling earlier intervention and improved outcomes.',
                    'variables': {
                        'diagnostic_tool': ['Blood Panel Analysis', 'Imaging Recognition', 'Risk Stratification', 'Biomarker Panel'],
                        'condition': ['Type 2 Diabetes', 'Chronic Kidney Disease', 'Metabolic Syndrome', 'Autoimmune Disorders'],
                        'data_type': ['laboratory values', 'clinical parameters', 'patient history', 'biomarker profiles'],
                        'accuracy': ['89', '92', '94', '96', '87']
                    }
                },
                {
                    'template': 'Updated {guideline} Guidelines Recommend {intervention} for {population}',
                    'abstract_template': 'Latest evidence-based guidelines now recommend {intervention} as first-line therapy for {population}, based on recent clinical trials showing superior outcomes.',
                    'variables': {
                        'guideline': ['ACP', 'ADA', 'ACC/AHA', 'ESC', 'KDIGO'],
                        'intervention': ['Dual Therapy', 'Lifestyle Modification', 'Targeted Screening', 'Risk-Based Treatment'],
                        'population': ['Pre-diabetic Adults', 'CKD Patients', 'Hypertensive Patients', 'High-Risk Individuals']
                    }
                }
            ],
            'FAMILY PRACTICE': [
                {
                    'template': 'Telehealth {service} Integration Improves {outcome} in Primary Care',
                    'abstract_template': 'Implementation of telehealth {service} in primary care settings resulted in {improvement}% improvement in {outcome} and increased patient satisfaction scores.',
                    'variables': {
                        'service': ['Consultation Platform', 'Remote Monitoring', 'Digital Health Tools', 'Virtual Care'],
                        'outcome': ['Patient Adherence', 'Chronic Disease Management', 'Preventive Care Uptake', 'Follow-up Compliance'],
                        'improvement': ['28', '35', '42', '38', '45']
                    }
                },
                {
                    'template': 'Community-Based {program} Reduces {condition} Incidence by {percent}%',
                    'abstract_template': 'Large-scale community intervention program targeting {risk_factors} successfully reduced {condition} incidence, demonstrating the effectiveness of preventive care strategies.',
                    'variables': {
                        'program': ['Screening Initiative', 'Wellness Program', 'Health Education', 'Vaccination Campaign'],
                        'condition': ['Diabetes', 'Hypertension', 'Cardiovascular Disease', 'Infectious Disease'],
                        'risk_factors': ['lifestyle factors', 'environmental exposures', 'genetic predisposition', 'social determinants'],
                        'percent': ['22', '27', '31', '35', '29']
                    }
                }
            ],
            'GENERAL SURGERY': [
                {
                    'template': 'Robotic {procedure} Shows {percent}% Reduction in {complication}',
                    'abstract_template': 'Robotic-assisted {procedure} demonstrated significant reduction in {complication} rates compared to traditional open surgery, with faster recovery times and improved patient outcomes.',
                    'variables': {
                        'procedure': ['Cholecystectomy', 'Hernia Repair', 'Colorectal Surgery', 'Appendectomy', 'Thyroidectomy'],
                        'complication': ['Surgical Site Infection', 'Post-operative Pain', 'Hospital Stay Length', 'Recovery Time'],
                        'percent': ['32', '28', '35', '40', '25']
                    }
                },
                {
                    'template': 'Enhanced Recovery After Surgery (ERAS) Protocol Improves {outcome}',
                    'abstract_template': 'Implementation of standardized ERAS protocol across multiple surgical specialties resulted in significant improvements in {outcome} and reduced healthcare costs.',
                    'variables': {
                        'outcome': ['Patient Satisfaction', 'Length of Stay', 'Complication Rates', 'Recovery Speed', 'Readmission Rates']
                    }
                }
            ],
            'ORTHOPEDIC SURGERY': [
                {
                    'template': 'Advanced {implant} Technology Extends {joint} Replacement Longevity',
                    'abstract_template': 'Next-generation {implant} materials and design innovations show promise for extending {joint} replacement durability, with early studies indicating {years}-year survival rates.',
                    'variables': {
                        'implant': ['Ceramic', 'Titanium', 'Polyethylene', 'Metal-on-Metal', 'Biomimetic'],
                        'joint': ['Hip', 'Knee', 'Shoulder', 'Ankle', 'Wrist'],
                        'years': ['20', '25', '30', '15', '18']
                    }
                },
                {
                    'template': 'Minimally Invasive {procedure} Reduces Recovery Time by {percent}%',
                    'abstract_template': 'New minimally invasive approach to {procedure} demonstrates significant reduction in recovery time and improved functional outcomes in {population}.',
                    'variables': {
                        'procedure': ['ACL Reconstruction', 'Rotator Cuff Repair', 'Spinal Fusion', 'Fracture Fixation'],
                        'population': ['Athletes', 'Elderly Patients', 'Active Adults', 'Young Patients'],
                        'percent': ['35', '40', '45', '30', '38']
                    }
                }
            ],
            'RADIATION ONCOLOGY': [
                {
                    'template': 'Precision {therapy} Improves {outcome} in {cancer_type}',
                    'abstract_template': 'Advanced {therapy} targeting specific molecular pathways shows remarkable efficacy in {cancer_type}, with {response_rate}% objective response rate in clinical trials.',
                    'variables': {
                        'therapy': ['Immunotherapy', 'Targeted Therapy', 'CAR-T Cell Therapy', 'Proton Beam Therapy'],
                        'cancer_type': ['Non-Small Cell Lung Cancer', 'Melanoma', 'Breast Cancer', 'Prostate Cancer', 'Brain Tumors'],
                        'outcome': ['Overall Survival', 'Progression-Free Survival', 'Quality of Life', 'Treatment Response'],
                        'response_rate': ['65', '72', '58', '81', '69']
                    }
                },
                {
                    'template': 'Novel {biomarker} Predicts {therapy} Response in {cancer_type}',
                    'abstract_template': 'Discovery of {biomarker} as predictive marker for {therapy} response enables personalized treatment selection and improved outcomes in {cancer_type}.',
                    'variables': {
                        'biomarker': ['Genetic Mutation', 'Protein Expression', 'Circulating DNA', 'Immune Signature'],
                        'therapy': ['Checkpoint Inhibitor', 'Chemotherapy', 'Radiation Therapy', 'Targeted Agent'],
                        'cancer_type': ['Lung Cancer', 'Colorectal Cancer', 'Ovarian Cancer', 'Pancreatic Cancer']
                    }
                }
            ],
            'INFECTIOUS DISEASE': [
                {
                    'template': 'Novel {antibiotic_class} Effective Against {pathogen} Resistance',
                    'abstract_template': 'New {antibiotic_class} demonstrates potent activity against multidrug-resistant {pathogen}, offering hope for treating previously untreatable infections.',
                    'variables': {
                        'antibiotic_class': ['Beta-lactam', 'Fluoroquinolone', 'Macrolide', 'Carbapenem', 'Oxazolidinone'],
                        'pathogen': ['Staphylococcus aureus', 'Pseudomonas aeruginosa', 'Acinetobacter', 'Enterococcus', 'Klebsiella']
                    }
                },
                {
                    'template': 'Rapid {diagnostic} Test Reduces {infection} Treatment Delay',
                    'abstract_template': 'Point-of-care {diagnostic} testing enables same-day pathogen identification and antimicrobial susceptibility, reducing treatment delays and improving outcomes.',
                    'variables': {
                        'diagnostic': ['PCR', 'Antigen', 'Molecular', 'Serologic', 'Culture-Independent'],
                        'infection': ['Sepsis', 'Pneumonia', 'UTI', 'Bloodstream Infection', 'Meningitis']
                    }
                }
            ],
            'UROLOGY': [
                {
                    'template': 'Minimally Invasive {procedure} Improves {outcome} in {condition}',
                    'abstract_template': 'Advanced laparoscopic {procedure} technique shows superior outcomes compared to traditional approaches, with reduced morbidity and faster recovery.',
                    'variables': {
                        'procedure': ['Nephrectomy', 'Prostatectomy', 'Cystectomy', 'Pyeloplasty', 'Stone Removal'],
                        'outcome': ['Functional Outcome', 'Cosmetic Result', 'Recovery Time', 'Complication Rate'],
                        'condition': ['Kidney Cancer', 'Prostate Cancer', 'Bladder Cancer', 'Kidney Stones', 'BPH']
                    }
                }
            ],
            'PAIN MANAGEMENT': [
                {
                    'template': 'Non-Opioid {therapy} Effective for {pain_type} Management',
                    'abstract_template': 'Alternative {therapy} approach demonstrates significant pain reduction in {pain_type} without opioid-related side effects, offering safer treatment option.',
                    'variables': {
                        'therapy': ['Nerve Block', 'Radiofrequency Ablation', 'Spinal Cord Stimulation', 'Regenerative Medicine'],
                        'pain_type': ['Chronic Low Back Pain', 'Neuropathic Pain', 'Arthritis Pain', 'Cancer Pain', 'Fibromyalgia']
                    }
                }
            ],
            'PHYSICAL MEDICINE AND REHABILITATION': [
                {
                    'template': 'Advanced {therapy} Accelerates Recovery in {condition}',
                    'abstract_template': 'Innovative {therapy} protocol shows significant improvement in functional recovery and quality of life for patients with {condition}.',
                    'variables': {
                        'therapy': ['Robotic Therapy', 'Virtual Reality Training', 'Electrical Stimulation', 'Aquatic Therapy'],
                        'condition': ['Stroke', 'Spinal Cord Injury', 'Traumatic Brain Injury', 'Multiple Sclerosis', 'Parkinson Disease']
                    }
                }
            ]
        }
    
    def _generate_realistic_url(self, specialty: str) -> str:
        """Generate a realistic journal URL for the given specialty"""
        # Use real research URLs from our database
        return get_real_research_url(specialty)

    def generate_research_for_specialty(self, specialty: str, count: int = 3) -> List[Dict]:
        """Generate realistic research articles for a specific specialty"""
        articles = []
        
        # Get templates for this specialty, fallback to Internal Medicine
        templates = self.research_templates.get(specialty, self.research_templates['INTERNAL MEDICINE'])
        
        for i in range(count):
            template_data = random.choice(templates)
            
            # Generate title
            title = template_data['template']
            for variable, options in template_data['variables'].items():
                placeholder = f'{{{variable}}}'
                if placeholder in title:
                    title = title.replace(placeholder, random.choice(options))
            
            # Generate abstract
            abstract = template_data.get('abstract_template', 'Clinical research study demonstrates significant improvements in patient outcomes using innovative medical approaches.')
            for variable, options in template_data['variables'].items():
                placeholder = f'{{{variable}}}'
                if placeholder in abstract:
                    abstract = abstract.replace(placeholder, random.choice(options))
            
            # Generate realistic date (within last 30 days)
            days_ago = random.randint(1, 30)
            research_date = datetime.now().date() - timedelta(days=days_ago)
            
            articles.append({
                'title': title,
                'abstract': abstract,
                'specialty': specialty,
                'date': research_date,
                'source': random.choice(['Clinical Research Network', 'Medical Journal Database', 'International Medical Consortium', 'Academic Medical Centers']),
                'source_url': self._generate_realistic_url(specialty),
                'relevance_score': random.uniform(0.7, 1.0),
                'is_high_impact': random.choice([True, False, False])  # 33% chance of high impact
            })
        
        return articles

    def update_all_specialties(self) -> Dict:
        """Generate research for all medical specialties"""
        logger.info("Generating research updates for all specialties...")
        
        # Clear old research (keep last 30 days)
        cutoff_date = datetime.now().date() - timedelta(days=30)
        old_research = ResearchUpdate.objects.filter(date__lt=cutoff_date)
        deleted_count = old_research.count()
        old_research.delete()
        
        created_count = 0
        updated_count = 0
        
        # Generate research for each specialty
        for specialty in self.research_templates.keys():
            articles = self.generate_research_for_specialty(specialty, 3)
            
            for article in articles:
                try:
                    # Check if similar article exists (by title similarity)
                    existing = ResearchUpdate.objects.filter(
                        headline__icontains=article['title'][:50]  # First 50 chars
                    ).first()
                    
                    if existing:
                        # Update existing
                        existing.specialty = article['specialty']
                        existing.date = article['date']
                        existing.abstract = article['abstract']
                        existing.source = article['source']
                        existing.source_url = article.get('source_url', '')
                        existing.relevance_score = article['relevance_score']
                        existing.is_high_impact = article['is_high_impact']
                        existing.save()
                        updated_count += 1
                    else:
                        # Create new
                        ResearchUpdate.objects.create(
                            headline=article['title'],
                            specialty=article['specialty'],
                            date=article['date'],
                            abstract=article['abstract'],
                            source=article['source'],
                            source_url=article.get('source_url', ''),
                            relevance_score=article['relevance_score'],
                            is_high_impact=article['is_high_impact']
                        )
                        created_count += 1
                        
                except Exception as e:
                    logger.error(f"Error saving article '{article['title']}': {e}")
        
        # Calculate results
        result = {
            'deleted_old': deleted_count,
            'created_new': created_count,
            'updated_existing': updated_count,
            'total_articles': ResearchUpdate.objects.count(),
            'specialty_distribution': self._get_specialty_distribution()
        }
        
        logger.info(f"Research generation complete: {result}")
        return result

    def _get_specialty_distribution(self) -> Dict:
        """Get distribution of research by specialty"""
        from django.db.models import Count
        
        distribution = ResearchUpdate.objects.values('specialty').annotate(
            count=Count('specialty')
        ).order_by('-count')
        
        return {item['specialty']: item['count'] for item in distribution}

    def get_personalized_research(self, hcp_specialty: str, limit: int = 10) -> List:
        """Get personalized research for an HCP based on their specialty"""
        try:
            # Get specialty-specific research (60% of results)
            specialty_limit = int(limit * 0.6)
            specialty_research = ResearchUpdate.objects.filter(
                specialty=hcp_specialty
            ).order_by('-relevance_score', '-date')[:specialty_limit]
            
            # Get high-impact research from related specialties (25% of results)
            related_limit = int(limit * 0.25)
            related_specialties = self._get_related_specialties(hcp_specialty)
            related_research = ResearchUpdate.objects.filter(
                specialty__in=related_specialties,
                is_high_impact=True
            ).exclude(
                specialty=hcp_specialty
            ).order_by('-relevance_score', '-date')[:related_limit]
            
            # Get general high-impact research (15% of results)
            general_limit = limit - specialty_limit - related_limit
            general_research = ResearchUpdate.objects.filter(
                is_high_impact=True
            ).exclude(
                specialty=hcp_specialty
            ).exclude(
                specialty__in=related_specialties
            ).order_by('-relevance_score', '-date')[:general_limit]
            
            # Combine all research
            all_research = list(specialty_research) + list(related_research) + list(general_research)
            return all_research[:limit]
            
        except Exception as e:
            logger.error(f"Error getting personalized research: {e}")
            return ResearchUpdate.objects.order_by('-relevance_score', '-date')[:limit]

    def _get_related_specialties(self, specialty: str) -> List[str]:
        """Get related medical specialties"""
        specialty_relationships = {
            'CARDIOVASCULAR DISEASE (CARDIOLOGY)': ['INTERNAL MEDICINE', 'GENERAL SURGERY'],
            'INTERNAL MEDICINE': ['FAMILY PRACTICE', 'CARDIOVASCULAR DISEASE (CARDIOLOGY)', 'INFECTIOUS DISEASE'],
            'FAMILY PRACTICE': ['INTERNAL MEDICINE', 'PAIN MANAGEMENT'],
            'GENERAL SURGERY': ['ORTHOPEDIC SURGERY', 'UROLOGY', 'RADIATION ONCOLOGY'],
            'ORTHOPEDIC SURGERY': ['GENERAL SURGERY', 'PHYSICAL MEDICINE AND REHABILITATION', 'PAIN MANAGEMENT'],
            'RADIATION ONCOLOGY': ['INTERNAL MEDICINE', 'GENERAL SURGERY'],
            'INFECTIOUS DISEASE': ['INTERNAL MEDICINE', 'FAMILY PRACTICE'],
            'UROLOGY': ['GENERAL SURGERY', 'INTERNAL MEDICINE'],
            'PAIN MANAGEMENT': ['FAMILY PRACTICE', 'PHYSICAL MEDICINE AND REHABILITATION', 'ORTHOPEDIC SURGERY'],
            'PHYSICAL MEDICINE AND REHABILITATION': ['ORTHOPEDIC SURGERY', 'PAIN MANAGEMENT']
        }
        
        return specialty_relationships.get(specialty, ['INTERNAL MEDICINE'])


# Utility function for easy access
def generate_medical_research():
    """Utility function to generate medical research - simpler version without web scraping"""
    generator = SimplifiedResearchGenerator()
    return generator.update_all_specialties()