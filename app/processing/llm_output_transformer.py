import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
import logging

logger = logging.getLogger(__name__)

# --- Helper Functions for Extraction ---

def _extract_field(text: str, pattern: str, group_index: int = 1, default: Any = None) -> Optional[str]:
    """Extracts a field using regex, returns default if not found or error."""
    try:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match and len(match.groups()) >= group_index:
            return match.group(group_index).strip()
    except Exception as e:
        logger.debug(f"Regex error for pattern '{pattern}': {e}")
    return default

def _extract_keywords(text: str, keyword_patterns: Optional[List[str]] = None) -> List[str]:
    """Extracts keywords based on a list of patterns or common keyword indicators."""
    keywords = set()
    if keyword_patterns:
        for pattern in keyword_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple): # some patterns might return tuples
                    for m_item in match:
                        if m_item.strip(): keywords.add(m_item.strip())
                elif match.strip():
                    keywords.add(match.strip())
    else:
        # Default keyword extraction (example)
        # Look for sections like "Skills:", "Keywords:", or common tech terms
        skills_match = re.search(r"(?:Skills|Keywords|Technologies):(.*?)(

|\Z)", text, re.IGNORECASE | re.DOTALL)
        if skills_match:
            kw_text = skills_match.group(1)
            # Split by comma, newline, or common delimiters, then clean up
            possible_keywords = re.split(r'[
,;•*-]+', kw_text)
            for kw in possible_keywords:
                kw_cleaned = kw.strip()
                if kw_cleaned and len(kw_cleaned) > 1: # Avoid single characters
                    keywords.add(kw_cleaned)
    return sorted(list(keywords))

def _parse_salary(text: str) -> Dict[str, Optional[Union[int, str]]]:
    """Parses various salary string formats into min_salary, max_salary, and string."""
    # Example patterns (can be made much more comprehensive)
    # $100k - $120k, $100,000-$120,000, $100K-$120K
    range_match1 = re.search(r"\$(\d{1,3}(?:[kK]|,\d{3}))\s*-\s*\$(\d{1,3}(?:[kK]|,\d{3}))", text)
    # $100,000 to $120,000
    range_match2 = re.search(r"\$(\d{1,3}(?:,\d{3})?)\s*(?:to|-)\s*\$(\d{1,3}(?:,\d{3})?)", text)
    # $100k+
    min_plus_match = re.search(r"\$(\d{1,3}(?:[kK]|,\d{3}))\s*\+", text)
    # Up to $120k
    up_to_match = re.search(r"(?:Up to|Max(?:imum)?)\s*\$(\d{1,3}(?:[kK]|,\d{3}))", text)
    # Single value $100k
    single_match = re.search(r"\$(?<!(?:to|-)\s)(\d{1,3}(?:[kK]|,\d{3}))(?!\s*\+)", text)

    def convert_salary_value(s_val: str) -> int:
        s_val = s_val.upper().replace(',', '')
        if 'K' in s_val:
            return int(s_val.replace('K', '')) * 1000
        return int(s_val)

    min_salary, max_salary, salary_str = None, None, None

    if range_match1:
        min_salary = convert_salary_value(range_match1.group(1))
        max_salary = convert_salary_value(range_match1.group(2))
        salary_str = f"${min_salary:,} - ${max_salary:,}"
    elif range_match2:
        min_salary = convert_salary_value(range_match2.group(1))
        max_salary = convert_salary_value(range_match2.group(2))
        salary_str = f"${min_salary:,} - ${max_salary:,}"
    elif min_plus_match:
        min_salary = convert_salary_value(min_plus_match.group(1))
        salary_str = f"${min_salary:,}+"
    elif up_to_match:
        max_salary = convert_salary_value(up_to_match.group(1))
        salary_str = f"Up to ${max_salary:,}"
    elif single_match: # Must be after range_match1/2 to avoid partial match
        val = convert_salary_value(single_match.group(1))
        min_salary = val
        max_salary = val # Or consider it just min_salary, depends on policy
        salary_str = f"${val:,}"
    else: # Fallback: look for any mention of salary
        salary_text_match = re.search(r"Salary:\s*(.*)", text, re.IGNORECASE)
        if salary_text_match:
            salary_str = salary_text_match.group(1).strip()
        elif "competitive" in text.lower():
            salary_str = "Competitive"

    return {"min_salary": min_salary, "max_salary": max_salary, "salary_range_string": salary_str}

def _parse_date(date_str: Optional[str]) -> Optional[str]:
    """Parses date string into YYYY-MM-DD format."""
    if not date_str:
        return None
    try:
        # Try common formats, e.g., "2023-10-15", "Oct 15, 2023", "10/15/2023"
        # This is simplified; a robust parser would handle more.
        dt_obj = None
        if re.match(r"\d{4}-\d{2}-\d{2}", date_str):
            dt_obj = datetime.strptime(date_str, "%Y-%m-%d")
        elif re.match(r"\w{3}\s\d{1,2},\s\d{4}", date_str): # Oct 15, 2023
            dt_obj = datetime.strptime(date_str, "%b %d, %Y")
        elif re.match(r"\d{1,2}/\d{1,2}/\d{4}", date_str): # 10/15/2023
            dt_obj = datetime.strptime(date_str, "%m/%d/%Y")

        return dt_obj.strftime("%Y-%m-%d") if dt_obj else date_str # return original if not parsed
    except ValueError:
        return date_str # Return original if parsing fails

# --- Main Transformation Functions ---

def transform_llm_job_output_to_json(llm_output: str, source_url: str, source_site_name: str) -> Dict[str, Any]:
    """
    Transforms raw LLM text output for a job posting into the standardized Job Posting JSON schema.
    Assumes LLM output might be semi-structured text with common labels.
    """
    logger.info(f"Transforming LLM job output for URL: {source_url}")

    job_data = {
        "title": _extract_field(llm_output, r"Title:\s*(.*?)
"),
        "company": _extract_field(llm_output, r"Company:\s*(.*?)
"),
        "company_domain": _extract_field(llm_output, r"Domain:\s*(.*?)
"),
        "location": _extract_field(llm_output, r"Location:\s*(.*?)
"),
        "job_url": source_url, # URL is usually a known input to the LLM task
        "source_site": source_site_name,
        "description": _extract_field(llm_output, r"Description:\s*(.*?)(?=
\w+:\s*|\Z)", default=""),
        "requirements": _extract_field(llm_output, r"Requirements:\s*(.*?)(?=
\w+:\s*|\Z)", default=""),
        "benefits": _extract_field(llm_output, r"Benefits:\s*(.*?)(?=
\w+:\s*|\Z)", default=""),
        "job_type": _extract_field(llm_output, r"Type:\s*(.*?)
"),
        "experience_level": _extract_field(llm_output, r"Experience(?: Level)?:\s*(.*?)
"),
        "industry": _extract_field(llm_output, r"Industry:\s*(.*?)
"),
        "posting_date": _parse_date(_extract_field(llm_output, r"Posted(?: Date)?:\s*(.*?)
")),
        "application_deadline": _parse_date(_extract_field(llm_output, r"Application Deadline:\s*(.*?)
")),
        "is_remote": "remote" in (_extract_field(llm_output, r"Location:\s*(.*?)
", default="").lower() or ""),
        "raw_text_content": llm_output # Store the full raw output if needed
    }

    salary_info = _parse_salary(_extract_field(llm_output, r"Salary:\s*(.*?)
", default=""))
    job_data.update(salary_info)

    job_data["keywords"] = _extract_keywords(
        f"{job_data.get('title','')} {job_data.get('description','')} {job_data.get('requirements','')}"
    )

    # Ensure required fields have fallbacks or are handled if None
    job_data["title"] = job_data["title"] or "N/A"
    job_data["company"] = job_data["company"] or "N/A"

    # Validate against schema (basic check for required fields)
    if not all([job_data.get("title"), job_data.get("company"), job_data.get("job_url"), job_data.get("source_site")]):
        logger.warning(f"Transformed job data missing required fields for URL {source_url}")
        # Potentially raise an error or return a specific structure indicating failure

    return job_data

def transform_llm_company_output_to_json(llm_output: str, visited_urls: List[str]) -> Dict[str, Any]:
    """
    Transforms raw LLM text output for company intelligence into the standardized Company Intelligence JSON schema.
    Assumes LLM output might be markdown-like or sectioned text.
    """
    logger.info(f"Transforming LLM company output. Visited URLs: {', '.join(visited_urls[:1])}...")

    # Helper to extract sections from markdown-like text
    def _extract_section(text: str, section_title: str) -> Optional[str]:
        match = re.search(rf"##\s*{section_title}\s*##
(.*?)(?=
##\s|\Z)", text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else None

    def _parse_list_from_section(section_text: Optional[str]) -> List[str]:
        if not section_text:
            return []
        return [line.strip().lstrip("-* ").strip() for line in section_text.split('
') if line.strip().lstrip("-* ").strip()]

    def _parse_key_value_from_section(section_text: Optional[str]) -> Dict[str, str]:
        if not section_text:
            return {}
        data = {}
        for line in section_text.split('
'):
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
        return data

    company_data = {
        "company_name": _extract_field(llm_output, r"#\s*Company Intelligence:\s*(.*?)
") or                         _extract_field(llm_output, r"Company Name:\s*(.*?)
"),
        "company_domain": _extract_field(llm_output, r"Domain:\s*(.*?)
"),
        "website_url": None, # Often one of the visited_urls or explicitly stated
        "description_summary": _extract_section(llm_output, "Summary"),
        "industry_tags": _parse_list_from_section(_extract_section(llm_output, "Industry Tags")),
        "source_urls_visited": visited_urls,
        "session_notes": _extract_section(llm_output, "Session Notes")
    }

    if company_data["company_domain"] and not company_data["website_url"]:
        # Attempt to construct a plausible website_url if not explicitly given
        # This is a guess; LLM might provide it directly or it might be the primary visited_url
        for url in visited_urls:
            if company_data["company_domain"] in url:
                company_data["website_url"] = url
                break
        if not company_data["website_url"] and visited_urls:
             company_data["website_url"] = visited_urls[0]


    location_text = _extract_section(llm_output, "Location")
    if location_text:
        company_data["location_info"] = {"full_address": location_text} # Further parsing can be added

    size_text = _extract_section(llm_output, "Size")
    if size_text:
        company_data["size_info"] = {"employee_count_text": size_text} # Further parsing

    social_text = _extract_section(llm_output, "Social Media")
    if social_text:
        company_data["social_media_links"] = _parse_key_value_from_section(social_text)

    # Observed Tech Stack (simplified parsing)
    tech_section = _extract_section(llm_output, "Observed Tech")
    if tech_section:
        company_data["observed_tech_stack"] = []
        for line in _parse_list_from_section(tech_section):
            parts = line.split('(', 1)
            name = parts[0].strip()
            category_notes = parts[1].rstrip(')').strip() if len(parts) > 1 else "general"
            # Simplistic category split, could be improved
            category = category_notes.split(':')[0].strip() if ':' in category_notes else "Unknown"
            notes = category_notes.split(':',1)[1].strip() if ':' in category_notes else category_notes

            company_data["observed_tech_stack"].append({"name": name, "category": category, "notes": notes})


    # Pain Points / Opportunities (simplified parsing)
    pain_points_section = _extract_section(llm_output, "Pain Points / Opportunities")
    if pain_points_section:
        company_data["identified_pain_points"] = []
        company_data["potential_opportunities"] = []
        for item_desc in _parse_list_from_section(pain_points_section):
            # Crude split, LLM should ideally structure this better or use sub-sections
            if "opportunity" in item_desc.lower():
                 company_data["potential_opportunities"].append({"type": "General", "description": item_desc})
            else:
                 company_data["identified_pain_points"].append({"description": item_desc})


    # Key Personnel (simplified parsing)
    people_section = _extract_section(llm_output, "Key People")
    if people_section:
        company_data["key_personnel"] = []
        for line in _parse_list_from_section(people_section):
            name_parts = line.split('(', 1)
            name = name_parts[0].strip()
            title_email = name_parts[1].rstrip(')').strip() if len(name_parts) > 1 else ""
            # This parsing is very basic, relies on consistent LLM output
            title = title_email.split('-')[0].strip() if '-' in title_email else title_email
            email = title_email.split('-')[1].strip() if '-' in title_email and '@' in title_email else None
            company_data["key_personnel"].append({"name": name, "title": title, "email": email, "notes": title_email})

    # Website Audit Observations
    audit_section = _extract_section(llm_output, "Website Audit")
    if audit_section: # Assuming simple text, real audit would be more structured
        company_data["website_audit_observations"] = {"overall_impression": audit_section}


    # Ensure required fields
    company_data["company_name"] = company_data.get("company_name") or "Unknown Company"
    company_data["company_domain"] = company_data.get("company_domain") # Can be null if not found

    if not company_data.get("company_domain") and company_data.get("website_url"):
        try:
            from urllib.parse import urlparse
            company_data["company_domain"] = urlparse(company_data["website_url"]).netloc
        except:
            pass # keep domain as null

    if not company_data.get("company_name") or not company_data.get("company_domain"):
         logger.warning(f"Transformed company data missing name or domain. Primary URL: {visited_urls[0] if visited_urls else 'N/A'}")

    return company_data

# --- Example Usage (for testing this script directly) ---
if __name__ == "__main__":
    # Example LLM output for a job posting
    sample_llm_job_text = """
    Title: Senior Software Engineer
    Company: TechNova Solutions
    Domain: technova.com
    Location: New York, NY (Remote option available)
    Salary: $150k - $180K per year
    Type: Full-time
    Experience: 5+ years
    Posted Date: 2023-11-01
    Keywords: Python, Django, AWS, REST APIs
    Description:
    We are looking for a skilled Senior Software Engineer to join our dynamic team.
    You will be responsible for designing, developing, and maintaining our flagship product.
    Requirements:
    - Bachelor's degree in Computer Science or related field.
    - 5+ years of experience with Python and Django.
    - Strong understanding of AWS services.
    Benefits:
    - Competitive salary and stock options.
    - Comprehensive health, dental, and vision insurance.
    - Unlimited PTO.
    """
    job_json = transform_llm_job_output_to_json(sample_llm_job_text, "https://jobs.technova.com/sde", "TechNova Careers")
    print("--- Transformed Job JSON ---")
    print(json.dumps(job_json, indent=2))

    # Example LLM output for company intelligence
    sample_llm_company_text = """
    # Company Intelligence: Innovate Corp

    ## Domain:
    innovatecorp.com

    ## Source URLs Visited:
    - https://innovatecorp.com/about-us
    - https://innovatecorp.com/blog

    ## Summary:
    Innovate Corp provides cutting-edge AI solutions for the healthcare industry.
    They focus on predictive analytics and patient outcome improvement.

    ## Location:
    456 Future Drive, Suite 200, San Francisco, CA 94107

    ## Size:
    Around 150 employees. Recently closed a Series C funding round.

    ## Observed Tech:
    - Main website uses React and Next.js.
    - Blog appears to be on Medium.
    - Customer portal uses Auth0 for authentication.

    ## Pain Points / Opportunities:
    - Their careers page lists several DevOps roles, suggesting scaling challenges (Opportunity: DevOps consulting).
    - Blog mentions interest in expanding to European markets (Opportunity: Localization services).

    ## Key People:
    - Dr. Alice Quantum (Founder & CEO) - Found on About Us page.
    - Bob Architekt (Lead AI Researcher) - Mentioned in a blog post.

    ## Session Notes:
    LLM successfully identified their core business from the About Us page.
    Funding info was cross-referenced by human operator from a (fictional) news link.
    """
    company_json = transform_llm_company_output_to_json(sample_llm_company_text, ["https://innovatecorp.com/about-us", "https://innovatecorp.com/blog"])
    print("\n--- Transformed Company Intelligence JSON ---")
    print(json.dumps(company_json, indent=2))
