"""
Automated Outreach Campaign System

Manages personalized email sequences, LinkedIn outreach, follow-up automation,
and response tracking for business development campaigns.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.business_intelligence import (
    Company, DecisionMaker, OutreachRecord
)
from app.services.intelligence_generator import BusinessIntelligenceReportGenerator


class OutreachCampaignManager:
    """
    Manage automated outreach campaigns with personalization and tracking
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        
        # Email configuration (would use environment variables in production)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_user = "your-business@email.com"  # Configure in production
        self.email_password = "app-password"  # Use app password
        
        # Template directories
        self.templates_dir = Path("app/templates/outreach")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Tracking directory
        self.tracking_dir = Path("outreach_tracking")
        self.tracking_dir.mkdir(exist_ok=True)
        
        # Initialize templates
        self._create_default_templates()
    
    async def launch_outreach_campaign(
        self,
        company_ids: List[int],
        campaign_type: str = "value_proposition",
        send_emails: bool = False,  # Set to True for live sending
        follow_up_sequence: bool = True
    ) -> Dict:
        """
        Launch comprehensive outreach campaign for multiple companies
        """
        
        campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        campaign_stats = {
            'campaign_id': campaign_id,
            'launched_at': datetime.now().isoformat(),
            'campaign_type': campaign_type,
            'target_companies': len(company_ids),
            'emails_sent': 0,
            'linkedin_messages': 0,
            'follow_ups_scheduled': 0,
            'responses_tracked': 0,
            'errors': 0
        }
        
        outreach_records = []
        
        for company_id in company_ids:
            try:
                # Get company and decision makers
                company = self.db.query(Company).filter(Company.id == company_id).first()
                if not company:
                    continue
                
                decision_makers = self.db.query(DecisionMaker).filter(
                    DecisionMaker.company_id == company_id
                ).order_by(DecisionMaker.contact_priority.desc()).all()
                
                # Generate personalized outreach for primary contact
                primary_contact = decision_makers[0] if decision_makers else None
                
                outreach_content = await self._generate_personalized_outreach(
                    company, primary_contact, campaign_type
                )
                
                # Create outreach record
                outreach_record = await self._create_outreach_record(
                    campaign_id, company, primary_contact, outreach_content
                )
                
                if outreach_record:
                    outreach_records.append(outreach_record)
                
                # Send email if enabled
                if send_emails and primary_contact:
                    email_sent = await self._send_email(
                        outreach_content, primary_contact, company
                    )
                    if email_sent:
                        campaign_stats['emails_sent'] += 1
                    else:
                        campaign_stats['errors'] += 1
                
                # Schedule follow-up sequence
                if follow_up_sequence:
                    await self._schedule_follow_up_sequence(
                        outreach_record, company, primary_contact
                    )
                    campaign_stats['follow_ups_scheduled'] += 1
                
            except Exception as e:
                print(f"Error processing company {company_id}: {e}")
                campaign_stats['errors'] += 1
                continue
        
        # Save campaign summary
        campaign_file = await self._save_campaign_summary(campaign_id, campaign_stats, outreach_records)
        
        return {
            'campaign_summary': campaign_stats,
            'outreach_records': len(outreach_records),
            'campaign_file': str(campaign_file),
            'next_actions': [
                "Monitor email responses and engagement",
                "Track follow-up sequence performance", 
                "Update outreach records with responses",
                "Analyze campaign performance metrics"
            ]
        }
    
    async def _generate_personalized_outreach(
        self,
        company: Company,
        decision_maker: Optional[DecisionMaker],
        campaign_type: str
    ) -> Dict:
        """Generate personalized outreach content"""
        
        # Get intelligence report for personalization
        intelligence_generator = BusinessIntelligenceReportGenerator(self.db)
        try:
            report = await intelligence_generator.generate_company_intelligence_report(company.id)
            outreach_strategy = report.get('outreach_strategy', {})
        except Exception:
            outreach_strategy = {}
        
        # Base personalization data
        personalization = {
            'company_name': company.name,
            'contact_name': decision_maker.name if decision_maker else 'Hello',
            'contact_title': decision_maker.title if decision_maker else 'Decision Maker',
            'industry': company.industry or 'business',
            'city': company.city or 'your area',
            'website_url': company.website_url or company.domain
        }
        
        # Generate content based on campaign type
        if campaign_type == "value_proposition":
            content = self._generate_value_proposition_outreach(personalization, outreach_strategy)
        elif campaign_type == "free_audit":
            content = self._generate_free_audit_outreach(personalization, outreach_strategy)
        elif campaign_type == "case_study":
            content = self._generate_case_study_outreach(personalization, outreach_strategy)
        else:
            content = self._generate_consultation_outreach(personalization, outreach_strategy)
        
        return content
    
    def _generate_value_proposition_outreach(self, personalization: Dict, strategy: Dict) -> Dict:
        """Generate value proposition focused outreach"""
        
        subject_line = f"Quick question about {personalization['company_name']}'s digital strategy"
        
        email_body = f"""Hi {personalization['contact_name']},

I was researching {personalization['industry']} companies in {personalization['city']} and came across {personalization['company_name']}. 

I noticed a few opportunities that could help you increase online visibility and generate more qualified leads:

• Website optimization for better search rankings
• Technology modernization for improved performance  
• Local SEO to capture more {personalization['city']} customers

I've helped similar {personalization['industry']} businesses increase their leads by 40-60% within 90 days.

Would you be open to a brief 15-minute conversation about growth opportunities for {personalization['company_name']}? I can share some specific insights I found during my research.

Best regards,
[Your Name]
[Your Title]
[Contact Information]

P.S. I can provide a free digital assessment of your current online presence - no strings attached."""
        
        linkedin_message = f"""Hi {personalization['contact_name']}, I researched {personalization['company_name']} and identified some digital growth opportunities for {personalization['industry']} businesses in {personalization['city']}. Would you be open to a brief conversation about increasing online leads? I've helped similar companies grow 40-60% in 90 days."""
        
        return {
            'outreach_type': 'value_proposition',
            'subject_line': subject_line,
            'email_body': email_body,
            'linkedin_message': linkedin_message,
            'personalization_data': personalization,
            'call_to_action': 'Schedule 15-minute consultation',
            'follow_up_days': [3, 7, 14, 21]
        }
    
    def _generate_free_audit_outreach(self, personalization: Dict, strategy: Dict) -> Dict:
        """Generate free audit offer outreach"""
        
        subject_line = f"Free digital audit for {personalization['company_name']} (5-minute read)"
        
        email_body = f"""Hi {personalization['contact_name']},

I specialize in helping {personalization['industry']} companies in {personalization['city']} improve their digital presence and generate more leads.

I'd like to offer {personalization['company_name']} a complimentary digital audit that includes:

✓ Website performance analysis
✓ SEO opportunity assessment  
✓ Competitor comparison
✓ Local search optimization review
✓ Technology stack evaluation

The audit typically reveals $5,000-$15,000 in missed revenue opportunities that can be captured within 60-90 days.

There's no cost for this assessment, and no obligation to work together. I simply enjoy helping local {personalization['industry']} businesses succeed.

Would you like me to prepare this audit for {personalization['company_name']}? It takes about a week to complete.

Best regards,
[Your Name]

P.S. Recent audits have helped businesses increase leads by 25-50% within their first quarter."""
        
        linkedin_message = f"""Hi {personalization['contact_name']}, I'm offering complimentary digital audits for {personalization['industry']} companies in {personalization['city']}. These typically reveal $5K-$15K in missed opportunities. Would you like me to prepare one for {personalization['company_name']}? No cost, no obligation."""
        
        return {
            'outreach_type': 'free_audit',
            'subject_line': subject_line,
            'email_body': email_body,
            'linkedin_message': linkedin_message,
            'personalization_data': personalization,
            'call_to_action': 'Request free audit',
            'follow_up_days': [5, 10, 20]
        }
    
    def _generate_case_study_outreach(self, personalization: Dict, strategy: Dict) -> Dict:
        """Generate case study focused outreach"""
        
        subject_line = f"How [Similar Company] increased leads 67% (relevant to {personalization['company_name']})"
        
        email_body = f"""Hi {personalization['contact_name']},

I recently helped a {personalization['industry']} company similar to {personalization['company_name']} increase their qualified leads by 67% in just 4 months.

Here's what we accomplished:

• Improved website conversion rate from 2.1% to 3.8%
• Increased local search visibility by 300%
• Generated 23 additional qualified leads per month
• ROI of 340% within 6 months

The strategy involved three key improvements:
1. Website optimization for local search
2. Technology modernization for better performance
3. Targeted content marketing for {personalization['industry']} prospects

I see similar opportunities at {personalization['company_name']} based on my initial research.

Would you like me to share the specific strategies that worked? I can explain how they might apply to your business in a brief 15-minute call.

Best regards,
[Your Name]

P.S. I can provide references from the company if you'd like to hear directly about their results."""
        
        linkedin_message = f"""Hi {personalization['contact_name']}, I helped a {personalization['industry']} company increase leads 67% in 4 months. Similar opportunities exist for {personalization['company_name']}. Would you like me to share the specific strategies that worked?"""
        
        return {
            'outreach_type': 'case_study',
            'subject_line': subject_line,
            'email_body': email_body,
            'linkedin_message': linkedin_message,
            'personalization_data': personalization,
            'call_to_action': 'Learn about case study strategies',
            'follow_up_days': [4, 8, 16]
        }
    
    def _generate_consultation_outreach(self, personalization: Dict, strategy: Dict) -> Dict:
        """Generate consultation focused outreach"""
        
        subject_line = f"15-minute consultation offer for {personalization['company_name']}"
        
        email_body = f"""Hi {personalization['contact_name']},

I help {personalization['industry']} companies in {personalization['city']} grow their business through strategic digital improvements.

I'd like to offer you a complimentary 15-minute consultation to discuss:

• Current digital marketing performance
• Opportunities for lead generation improvement  
• Technology optimization strategies
• Local market positioning

During our brief conversation, I'll share 2-3 specific recommendations that could benefit {personalization['company_name']} immediately.

No sales pitch - just professional insights from someone who understands the {personalization['industry']} market in {personalization['city']}.

Are you available for a quick call this week or next?

Best regards,
[Your Name]

P.S. Most business owners find at least one actionable insight they can implement right away."""
        
        linkedin_message = f"""Hi {personalization['contact_name']}, I offer complimentary 15-minute consultations for {personalization['industry']} companies in {personalization['city']}. Could we discuss growth opportunities for {personalization['company_name']} this week?"""
        
        return {
            'outreach_type': 'consultation',
            'subject_line': subject_line,
            'email_body': email_body,
            'linkedin_message': linkedin_message,
            'personalization_data': personalization,
            'call_to_action': 'Schedule consultation call',
            'follow_up_days': [3, 7, 14]
        }
    
    async def _create_outreach_record(
        self,
        campaign_id: str,
        company: Company,
        decision_maker: Optional[DecisionMaker],
        outreach_content: Dict
    ) -> Optional[OutreachRecord]:
        """Create outreach record in database"""
        
        try:
            outreach_record = OutreachRecord(
                company_id=company.id,
                decision_maker_id=decision_maker.id if decision_maker else None,
                outreach_type='email',
                subject_line=outreach_content['subject_line'],
                message_content=outreach_content['email_body'],
                personalization_data=json.dumps(outreach_content['personalization_data']),
                campaign_id=campaign_id,
                sequence_step=1,
                scheduled_date=datetime.now(),
                status='drafted',
                response_expected=True
            )
            
            self.db.add(outreach_record)
            self.db.commit()
            self.db.refresh(outreach_record)
            
            return outreach_record
            
        except Exception as e:
            print(f"Error creating outreach record: {e}")
            self.db.rollback()
            return None
    
    async def _send_email(
        self,
        outreach_content: Dict,
        decision_maker: DecisionMaker,
        company: Company
    ) -> bool:
        """Send personalized email (mock implementation)"""
        
        # Mock email sending - in production, use actual SMTP
        try:
            email_data = {
                'to': decision_maker.email if hasattr(decision_maker, 'email') else f"contact@{company.domain}",
                'subject': outreach_content['subject_line'],
                'body': outreach_content['email_body'],
                'sent_at': datetime.now().isoformat(),
                'campaign_type': outreach_content['outreach_type']
            }
            
            # Save email to tracking file (mock sent email)
            tracking_file = self.tracking_dir / f"sent_email_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(tracking_file, 'w') as f:
                json.dump(email_data, f, indent=2)
            
            print(f"📧 Mock email sent to {decision_maker.name} at {company.name}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False
    
    async def _schedule_follow_up_sequence(
        self,
        outreach_record: OutreachRecord,
        company: Company,
        decision_maker: Optional[DecisionMaker]
    ) -> None:
        """Schedule automated follow-up sequence"""
        
        if not outreach_record:
            return
        
        # Get follow-up days from outreach content
        follow_up_days = [3, 7, 14, 21]  # Default sequence
        
        for i, days in enumerate(follow_up_days):
            try:
                follow_up_date = datetime.now() + timedelta(days=days)
                
                # Generate follow-up content
                follow_up_content = self._generate_follow_up_content(
                    company, decision_maker, i + 2  # Sequence step
                )
                
                # Create follow-up record
                follow_up_record = OutreachRecord(
                    company_id=company.id,
                    decision_maker_id=decision_maker.id if decision_maker else None,
                    outreach_type='email_follow_up',
                    subject_line=follow_up_content['subject_line'],
                    message_content=follow_up_content['email_body'],
                    campaign_id=outreach_record.campaign_id,
                    sequence_step=i + 2,
                    scheduled_date=follow_up_date,
                    status='scheduled',
                    response_expected=True,
                    parent_outreach_id=outreach_record.id
                )
                
                self.db.add(follow_up_record)
                
            except Exception as e:
                print(f"Error scheduling follow-up {i+1}: {e}")
                continue
        
        self.db.commit()
    
    def _generate_follow_up_content(
        self,
        company: Company,
        decision_maker: Optional[DecisionMaker],
        sequence_step: int
    ) -> Dict:
        """Generate follow-up email content based on sequence step"""
        
        contact_name = decision_maker.name if decision_maker else "Hello"
        company_name = company.name
        
        if sequence_step == 2:  # First follow-up
            subject_line = f"Quick follow-up: {company_name} digital opportunities"
            email_body = f"""Hi {contact_name},

I wanted to follow up on my message about digital growth opportunities for {company_name}.

I know you're busy, so I'll keep this brief. The three areas where I see the biggest potential impact are:

1. Local search optimization (could increase leads by 25-40%)
2. Website performance improvements (better user experience = higher conversions)
3. Technology modernization (improved security and efficiency)

These improvements typically pay for themselves within 60-90 days.

Would you be interested in a brief 10-minute conversation to discuss what this could mean for {company_name}?

Best regards,
[Your Name]

P.S. If timing isn't right, just let me know when might be better."""
            
        elif sequence_step == 3:  # Second follow-up
            subject_line = f"Last follow-up: Free assessment for {company_name}"
            email_body = f"""Hi {contact_name},

This will be my last follow-up about the complimentary digital assessment for {company_name}.

I completely understand if this isn't a priority right now. Business owners have countless demands on their time.

However, if you're interested in understanding how {company_name} compares to competitors online, or want to identify missed revenue opportunities, I'm happy to provide that assessment at no cost.

The analysis usually takes me about a week, and there's absolutely no obligation to work together afterward.

Just reply "Yes" if you'd like me to proceed, or "No thanks" if it's not something you're interested in.

Best regards,
[Your Name]"""
            
        else:  # Final follow-up
            subject_line = f"Final note: Door always open for {company_name}"
            email_body = f"""Hi {contact_name},

I'll stop reaching out after this message, but wanted to leave the door open.

If you ever want to discuss digital growth strategies for {company_name}, or if circumstances change and you'd like that complimentary assessment, please don't hesitate to reach out.

I genuinely enjoy helping {company.industry or 'business'} companies succeed, and I'm always happy to share insights when the timing is right.

Wishing you continued success with {company_name}.

Best regards,
[Your Name]

P.S. I'll add you to my monthly newsletter with {company.industry or 'business'} insights. Easy to unsubscribe if it's not valuable."""
        
        return {
            'subject_line': subject_line,
            'email_body': email_body,
            'sequence_step': sequence_step
        }
    
    async def track_email_responses(self, campaign_id: str) -> Dict:
        """Track and analyze email responses for campaign"""
        
        # Get all outreach records for campaign
        outreach_records = self.db.query(OutreachRecord).filter(
            OutreachRecord.campaign_id == campaign_id
        ).all()
        
        stats = {
            'total_sent': len([r for r in outreach_records if r.status == 'sent']),
            'responses_received': len([r for r in outreach_records if r.response_received]),
            'positive_responses': len([r for r in outreach_records if r.response_sentiment == 'positive']),
            'meetings_scheduled': len([r for r in outreach_records if r.meeting_scheduled]),
            'response_rate': 0,
            'meeting_conversion_rate': 0
        }
        
        if stats['total_sent'] > 0:
            stats['response_rate'] = (stats['responses_received'] / stats['total_sent']) * 100
            
        if stats['responses_received'] > 0:
            stats['meeting_conversion_rate'] = (stats['meetings_scheduled'] / stats['responses_received']) * 100
        
        return stats
    
    async def _save_campaign_summary(
        self,
        campaign_id: str,
        campaign_stats: Dict,
        outreach_records: List[OutreachRecord]
    ) -> Path:
        """Save campaign summary to file"""
        
        summary = {
            'campaign_details': campaign_stats,
            'outreach_records': [
                {
                    'company_name': record.company.name,
                    'contact_name': record.decision_maker.name if record.decision_maker else 'Unknown',
                    'outreach_type': record.outreach_type,
                    'subject_line': record.subject_line,
                    'scheduled_date': record.scheduled_date.isoformat(),
                    'status': record.status
                }
                for record in outreach_records
            ]
        }
        
        filename = f"campaign_summary_{campaign_id}.json"
        file_path = self.tracking_dir / filename
        
        with open(file_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        return file_path
    
    def _create_default_templates(self) -> None:
        """Create default email templates"""
        
        templates = {
            'value_proposition': {
                'subject': "Quick question about {company_name}'s digital strategy",
                'body': "Template for value proposition outreach..."
            },
            'free_audit': {
                'subject': "Free digital audit for {company_name}",
                'body': "Template for free audit offer..."
            },
            'case_study': {
                'subject': "How [Similar Company] increased leads 67%",
                'body': "Template for case study outreach..."
            }
        }
        
        # Save templates to files
        for template_name, template_data in templates.items():
            template_file = self.templates_dir / f"{template_name}.json"
            if not template_file.exists():
                with open(template_file, 'w') as f:
                    json.dump(template_data, f, indent=2)


# Convenience functions
async def launch_campaign_for_companies(company_ids: List[int], campaign_type: str = "value_proposition") -> Dict:
    """Launch outreach campaign for list of companies"""
    from app.core.database import get_db
    
    db = next(get_db())
    try:
        campaign_manager = OutreachCampaignManager(db)
        result = await campaign_manager.launch_outreach_campaign(
            company_ids, campaign_type, send_emails=False  # Mock mode
        )
        return result
    finally:
        db.close()


async def track_campaign_performance(campaign_id: str) -> Dict:
    """Track performance of specific campaign"""
    from app.core.database import get_db
    
    db = next(get_db())
    try:
        campaign_manager = OutreachCampaignManager(db)
        stats = await campaign_manager.track_email_responses(campaign_id)
        return stats
    finally:
        db.close()