import requests
from bs4 import BeautifulSoup
import json

# Define a data structure for job postings
class JobPosting:
    def __init__(self, title, company, location, summary, url):
        self.title = title
        self.company = company
        self.location = location
        self.summary = summary
        self.url = url

    def to_dict(self):
        return {
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "summary": self.summary,
            "url": self.url
        }

def scrape_indeed(query, location, num_pages=1):
    """
    Scrapes job postings from Indeed.

    Args:
        query (str): The job title, keyword, or company to search for.
        location (str): The location to search in.
        num_pages (int): The number of pages to scrape.

    Returns:
        list: A list of JobPosting objects.
    """
    job_postings = []
    base_url = "https://www.indeed.com/jobs"

    for page in range(num_pages):
        start = page * 10  # Indeed shows 10-15 results per page, using 10 for safety
        params = {
            "q": query,
            "l": location,
            "start": start
        }
        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Indeed page {page + 1}: {e}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # Indeed's job card selectors can change. These are examples and might need updates.
        # It's crucial to inspect Indeed's HTML structure to get the correct selectors.
        job_cards = soup.find_all('div', class_='job_seen_beacon') # This is a common top-level container

        if not job_cards:
            print(f"No job cards found on page {page + 1}. Indeed's HTML structure might have changed.")
            continue

        for card in job_cards:
            title_element = card.find('h2', class_='jobTitle')
            title = title_element.get_text(strip=True) if title_element else "N/A"

            # Extract the link if possible
            link_element = title_element.find('a') if title_element else None
            job_url = "https://www.indeed.com" + link_element['href'] if link_element and link_element.has_attr('href') else "N/A"


            company_element = card.find('span', class_='companyName')
            company = company_element.get_text(strip=True) if company_element else "N/A"

            location_element = card.find('div', class_='companyLocation')
            location_text = location_element.get_text(strip=True) if location_element else "N/A"

            summary_element = card.find('div', class_='job-snippet')
            summary = summary_element.get_text(strip=True) if summary_element else "N/A"

            if title != "N/A": # Basic check to ensure it's a valid job posting
                job_postings.append(JobPosting(title, company, location_text, summary, job_url))

    return job_postings

if __name__ == '__main__':
    # Example usage:
    print("Scraping software engineer jobs in San Francisco...")
    jobs = scrape_indeed("software engineer", "San Francisco, CA", num_pages=1)
    if jobs:
        print(f"Found {len(jobs)} job postings.")
        for job in jobs:
            print(json.dumps(job.to_dict(), indent=2))
            print("-" * 20)
    else:
        print("No jobs found or an error occurred.")

    print("\nScraping data scientist jobs in New York...")
    jobs_ny = scrape_indeed("data scientist", "New York, NY", num_pages=1)
    if jobs_ny:
        print(f"Found {len(jobs_ny)} job postings.")
        for job in jobs_ny:
            print(json.dumps(job.to_dict(), indent=2))
            print("-" * 20)
    else:
        print("No jobs found or an error occurred for New York.")
