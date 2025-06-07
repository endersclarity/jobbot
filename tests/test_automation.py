import unittest
import datetime
import sqlite3
import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import src.database as db_module # Alias to avoid conflict
from src.automation import check_pending_follow_ups, draft_follow_up_email, display_application_dashboard

# Store original DB name
ORIGINAL_DATABASE_NAME = db_module.DATABASE_NAME

class TestAutomation(unittest.TestCase):

    def setUp(self):
        db_module.DATABASE_NAME = ':memory:'
        self.conn = db_module.get_db_connection()
        db_module.create_tables()

        # Sample data
        self.job1_details = {'title': 'Software Dev', 'company': 'FollowUp Inc.', 'location': 'Remote', 'summary': 'Dev job', 'url': 'http://example.com/job1_followup'}
        self.job2_details = {'title': 'Data Analyst', 'company': 'Analytics Co.', 'location': 'Remote', 'summary': 'Data job', 'url': 'http://example.com/job2_nofollowup'}
        self.job3_details = {'title': 'Project Manager', 'company': 'Org LLC', 'location': 'NY', 'summary': 'PM job', 'url': 'http://example.com/job3_past_response'}

        self.job1_id = db_module.add_job_posting(self.job1_details)
        self.job2_id = db_module.add_job_posting(self.job2_details)
        self.job3_id = db_module.add_job_posting(self.job3_details)

        self.assertIsNotNone(self.job1_id, "Failed to add job1 for setup")
        self.assertIsNotNone(self.job2_id, "Failed to add job2 for setup")
        self.assertIsNotNone(self.job3_id, "Failed to add job3 for setup")

        # Add communication logs
        self.past_date_due = (datetime.date.today() - datetime.timedelta(days=3)).isoformat()
        self.future_date_not_due = (datetime.date.today() + datetime.timedelta(days=5)).isoformat()
        self.today_date_due = datetime.date.today().isoformat()

        # Log 1: Needs follow-up (past due date)
        self.log1_id = self._add_comm_log(self.job1_id, 'Initial Email', self.past_date_due, response_received=False)

        # Log 2: Does not need follow-up (future due date)
        self._add_comm_log(self.job2_id, 'Inquiry', self.future_date_not_due, response_received=False)

        # Log 3: Needs follow-up (today's due date) - associate with job1 as well
        self.log3_id = self._add_comm_log(self.job1_id, 'Second Email', self.today_date_due, response_received=False, contact_name="John Doe")

        # Log 4: Past due date but response_received is True
        self._add_comm_log(self.job3_id, 'Application Sent', self.past_date_due, response_received=True)


    def _add_comm_log(self, job_id, subject, follow_up_date_iso, response_received=False, contact_name=None):
        """Helper to add communication logs and contacts if needed."""
        contact_id = None
        if contact_name:
            try:
                # Add a contact (simplified, no full contact details needed for these tests)
                self.conn.execute("INSERT INTO contacts (name, email) VALUES (?, ?)", (contact_name, f"{contact_name.replace(' ', '').lower()}@example.com"))
                contact_id = self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            except sqlite3.IntegrityError: # Contact might already exist from a previous helper call
                contact_id = self.conn.execute("SELECT id FROM contacts WHERE name = ?", (contact_name,)).fetchone()[0]


        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO communication_log
                (job_posting_id, contact_id, type, subject, body, follow_up_date, response_received)
            VALUES (?, ?, 'Email', ?, 'Test body', ?, ?)
        """, (job_id, contact_id, subject, follow_up_date_iso, response_received))
        self.conn.commit()
        return cursor.lastrowid

    def tearDown(self):
        self.conn.close()
        db_module.DATABASE_NAME = ORIGINAL_DATABASE_NAME

    def test_check_pending_follow_ups(self):
        pending = check_pending_follow_ups(self.conn)
        self.assertEqual(len(pending), 2, "Should find two logs needing follow-up.")

        # Check that the correct logs are identified (IDs might vary based on insertion order)
        pending_log_ids = sorted([log['id'] for log in pending])
        expected_log_ids = sorted([self.log1_id, self.log3_id]) # These were set up to be due
        self.assertListEqual(pending_log_ids, expected_log_ids)

        # Verify details of one of the pending items
        for p_log in pending:
            if p_log['id'] == self.log1_id:
                self.assertEqual(p_log['job_title'], self.job1_details['title'])
                self.assertEqual(p_log['company_name'], self.job1_details['company'])
                self.assertEqual(p_log['follow_up_date'], self.past_date_due)
                self.assertIsNone(p_log['contact_name']) # No contact for log1
            if p_log['id'] == self.log3_id:
                self.assertEqual(p_log['job_title'], self.job1_details['title'])
                self.assertEqual(p_log['company_name'], self.job1_details['company'])
                self.assertEqual(p_log['follow_up_date'], self.today_date_due)
                self.assertEqual(p_log['contact_name'], "John Doe")


    def test_draft_follow_up_email_with_contact(self):
        draft = draft_follow_up_email(
            job_title="Software Engineer",
            company_name="TestCorp",
            contact_name="Jane Smith",
            previous_comm_subject="Application for SE"
        )
        self.assertIn("Dear Jane Smith,", draft['body'])
        self.assertEqual(draft['subject'], "Re: Application for SE")
        self.assertIn("Software Engineer", draft['body'])
        self.assertIn("TestCorp", draft['body'])

    def test_draft_follow_up_email_no_contact_no_prev_subject(self):
        draft = draft_follow_up_email(
            job_title="Product Manager",
            company_name="Innovate Solutions"
        )
        self.assertIn("Dear Hiring Team,", draft['body'])
        self.assertEqual(draft['subject'], "Following Up: Application for Product Manager at Innovate Solutions")
        self.assertIn("Product Manager", draft['body'])
        self.assertIn("Innovate Solutions", draft['body'])

    def test_display_application_dashboard(self):
        # Update status for one job to test grouping
        db_module.update_job_posting_status(self.job1_id, "Applied")
        # job2_id and job3_id remain 'New' by default

        dashboard_str = display_application_dashboard(self.conn)

        self.assertIn("--- Application Status Dashboard ---", dashboard_str)
        self.assertIn("Applied: 1", dashboard_str) # From job1_id
        self.assertIn("New: 2", dashboard_str)     # From job2_id and job3_id

        self.assertIn("--- Recently Added Jobs ---", dashboard_str)
        # Check if job titles from setup appear (order might vary based on insertion time if not controlled)
        self.assertIn(self.job1_details['title'], dashboard_str)
        self.assertIn(self.job2_details['title'], dashboard_str)
        self.assertIn(self.job3_details['title'], dashboard_str)
        self.assertIn(self.job1_details['company'], dashboard_str)

    def test_check_pending_follow_ups_error_handling(self):
        # Close the connection to simulate a database error
        self.conn.close()
        with patch('builtins.print') as mock_print:
            pending = check_pending_follow_ups(self.conn) # Should trigger the except block
            self.assertEqual(len(pending), 0)
            mock_print.assert_any_call("Error checking pending follow-ups: Cannot operate on a closed database.")

    def test_display_application_dashboard_error_handling(self):
        # Close the connection to simulate a database error
        self.conn.close()
        with patch('builtins.print') as mock_print: # automation.py's display_application_dashboard doesn't print errors, it appends to output
            dashboard_str = display_application_dashboard(self.conn)
            self.assertIn("Error generating dashboard: Cannot operate on a closed database.", dashboard_str)


if __name__ == '__main__':
    unittest.main()
