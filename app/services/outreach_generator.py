"""
Personalized Outreach Message Generation

AI-powered system for generating highly personalized outreach messages that:
- Analyzes company data and business context
- Creates compelling value propositions
- Generates multi-stage email sequences
- Personalizes messages based on recipient role and company profile
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json

from sqlalchemy.orm import Session
from jinja2 import Environment, DictLoader

from app.models.business_intelligence import Company, Opportunity, OutreachContact, OutreachCampaign
from app.core.database import get_db


class OutreachMessageGenerator:
    """
    AI-powered personalized outreach message generation
    """
    
    def __init__(self, db: Session):
        self.db = db
        
        # Email templates with personalization variables
        self.templates = {
            "cold_intro": {
                "subject": "Quick question about {{company_name}}'s {{pain_point}}",
                "message": """Hi {{contact_name}},

I was researching {{industry}} companies and came across {{company_name}}. {{company_insight}}

I noticed that companies like yours often struggle with {{pain_point}}. We recently helped {{similar_company}} {{success_story}}, resulting in {{specific_benefit}}.

I'd love to show you how {{solution_name}} could help {{company_name}} {{value_proposition}}.

Would you be open to a brief 15-minute call next week to discuss how we might be able to help?

Best regards,
{{sender_name}}

P.S. {{personal_touch}}"""
            },
            
            "follow_up_1": {
                "subject": "Re: {{company_name}}'s automation opportunities",
                "message": """Hi {{contact_name}},

I wanted to follow up on my previous email about helping {{company_name}} with {{pain_point}}.

I understand you're probably busy, but I thought you might find this interesting: {{industry_statistic}}.

Companies in {{industry}} typically see {{roi_percentage}}% ROI when they implement {{solution_category}} solutions like ours.

For {{company_name}} specifically, based on your {{company_size}} and {{business_model}}, I estimate you could save approximately {{estimated_savings}} annually.

Would you be interested in a quick call to explore this further?

Best,
{{sender_name}}"""
            },
            
            "value_demonstration": {
                "subject": "Here's how {{company_name}} could save {{estimated_savings}}",
                "message": """Hi {{contact_name}},

I put together a quick analysis of how {{company_name}} could benefit from automation.

Here's what I found:

🎯 Current Challenge: {{current_challenge}}
⚡ Our Solution: {{proposed_solution}}
💰 Estimated Annual Savings: {{estimated_savings}}
📈 ROI Timeline: {{payback_period}}

{{success_story_detailed}}

I've created a brief demo specifically for {{company_name}} that shows this in action: {{demo_url}}

Would you like to schedule 20 minutes to walk through this together?

Best,
{{sender_name}}

P.S. {{industry_insight}}"""
            },
            
            "final_attempt": {
                "subject": "Last attempt - {{value_proposition}} for {{company_name}}",
                "message": """Hi {{contact_name}},

I've reached out a few times about helping {{company_name}} with {{pain_point}}, but I understand you're busy.

This will be my last email, but I wanted to share one final thought:

{{compelling_insight}}

If timing isn't right now, no worries at all. But if you'd ever like to explore how {{solution_name}} could help {{company_name}} {{key_benefit}}, feel free to reach out.

Best of luck with {{company_goal}},
{{sender_name}}

P.S. Feel free to connect with me on LinkedIn if you'd like to stay in touch: {{linkedin_url}}"""
            },
            
            "response_positive": {
                "subject": "Great! Next steps for {{company_name}}",
                "message": """Hi {{contact_name}},

Thanks for your interest in learning more about how we can help {{company_name}}!

I've put together a customized presentation that covers:
- How {{solution_name}} addresses {{specific_pain_point}}
- Case study from {{similar_company}} with {{results_achieved}}
- Implementation timeline and next steps for {{company_name}}

I have availability for a 30-minute call on:
- {{time_slot_1}}
- {{time_slot_2}}
- {{time_slot_3}}

Or feel free to book directly on my calendar: {{calendar_link}}

Looking forward to our conversation!

Best,
{{sender_name}}"""
            }
        }
        
        # Industry-specific insights and pain points
        self.industry_data = {
            "technology": {
                "pain_points": ["manual deployment processes", "data silos", "scaling challenges", "technical debt"],
                "success_metrics": ["deployment frequency", "system reliability", "developer productivity", "time to market"],
                "insights": ["Tech companies waste 40% of developer time on manual tasks", "Automation can reduce deployment time by 85%"],
                "similar_companies": ["TechCorp", "DataFlow Systems", "CloudScale Inc"]
            },
            "healthcare": {
                "pain_points": ["patient data management", "appointment scheduling", "billing automation", "compliance reporting"],
                "success_metrics": ["patient satisfaction", "operational efficiency", "cost reduction", "compliance scores"],
                "insights": ["Healthcare organizations save 25+ hours per week with automation", "Patient satisfaction increases 30% with streamlined processes"],
                "similar_companies": ["MedTech Solutions", "HealthFlow Partners", "CareSync Systems"]
            },
            "finance": {
                "pain_points": ["manual reporting", "risk assessment", "customer onboarding", "compliance monitoring"],
                "success_metrics": ["processing time", "accuracy rates", "customer satisfaction", "regulatory compliance"],
                "insights": ["Financial firms reduce processing time by 75% with automation", "Automated compliance reduces risk by 60%"],
                "similar_companies": ["FinanceFirst", "Capital Automation", "SecureBank Systems"]
            },
            "retail": {
                "pain_points": ["inventory management", "customer service", "order processing", "supply chain optimization"],
                "success_metrics": ["order accuracy", "customer satisfaction", "inventory turnover", "fulfillment speed"],
                "insights": ["Retailers increase efficiency by 45% with automation", "Customer satisfaction improves 35% with automated processes"],
                "similar_companies": ["RetailMax", "ShopFlow Solutions", "CommerceHub"]
            },
            "manufacturing": {
                "pain_points": ["production scheduling", "quality control", "supply chain management", "equipment maintenance"],
                "success_metrics": ["production efficiency", "quality scores", "downtime reduction", "cost savings"],
                "insights": ["Manufacturers reduce costs by 30% with automation", "Quality improves 50% with automated monitoring"],
                "similar_companies": ["ManuTech Corp", "ProductionFlow", "IndustryMax Systems"]
            }
        }
        
        # Company size-based messaging
        self.size_messaging = {
            "startup": {
                "focus": "scaling efficiently without increasing overhead",
                "concerns": ["limited resources", "rapid growth", "technical debt"],
                "benefits": ["scale without hiring", "reduce manual work", "focus on core business"]
            },
            "small": {
                "focus": "automating repetitive tasks to free up valuable time",
                "concerns": ["resource constraints", "operational efficiency", "cost management"],
                "benefits": ["save time", "reduce costs", "improve accuracy"]
            },
            "medium": {
                "focus": "standardizing processes and improving operational efficiency",
                "concerns": ["process standardization", "team coordination", "growth management"],
                "benefits": ["streamline operations", "improve consistency", "enable growth"]
            },
            "large": {
                "focus": "enterprise-scale automation and digital transformation",
                "concerns": ["legacy systems", "compliance", "organizational alignment"],
                "benefits": ["digital transformation", "competitive advantage", "operational excellence"]
            }
        }
    
    def generate_personalized_message(
        self,
        contact: OutreachContact,
        message_type: str = "cold_intro",
        custom_variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Generate a personalized outreach message for a specific contact
        """
        company = contact.company
        
        # Analyze company and build context
        context = self._build_message_context(company, contact)
        
        # Add custom variables if provided
        if custom_variables:
            context.update(custom_variables)
        
        # Get template
        template_data = self.templates.get(message_type, self.templates["cold_intro"])
        
        # Render template with context
        env = Environment(loader=DictLoader({"subject": template_data["subject"], "message": template_data["message"]}))
        
        subject_template = env.get_template("subject")
        message_template = env.get_template("message")
        
        try:
            subject = subject_template.render(**context)
            message = message_template.render(**context)
            
            return {
                "subject": subject,
                "message": message,
                "personalization_score": self._calculate_personalization_score(context),
                "context_used": context
            }
        except Exception as e:
            # Fallback to basic template if rendering fails
            return self._generate_fallback_message(contact, message_type)
    
    def _build_message_context(self, company: Company, contact: OutreachContact) -> Dict[str, Any]:
        """
        Build comprehensive context for message personalization
        """
        # Basic contact and company info
        context = {
            "contact_name": contact.name,
            "company_name": company.name,
            "industry": company.industry or "technology",
            "sender_name": "Kaelen Jennings",
            "sender_title": "Business Automation Specialist",
            "linkedin_url": "https://linkedin.com/in/kaelen-jennings",
            "calendar_link": "https://calendly.com/kaelen-jennings"
        }
        
        # Determine company size
        company_size = self._determine_company_size(company.employee_count)
        context["company_size"] = company_size
        
        # Get industry-specific data
        industry_info = self.industry_data.get(company.industry, self.industry_data["technology"])
        
        # Select appropriate pain point and messaging
        pain_point = self._select_pain_point(company, industry_info)
        context["pain_point"] = pain_point
        context["current_challenge"] = f"managing {pain_point} manually"
        
        # Build value proposition
        size_info = self.size_messaging[company_size]
        context["value_proposition"] = size_info["focus"]
        context["key_benefit"] = size_info["benefits"][0]
        
        # Add industry insights and statistics
        context["industry_statistic"] = industry_info["insights"][0]
        context["industry_insight"] = industry_info["insights"][1] if len(industry_info["insights"]) > 1 else industry_info["insights"][0]
        
        # Success story and social proof
        similar_company = industry_info["similar_companies"][0]
        context["similar_company"] = similar_company
        context["success_story"] = f"reduce their {pain_point} workload by 75%"
        context["success_story_detailed"] = f"We recently helped {similar_company}, a similar {company.industry} company, automate their {pain_point} process. They saw a 75% reduction in manual work and saved over $50,000 annually."
        
        # Financial projections
        estimated_savings = self._calculate_estimated_savings(company, pain_point)
        context["estimated_savings"] = f"${estimated_savings:,}"
        context["specific_benefit"] = f"${estimated_savings:,} in annual savings"
        context["roi_percentage"] = "250"
        context["payback_period"] = "4-6 months"
        
        # Solution naming and positioning
        context["solution_name"] = "JobBot Automation Platform"
        context["solution_category"] = "business process automation"
        context["proposed_solution"] = f"Automated {pain_point} system with real-time monitoring and reporting"
        
        # Company-specific insights
        context["company_insight"] = self._generate_company_insight(company)
        context["business_model"] = self._infer_business_model(company)
        context["company_goal"] = f"scaling {company.name}'s operations"
        
        # Personal touches and compelling insights
        context["personal_touch"] = self._generate_personal_touch(company, contact)
        context["compelling_insight"] = self._generate_compelling_insight(company, pain_point)
        
        # Demo and next steps
        context["demo_url"] = f"https://demos.jobbot.ai/{company.id}"
        context["time_slot_1"] = self._generate_time_slot(1)
        context["time_slot_2"] = self._generate_time_slot(2)
        context["time_slot_3"] = self._generate_time_slot(3)
        
        return context
    
    def _determine_company_size(self, employee_count: Optional[int]) -> str:
        """Determine company size category"""
        if not employee_count:
            return "small"
        
        if employee_count < 10:
            return "startup"
        elif employee_count < 50:
            return "small"
        elif employee_count < 500:
            return "medium"
        else:
            return "large"
    
    def _select_pain_point(self, company: Company, industry_info: Dict[str, Any]) -> str:
        """Select most relevant pain point for the company"""
        # Use company's automation opportunities if available
        if company.automation_opportunities:
            return company.automation_opportunities[0]
        
        # Fall back to industry-specific pain points
        return industry_info["pain_points"][0]
    
    def _calculate_estimated_savings(self, company: Company, pain_point: str) -> int:
        """Calculate estimated annual savings"""
        base_savings = 25000  # Base savings amount
        
        # Adjust based on company size
        size_multiplier = {
            "startup": 0.5,
            "small": 1.0,
            "medium": 2.0,
            "large": 4.0
        }
        
        company_size = self._determine_company_size(company.employee_count)
        multiplier = size_multiplier[company_size]
        
        # Adjust based on pain point complexity
        pain_point_multiplier = {
            "manual deployment": 1.5,
            "data silos": 2.0,
            "patient data management": 1.8,
            "manual reporting": 1.3,
            "inventory management": 1.6
        }
        
        pain_multiplier = 1.0
        for key, mult in pain_point_multiplier.items():
            if key in pain_point.lower():
                pain_multiplier = mult
                break
        
        return int(base_savings * multiplier * pain_multiplier)
    
    def _generate_company_insight(self, company: Company) -> str:
        """Generate specific insight about the company"""
        insights = [
            f"I see you're in the {company.industry} space",
            f"I noticed {company.name} has been growing rapidly",
            f"Your team at {company.name} is doing great work",
            f"I was impressed by {company.name}'s approach to {company.industry}"
        ]
        
        if company.website:
            insights.append(f"I was browsing {company.website} and was impressed by your approach")
        
        if company.description:
            insights.append(f"I read about {company.name}'s mission and it really resonated with me")
        
        # Return first insight that makes sense
        return insights[0]
    
    def _infer_business_model(self, company: Company) -> str:
        """Infer business model from company data"""
        if company.industry == "technology":
            return "SaaS platform"
        elif company.industry == "retail":
            return "e-commerce business"
        elif company.industry == "healthcare":
            return "healthcare services"
        elif company.industry == "finance":
            return "financial services"
        else:
            return "business operations"
    
    def _generate_personal_touch(self, company: Company, contact: OutreachContact) -> str:
        """Generate a personal touch for the message"""
        touches = [
            f"I'd love to learn more about {company.name}'s automation journey",
            f"Hope you're having a great week at {company.name}",
            f"I'm excited about the potential to help {company.name} grow",
            f"Looking forward to potentially working together"
        ]
        
        if contact.linkedin_url:
            touches.append("I saw your profile on LinkedIn and was impressed by your background")
        
        return touches[0]
    
    def _generate_compelling_insight(self, company: Company, pain_point: str) -> str:
        """Generate a compelling final insight"""
        insights = [
            f"Companies that don't automate {pain_point} typically spend 40% more on operational costs",
            f"Your competitors are likely already automating {pain_point} - don't get left behind",
            f"The cost of not addressing {pain_point} compounds every month you wait",
            f"I've seen companies double their efficiency by automating {pain_point}"
        ]
        
        return insights[0]
    
    def _generate_time_slot(self, slot_number: int) -> str:
        """Generate available time slots for meetings"""
        base_date = datetime.now() + timedelta(days=2 + slot_number)
        time_options = ["10:00 AM", "2:00 PM", "4:00 PM"]
        
        return f"{base_date.strftime('%A, %B %d')} at {time_options[slot_number % 3]}"
    
    def _calculate_personalization_score(self, context: Dict[str, Any]) -> float:
        """Calculate how personalized the message is (0-100 score)"""
        score = 0
        max_score = 100
        
        # Company name mentioned: +20 points
        if context.get("company_name"):
            score += 20
        
        # Industry-specific content: +15 points
        if context.get("industry") and context.get("pain_point"):
            score += 15
        
        # Financial projections: +15 points
        if context.get("estimated_savings"):
            score += 15
        
        # Company-specific insights: +20 points
        if context.get("company_insight"):
            score += 20
        
        # Success story relevance: +10 points
        if context.get("similar_company"):
            score += 10
        
        # Contact name: +10 points
        if context.get("contact_name"):
            score += 10
        
        # Demo URL: +10 points
        if context.get("demo_url"):
            score += 10
        
        return min(score, max_score)
    
    def _generate_fallback_message(self, contact: OutreachContact, message_type: str) -> Dict[str, str]:
        """Generate a basic fallback message if template rendering fails"""
        company = contact.company
        
        subject = f"Automation opportunity for {company.name}"
        message = f"""Hi {contact.name},

I hope this email finds you well. I've been researching companies in the {company.industry or 'your'} industry and came across {company.name}.

We help companies like yours automate their business processes, typically saving 20-30 hours per week and reducing operational costs significantly.

Would you be interested in a brief conversation about how this might benefit {company.name}?

Best regards,
Kaelen Jennings"""
        
        return {
            "subject": subject,
            "message": message,
            "personalization_score": 30.0,
            "context_used": {"fallback": True}
        }
    
    def generate_email_sequence(
        self,
        contact: OutreachContact,
        sequence_length: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Generate a complete email sequence for a contact
        """
        sequence_types = ["cold_intro", "follow_up_1", "value_demonstration", "final_attempt"]
        sequence = []
        
        for i in range(min(sequence_length, len(sequence_types))):
            message_type = sequence_types[i]
            
            # Generate message with sequence-specific timing
            message_data = self.generate_personalized_message(contact, message_type)
            
            # Add sequence metadata
            message_data.update({
                "sequence_position": i + 1,
                "send_delay_days": [0, 3, 7, 14][i],  # Send immediately, then 3, 7, 14 days later
                "message_type": message_type,
                "recommended_send_time": self._get_optimal_send_time(i + 1)
            })
            
            sequence.append(message_data)
        
        return sequence
    
    def _get_optimal_send_time(self, sequence_position: int) -> str:
        """Get optimal send time based on sequence position"""
        optimal_times = {
            1: "Tuesday 10:00 AM",  # Cold intro - Tuesday morning
            2: "Thursday 2:00 PM",  # First follow-up - Thursday afternoon
            3: "Tuesday 9:00 AM",   # Value demo - Tuesday morning
            4: "Friday 11:00 AM"    # Final attempt - Friday late morning
        }
        
        return optimal_times.get(sequence_position, "Tuesday 10:00 AM")
    
    def analyze_response_sentiment(self, response_text: str) -> Dict[str, Any]:
        """
        Analyze sentiment and intent of email responses
        """
        # Simple keyword-based sentiment analysis
        positive_keywords = ["interested", "yes", "sounds good", "let's schedule", "tell me more", "curious"]
        negative_keywords = ["not interested", "no thanks", "remove", "unsubscribe", "stop", "busy"]
        neutral_keywords = ["maybe", "later", "think about it", "not now", "timing"]
        
        response_lower = response_text.lower()
        
        positive_score = sum(1 for keyword in positive_keywords if keyword in response_lower)
        negative_score = sum(1 for keyword in negative_keywords if keyword in response_lower)
        neutral_score = sum(1 for keyword in neutral_keywords if keyword in response_lower)
        
        if positive_score > negative_score and positive_score > neutral_score:
            sentiment = "positive"
            confidence = min(positive_score * 0.3, 1.0)
        elif negative_score > positive_score and negative_score > neutral_score:
            sentiment = "negative"
            confidence = min(negative_score * 0.3, 1.0)
        else:
            sentiment = "neutral"
            confidence = min(neutral_score * 0.2, 0.6)
        
        # Extract intent
        intent = "unknown"
        if any(word in response_lower for word in ["schedule", "meeting", "call", "demo"]):
            intent = "schedule_meeting"
        elif any(word in response_lower for word in ["information", "details", "tell me more"]):
            intent = "request_information"
        elif any(word in response_lower for word in ["not interested", "remove", "stop"]):
            intent = "opt_out"
        elif any(word in response_lower for word in ["later", "busy", "timing"]):
            intent = "timing_issue"
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "intent": intent,
            "positive_score": positive_score,
            "negative_score": negative_score,
            "neutral_score": neutral_score,
            "response_length": len(response_text),
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def get_campaign_metrics(self, campaign_id: int) -> Dict[str, Any]:
        """
        Get comprehensive metrics for an outreach campaign
        """
        campaign = self.db.query(OutreachCampaign).filter(OutreachCampaign.id == campaign_id).first()
        if not campaign:
            return {"error": "Campaign not found"}
        
        contacts = self.db.query(OutreachContact).filter(OutreachContact.campaign_id == campaign_id).all()
        
        total_contacts = len(contacts)
        sent_count = sum(1 for contact in contacts if contact.status in ["sent", "delivered", "opened", "replied"])
        opened_count = sum(1 for contact in contacts if contact.status in ["opened", "replied"])
        replied_count = sum(1 for contact in contacts if contact.status == "replied")
        
        # Calculate average personalization score
        total_score = 0
        scored_messages = 0
        
        for contact in contacts:
            if contact.personalization_data and "personalization_score" in contact.personalization_data:
                total_score += contact.personalization_data["personalization_score"]
                scored_messages += 1
        
        avg_personalization = total_score / scored_messages if scored_messages > 0 else 0
        
        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign.name,
            "total_contacts": total_contacts,
            "sent_count": sent_count,
            "opened_count": opened_count,
            "replied_count": replied_count,
            "open_rate": (opened_count / sent_count * 100) if sent_count > 0 else 0,
            "response_rate": (replied_count / sent_count * 100) if sent_count > 0 else 0,
            "average_personalization_score": avg_personalization,
            "campaign_status": campaign.status,
            "created_at": campaign.created_at.isoformat(),
            "last_updated": campaign.updated_at.isoformat() if campaign.updated_at else None
        }


# Utility functions for outreach generation
def generate_message_for_contact(contact_id: int, message_type: str = "cold_intro") -> Dict[str, str]:
    """
    Convenience function to generate a message for a specific contact
    """
    db = next(get_db())
    generator = OutreachMessageGenerator(db)
    
    contact = db.query(OutreachContact).filter(OutreachContact.id == contact_id).first()
    if not contact:
        raise ValueError(f"Contact {contact_id} not found")
    
    return generator.generate_personalized_message(contact, message_type)


def create_outreach_sequence(contact_id: int) -> List[Dict[str, Any]]:
    """
    Create a complete outreach sequence for a contact
    """
    db = next(get_db())
    generator = OutreachMessageGenerator(db)
    
    contact = db.query(OutreachContact).filter(OutreachContact.id == contact_id).first()
    if not contact:
        raise ValueError(f"Contact {contact_id} not found")
    
    return generator.generate_email_sequence(contact)


def analyze_campaign_performance(campaign_id: int) -> Dict[str, Any]:
    """
    Analyze the performance of an outreach campaign
    """
    db = next(get_db())
    generator = OutreachMessageGenerator(db)
    
    return generator.get_campaign_metrics(campaign_id)