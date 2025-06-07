import datetime
from string import Template # For simple template substitution
# import database # Assuming database.py is in the same directory or PYTHONPATH

# --- Resume and Cover Letter Templating ---

def generate_resume_template(job_details, user_profile):
    """
    Generates a basic resume outline based on job details and user profile.
    This is a very simplified version. Real-world usage would involve more sophisticated
    templating engines (e.g., Jinja2) and more structured user profile data.

    Args:
        job_details (dict): A dictionary containing job title, company, description, required skills.
                            (e.g., {'title': 'Software Engineer', 'company': 'Acme Corp',
                                    'description': 'Develop amazing software...', 'skills': ['Python', 'Django']})
        user_profile (dict): A dictionary containing user's name, contact, experience, skills.
                             (e.g., {'name': 'John Doe', 'email': 'john.doe@email.com',
                                     'experience': [{'title': 'Dev', 'company': 'Old Corp', 'duration': '2 years'}],
                                     'skills': ['Python', 'Java', 'SQL']})
    Returns:
        str: A string representing a tailored resume draft.
    """

    resume_str = f"""
# {user_profile.get('name', 'Your Name')}
{user_profile.get('email', 'your.email@example.com')} | {user_profile.get('phone', 'Your Phone')} | {user_profile.get('linkedin', 'Your LinkedIn')}

## Objective
To secure a challenging position as a {job_details.get('title', '[Job Title]')} at {job_details.get('company', '[Company Name]')} where I can leverage my skills in {', '.join(job_details.get('skills', ['[relevant skills]']))} to contribute to the company's success.

## Skills
* Programming Languages: {', '.join(skill for skill in user_profile.get('skills', []) if skill in job_details.get('skills', []))} (Prioritized based on job)
* Other Relevant Skills: [Add other skills from your profile that are relevant]
* Tools: [Your tools, e.g., Git, Docker, JIRA]

## Experience
"""
    for exp in user_profile.get('experience', []):
        resume_str += f"""
### {exp.get('title', '[Your Title]')} | {exp.get('company', '[Company Name]')} | {exp.get('duration', '[Dates]')}
* [Responsibility or achievement relevant to {job_details.get('title', 'the job')}]
* [Another responsibility or achievement]
"""

    resume_str += f"""
## Projects
* [Project Name 1]: [Brief description, highlighting skills relevant to {', '.join(job_details.get('skills', []))}]
* [Project Name 2]: [Brief description]

## Education
* [Your Degree] | [University Name] | [Graduation Year]
"""
    return resume_str

def generate_cover_letter_template(job_details, user_profile, hiring_manager="Hiring Manager"):
    """
    Generates a basic cover letter based on job details and user profile.

    Args:
        job_details (dict): Job title, company, description.
        user_profile (dict): User's name.
        hiring_manager (str): Name of the hiring manager, if known.

    Returns:
        str: A string representing a tailored cover letter draft.
    """

    letter_template = Template(f"""
Dear {hiring_manager},

I am writing to express my enthusiastic interest in the {job_details.get('title', '[Job Title]')} position at {job_details.get('company', '[Company Name]')}, as advertised on [Platform where you saw the ad - e.g., LinkedIn, company website]. With my background in [Your Key Area, e.g., software development] and specific experience in [Mention 1-2 skills from job_details.get('skills', []) that you possess, e.g., Python and Django], I am confident I possess the qualifications to make a significant contribution to your team.

In my previous role at [Your Previous Company, if relevant], I was responsible for [Key Responsibility relevant to the job description, e.g., "developing and maintaining web applications using Python and Django, similar to what is required for this role."]. I am particularly drawn to {job_details.get('company', '[Company Name]')}'s work in [Mention something specific about the company or its projects that excites you, if known from your research].

I am eager to learn more about this opportunity and discuss how my skills and experience align with the needs of {job_details.get('company', '[Company Name]')}. Thank you for your time and consideration.

Sincerely,
{user_profile.get('name', 'Your Name')}
{user_profile.get('email', 'your.email@example.com')}
{user_profile.get('phone', 'Your Phone Number (Optional)')}
""")

    return letter_template.safe_substitute(
        job_title=job_details.get('title', '[Job Title]'),
        company_name=job_details.get('company', '[Company Name]'),
        user_name=user_profile.get('name', 'Your Name')
    )

# --- Communication Log (Basic Structure - DB interaction will be in database.py) ---

def log_communication(db_conn, job_posting_id, contact_id, comm_type, subject, body, follow_up_date=None):
    """
    Logs a communication event.
    (This function would ideally call a method in database.py to insert into communication_log table)

    Args:
        db_conn: Active database connection object.
        job_posting_id (int): ID of the job posting related to this communication.
        contact_id (int): ID of the contact (if any).
        comm_type (str): e.g., 'Email', 'Call', 'LinkedIn Message'.
        subject (str): Subject of the communication.
        body (text): Content of the communication.
        follow_up_date (str, optional): ISO format date for follow-up.

    Returns:
        int: ID of the logged communication, or None if failed.
    """
    cursor = db_conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO communication_log (job_posting_id, contact_id, communication_date, type, subject, body, follow_up_date)
            VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?)
        """, (job_posting_id, contact_id, comm_type, subject, body, follow_up_date))
        db_conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error logging communication: {e}")
        return None

# --- Main / Example Usage ---
if __name__ == '__main__':
    # Mock data for demonstration
    mock_job_details = {
        'title': 'Senior Python Developer',
        'company': 'Innovatech Ltd.',
        'description': 'Looking for an experienced Python developer to build scalable web applications. Must know Django and REST APIs.',
        'skills': ['Python', 'Django', 'REST APIs', 'PostgreSQL'],
        'url': 'http://innovatech.com/job/123'
    }
    mock_user_profile = {
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
        'skills': ['Python', 'Django', 'Flask', 'JavaScript', 'SQL', 'REST APIs']
    }

    print("--- Generating Resume Draft ---")
    resume_draft = generate_resume_template(mock_job_details, mock_user_profile)
    print(resume_draft)

    print("\n--- Generating Cover Letter Draft ---")
    cover_letter_draft = generate_cover_letter_template(mock_job_details, mock_user_profile, hiring_manager="Mr. Bob Smith")
    print(cover_letter_draft)

    # Example of logging communication (requires database setup and connection)
    # print("\n--- Logging Communication (Example) ---")
    # import src.database as db # Make sure to import your database module
    # conn = db.get_db_connection()
    # db.create_tables() # Ensure tables exist

    # # First, add the job posting to get an ID (if not already present)
    # job_id = db.add_job_posting(mock_job_details)
    # if not job_id:
    #     # If it failed, try to get it by URL assuming it was added before
    #     existing_job = db.get_job_posting_by_url(mock_job_details['url'])
    #     if existing_job:
    #         job_id = existing_job['id']

    # if job_id:
    #     print(f"Using Job ID: {job_id} for communication log.")
    #     log_id = log_communication(
    #         db_conn=conn,
    #         job_posting_id=job_id, # Replace with actual job_posting_id from DB
    #         contact_id=None, # Replace with actual contact_id from DB if available
    #         comm_type='Initial Application Email',
    #         subject=f"Application for {mock_job_details['title']}",
    #         body="Dear Mr. Smith, Please find my application attached for the Senior Python Developer role...",
    #         follow_up_date=(datetime.date.today() + datetime.timedelta(days=7)).isoformat()
    #     )
    #     if log_id:
    #         print(f"Communication logged with ID: {log_id}")
    #     else:
    #         print("Failed to log communication.")

    #     # Example: Retrieving logs (would be a function in database.py)
    #     cursor = conn.cursor()
    #     cursor.execute("SELECT * FROM communication_log WHERE job_posting_id = ?", (job_id,))
    #     logs = cursor.fetchall()
    #     print(f"\nFound {len(logs)} log(s) for job ID {job_id}:")
    #     for log_entry in logs:
    #         print(dict(log_entry))

    # else:
    #     print("Could not obtain a valid job_id to log communication against.")

    # if conn:
    #    conn.close()
