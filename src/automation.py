import datetime
# import src.database as db # Assuming database.py for direct DB access
# from src.crm import generate_cover_letter_template # For reusing parts or similar logic

def check_pending_follow_ups(db_conn):
    """
    Checks for communications that are due for a follow-up.

    Args:
        db_conn: Active database connection object.

    Returns:
        list: A list of communication log entries (as dicts) that need follow-up.
    """
    pending = []
    today_date = datetime.date.today()
    cursor = db_conn.cursor()

    try:
        # Select communications where follow_up_date is today or in the past,
        # and response_received is False (or not explicitly marked as True).
        # Assumes 'follow_up_date' is stored as TEXT in ISO format (YYYY-MM-DD)
        # or a comparable TIMESTAMP format that allows direct string comparison.
        cursor.execute("""
            SELECT cl.*, jp.title as job_title, jp.company_name as company_name, c.name as contact_name
            FROM communication_log cl
            JOIN job_postings jp ON cl.job_posting_id = jp.id
            LEFT JOIN contacts c ON cl.contact_id = c.id
            WHERE cl.follow_up_date <= ?
            AND (cl.response_received IS FALSE OR cl.response_received = 0)
            ORDER BY cl.follow_up_date ASC
        """, (today_date.isoformat(),))

        follow_ups = cursor.fetchall()
        for item in follow_ups:
            pending.append(dict(item)) # Convert sqlite3.Row to dict
    except Exception as e:
        print(f"Error checking pending follow-ups: {e}")

    return pending

def draft_follow_up_email(job_title, company_name, contact_name=None, previous_comm_subject=None):
    """
    Generates a draft for a follow-up email.

    Args:
        job_title (str): The title of the job.
        company_name (str): The name of the company.
        contact_name (str, optional): The name of the contact person.
        previous_comm_subject (str, optional): Subject of the previous communication.

    Returns:
        dict: A dictionary containing the 'subject' and 'body' of the draft email.
    """

    salutation = f"Dear {contact_name}," if contact_name else "Dear Hiring Team,"

    subject_line = f"Following Up: Application for {job_title} at {company_name}"
    if previous_comm_subject:
        subject_line = f"Re: {previous_comm_subject}" # More likely for direct reply

    email_body = f"""
{salutation}

I hope this email finds you well.

I am writing to follow up on my application for the {job_title} position at {company_name}.
I submitted my application on [Date of original application - retrieve from DB or user input] and am very enthusiastic about the opportunity to contribute to your team.

[Optional: Briefly reiterate your key qualification or interest in the role/company.
e.g., "My experience in [Specific Skill] aligns well with the requirements you outlined, and I am particularly interested in [Company's Project/Value]."]

Could you please let me know if there is any additional information I can provide to assist in your decision-making process?
I am available for an interview at your earliest convenience.

Thank you for your time and consideration.

Best regards,

[Your Name]
[Your Contact Information]
"""
    return {"subject": subject_line, "body": email_body}

def display_application_dashboard(db_conn):
    """
    Provides a summary of application statuses.
    (This is a simplified console output. A real dashboard would be web-based.)

    Args:
        db_conn: Active database connection object.
    Returns:
        str: A string summary of the dashboard.
    """
    dashboard_output = "--- Application Status Dashboard ---\n"
    cursor = db_conn.cursor()

    try:
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM job_postings
            GROUP BY status
        """)
        statuses = cursor.fetchall()
        if statuses:
            for status_info in statuses:
                dashboard_output += f"{status_info['status']}: {status_info['count']}\n"
        else:
            dashboard_output += "No applications tracked yet.\n"

        # Add more info, like recent applications or upcoming follow-ups
        cursor.execute("SELECT title, company_name, date_scraped FROM job_postings ORDER BY date_scraped DESC LIMIT 5")
        recent_jobs = cursor.fetchall()
        dashboard_output += "\n--- Recently Added Jobs ---\n"
        if recent_jobs:
            for job in recent_jobs:
                dashboard_output += f"- {job['title']} at {job['company_name']} (Added: {job['date_scraped']})\n"
        else:
            dashboard_output += "No recent jobs.\n"

    except Exception as e:
        dashboard_output += f"Error generating dashboard: {e}\n"

    return dashboard_output

if __name__ == '__main__':
    # This main block requires a database connection and data to be meaningful.
    # It's primarily for illustration.

    # --- Setup (mocking database interactions for standalone run) ---
    # In a real scenario, you'd get a connection from your database module
    # For now, let's simulate an in-memory DB for table creation and example data.
    import sqlite3

    # Use :memory: for a temporary DB for this example run
    # conn = sqlite3.connect(':memory:')
    # For persistence, use the actual DB file:
    from src.database import DATABASE_NAME, create_tables, get_db_connection, add_job_posting
    # from src.crm import log_communication # For adding communication logs

    # Initialize DB and tables
    create_tables() # Ensures tables are created in job_app_crm.db
    conn = get_db_connection()

    print(f"Using database: {DATABASE_NAME}")

    # --- Example Data Population (Simplified) ---
    # Clear existing data for a clean run of this example (optional)
    # c = conn.cursor()
    # c.execute("DELETE FROM communication_log")
    # c.execute("DELETE FROM job_postings")
    # conn.commit()
    # c.close()

    # Add some job postings if they don't exist
    job1_url = "http://example.com/job1_followup"
    job1_id = add_job_posting({'title': 'Software Dev', 'company': 'FollowUp Inc.', 'location': 'Remote', 'summary': 'Dev job', 'url': job1_url})
    if not job1_id: # If already exists
        job1_data = conn.execute("SELECT id FROM job_postings WHERE url = ?", (job1_url,)).fetchone()
        if job1_data: job1_id = job1_data['id']

    job2_url = "http://example.com/job2_nofollowup"
    job2_id = add_job_posting({'title': 'Data Analyst', 'company': 'Analytics Co.', 'location': 'Remote', 'summary': 'Data job', 'url': job2_url})
    if not job2_id:
        job2_data = conn.execute("SELECT id FROM job_postings WHERE url = ?", (job2_url,)).fetchone()
        if job2_data: job2_id = job2_data['id']

    # Add communication logs
    if job1_id:
        # Log a communication that needs follow-up (follow_up_date in the past)
        past_follow_up_date = (datetime.date.today() - datetime.timedelta(days=3)).isoformat()
        # Using crm.log_communication would be cleaner if it's adapted to take a connection
        # For now, direct insert for simplicity of this example:
        try:
            conn.execute("""
                INSERT INTO communication_log (job_posting_id, type, subject, body, follow_up_date, response_received)
                VALUES (?, 'Email', 'Initial Application', 'Sent resume and cover letter.', ?, FALSE)
            """, (job1_id, past_follow_up_date))
            conn.commit()
            print(f"Added communication log for job ID {job1_id} needing follow-up.")
        except sqlite3.IntegrityError:
             print(f"Communication log for job ID {job1_id} might already exist.")


    if job2_id:
        # Log a communication that does NOT need follow-up (follow_up_date in the future)
        future_follow_up_date = (datetime.date.today() + datetime.timedelta(days=5)).isoformat()
        try:
            conn.execute("""
                INSERT INTO communication_log (job_posting_id, type, subject, body, follow_up_date, response_received)
                VALUES (?, 'Email', 'Inquiry', 'Asked a question.', ?, FALSE)
            """, (job2_id, future_follow_up_date))
            conn.commit()
            print(f"Added communication log for job ID {job2_id} with future follow-up.")
        except sqlite3.IntegrityError:
            print(f"Communication log for job ID {job2_id} might already exist.")

    # --- Test Automation Functions ---
    print("\n--- Checking for Pending Follow-ups ---")
    pending_tasks = check_pending_follow_ups(conn)
    if pending_tasks:
        print(f"Found {len(pending_tasks)} item(s) needing follow-up:")
        for task in pending_tasks:
            print(f"  - Job: {task['job_title']} at {task['company_name']} (Log ID: {task['id']}), Follow-up Date: {task['follow_up_date']}")

            # Draft a follow-up for the first pending task
            if 'drafted' not in task: # Simple flag to avoid re-drafting in this demo loop
                print("\n  --- Drafting Follow-up Email ---")
                draft = draft_follow_up_email(
                    job_title=task['job_title'],
                    company_name=task['company_name'],
                    contact_name=task.get('contact_name'), # Might be None
                    previous_comm_subject=task['subject']
                )
                print(f"  Subject: {draft['subject']}")
                print(f"  Body:\n{draft['body']}")
                task['drafted'] = True # Mark as drafted for this demo
    else:
        print("No pending follow-ups found.")

    print("\n--- Displaying Application Dashboard ---")
    dashboard_info = display_application_dashboard(conn)
    print(dashboard_info)

    if conn:
        conn.close()
