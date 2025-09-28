"""
Simplified Real Medical Research Scraper
Uses reliable RSS feeds and web scraping methods
"""
import requests
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Optional
from .models import ResearchUpdate, HCP, ScrapedResearch
from django.conf import settings
import json
import xml.etree.ElementTree as ET
import feedparser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealMedicalResearchScraper:
    """Scrapes real medical research from verified sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Medical specialty mapping for real research
        self.specialty_keywords = {
            'CARDIOLOGY': {
                'keywords': ['cardiology', 'heart', 'cardiac', 'cardiovascular', 'coronary', 'artery', 
                           'myocardial', 'valve', 'rhythm', 'hypertension', 'cholesterol', 'stent', 'bypass'],
                'search_terms': ['heart disease', 'cardiovascular', 'cardiac surgery', 'hypertension']
            },
            'INTERNAL MEDICINE': {
                'keywords': ['internal medicine', 'diabetes', 'hypertension', 'metabolic', 'endocrine', 
                           'primary care', 'chronic disease', 'prevention', 'geriatric', 'adult medicine'],
                'search_terms': ['diabetes', 'hypertension', 'metabolic syndrome', 'chronic disease']
            },
            'ONCOLOGY': {
                'keywords': ['oncology', 'cancer', 'tumor', 'chemotherapy', 'radiation', 'immunotherapy',
                           'oncology', 'malignancy', 'carcinoma', 'sarcoma', 'leukemia', 'lymphoma'],
                'search_terms': ['cancer treatment', 'oncology', 'chemotherapy', 'immunotherapy']
            },
            'NEUROLOGY': {
                'keywords': ['neurology', 'brain', 'stroke', 'alzheimer', 'parkinson', 'migraine', 
                           'epilepsy', 'dementia', 'neuropathy', 'multiple sclerosis'],
                'search_terms': ['stroke', 'alzheimer', 'parkinson', 'neurology']
            },
            'PEDIATRICS': {
                'keywords': ['pediatrics', 'children', 'infant', 'child health', 'pediatric disease',
                           'vaccination', 'growth', 'development', 'adolescent'],
                'search_terms': ['pediatric', 'child health', 'vaccination', 'pediatric medicine']
            }
        }

    def _parse_date(self, date_str: str) -> datetime.date:
        """Parse various date formats"""
        try:
            # Try common date formats
            formats = [
                '%Y-%m-%d',
                '%Y-%m-%d %H:%M:%S',
                '%a, %d %b %Y %H:%M:%S %Z',
                '%d %b %Y',
                '%Y-%m-%dT%H:%M:%S'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            
            # If all else fails, return today's date
            return datetime.now().date()
        except:
            return datetime.now().date()

    def scrape_medical_news_today(self, specialty: str, max_results: int = 5) -> List[Dict]:
        """Scrape from Medical News Today using web scraping"""
        try:
            logger.info(f"Scraping Medical News Today for {specialty}...")
            
            specialty_data = self.specialty_keywords.get(specialty, self.specialty_keywords['INTERNAL MEDICINE'])
            search_term = specialty_data['search_terms'][0]
            
            # Search Medical News Today
            search_url = f"https://www.medicalnewstoday.com/search?q={search_term}"
            
            response = self.session.get(search_url, timeout=15)
            if response.status_code != 200:
                logger.warning(f"Medical News Today returned status {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Find article links
            article_links = soup.find_all('a', href=re.compile(r'/articles/'))
            
            for link in article_links[:max_results]:
                try:
                    article_url = link.get('href')
                    if not article_url.startswith('http'):
                        article_url = 'https://www.medicalnewstoday.com' + article_url
                    
                    # Get article details
                    article_response = self.session.get(article_url, timeout=10)
                    if article_response.status_code == 200:
                        article_soup = BeautifulSoup(article_response.content, 'html.parser')
                        
                        title_elem = article_soup.find('h1')
                        title = title_elem.text.strip() if title_elem else 'No title'
                        
                        # Find abstract/summary
                        abstract_elem = article_soup.find('div', class_=re.compile(r'summary|abstract|intro'))
                        if not abstract_elem:
                            abstract_elem = article_soup.find('p')
                        abstract = abstract_elem.text.strip() if abstract_elem else 'No abstract available'
                        
                        # Find date
                        date_elem = article_soup.find('time')
                        pub_date = self._parse_date(date_elem.get('datetime')) if date_elem and date_elem.get('datetime') else datetime.now().date()
                        
                        article = {
                            'title': title,
                            'abstract': abstract[:500] + '...' if len(abstract) > 500 else abstract,
                            'authors': 'Medical News Today Staff',
                            'journal': 'Medical News Today',
                            'publication_date': pub_date,
                            'specialty': specialty,
                            'source_url': article_url,
                            'relevance_score': 0.7,
                            'source': 'Medical News Today'
                        }
                        articles.append(article)
                        
                except Exception as e:
                    logger.warning(f"Error scraping article from Medical News Today: {e}")
                    continue
            
            logger.info(f"Scraped {len(articles)} articles from Medical News Today")
            return articles
            
        except Exception as e:
            logger.error(f"Medical News Today scraping failed for {specialty}: {e}")
            return []

    def scrape_pubmed_rss(self, specialty: str, max_results: int = 5) -> List[Dict]:
        """Scrape from PubMed using RSS feeds"""
        try:
            logger.info(f"Scraping PubMed RSS for {specialty}...")
            
            specialty_data = self.specialty_keywords.get(specialty, self.specialty_keywords['INTERNAL MEDICINE'])
            keyword = specialty_data['keywords'][0]
            
            # Use PubMed RSS feed
            rss_url = f"https://pubmed.ncbi.nlm.nih.gov/rss/search/{keyword}/?limit=10&utm_campaign=pubmed-2&fc=Y"
            
            response = self.session.get(rss_url, timeout=15)
            if response.status_code != 200:
                logger.warning(f"PubMed RSS returned status {response.status_code}")
                return []
            
            # Parse RSS feed
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')
            
            articles = []
            for item in items[:max_results]:
                try:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    desc_elem = item.find('description')
                    pub_date_elem = item.find('pubDate')
                    
                    if title_elem and link_elem:
                        title = title_elem.text.strip()
                        link = link_elem.text.strip()
                        abstract = desc_elem.text.strip() if desc_elem else 'No abstract available'
                        pub_date = self._parse_date(pub_date_elem.text.strip()) if pub_date_elem else datetime.now().date()
                        
                        article = {
                            'title': title,
                            'abstract': abstract,
                            'authors': 'Multiple Authors',
                            'journal': 'PubMed',
                            'publication_date': pub_date,
                            'specialty': specialty,
                            'source_url': link,
                            'relevance_score': 0.9,
                            'source': 'PubMed'
                        }
                        articles.append(article)
                        
                except Exception as e:
                    logger.warning(f"Error parsing PubMed RSS item: {e}")
                    continue
            
            logger.info(f"Scraped {len(articles)} articles from PubMed RSS")
            return articles
            
        except Exception as e:
            logger.error(f"PubMed RSS scraping failed for {specialty}: {e}")
            return []

    def scrape_all_real_sources(self, specialty: str, max_results: int = 10) -> List[Dict]:
        """Scrape from all available sources"""
        all_articles = []
        
        # Scrape from different sources
        sources = [
            self.scrape_pubmed_rss,
            self.scrape_medical_news_today,
        ]
        
        for source_func in sources:
            try:
                articles = source_func(specialty, max_results // len(sources))
                all_articles.extend(articles)
                time.sleep(1)  # Be respectful to servers
            except Exception as e:
                logger.error(f"Source {source_func.__name__} failed: {e}")
                continue
        
        # Remove duplicates based on title
        unique_articles = []
        seen_titles = set()
        for article in all_articles:
            if article['title'] not in seen_titles:
                unique_articles.append(article)
                seen_titles.add(article['title'])
        
        logger.info(f"Total unique articles scraped for {specialty}: {len(unique_articles)}")
        return unique_articles[:max_results]

    def update_research_database_real(self):
        """Update the research database with real scraped data"""
        from django.db import transaction
        
        total_scraped = 0
        specialty_distribution = {}
        
        with transaction.atomic():
            for specialty in self.specialty_keywords.keys():
                logger.info(f"Scraping real research for specialty: {specialty}")
                articles = self.scrape_all_real_sources(specialty, max_results=5)
                
                scraped_count = 0
                for article_data in articles:
                    try:
                        # Create ScrapedResearch
                        scraped_research, created = ScrapedResearch.objects.get_or_create(
                            title=article_data['title'],
                            source_url=article_data['source_url'],
                            defaults={
                                'abstract': article_data['abstract'],
                                'authors': article_data['authors'],
                                'journal': article_data['journal'],
                                'publication_date': article_data['publication_date'],
                                'specialties': [article_data['specialty']],
                                'relevance_score': article_data['relevance_score'],
                                'keywords': self._extract_keywords(article_data['title'] + " " + article_data['abstract']),
                                'conditions_mentioned': self._extract_conditions(article_data['title'] + " " + article_data['abstract']),
                                'treatments_mentioned': self._extract_treatments(article_data['title'] + " " + article_data['abstract']),
                                'source_database': article_data['source']
                            }
                        )
                        
                        if created:
                            scraped_count += 1
                            total_scraped += 1
                            
                    except Exception as e:
                        logger.error(f"Error processing article '{article_data.get('title', 'N/A')}': {e}")
                        continue
                
                specialty_distribution[specialty] = scraped_count
                logger.info(f"Scraped {scraped_count} articles for {specialty}")
        
        logger.info(f"Real research update completed. Total articles scraped: {total_scraped}")
        return {'total_scraped': total_scraped, 'specialty_distribution': specialty_distribution}

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        words = re.findall(r'\b\w+\b', text.lower())
        common_words = {'a', 'an', 'the', 'in', 'on', 'of', 'and', 'or', 'for', 'with', 'is', 'are', 'this', 'that', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must'}
        keywords = [word for word in words if word not in common_words and len(word) > 3]
        return list(set(keywords))[:10]  # Limit to 10 keywords

    def _extract_conditions(self, text: str) -> List[str]:
        """Extract medical conditions from text"""
        conditions = []
        condition_patterns = [
            r'diabetes', r'hypertension', r'cancer', r'stroke', r'alzheimer', 
            r'parkinson', r'heart disease', r'coronary', r'asthma', r'copd'
        ]
        
        for pattern in condition_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                conditions.append(pattern.replace('r\'', '').replace('\'', '').title())
        
        return list(set(conditions))

    def _extract_treatments(self, text: str) -> List[str]:
        """Extract treatments from text"""
        treatments = []
        treatment_patterns = [
            r'insulin', r'chemotherapy', r'statin', r'surgery', r'radiation',
            r'immunotherapy', r'vaccination', r'medication', r'therapy'
        ]
        
        for pattern in treatment_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                treatments.append(pattern.replace('r\'', '').replace('\'', '').title())
        
        return list(set(treatments))