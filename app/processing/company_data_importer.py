import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from app.core.database import get_db, SessionLocal
from app.models.business_intelligence import (
    Company, CompanyTechStack, DecisionMaker, BusinessOpportunity, WebsiteAudit
    # Assuming 'Opportunity' is the more detailed one and 'BusinessOpportunity' might be an initial stub
    # or a different concept. For now, focusing on BusinessOpportunity for LLM-identified leads.
)
# Placeholder for actual Job model if needed for linking, though this importer is company-centric
# from app.models.jobs import Job

logger = logging.getLogger(__name__)

class CompanyDataImporter:
    """Imports company intelligence data (from LLM-guided scraping) into the database."""

    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize the company data importer.
        Args:
            db_session: Optional database session. If None, a new session will be created for operations.
        """
        self._db_session_managed_internally = db_session is None
        self.db = db_session if db_session else SessionLocal() # Use SessionLocal for a new session
        self.import_stats = {
            "companies_created": 0,
            "companies_updated": 0,
            "related_records_created": 0,
            "errors": [],
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._db_session_managed_internally:
            self.db.close()

    def import_company_intelligence(self, company_intel_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Imports a single company's intelligence data.
        Args:
            company_intel_data: A dictionary conforming to the Company Intelligence JSON schema.
        Returns:
            A dictionary with import status and company ID.
        """
        company_name = company_intel_data.get("company_name", "Unknown Company")
        company_domain = company_intel_data.get("company_domain")

        if not company_domain:
            logger.error(f"Company domain is required to import intelligence for '{company_name}'. Skipping.")
            self.import_stats["errors"].append({
                "company_name": company_name,
                "error": "Missing company_domain"
            })
            return {"status": "error", "message": "Missing company_domain"}

        try:
            company = self.db.query(Company).filter(Company.domain == company_domain).first()

            if company:
                # Update existing company
                self._update_company_record(company, company_intel_data)
                self.import_stats["companies_updated"] += 1
                action = "updated"
            else:
                # Create new company
                company = self._create_company_record(company_intel_data)
                if not company: # Should not happen if domain exists
                    return {"status": "error", "message": "Failed to create company record"}
                self.db.add(company)
                self.db.flush() # To get company.id for related records
                self.import_stats["companies_created"] += 1
                action = "created"

            # Process related entities
            if company:
                self._process_related_tech_stack(company, company_intel_data.get("observed_tech_stack", []))
                self._process_related_decision_makers(company, company_intel_data.get("key_personnel", []))
                self._process_related_opportunities(company, company_intel_data.get("potential_opportunities", []))
                self._process_related_website_observations(company, company_intel_data.get("website_audit_observations"))
                # pain_points and automation_opportunities are often JSON fields in Company model itself

            if self._db_session_managed_internally: # Commit if session is managed here
                self.db.commit()

            logger.info(f"Successfully {action} company '{company_name}' (ID: {company.id}).")
            return {"status": "success", "action": action, "company_id": company.id}

        except IntegrityError as e:
            if self._db_session_managed_internally: self.db.rollback()
            logger.error(f"Database integrity error for company '{company_name}': {e}")
            self.import_stats["errors"].append({"company_name": company_name, "error": f"IntegrityError: {e}"})
            return {"status": "error", "message": f"Database integrity error: {e}"}
        except Exception as e:
            if self._db_session_managed_internally: self.db.rollback()
            logger.error(f"Failed to import company intelligence for '{company_name}': {e}", exc_info=True)
            self.import_stats["errors"].append({"company_name": company_name, "error": str(e)})
            return {"status": "error", "message": str(e)}

    def _create_company_record(self, intel_data: Dict[str, Any]) -> Company:
        """Creates a new Company SQLAlchemy model instance from intelligence data."""
        # Map fields from Company Intelligence JSON to Company model
        # This is a simplified mapping; a more detailed one would be needed.
        new_company = Company(
            name=intel_data.get("company_name", "N/A"),
            domain=intel_data.get("company_domain"),
            website_url=intel_data.get("website_url"),
            description=intel_data.get("description_summary"),
            industry=", ".join(intel_data.get("industry_tags", [])) if intel_data.get("industry_tags") else None,
            # Location - requires parsing location_info
            city=intel_data.get("location_info", {}).get("city"),
            state=intel_data.get("location_info", {}).get("state"),
            country=intel_data.get("location_info", {}).get("country"),
            address=intel_data.get("location_info", {}).get("full_address"),
            # Size - requires parsing size_info
            size_estimate=intel_data.get("size_info", {}).get("employee_count_text"),
            # social_media (JSON field in Company model)
            social_media=intel_data.get("social_media_links"),
            # tech_stack (JSON field in Company model) - for high-level summary
            tech_stack=[tech.get('name') for tech in intel_data.get("observed_tech_stack", []) if tech.get('name')],
            pain_points=[pp.get('description') for pp in intel_data.get("identified_pain_points", []) if pp.get('description')],
            automation_opportunities=[op.get('description') for op in intel_data.get("potential_opportunities", []) if op.get('description')],
            discovery_source="LLM-Guided Session",
            discovery_date=datetime.utcnow(),
            last_scraped=datetime.utcnow(), # Mark as scraped now
            analysis_status="pending" # Needs further analysis by other modules
        )
        # TODO: Parse location_info and size_info more robustly
        # TODO: Handle other Company fields like phone, email, specific social handles if available
        return new_company

    def _update_company_record(self, company: Company, intel_data: Dict[str, Any]):
        """Updates an existing Company record with new intelligence data. (Merge logic)."""
        logger.debug(f"Updating company ID {company.id} ({company.name})")

        # Example: Update description if new one is longer or company's is empty
        new_desc = intel_data.get("description_summary")
        if new_desc and (not company.description or len(new_desc) > len(company.description)):
            company.description = new_desc

        if not company.industry and intel_data.get("industry_tags"):
            company.industry = ", ".join(intel_data.get("industry_tags", []))

        # Update JSON fields like pain_points, tech_stack by merging/appending
        # This needs careful consideration to avoid duplicate entries if run multiple times

        current_pain_points = set(company.pain_points or [])
        for pp_data in intel_data.get("identified_pain_points", []):
            current_pain_points.add(pp_data.get("description"))
        company.pain_points = sorted([p for p in list(current_pain_points) if p])

        current_tech = set(company.tech_stack or [])
        for tech_data in intel_data.get("observed_tech_stack", []):
            current_tech.add(tech_data.get("name"))
        company.tech_stack = sorted([t for t in list(current_tech) if t])

        company.last_scraped = datetime.utcnow() # Update last scraped time
        company.updated_at = datetime.utcnow()
        # More sophisticated merging logic would go here for other fields.
        pass

    def _process_related_tech_stack(self, company: Company, tech_stack_list: List[Dict[str, Any]]):
        """Processes observed_tech_stack and populates CompanyTechStack."""
        if not tech_stack_list:
            return

        for tech_data in tech_stack_list:
            tech_name = tech_data.get("name")
            if not tech_name:
                continue

            # Check if this tech already exists for the company
            existing_tech = self.db.query(CompanyTechStack).filter_by(
                company_id=company.id,
                tech_name=tech_name
            ).first()

            if existing_tech:
                # Update logic if needed, e.g., update confidence, notes
                if tech_data.get("notes") and (not existing_tech.tech_description or "LLM" not in existing_tech.tech_description): # Avoid overwriting detailed analysis
                    existing_tech.tech_description = tech_data.get("notes")
                existing_tech.detection_method = "LLM Observation" # Could append
            else:
                new_tech = CompanyTechStack(
                    company_id=company.id,
                    tech_name=tech_name,
                    tech_category=tech_data.get("category"),
                    tech_description=tech_data.get("notes"),
                    detection_method="LLM Observation", # Mark as LLM sourced
                    confidence_score=0.7 # Default confidence for LLM observation
                )
                self.db.add(new_tech)
                self.import_stats["related_records_created"] += 1
        self.db.flush()


    def _process_related_decision_makers(self, company: Company, personnel_list: List[Dict[str, Any]]):
        """Processes key_personnel and populates DecisionMaker."""
        if not personnel_list:
            return

        for person_data in personnel_list:
            name = person_data.get("name")
            if not name:
                continue

            # Try to find existing decision maker by name and company
            # More robust matching might involve email or LinkedIn if available
            existing_dm = self.db.query(DecisionMaker).filter_by(
                company_id=company.id,
                name=name
            ).first()

            if existing_dm:
                # Update logic (e.g., if new title or contact info is found)
                if person_data.get("title") and not existing_dm.title: # Example update
                    existing_dm.title = person_data.get("title")
                if person_data.get("email") and not existing_dm.email:
                    existing_dm.email = person_data.get("email")
                # ... other fields
            else:
                new_dm = DecisionMaker(
                    company_id=company.id,
                    name=name,
                    title=person_data.get("title"),
                    email=person_data.get("email"),
                    linkedin_url=person_data.get("linkedin_url"),
                    # notes from LLM could go into a specific field if model has one, or concatenated
                    # For now, DecisionMaker model might need a 'source_notes' field.
                    # Defaulting some values as LLM provides observations not full profiles
                    contact_priority=5,
                    influence_level="unknown",
                )
                self.db.add(new_dm)
                self.import_stats["related_records_created"] += 1
        self.db.flush()

    def _process_related_opportunities(self, company: Company, opportunity_list: List[Dict[str, Any]]):
        """Processes potential_opportunities and creates stubs in BusinessOpportunity."""
        if not opportunity_list:
            return

        for opp_data in opportunity_list:
            opp_type = opp_data.get("type", "General LLM Observation")
            description = opp_data.get("description")
            if not description:
                continue

            # Check if a similar opportunity already exists
            existing_opp = self.db.query(BusinessOpportunity).filter_by(
                company_id=company.id,
                opportunity_type=opp_type,
                # A more robust check might involve description similarity
            ).first() # This simple check might not be enough

            if not existing_opp: # Only create if not found; updates are complex here
                new_opp = BusinessOpportunity(
                    company_id=company.id,
                    opportunity_type=opp_type,
                    title=f"{opp_type} for {company.name}", # Generic title
                    description=description,
                    problem_statement=description, # Assuming description is the problem
                    proposed_solution=opp_data.get("value_proposition"),
                    status="identified", # Initial status
                    pain_point_source="LLM-Guided Session",
                    discovery_date=datetime.utcnow()
                    # Scores and other details to be filled by OpportunityScorer later
                )
                self.db.add(new_opp)
                self.import_stats["related_records_created"] += 1
        self.db.flush()

    def _process_related_website_observations(self, company: Company, audit_observations: Optional[Dict[str, Any]]):
        """Processes website_audit_observations and potentially creates/updates a basic WebsiteAudit record."""
        if not audit_observations:
            return

        # Check for an existing audit record (e.g., from TechStackDetector)
        # This LLM observation is likely less detailed, so be careful not to overwrite.
        # For now, this might just update notes on the Company record or a specific field.
        # A full WebsiteAudit record creation from just LLM notes might be too presumptive.

        # Example: Add to company description or a new 'llm_website_notes' field if it existed
        if audit_observations.get("overall_impression") and company.description:
            if "LLM Impression:" not in company.description: # Avoid multiple additions
                 company.description += f"\nLLM Impression: {audit_observations.get('overall_impression')}"

        # A more robust approach would be a dedicated field or a simplified audit entry
        # linked to the LLM session.
        logger.info(f"Website observations for {company.name}: {audit_observations}")
        self.db.flush()


if __name__ == "__main__":
    # Example usage (requires a database connection and the Company Intelligence JSON)

    # Sample Company Intelligence JSON (matches the schema defined in previous step)
    sample_company_intel = {
        "company_name": "Innovate Corp LLM",
        "company_domain": "innovatecorp-llm.com", # Unique domain for testing
        "website_url": "https://innovatecorp-llm.com",
        "description_summary": "Innovate Corp provides AI solutions for healthcare (LLM observed).",
        "industry_tags": ["AI", "Healthcare", "Predictive Analytics"],
        "location_info": {"full_address": "456 Future Drive, SF, CA", "city": "San Francisco", "state": "CA"},
        "size_info": {"employee_count_text": "Approx. 150 employees (LLM found)"},
        "social_media_links": {"linkedin": "https://linkedin.com/company/innovatecorp-llm"},
        "observed_tech_stack": [
            {"name": "React", "category": "Framework", "notes": "Main site uses React components."},
            {"name": "Auth0", "category": "Authentication", "notes": "Customer portal login."}
        ],
        "identified_pain_points": [
            {"description": "Careers page lists DevOps roles, suggesting scaling challenges.", "severity_guess": "medium"}
        ],
        "potential_opportunities": [
            {"type": "DevOps Consulting", "description": "Scaling challenges imply need for DevOps help.", "value_proposition": "Streamline deployment and scaling."},
            {"type": "Localization Services", "description": "Blog mentions European market expansion.", "value_proposition": "Adapt product for European market."}
        ],
        "key_personnel": [
            {"name": "Dr. Alice Quantum (LLM)", "title": "Founder & CEO", "notes": "From About Us page"}
        ],
        "website_audit_observations": {
            "overall_impression": "Modern design, but blog seems inactive.",
            "performance_notes": "Main page interactive quickly."
        },
        "source_urls_visited": ["https://innovatecorp-llm.com/about-us"],
        "session_notes": "Initial LLM pass for Innovate Corp."
    }

    # Create an importer instance (manages its own session for this example)
    importer = CompanyDataImporter()

    print(f"Attempting to import company intelligence for: {sample_company_intel['company_name']}")
    result = importer.import_company_intelligence(sample_company_intel)
    print(f"Import result: {result}")
    print(f"Import stats: {importer.import_stats}")

    # Example of updating the same company (if it exists)
    if result.get("status") == "success":
        sample_company_intel_update = {
            "company_name": "Innovate Corp LLM", # Must match
            "company_domain": "innovatecorp-llm.com", # Must match
            "description_summary": "Updated description: Now also focusing on biotech (LLM observed).",
            "identified_pain_points": [ # This should append or merge
                {"description": "New pain point: Lack of mobile app.", "severity_guess": "high"}
            ],
            "source_urls_visited": ["https://innovatecorp-llm.com/products"], # New visited URL
            "session_notes": "Second LLM pass, focused on products."
        }
        print(f"\nAttempting to update company intelligence for: {sample_company_intel_update['company_name']}")
        update_result = importer.import_company_intelligence(sample_company_intel_update)
        print(f"Update result: {update_result}")
        print(f"Updated import stats: {importer.import_stats}")

    # Remember to close the session if managed by the importer instance directly
    if importer._db_session_managed_internally:
        importer.db.close()
        print("\nDB session closed.")
