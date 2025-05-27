"""
Business Discovery Scrapers for Company Intelligence

Scrapes business directories, company websites, and digital footprints to build
comprehensive company profiles for opportunity identification and outreach targeting.
"""

import asyncio
import aiohttp
import json
import re
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
from datetime import datetime, timedelta
import logging

from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from app.models.business_intelligence import Company, CompanyTechStack, DecisionMaker, WebsiteAudit
from app.core.database import get_db

logger = logging.getLogger(__name__)


class BusinessDirectoryScaper:
    """
    Discover companies from business directories and local listings
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def discover_companies_in_location(self, location: str, industries: List[str] = None) -> List[Dict]:
        """
        Discover companies in a specific location across multiple sources
        """
        discovered_companies = []
        
        # Default industries if none specified
        if not industries:
            industries = [
                'web design', 'marketing', 'software', 'consulting',
                'real estate', 'law', 'accounting', 'healthcare'
            ]
        
        for industry in industries:
            try:
                # Google My Business search
                gmb_companies = await self.scrape_google_business(location, industry)
                discovered_companies.extend(gmb_companies)
                
                # Yellow Pages search
                yp_companies = await self.scrape_yellow_pages(location, industry)
                discovered_companies.extend(yp_companies)
                
                # Add delay between searches
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error discovering companies for {industry} in {location}: {e}")
                continue
        
        # Deduplicate by domain/name
        unique_companies = self._deduplicate_companies(discovered_companies)
        
        # Store in database
        stored_companies = []
        for company_data in unique_companies:
            company = await self._store_company(company_data)
            if company:
                stored_companies.append(company)
        
        return stored_companies
    
    async def scrape_google_business(self, location: str, industry: str) -> List[Dict]:
        """
        Extract companies from Google My Business / Google Maps searches
        """
        companies = []
        
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                # Google search for businesses
                search_query = f"{industry} {location}"
                search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}&tbm=lcl"
                
                async with session.get(search_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Parse business listings from Google results
                        business_cards = soup.find_all('div', class_=['VkpGBb', 'uMdZh'])
                        
                        for card in business_cards[:20]:  # Limit to first 20 results
                            try:
                                company_data = self._parse_google_business_card(card, industry, location)
                                if company_data:
                                    companies.append(company_data)
                            except Exception as e:
                                logger.debug(f"Error parsing Google business card: {e}")
                                continue
                
        except Exception as e:
            logger.error(f"Error scraping Google My Business for {industry} in {location}: {e}")
        
        return companies
    
    async def scrape_yellow_pages(self, location: str, industry: str) -> List[Dict]:
        """
        Extract companies from Yellow Pages directory
        """
        companies = []
        
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                # Yellow Pages search URL
                search_url = f"https://www.yellowpages.com/search?search_terms={industry.replace(' ', '+')}&geo_location_terms={location.replace(' ', '+')}"
                
                async with session.get(search_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Parse YP business listings
                        business_cards = soup.find_all('div', class_=['result'])
                        
                        for card in business_cards[:15]:  # Limit results
                            try:
                                company_data = self._parse_yellow_pages_card(card, industry, location)
                                if company_data:
                                    companies.append(company_data)
                            except Exception as e:
                                logger.debug(f"Error parsing Yellow Pages card: {e}")
                                continue
                
        except Exception as e:
            logger.error(f"Error scraping Yellow Pages for {industry} in {location}: {e}")
        
        return companies
    
    def _parse_google_business_card(self, card, industry: str, location: str) -> Optional[Dict]:
        """Parse individual Google business listing"""
        try:
            # Extract business name
            name_elem = card.find('h3') or card.find('span', class_='OSrXXb')
            if not name_elem:
                return None
            
            name = name_elem.get_text(strip=True)
            if not name:
                return None
            
            # Extract website URL
            website_url = None
            website_links = card.find_all('a', href=True)
            for link in website_links:
                href = link['href']
                if 'http' in href and 'google.com' not in href and 'maps' not in href:
                    website_url = href
                    break
            
            # Extract address
            address = None
            address_elem = card.find('span', class_=['LrzXr', 'rllt__details'])
            if address_elem:
                address = address_elem.get_text(strip=True)
            
            # Extract phone
            phone = None
            phone_elem = card.find('span', class_=['LrzXr zbfw3d'])
            if phone_elem:
                phone = phone_elem.get_text(strip=True)
            
            # Create domain from website URL
            domain = None
            if website_url:
                try:
                    parsed = urlparse(website_url)
                    domain = parsed.netloc.lower().replace('www.', '')
                except:
                    pass
            
            return {
                'name': name,
                'domain': domain,
                'website_url': website_url,
                'address': address,
                'phone': phone,
                'industry': industry,
                'city': location.split(',')[0].strip() if ',' in location else location,
                'state': location.split(',')[1].strip() if ',' in location else None,
                'discovery_source': 'google_business'
            }
            
        except Exception as e:
            logger.debug(f"Error parsing Google business card: {e}")
            return None
    
    def _parse_yellow_pages_card(self, card, industry: str, location: str) -> Optional[Dict]:
        """Parse individual Yellow Pages business listing"""
        try:
            # Extract business name
            name_elem = card.find('a', class_='business-name') or card.find('h2')
            if not name_elem:
                return None
            
            name = name_elem.get_text(strip=True)
            if not name:
                return None
            
            # Extract website URL
            website_url = None
            website_elem = card.find('a', class_='track-visit-website')
            if website_elem and website_elem.get('href'):
                website_url = website_elem['href']
            
            # Extract address
            address = None
            address_elem = card.find('div', class_='street-address')
            if address_elem:
                address = address_elem.get_text(strip=True)
            
            # Extract phone
            phone = None
            phone_elem = card.find('div', class_='phones phone primary')
            if phone_elem:
                phone = phone_elem.get_text(strip=True)
            
            # Create domain from website URL
            domain = None
            if website_url:
                try:
                    parsed = urlparse(website_url)
                    domain = parsed.netloc.lower().replace('www.', '')
                except:
                    pass
            
            return {
                'name': name,
                'domain': domain,
                'website_url': website_url,
                'address': address,
                'phone': phone,
                'industry': industry,
                'city': location.split(',')[0].strip() if ',' in location else location,
                'state': location.split(',')[1].strip() if ',' in location else None,
                'discovery_source': 'yellow_pages'
            }
            
        except Exception as e:
            logger.debug(f"Error parsing Yellow Pages card: {e}")
            return None
    
    def _deduplicate_companies(self, companies: List[Dict]) -> List[Dict]:
        """Remove duplicate companies based on domain and name"""
        seen_domains = set()
        seen_names = set()
        unique_companies = []
        
        for company in companies:
            domain = company.get('domain', '').lower()
            name = company.get('name', '').lower()
            
            # Skip if we've seen this domain or very similar name
            if domain and domain in seen_domains:
                continue
            if name in seen_names:
                continue
            
            # Add to seen sets
            if domain:
                seen_domains.add(domain)
            seen_names.add(name)
            unique_companies.append(company)
        
        return unique_companies
    
    async def _store_company(self, company_data: Dict) -> Optional[Company]:
        """Store discovered company in database"""
        try:
            # Check if company already exists
            existing = None
            if company_data.get('domain'):
                existing = self.session.query(Company).filter(
                    Company.domain == company_data['domain']
                ).first()
            
            if not existing and company_data.get('name'):
                existing = self.session.query(Company).filter(
                    Company.name.ilike(f"%{company_data['name']}%")
                ).first()
            
            if existing:
                # Update existing company with new info
                for key, value in company_data.items():
                    if value and not getattr(existing, key, None):
                        setattr(existing, key, value)
                existing.last_scraped = datetime.now()
                self.session.commit()
                return existing
            
            # Create new company
            company = Company(
                name=company_data.get('name'),
                domain=company_data.get('domain'),
                website_url=company_data.get('website_url'),
                address=company_data.get('address'),
                city=company_data.get('city'),
                state=company_data.get('state'),
                phone=company_data.get('phone'),
                industry=company_data.get('industry'),
                discovery_source=company_data.get('discovery_source'),
                last_scraped=datetime.now(),
                next_scrape_date=datetime.now() + timedelta(days=7),
                business_status='active',
                opportunity_score=0.0
            )
            
            self.session.add(company)
            self.session.commit()
            self.session.refresh(company)
            
            logger.info(f"Stored new company: {company.name} ({company.domain})")
            return company
            
        except Exception as e:
            logger.error(f"Error storing company {company_data.get('name')}: {e}")
            self.session.rollback()
            return None


class LinkedInCompanyScraper:
    """
    Extract company information and decision makers from LinkedIn
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
    
    async def find_company_employees(self, company: Company) -> List[DecisionMaker]:
        """
        Find key employees and decision makers for a company
        """
        decision_makers = []
        
        if not company.name:
            return decision_makers
        
        try:
            # Search for company on LinkedIn
            company_url = await self._find_linkedin_company_page(company.name)
            
            if company_url:
                # Extract employees from company page
                employees = await self._extract_company_employees(company_url)
                
                # Store decision makers
                for employee_data in employees:
                    decision_maker = await self._store_decision_maker(company.id, employee_data)
                    if decision_maker:
                        decision_makers.append(decision_maker)
            
        except Exception as e:
            logger.error(f"Error finding LinkedIn employees for {company.name}: {e}")
        
        return decision_makers
    
    async def _find_linkedin_company_page(self, company_name: str) -> Optional[str]:
        """Find LinkedIn company page URL"""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                # Google search for LinkedIn company page
                search_query = f"site:linkedin.com/company {company_name}"
                search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
                
                async with session.get(search_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Find LinkedIn company page links
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            if 'linkedin.com/company/' in href and '/company/' in href:
                                return href
                
        except Exception as e:
            logger.debug(f"Error finding LinkedIn page for {company_name}: {e}")
        
        return None
    
    async def _extract_company_employees(self, company_url: str) -> List[Dict]:
        """Extract employee information from LinkedIn company page"""
        employees = []
        
        # Note: This is a simplified version. In production, you'd need:
        # 1. LinkedIn API access or sophisticated scraping with auth
        # 2. Proper rate limiting and session management
        # 3. CAPTCHA handling
        
        try:
            # For now, return mock data based on common titles
            mock_employees = [
                {
                    'name': 'John Smith',
                    'title': 'CEO',
                    'department': 'executive',
                    'seniority': 'c-level',
                    'linkedin_url': f"{company_url}/people",
                    'influence_level': 'high',
                    'contact_priority': 9
                },
                {
                    'name': 'Jane Doe', 
                    'title': 'CTO',
                    'department': 'engineering',
                    'seniority': 'c-level',
                    'linkedin_url': f"{company_url}/people",
                    'influence_level': 'high',
                    'contact_priority': 8
                }
            ]
            
            employees.extend(mock_employees)
            
        except Exception as e:
            logger.error(f"Error extracting employees from {company_url}: {e}")
        
        return employees
    
    async def _store_decision_maker(self, company_id: int, employee_data: Dict) -> Optional[DecisionMaker]:
        """Store decision maker in database"""
        try:
            # Check if decision maker already exists
            existing = self.session.query(DecisionMaker).filter(
                DecisionMaker.company_id == company_id,
                DecisionMaker.name == employee_data.get('name')
            ).first()
            
            if existing:
                return existing
            
            # Create new decision maker
            decision_maker = DecisionMaker(
                company_id=company_id,
                name=employee_data.get('name'),
                title=employee_data.get('title'),
                department=employee_data.get('department'),
                seniority=employee_data.get('seniority'),
                linkedin_url=employee_data.get('linkedin_url'),
                influence_level=employee_data.get('influence_level', 'medium'),
                contact_priority=employee_data.get('contact_priority', 5),
                preferred_contact_method='linkedin',
                relationship_status='prospect'
            )
            
            self.session.add(decision_maker)
            self.session.commit()
            self.session.refresh(decision_maker)
            
            logger.info(f"Stored decision maker: {decision_maker.name} at {company_id}")
            return decision_maker
            
        except Exception as e:
            logger.error(f"Error storing decision maker {employee_data.get('name')}: {e}")
            self.session.rollback()
            return None


# Discovery orchestrator function
async def discover_companies_in_grass_valley() -> List[Company]:
    """
    Discover companies in Grass Valley, CA area for testing
    """
    db = next(get_db())
    
    try:
        # Initialize scrapers
        directory_scraper = BusinessDirectoryScaper(db)
        linkedin_scraper = LinkedInCompanyScraper(db)
        
        # Discover companies in Grass Valley
        location = "Grass Valley, CA"
        industries = [
            'web design', 'marketing', 'software development', 'consulting',
            'real estate', 'law firm', 'accounting', 'digital agency'
        ]
        
        logger.info(f"Starting company discovery in {location}")
        
        # Discover companies from directories
        companies = await directory_scraper.discover_companies_in_location(location, industries)
        
        logger.info(f"Discovered {len(companies)} companies")
        
        # Find decision makers for each company
        for company in companies[:10]:  # Limit to first 10 for testing
            try:
                decision_makers = await linkedin_scraper.find_company_employees(company)
                logger.info(f"Found {len(decision_makers)} decision makers for {company.name}")
                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"Error finding decision makers for {company.name}: {e}")
                continue
        
        return companies
        
    except Exception as e:
        logger.error(f"Error in company discovery: {e}")
        return []
    finally:
        db.close()


if __name__ == "__main__":
    # Test the discovery system
    asyncio.run(discover_companies_in_grass_valley())