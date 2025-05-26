"""
Technology Stack Detection and Website Analysis

Analyzes company websites to identify technologies, performance issues, security gaps,
and opportunities for improvement. Creates detailed technical profiles for opportunity scoring.
"""

import asyncio
import aiohttp
import ssl
import socket
import json
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
from datetime import datetime
import logging

from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from app.models.business_intelligence import Company, CompanyTechStack, WebsiteAudit, BusinessOpportunity

logger = logging.getLogger(__name__)


class TechStackDetector:
    """
    Detect technologies used by websites (Wappalyzer-style analysis)
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        }
        
        # Technology detection patterns
        self.tech_patterns = {
            'cms': {
                'WordPress': {
                    'patterns': [
                        r'wp-content',
                        r'wp-includes',
                        r'wordpress',
                        r'<meta name=["\']generator["\'] content=["\']WordPress'
                    ],
                    'headers': ['x-pingback'],
                    'category': 'cms'
                },
                'Shopify': {
                    'patterns': [
                        r'shopify',
                        r'shopifycdn',
                        r'myshopify'
                    ],
                    'headers': ['x-shopid'],
                    'category': 'cms'
                },
                'Squarespace': {
                    'patterns': [
                        r'squarespace',
                        r'static\.squarespace',
                        r'squarespace-config'
                    ],
                    'category': 'cms'
                },
                'Wix': {
                    'patterns': [
                        r'wix\.com',
                        r'wixstatic',
                        r'wix-code'
                    ],
                    'category': 'cms'
                }
            },
            'frameworks': {
                'React': {
                    'patterns': [
                        r'react',
                        r'_react',
                        r'data-reactroot'
                    ],
                    'category': 'framework'
                },
                'Vue.js': {
                    'patterns': [
                        r'vue\.js',
                        r'data-v-'
                    ],
                    'category': 'framework'
                },
                'Angular': {
                    'patterns': [
                        r'angular',
                        r'ng-app',
                        r'ng-controller'
                    ],
                    'category': 'framework'
                },
                'jQuery': {
                    'patterns': [
                        r'jquery',
                        r'jQuery'
                    ],
                    'category': 'library'
                }
            },
            'analytics': {
                'Google Analytics': {
                    'patterns': [
                        r'google-analytics',
                        r'gtag',
                        r'UA-\d+-\d+'
                    ],
                    'category': 'analytics'
                },
                'Facebook Pixel': {
                    'patterns': [
                        r'facebook\.net/tr',
                        r'fbevents\.js'
                    ],
                    'category': 'analytics'
                }
            },
            'hosting': {
                'Cloudflare': {
                    'headers': ['cf-ray', 'server'],
                    'patterns': [r'cloudflare'],
                    'category': 'hosting'
                },
                'AWS': {
                    'headers': ['x-amz-id', 'x-amz-request-id'],
                    'patterns': [r'amazonaws'],
                    'category': 'hosting'
                },
                'Netlify': {
                    'headers': ['x-nf-request-id'],
                    'patterns': [r'netlify'],
                    'category': 'hosting'
                }
            }
        }
    
    async def analyze_company_website(self, company: Company) -> Dict:
        """
        Comprehensive analysis of a company's website
        """
        if not company.website_url:
            return {'error': 'No website URL provided'}
        
        analysis_results = {
            'company_id': company.id,
            'website_url': company.website_url,
            'analysis_date': datetime.now().isoformat(),
            'tech_stack': [],
            'performance': {},
            'security': {},
            'opportunities': []
        }
        
        try:
            # Fetch website content
            website_data = await self._fetch_website_data(company.website_url)
            
            if website_data['success']:
                # Detect technologies
                tech_stack = await self._detect_technologies(website_data)
                analysis_results['tech_stack'] = tech_stack
                
                # Analyze performance
                performance = await self._analyze_performance(website_data)
                analysis_results['performance'] = performance
                
                # Security analysis
                security = await self._analyze_security(website_data)
                analysis_results['security'] = security
                
                # Store results in database
                await self._store_tech_stack(company.id, tech_stack)
                await self._store_website_audit(company.id, website_data, performance, security)
                
                # Identify opportunities
                opportunities = await self._identify_opportunities(company, analysis_results)
                analysis_results['opportunities'] = opportunities
                
            else:
                analysis_results['error'] = website_data.get('error', 'Failed to fetch website')
                
        except Exception as e:
            logger.error(f"Error analyzing website for {company.name}: {e}")
            analysis_results['error'] = str(e)
        
        return analysis_results
    
    async def _fetch_website_data(self, url: str) -> Dict:
        """
        Fetch website HTML, headers, and basic metadata
        """
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with aiohttp.ClientSession(headers=self.headers, timeout=timeout) as session:
                start_time = asyncio.get_event_loop().time()
                
                async with session.get(url, allow_redirects=True) as response:
                    end_time = asyncio.get_event_loop().time()
                    load_time = end_time - start_time
                    
                    html = await response.text()
                    
                    return {
                        'success': True,
                        'url': str(response.url),
                        'status_code': response.status,
                        'headers': dict(response.headers),
                        'html': html,
                        'load_time': load_time,
                        'content_length': len(html),
                        'redirected': url != str(response.url)
                    }
                    
        except asyncio.TimeoutError:
            return {'success': False, 'error': 'Request timeout'}
        except aiohttp.ClientError as e:
            return {'success': False, 'error': f'Client error: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': f'Unexpected error: {str(e)}'}
    
    async def _detect_technologies(self, website_data: Dict) -> List[Dict]:
        """
        Detect technologies from HTML content and headers
        """
        detected_tech = []
        html = website_data.get('html', '')
        headers = website_data.get('headers', {})
        
        # Check all technology patterns
        for category, technologies in self.tech_patterns.items():
            for tech_name, tech_config in technologies.items():
                confidence = 0.0
                detection_methods = []
                
                # Check HTML patterns
                if 'patterns' in tech_config:
                    for pattern in tech_config['patterns']:
                        if re.search(pattern, html, re.IGNORECASE):
                            confidence += 0.3
                            detection_methods.append(f'html_pattern:{pattern}')
                
                # Check headers
                if 'headers' in tech_config:
                    for header_name in tech_config['headers']:
                        if header_name.lower() in [h.lower() for h in headers.keys()]:
                            confidence += 0.5
                            detection_methods.append(f'header:{header_name}')
                
                # If we detected this technology
                if confidence > 0:
                    # Cap confidence at 1.0
                    confidence = min(confidence, 1.0)
                    
                    detected_tech.append({
                        'name': tech_name,
                        'category': tech_config.get('category', category),
                        'confidence': confidence,
                        'detection_methods': detection_methods,
                        'version': self._extract_version(tech_name, html)
                    })
        
        return detected_tech
    
    def _extract_version(self, tech_name: str, html: str) -> Optional[str]:
        """
        Try to extract version information for detected technologies
        """
        version_patterns = {
            'WordPress': [
                r'<meta name=["\']generator["\'] content=["\']WordPress ([0-9.]+)',
                r'wp-includes/js/[^/]+/[^/]+\.js\?ver=([0-9.]+)'
            ],
            'jQuery': [
                r'jquery[/-]([0-9.]+)',
                r'jQuery v([0-9.]+)'
            ]
        }
        
        if tech_name in version_patterns:
            for pattern in version_patterns[tech_name]:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    return match.group(1)
        
        return None
    
    async def _analyze_performance(self, website_data: Dict) -> Dict:
        """
        Analyze website performance metrics
        """
        performance = {
            'load_time': website_data.get('load_time', 0),
            'content_size': website_data.get('content_length', 0),
            'status_code': website_data.get('status_code'),
            'redirected': website_data.get('redirected', False)
        }
        
        html = website_data.get('html', '')
        
        # Count resources
        soup = BeautifulSoup(html, 'html.parser')
        
        performance.update({
            'image_count': len(soup.find_all('img')),
            'script_count': len(soup.find_all('script')),
            'css_count': len(soup.find_all('link', rel='stylesheet')),
            'external_requests': self._count_external_requests(soup, website_data.get('url'))
        })
        
        # Performance scoring (0-100)
        performance_score = 100
        
        # Deduct points for slow loading
        if performance['load_time'] > 3:
            performance_score -= 30
        elif performance['load_time'] > 2:
            performance_score -= 15
        
        # Deduct points for large content
        if performance['content_size'] > 2000000:  # 2MB
            performance_score -= 20
        elif performance['content_size'] > 1000000:  # 1MB
            performance_score -= 10
        
        # Deduct points for too many resources
        total_resources = performance['image_count'] + performance['script_count'] + performance['css_count']
        if total_resources > 50:
            performance_score -= 15
        elif total_resources > 30:
            performance_score -= 10
        
        performance['performance_score'] = max(0, performance_score)
        
        return performance
    
    def _count_external_requests(self, soup: BeautifulSoup, base_url: str) -> int:
        """Count external resource requests"""
        if not base_url:
            return 0
        
        base_domain = urlparse(base_url).netloc
        external_count = 0
        
        # Check images
        for img in soup.find_all('img', src=True):
            src_domain = urlparse(img['src']).netloc
            if src_domain and src_domain != base_domain:
                external_count += 1
        
        # Check scripts
        for script in soup.find_all('script', src=True):
            src_domain = urlparse(script['src']).netloc
            if src_domain and src_domain != base_domain:
                external_count += 1
        
        # Check CSS
        for link in soup.find_all('link', href=True):
            href_domain = urlparse(link['href']).netloc
            if href_domain and href_domain != base_domain:
                external_count += 1
        
        return external_count
    
    async def _analyze_security(self, website_data: Dict) -> Dict:
        """
        Analyze website security features
        """
        headers = website_data.get('headers', {})
        url = website_data.get('url', '')
        
        security = {
            'ssl_enabled': url.startswith('https://'),
            'security_headers': {},
            'security_score': 0,
            'vulnerabilities': []
        }
        
        # Check security headers
        security_headers = [
            'strict-transport-security',
            'x-frame-options', 
            'x-content-type-options',
            'x-xss-protection',
            'content-security-policy',
            'referrer-policy'
        ]
        
        for header in security_headers:
            header_value = headers.get(header, headers.get(header.title(), ''))
            security['security_headers'][header] = bool(header_value)
            if header_value:
                security['security_score'] += 15
        
        # SSL check
        if security['ssl_enabled']:
            security['security_score'] += 10
        else:
            security['vulnerabilities'].append('No SSL/HTTPS encryption')
        
        # Check for common vulnerabilities
        html = website_data.get('html', '')
        
        # Check for outdated WordPress
        wp_version_match = re.search(r'WordPress ([0-9.]+)', html, re.IGNORECASE)
        if wp_version_match:
            version = wp_version_match.group(1)
            # Simplified version check (in production, use a vulnerability database)
            if version.startswith('4.') or version.startswith('5.0') or version.startswith('5.1'):
                security['vulnerabilities'].append(f'Outdated WordPress version: {version}')
                security['security_score'] -= 20
        
        # Check for exposed sensitive files (simplified)
        sensitive_patterns = [
            r'wp-config\.php',
            r'\.env',
            r'database\.yml'
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, html, re.IGNORECASE):
                security['vulnerabilities'].append(f'Potentially exposed sensitive file: {pattern}')
                security['security_score'] -= 10
        
        security['security_score'] = max(0, min(100, security['security_score']))
        
        return security
    
    async def _store_tech_stack(self, company_id: int, tech_stack: List[Dict]):
        """Store detected technologies in database"""
        try:
            # Clear existing tech stack
            self.session.query(CompanyTechStack).filter(
                CompanyTechStack.company_id == company_id
            ).delete()
            
            # Add detected technologies
            for tech in tech_stack:
                tech_record = CompanyTechStack(
                    company_id=company_id,
                    tech_name=tech['name'],
                    tech_category=tech['category'],
                    tech_version=tech.get('version'),
                    detection_method=', '.join(tech['detection_methods']),
                    confidence_score=tech['confidence'],
                    detection_date=datetime.now()
                )
                
                self.session.add(tech_record)
            
            self.session.commit()
            logger.info(f"Stored {len(tech_stack)} technologies for company {company_id}")
            
        except Exception as e:
            logger.error(f"Error storing tech stack for company {company_id}: {e}")
            self.session.rollback()
    
    async def _store_website_audit(self, company_id: int, website_data: Dict, performance: Dict, security: Dict):
        """Store website audit results"""
        try:
            audit = WebsiteAudit(
                company_id=company_id,
                audit_date=datetime.now(),
                audit_type='full',
                audit_tool='custom_analyzer',
                
                # Performance metrics
                page_load_time=performance.get('load_time'),
                performance_score=performance.get('performance_score'),
                
                # Technical analysis
                mobile_friendly=None,  # Would need additional analysis
                ssl_enabled=security.get('ssl_enabled'),
                
                # Content analysis
                page_size_bytes=performance.get('content_size'),
                
                # Security analysis
                security_headers=security.get('security_headers'),
                security_issues=security.get('vulnerabilities'),
                vulnerability_count=len(security.get('vulnerabilities', [])),
                
                # Improvement opportunities will be populated by opportunity identifier
                improvement_opportunities=[],
                estimated_improvement_impact=0.0,
                priority_fixes=[]
            )
            
            self.session.add(audit)
            self.session.commit()
            self.session.refresh(audit)
            
            logger.info(f"Stored website audit for company {company_id}")
            return audit
            
        except Exception as e:
            logger.error(f"Error storing website audit for company {company_id}: {e}")
            self.session.rollback()
            return None
    
    async def _identify_opportunities(self, company: Company, analysis: Dict) -> List[Dict]:
        """
        Identify business opportunities based on technical analysis
        """
        opportunities = []
        
        # Website performance opportunities
        performance = analysis.get('performance', {})
        if performance.get('load_time', 0) > 3:
            opportunities.append({
                'type': 'performance_optimization',
                'title': 'Website Speed Optimization',
                'description': f"Website loads in {performance.get('load_time', 0):.1f}s - could be optimized to under 2s",
                'estimated_value': 2500,
                'effort_hours': 16,
                'urgency_score': 7.0,
                'evidence': f"Current load time: {performance.get('load_time', 0):.1f}s"
            })
        
        # Security opportunities
        security = analysis.get('security', {})
        if not security.get('ssl_enabled'):
            opportunities.append({
                'type': 'security_upgrade',
                'title': 'SSL Certificate Installation',
                'description': 'Website lacks SSL encryption - critical for security and SEO',
                'estimated_value': 500,
                'effort_hours': 4,
                'urgency_score': 9.0,
                'evidence': 'No HTTPS encryption detected'
            })
        
        if security.get('vulnerabilities'):
            opportunities.append({
                'type': 'security_audit',
                'title': 'Security Vulnerability Assessment',
                'description': f"Found {len(security['vulnerabilities'])} potential security issues",
                'estimated_value': 1500,
                'effort_hours': 12,
                'urgency_score': 8.0,
                'evidence': ', '.join(security['vulnerabilities'])
            })
        
        # Technology modernization opportunities
        tech_stack = analysis.get('tech_stack', [])
        outdated_tech = [tech for tech in tech_stack if self._is_outdated_technology(tech)]
        
        if outdated_tech:
            opportunities.append({
                'type': 'tech_modernization',
                'title': 'Technology Stack Modernization',
                'description': f"Outdated technologies detected: {', '.join([tech['name'] for tech in outdated_tech])}",
                'estimated_value': 5000,
                'effort_hours': 40,
                'urgency_score': 6.0,
                'evidence': f"Outdated: {', '.join([tech['name'] + ' ' + tech.get('version', '') for tech in outdated_tech])}"
            })
        
        # Mobile optimization opportunity
        if performance.get('performance_score', 100) < 70:
            opportunities.append({
                'type': 'mobile_optimization',
                'title': 'Mobile Experience Optimization',
                'description': 'Website needs mobile performance and user experience improvements',
                'estimated_value': 3000,
                'effort_hours': 24,
                'urgency_score': 7.5,
                'evidence': f"Performance score: {performance.get('performance_score', 0)}/100"
            })
        
        # Store opportunities in database
        await self._store_opportunities(company.id, opportunities)
        
        return opportunities
    
    def _is_outdated_technology(self, tech: Dict) -> bool:
        """
        Check if a detected technology is outdated
        """
        # Simplified version checking
        outdated_versions = {
            'WordPress': ['4.', '5.0', '5.1', '5.2'],
            'jQuery': ['1.', '2.']
        }
        
        tech_name = tech['name']
        version = tech.get('version', '')
        
        if tech_name in outdated_versions and version:
            for outdated in outdated_versions[tech_name]:
                if version.startswith(outdated):
                    return True
        
        return False
    
    async def _store_opportunities(self, company_id: int, opportunities: List[Dict]):
        """Store identified opportunities in database"""
        try:
            for opp_data in opportunities:
                # Check if similar opportunity already exists
                existing = self.session.query(BusinessOpportunity).filter(
                    BusinessOpportunity.company_id == company_id,
                    BusinessOpportunity.opportunity_type == opp_data['type']
                ).first()
                
                if existing:
                    # Update existing opportunity
                    existing.description = opp_data['description']
                    existing.estimated_value = opp_data['estimated_value']
                    existing.effort_estimate_hours = opp_data['effort_hours']
                    existing.urgency_score = opp_data['urgency_score']
                    existing.evidence_data = {'evidence': opp_data['evidence']}
                    existing.updated_at = datetime.now()
                else:
                    # Create new opportunity
                    opportunity = BusinessOpportunity(
                        company_id=company_id,
                        opportunity_type=opp_data['type'],
                        title=opp_data['title'],
                        description=opp_data['description'],
                        estimated_value=opp_data['estimated_value'],
                        effort_estimate_hours=opp_data['effort_hours'],
                        urgency_score=opp_data['urgency_score'],
                        feasibility_score=8.0,  # Default high feasibility
                        value_score=opp_data['urgency_score'],
                        evidence_data={'evidence': opp_data['evidence']},
                        pain_point_source='website_analysis',
                        status='identified'
                    )
                    
                    self.session.add(opportunity)
            
            self.session.commit()
            logger.info(f"Stored {len(opportunities)} opportunities for company {company_id}")
            
        except Exception as e:
            logger.error(f"Error storing opportunities for company {company_id}: {e}")
            self.session.rollback()


# Main analysis function
async def analyze_company_tech_stack(company: Company, session: Session) -> Dict:
    """
    Analyze a company's technology stack and identify opportunities
    """
    detector = TechStackDetector(session)
    return await detector.analyze_company_website(company)