import unittest
import sqlite3
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Module to be tested
import src.database as db

# Store original DB name
ORIGINAL_DATABASE_NAME = db.DATABASE_NAME

class TestDatabase(unittest.TestCase):

    def setUp(self):
        """Set up for test methods."""
        # Override the database name to use an in-memory SQLite database
        db.DATABASE_NAME = ':memory:'
        self.conn = db.get_db_connection() # Get connection to the in-memory DB
        db.create_tables() # Create tables in the in-memory DB

        # Sample job data
        self.job_data_1 = {
            'title': 'Software Engineer',
            'company': 'TestCo',
            'location': 'Remote',
            'summary': 'Develop great software.',
            'url': 'http://example.com/job/1'
        }
        self.job_data_2 = {
            'title': 'Data Analyst',
            'company': 'AnotherTestCo',
            'location': 'New York',
            'summary': 'Analyze interesting data.',
            'url': 'http://example.com/job/2'
        }

    def tearDown(self):
        """Tear down after test methods."""
        if self.conn:
            self.conn.close()
        # Restore the original database name
        db.DATABASE_NAME = ORIGINAL_DATABASE_NAME

    def test_create_tables(self):
        """Test if all tables are created successfully."""
        cursor = self.conn.cursor()
        tables_to_check = ['job_postings', 'companies', 'tech_stack', 'job_posting_tech_stack', 'contacts', 'communication_log']
        for table_name in tables_to_check:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
            self.assertIsNotNone(cursor.fetchone(), f"Table '{table_name}' was not created.")

    def test_add_job_posting_success(self):
        """Test adding a new job posting."""
        job_id = db.add_job_posting(self.job_data_1)
        self.assertIsNotNone(job_id, "add_job_posting should return an ID on success.")

        # Verify by fetching
        fetched_job = db.get_job_posting_by_url(self.job_data_1['url'])
        self.assertIsNotNone(fetched_job)
        self.assertEqual(fetched_job['title'], self.job_data_1['title'])
        self.assertEqual(fetched_job['company_name'], self.job_data_1['company']) # Note: dict key vs db column name
        self.assertEqual(fetched_job['url'], self.job_data_1['url'])

    def test_add_job_posting_duplicate_url(self):
        """Test that adding a job with a duplicate URL fails gracefully."""
        db.add_job_posting(self.job_data_1) # Add first time

        with patch('builtins.print') as mock_print: # Suppress and check print output
            job_id_duplicate = db.add_job_posting(self.job_data_1)
            self.assertIsNone(job_id_duplicate, "Adding a duplicate URL should return None.")
            mock_print.assert_any_call(f"Error adding job posting (URL might already exist or other integrity constraint): UNIQUE constraint failed: job_postings.url")


    def test_get_job_posting_by_url_exists(self):
        """Test retrieving an existing job posting by URL."""
        db.add_job_posting(self.job_data_1)
        fetched_job = db.get_job_posting_by_url(self.job_data_1['url'])
        self.assertIsNotNone(fetched_job)
        self.assertEqual(fetched_job['title'], self.job_data_1['title'])

    def test_get_job_posting_by_url_not_exists(self):
        """Test retrieving a non-existent job posting by URL."""
        fetched_job = db.get_job_posting_by_url('http://example.com/job/nonexistent')
        self.assertIsNone(fetched_job)

    def test_get_all_job_postings_empty(self):
        """Test retrieving all job postings when none exist."""
        jobs = db.get_all_job_postings()
        self.assertEqual(len(jobs), 0)

    def test_get_all_job_postings_with_data(self):
        """Test retrieving all job postings when some exist."""
        db.add_job_posting(self.job_data_1)
        db.add_job_posting(self.job_data_2)
        jobs = db.get_all_job_postings()
        self.assertEqual(len(jobs), 2)
        # Results should be ordered by date_scraped DESC (most recent first)
        # In this case, job_data_2 was added last if add_job_posting sets current timestamp
        self.assertEqual(jobs[0]['url'], self.job_data_2['url'])
        self.assertEqual(jobs[1]['url'], self.job_data_1['url'])


    def test_get_all_job_postings_with_status_filter(self):
        """Test retrieving job postings filtered by status."""
        job_id_1 = db.add_job_posting(self.job_data_1) # Default status 'New'
        job_id_2 = db.add_job_posting(self.job_data_2)

        db.update_job_posting_status(job_id_1, 'Applied')

        new_jobs = db.get_all_job_postings(status_filter='New')
        self.assertEqual(len(new_jobs), 1)
        self.assertEqual(new_jobs[0]['id'], job_id_2)

        applied_jobs = db.get_all_job_postings(status_filter='Applied')
        self.assertEqual(len(applied_jobs), 1)
        self.assertEqual(applied_jobs[0]['id'], job_id_1)

        non_existent_status_jobs = db.get_all_job_postings(status_filter='Interviewing')
        self.assertEqual(len(non_existent_status_jobs), 0)


    def test_update_job_posting_status(self):
        """Test updating the status of a job posting."""
        job_id = db.add_job_posting(self.job_data_1)
        self.assertIsNotNone(job_id)

        # Update status
        new_status = 'Applied'
        application_ts = '2023-01-15 10:00:00' # Example timestamp
        update_success = db.update_job_posting_status(job_id, new_status, application_ts)
        self.assertTrue(update_success)

        # Verify update
        fetched_job = db.get_job_posting_by_url(self.job_data_1['url'])
        self.assertEqual(fetched_job['status'], new_status)
        self.assertEqual(fetched_job['application_date'], application_ts)

    def test_update_job_posting_status_no_date(self):
        """Test updating status without an application date."""
        job_id = db.add_job_posting(self.job_data_1)
        update_success = db.update_job_posting_status(job_id, 'Interviewing')
        self.assertTrue(update_success)
        fetched_job = db.get_job_posting_by_url(self.job_data_1['url'])
        self.assertEqual(fetched_job['status'], 'Interviewing')
        self.assertIsNone(fetched_job['application_date']) # Should remain as it was (None by default)

    def test_update_job_posting_status_non_existent_id(self):
        """Test updating status for a non-existent job ID."""
        update_success = db.update_job_posting_status(9999, 'Applied')
        self.assertFalse(update_success) # Should return False or 0 rows affected

if __name__ == '__main__':
    unittest.main()
