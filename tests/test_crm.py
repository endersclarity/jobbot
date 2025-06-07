import unittest
import datetime
import sqlite3
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.crm import generate_resume_template, generate_cover_letter_template, log_communication
import src.database as db_module # Use an alias to avoid conflict with local 'db' variables

# Store original DB name from the imported module
ORIGINAL_DATABASE_NAME = db_module.DATABASE_NAME

class TestCRM(unittest.TestCase):

    def setUp(self):
        # Mock job and user profile data
        self.mock_job_details = {
            'title': 'Senior Python Developer',
            'company': 'Innovatech Ltd.',
            'description': 'Looking for an experienced Python developer...',
            'skills': ['Python', 'Django', 'REST APIs', 'PostgreSQL'],
            'url': 'http://innovatech.com/job/123'
        }
        self.mock_user_profile = {
            'name': 'Alice Wonderland',
            'email': 'alice.w@example.com',
            'phone': '555-1234',
            'linkedin': 'linkedin.com/in/alicew',
            'experience': [
                {'title': 'Software Developer', 'company': 'Old Tech Inc.', 'duration': '3 years',
                 'description': 'Developed features for a SaaS product using Python and Flask.'},
                {'title': 'Junior Developer', 'company': 'Startup X', 'duration': '1 year',
                 'description': 'Assisted in front-end and back-end development.'}
            ],
            'skills': ['Python', 'Django', 'Flask', 'JavaScript', 'SQL', 'REST APIs', 'Git']
        }

        # Setup in-memory SQLite database for log_communication testing
        db_module.DATABASE_NAME = ':memory:'
        self.conn = db_module.get_db_connection()
        db_module.create_tables() # Create tables in the in-memory DB

        # Add a sample job posting to the in-memory DB to get a valid job_posting_id
        self.test_job_id = db_module.add_job_posting(self.mock_job_details)
        if self.test_job_id is None:
             # If it already exists (e.g. from a previous failed test run if db wasn't reset)
            existing_job = db_module.get_job_posting_by_url(self.mock_job_details['url'])
            if existing_job:
                self.test_job_id = existing_job['id']
            else: # Should not happen in :memory: db normally, but as a fallback
                raise Exception("Failed to set up test_job_id for CRM tests.")


    def tearDown(self):
        if self.conn:
            self.conn.close()
        db_module.DATABASE_NAME = ORIGINAL_DATABASE_NAME # Restore original DB name

    def test_generate_resume_template(self):
        resume = generate_resume_template(self.mock_job_details, self.mock_user_profile)

        # Check for user profile details
        self.assertIn(self.mock_user_profile['name'], resume)
        self.assertIn(self.mock_user_profile['email'], resume)

        # Check for job details in objective
        self.assertIn(self.mock_job_details['title'], resume)
        self.assertIn(self.mock_job_details['company'], resume)

        # Check for prioritized skills (intersection of user and job skills)
        prioritized_skills_expected = ['Python', 'Django', 'REST APIs'] # PostgreSQL is not in user's skills
        for skill in prioritized_skills_expected:
            self.assertIn(skill, resume)
        self.assertNotIn('PostgreSQL', resume.split("Programming Languages:")[1].split("\n")[0]) # Check it's not in the languages line
        self.assertNotIn('JavaScript', resume.split("Programming Languages:")[1].split("\n")[0]) # User skill but not in job skills

        # Check for experience
        for exp in self.mock_user_profile['experience']:
            self.assertIn(exp['title'], resume)
            self.assertIn(exp['company'], resume)

        # Check for project and education placeholders
        self.assertIn("## Projects", resume)
        self.assertIn("## Education", resume)

    def test_generate_cover_letter_template(self):
        cover_letter = generate_cover_letter_template(self.mock_job_details, self.mock_user_profile, "Dr. Smith")

        self.assertIn("Dear Dr. Smith,", cover_letter)
        self.assertIn(self.mock_job_details['title'], cover_letter)
        self.assertIn(self.mock_job_details['company'], cover_letter)
        self.assertIn(self.mock_user_profile['name'], cover_letter)

        # Check that it mentions some skills from job_details.get('skills')
        # This part of the template is generic: "[Mention 1-2 skills from job_details.get('skills', []) that you possess]"
        # So we can't check for specific skills directly without more complex parsing.
        # We'll check for the placeholder phrase to ensure that part of the template is present.
        self.assertIn("[Mention 1-2 skills from job_details.get('skills', []) that you possess", cover_letter)

    def test_log_communication_success(self):
        self.assertIsNotNone(self.test_job_id, "Test job ID should be valid.")

        comm_type = "Email"
        subject = "Following up on application"
        body = "Dear Hiring Manager, I am writing to follow up..."
        follow_up_date_str = (datetime.date.today() + datetime.timedelta(days=7)).isoformat()

        log_id = log_communication(
            db_conn=self.conn,
            job_posting_id=self.test_job_id,
            contact_id=None, # Optional
            comm_type=comm_type,
            subject=subject,
            body=body,
            follow_up_date=follow_up_date_str
        )
        self.assertIsNotNone(log_id, "log_communication should return an ID on success.")

        # Verify by fetching from the database
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM communication_log WHERE id = ?", (log_id,))
        logged_comm = cursor.fetchone()

        self.assertIsNotNone(logged_comm)
        self.assertEqual(logged_comm['job_posting_id'], self.test_job_id)
        self.assertEqual(logged_comm['type'], comm_type)
        self.assertEqual(logged_comm['subject'], subject)
        self.assertEqual(logged_comm['body'], body)
        self.assertEqual(logged_comm['follow_up_date'], follow_up_date_str)
        self.assertFalse(logged_comm['response_received']) # Default

    def test_log_communication_invalid_job_id(self):
         # Attempt to log with a job_posting_id that doesn't exist
        with self.assertRaises(sqlite3.IntegrityError): # Foreign key constraint
            log_communication(
                db_conn=self.conn,
                job_posting_id=99999, # Non-existent ID
                contact_id=None,
                comm_type="Test",
                subject="Test",
                body="Test body",
                follow_up_date=datetime.date.today().isoformat()
            )
            # Note: The actual function `log_communication` in crm.py has a generic
            # `except Exception as e: print(...) return None`.
            # So, we might not see the sqlite3.IntegrityError directly from the function call itself,
            # but rather None is returned and an error is printed.
            # For a more robust test, we might need to mock `print` or make the exception handling
            # in `log_communication` more specific if we want to assert the type of DB error.
            # However, the current implementation in crm.py catches all exceptions.
            # The provided code for crm.py's log_communication prints an error and returns None.
            # Let's adjust the test to expect that behavior.

        # Re-testing with the actual behavior of the provided crm.py code
        with patch('builtins.print') as mock_print:
            log_id = log_communication(
                db_conn=self.conn,
                job_posting_id=99999, # Non-existent ID
                contact_id=None,
                comm_type="Test",
                subject="Test",
                body="Test body",
                follow_up_date=datetime.date.today().isoformat()
            )
            self.assertIsNone(log_id)
            mock_print.assert_any_call("Error logging communication: FOREIGN KEY constraint failed")


if __name__ == '__main__':
    unittest.main()
