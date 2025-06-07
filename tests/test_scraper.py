import unittest
from unittest.mock import patch, MagicMock
import requests
from bs4 import BeautifulSoup

# Assuming src/scraper.py is in a directory accessible via PYTHONPATH
# For direct relative import if tests are run as a module from project root:
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.scraper import JobPosting, scrape_indeed

class TestScraper(unittest.TestCase):

    def setUp(self):
        self.sample_job_data = {
            "title": "Software Engineer",
            "company": "Tech Innovations Inc.",
            "location": "San Francisco, CA",
            "summary": "Develop amazing software solutions.",
            "url": "http://example.com/job/123"
        }
        self.job_posting = JobPosting(**self.sample_job_data)

    def test_job_posting_creation_and_to_dict(self):
        self.assertEqual(self.job_posting.title, self.sample_job_data['title'])
        self.assertEqual(self.job_posting.company, self.sample_job_data['company'])
        self.assertEqual(self.job_posting.location, self.sample_job_data['location'])
        self.assertEqual(self.job_posting.summary, self.sample_job_data['summary'])
        self.assertEqual(self.job_posting.url, self.sample_job_data['url'])
        self.assertDictEqual(self.job_posting.to_dict(), self.sample_job_data)

    @patch('requests.get')
    def test_scrape_indeed_success(self, mock_get):
        # Mock HTML content for a successful scrape
        mock_html_content = """
        <html><body>
            <div class="job_seen_beacon">
                <h2 class="jobTitle"><a href="/job/123">Software Engineer</a></h2>
                <span class="companyName">Tech Innovations Inc.</span>
                <div class="companyLocation">San Francisco, CA</div>
                <div class="job-snippet">Develop amazing software solutions.</div>
            </div>
            <div class="job_seen_beacon">
                <h2 class="jobTitle"><a>Data Scientist</a></h2>
                <span class="companyName">Data Corp</span>
                <div class="companyLocation">New York, NY</div>
                <div class="job-snippet">Analyze complex datasets.</div>
            </div>
        </body></html>
        """
        # Configure the mock response
        mock_response = MagicMock()
        mock_response.text = mock_html_content
        mock_response.raise_for_status = MagicMock() # Ensure it doesn't raise error
        mock_get.return_value = mock_response

        jobs = scrape_indeed("software engineer", "San Francisco, CA", num_pages=1)

        self.assertEqual(len(jobs), 2)

        # Check first job
        self.assertIsInstance(jobs[0], JobPosting)
        self.assertEqual(jobs[0].title, "Software Engineer")
        self.assertEqual(jobs[0].company, "Tech Innovations Inc.")
        self.assertEqual(jobs[0].location, "San Francisco, CA")
        self.assertEqual(jobs[0].summary, "Develop amazing software solutions.")
        self.assertEqual(jobs[0].url, "https://www.indeed.com/job/123") # URL is prefixed

        # Check second job (ensure 'a' tag without href is handled)
        self.assertEqual(jobs[1].title, "Data Scientist")
        self.assertEqual(jobs[1].company, "Data Corp")
        self.assertEqual(jobs[1].url, "N/A") # No href, so should be N/A

        mock_get.assert_called_once_with(
            "https://www.indeed.com/jobs",
            params={"q": "software engineer", "l": "San Francisco, CA", "start": 0},
            timeout=10
        )

    @patch('requests.get')
    def test_scrape_indeed_no_results(self, mock_get):
        # Mock HTML content for a page with no job cards
        mock_html_content = "<html><body><div>No jobs here.</div></body></html>"

        mock_response = MagicMock()
        mock_response.text = mock_html_content
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Suppress print statements during this test
        with patch('builtins.print') as mock_print:
            jobs = scrape_indeed("nonexistent job", "nowhere", num_pages=1)
            self.assertEqual(len(jobs), 0)
            mock_print.assert_any_call("No job cards found on page 1. Indeed's HTML structure might have changed.")

    @patch('requests.get')
    def test_scrape_indeed_request_error(self, mock_get):
        # Configure the mock to raise a RequestException
        mock_get.side_effect = requests.exceptions.RequestException("Test network error")

        # Suppress print statements during this test and check if error is printed
        with patch('builtins.print') as mock_print:
            jobs = scrape_indeed("any job", "anywhere", num_pages=1)
            self.assertEqual(len(jobs), 0)
            # Check if the specific error message was printed
            mock_print.assert_any_call("Error fetching Indeed page 1: Test network error")

    @patch('requests.get')
    def test_scrape_indeed_missing_elements(self, mock_get):
        # HTML where some job cards might miss elements like company or snippet
        mock_html_content = """
        <html><body>
            <div class="job_seen_beacon">
                <h2 class="jobTitle"><a href="/job/1">Analyst</a></h2>
                <!-- Missing companyName -->
                <div class="companyLocation">Remote</div>
                <div class="job-snippet">Entry level analyst.</div>
            </div>
            <div class="job_seen_beacon">
                <h2 class="jobTitle"><a href="/job/2">Manager</a></h2>
                <span class="companyName">Big Corp</span>
                <!-- Missing companyLocation -->
                <div class="job-snippet">Manage a team.</div>
            </div>
            <div class="job_seen_beacon">
                 <!-- Missing jobTitle -->
                <span class="companyName">Ghost Company</span>
                <div class="companyLocation">Unknown</div>
                <div class="job-snippet">A job with no title.</div>
            </div>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.text = mock_html_content
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        jobs = scrape_indeed("various", "multiple locations", num_pages=1)

        self.assertEqual(len(jobs), 2) # The job with no title should be skipped

        self.assertEqual(jobs[0].title, "Analyst")
        self.assertEqual(jobs[0].company, "N/A") # Company was missing
        self.assertEqual(jobs[0].location, "Remote")
        self.assertEqual(jobs[0].url, "https://www.indeed.com/job/1")

        self.assertEqual(jobs[1].title, "Manager")
        self.assertEqual(jobs[1].company, "Big Corp")
        self.assertEqual(jobs[1].location, "N/A") # Location was missing
        self.assertEqual(jobs[1].url, "https://www.indeed.com/job/2")

if __name__ == '__main__':
    unittest.main()
