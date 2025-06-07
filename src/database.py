import sqlite3
import json

DATABASE_NAME = 'job_app_crm.db'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def create_tables():
    """Creates the necessary tables in the database if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Job Postings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_postings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company_name TEXT,
            location TEXT,
            summary TEXT,
            url TEXT UNIQUE, -- Ensure no duplicate job URLs
            date_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'New', -- e.g., New, Applied, Interviewing, Offer, Rejected
            application_date TIMESTAMP,
            notes TEXT,
            -- Foreign key to company (optional, can be denormalized or normalized)
            company_id INTEGER,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    ''')

    # Companies Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            industry TEXT,
            size TEXT,
            culture TEXT,
            github_url TEXT,
            key_projects TEXT,
            website TEXT
        )
    ''')

    # Technical Stack Table (Many-to-many relationship with job_postings)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tech_stack (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_posting_tech_stack (
            job_posting_id INTEGER,
            tech_stack_id INTEGER,
            PRIMARY KEY (job_posting_id, tech_stack_id),
            FOREIGN KEY (job_posting_id) REFERENCES job_postings(id) ON DELETE CASCADE,
            FOREIGN KEY (tech_stack_id) REFERENCES tech_stack(id) ON DELETE CASCADE
        )
    ''')

    # Contacts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            title TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            linkedin_profile TEXT,
            communication_style TEXT,
            company_id INTEGER, -- Link contact to a company
            job_posting_id INTEGER, -- Link contact to a specific job posting (e.g., hiring manager for that role)
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE SET NULL,
            FOREIGN KEY (job_posting_id) REFERENCES job_postings(id) ON DELETE SET NULL
        )
    ''')

    # Communications Log Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS communication_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_posting_id INTEGER,
            contact_id INTEGER,
            communication_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            type TEXT, -- e.g., Email, Call, LinkedIn Message
            subject TEXT,
            body TEXT,
            response_received BOOLEAN DEFAULT FALSE,
            follow_up_date TIMESTAMP,
            FOREIGN KEY (job_posting_id) REFERENCES job_postings(id) ON DELETE CASCADE,
            FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL
        )
    ''')

    conn.commit()
    conn.close()

def add_job_posting(job_data):
    """Adds a new job posting to the database.
    job_data should be a dictionary-like object (e.g., from scraper.JobPosting.to_dict()).
    Returns the ID of the newly inserted job posting or None if insertion failed.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO job_postings (title, company_name, location, summary, url)
            VALUES (?, ?, ?, ?, ?)
        ''', (job_data['title'], job_data['company'], job_data['location'], job_data['summary'], job_data['url']))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        print(f"Error adding job posting (URL might already exist or other integrity constraint): {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred when adding job posting: {e}")
        return None
    finally:
        conn.close()

def get_job_posting_by_url(url):
    """Retrieves a job posting by its URL."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_postings WHERE url = ?", (url,))
    job = cursor.fetchone()
    conn.close()
    return job

def get_all_job_postings(status_filter=None):
    """Retrieves all job postings, optionally filtered by status."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if status_filter:
        cursor.execute("SELECT * FROM job_postings WHERE status = ? ORDER BY date_scraped DESC", (status_filter,))
    else:
        cursor.execute("SELECT * FROM job_postings ORDER BY date_scraped DESC")
    jobs = cursor.fetchall()
    conn.close()
    return jobs

def update_job_posting_status(job_id, new_status, application_date=None):
    """Updates the status of a job posting."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if application_date:
            cursor.execute("UPDATE job_postings SET status = ?, application_date = ? WHERE id = ?", (new_status, application_date, job_id))
        else:
            cursor.execute("UPDATE job_postings SET status = ? WHERE id = ?", (new_status, job_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error updating job posting status: {e}")
        return False
    finally:
        conn.close()

# Placeholder for more functions (companies, tech_stack, contacts, communication_log)

if __name__ == '__main__':
    create_tables()
    print(f"Database '{DATABASE_NAME}' initialized with tables.")

    # Example usage:
    # Assuming you have run the scraper and have job objects
    # from scraper import scrape_indeed
    # example_jobs = scrape_indeed("python developer", "remote", 1)

    example_jobs = [
        {'title': 'Python Developer', 'company': 'Tech Solutions Inc.', 'location': 'Remote', 'summary': 'Developing Python applications.', 'url': 'http://example.com/pythondev'},
        {'title': 'Software Engineer', 'company': 'Innovate LLC', 'location': 'New York, NY', 'summary': 'Building cool software.', 'url': 'http://example.com/softeng'},
        {'title': 'Python Developer', 'company': 'Tech Solutions Inc.', 'location': 'Remote', 'summary': 'Developing Python applications.', 'url': 'http://example.com/pythondev2'} # Same job, different URL for testing
    ]

    if example_jobs:
        print(f"\nAttempting to add {len(example_jobs)} example jobs to the database...")
        for job_dict in example_jobs:
            job_id = add_job_posting(job_dict)
            if job_id:
                print(f"Added job: {job_dict['title']} with ID: {job_id}")
            else:
                print(f"Failed to add job or already exists: {job_dict['title']}")

        # Test duplicate URL insertion
        print("\nAttempting to add a duplicate job (should fail or be ignored)...")
        duplicate_job = {'title': 'Python Developer', 'company': 'Tech Solutions Inc.', 'location': 'Remote', 'summary': 'Developing Python applications.', 'url': 'http://example.com/pythondev'}
        add_job_posting(duplicate_job)


    print("\nFetching all job postings:")
    all_jobs = get_all_job_postings()
    if all_jobs:
        for job in all_jobs:
            print(dict(job)) # Print as dictionary
    else:
        print("No jobs found in the database.")

    if all_jobs:
        job_to_update_id = all_jobs[0]['id']
        print(f"\nUpdating status of job ID {job_to_update_id} to 'Applied'...")
        if update_job_posting_status(job_to_update_id, 'Applied', '2023-10-26 10:00:00'):
            print("Status updated successfully.")
            updated_job = get_job_posting_by_url(all_jobs[0]['url'])
            if updated_job:
                 print(f"Updated job details: {dict(updated_job)}")
        else:
            print("Failed to update status.")

    print("\nFetching 'Applied' jobs:")
    applied_jobs = get_all_job_postings(status_filter='Applied')
    if applied_jobs:
        for job in applied_jobs:
            print(dict(job))
    else:
        print("No 'Applied' jobs found.")
