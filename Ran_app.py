from flask import Flask, session, render_template, jsonify, redirect, request
import psycopg2
import user
import traceback

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
active_user = user.User()
app.secret_key = 'big secrete'


# from dbconfig import db_config # Database connection parameters
db_config = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '2024!Detroit',
    'host': 'localhost'
}



#------------------------------------------------------------------------------------------

try:
    # Connect to the database
    conn = psycopg2.connect(**db_config)

    # Create a cursor object
    cur = conn.cursor()

    # Execute a test query
    cur.execute('SELECT version();')

    # Fetch the result
    db_version = cur.fetchone()

    # Print the PostgreSQL version
    print("PostgreSQL version:", db_version)

    # Close cursor and connection
    cur.close()
    conn.close()

    print("Database connection successful!")

except Exception as e:
    # Print error message if connection fails
    print("Error:", e)
#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------
# Apr13 Copy of Alex's Branch app.py
#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------
@app.route('/')
def index():
    if active_user.is_valid():
        return redirect('/login_redirect')
    return redirect('/login')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    active_user.invalidate()
    return redirect('/')

@app.route('/login2/<loginid>')
def login2(loginid):
    if active_user.login(loginid):
        session['user_id'] = active_user.id  # Assign the user ID to the session
        return redirect('/login_redirect')
    else:
        return redirect("/error")




@app.route('/login_redirect')
def login_redirect():
    return redirect(active_user.get_home())

@app.route('/error')
def error():
    # return render_template('error.html')
    return render_template('course_registration.html')

@app.route('/university_applications')
def university_applications():
    return render_template('university_applications.html')

@app.route('/course_registration')
def course_registration():
    return render_template('course_registration.html')

@app.route('/graduation_application')
def graduation_application():
    return render_template('graduation_application.html')

@app.route('/alumni_page')
def alumni_page():
    return render_template('alumni_page.html')

@app.route('/faculty_page')
def faculty_page():
    return render_template('faculty_page.html')

@app.route('/applicant/home')
def applicant_home():
    if(active_user.isApplicant()):
        if not active_user.applicantInfoExists():
            active_user.get_applicant_info()
        if active_user.submittedApplication():
            return render_template('applicant_home.html', applicationSubmitted=1)
        else:
            return render_template('applicant_home.html', applicationSubmitted=0)
    else:
        return redirect('/error')

@app.route('/test_db')
def test_db():
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        cur.execute('SELECT version();')
        db_version = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"success": True, "PostgreSQL Version": db_version})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

#------------------------------------------------------------------------------------------
# Course Registration Process Begins - Apr 04 RD
#------------------------------------------------------------------------------------------


#Course Search------------------------------------------------------------------------------------------


@app.route('/submit_course_registration', methods=['POST'])
def submit_course_registration():
    try:
        # Access form data
        course_no = request.form['course_no']
        course_title = request.form['course_title']
        semester = request.form['semester']
        year = request.form['year']
        department = request.form['department']

        # Initialize the SQL query to fetch courses
        course_query = "SELECT * FROM starrs.\"COURSE\" WHERE 1=1"

        # Add conditions based on form inputs
        if course_no:
            course_query += f" AND \"COURSE_NO\" = '{course_no}'"
        if course_title:
            course_query += f" AND \"TITLE\" = '{course_title}'"
        if department != 'Any':
            course_query += f" AND \"DEPARTMENT\" = '{department}'"

        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # Execute the SQL query to fetch courses
        cur.execute(course_query)
        courses = cur.fetchall()


        course_info = []
        for course in courses:
            course_sections_query = f"""
                SELECT
                    s.*,
                    u."FIRST_NAME",
                    u."LAST_NAME",
                    EXISTS (
                        SELECT 1
                        FROM starrs."ATTENDS_SECTION" a
                        WHERE
                            a."STUDENT_ID" = %s
                            AND a."SECTION_NO" = s."SECTION_NO"
                            AND a."SEMESTER" = s."SEMESTER"
                            AND a."YEAR" = s."YEAR"
                    ) AS "enrolled"
                FROM
                    starrs."SECTION" s
                INNER JOIN
                    starrs."USER" u ON s."INSTRUCTOR_ID" = u."USER_ID"
                WHERE
                    s."COURSE_NO" = '{course[0]}'"""

            # Add conditions for semester and year
            if semester != 'Any':
                course_sections_query += f" AND s.\"SEMESTER\" = '{semester}'"
                if year != 'Any':
                    course_sections_query += f" AND s.\"YEAR\" = '{year}'"
            else:
                if year != 'Any':
                    course_sections_query += f" AND s.\"YEAR\" = '{year}'"

            cur.execute(course_sections_query, (session.get('user_id'),))  # Pass user_id as parameter
            sections = cur.fetchall()
            course_info.append((course, sections))

        # Render the template with the course information
        return render_template('course_results.html', course_info=course_info)
    except psycopg2.Error as e:
        # Print the error message and traceback for debugging
        print("Error executing SQL query:", e)
        traceback.print_exc()
        # Optionally, render an error page with a user-friendly message
        return render_template('error.html', message="An error occurred while fetching course information.")


#Course Enrollment------------------------------------------------------------------------------------------


@app.route('/enroll_course', methods=['POST'])
def enroll_course():
    try:
        # Access form data from the request object
        student_id = session.get('user_id')  # Get student ID from session
        course_no = request.form['course_no']
        section_no = request.form['section_no']
        semester = request.form['semester']
        year = request.form['year']
        instructor_id = request.form['instructor_id']  # Added instructor ID

        # Print the enrolled course information
        print("Enrolled Course Information:")
        print("Student ID:", student_id)
        print("Course Number:", course_no)
        print("Section Number:", section_no)
        print("Semester:", semester)
        print("Year:", year)

        # Establish connection to the database
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # Insert enrollment data into the ATTENDS_SECTION table
        cur.execute("""
            INSERT INTO starrs."ATTENDS_SECTION" (
                "STUDENT_ID", "COURSE_NO", "SECTION_NO", "SEMESTER", "YEAR", "Grade", "Registration Status")
            VALUES (%s, %s, %s, %s, %s, NULL, 'Registered')
        """, (student_id, course_no, section_no, semester, year))

        # Commit the transaction
        conn.commit()

        # Close cursor and connection
        cur.close()
        conn.close()

        # Return a success response
        return jsonify({'message': 'Enrollment successful'})

    except Exception as e:
        # Handle exceptions
        print("Error:", e)
        # Rollback the transaction in case of an error
        conn.rollback()  # Added rollback
        # Optionally, return an error response
        return jsonify({'error': 'Enrollment failed'}), 500




@app.route('/drop_course', methods=['POST'])
def drop_course():
    try:
        # Access form data
        course_no = request.form['course_no']
        section_no = request.form['section_no']
        semester = request.form['semester']
        year = request.form['year']
        instructor_id = request.form['instructor_id']

        # Check if the section is enrolled for the user ID in the ATTENDS_SECTION table
        user_id = session.get('user_id')
        if not user_id:
            return render_template('error.html', message="User ID not found in session.")

        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        cur.execute("""
            DELETE FROM starrs."ATTENDS_SECTION"
            WHERE "STUDENT_ID" = %s AND "SECTION_NO" = %s AND "SEMESTER" = %s AND "YEAR" = %s AND "INSTRUCTOR_ID" = %s
            RETURNING 1
            """,
                    (user_id, section_no, semester, year, instructor_id))
        deleted = cur.fetchone()

        # If the record is deleted successfully, return a success message
        if deleted:
            return jsonify({'message': 'Course dropped successfully'})

        # If the record does not exist, return an error message
        else:
            return jsonify({'error': 'Course not found or not enrolled'}), 404

    except Exception as e:
        # Handle exceptions
        print("Error:", e)
        # Optionally, return an error response
        return jsonify({'error': 'Failed to drop course'}), 500

    finally:
        # Close database connection
        cur.close()
        conn.close()



#Registration Record--------------------------------------------------------------------------------------------------------------
#

@app.route('/search_attendance_records', methods=['POST'])
def search_attendance_records():
    try:
        # Access user ID from session
        user_id = session.get('user_id')
        if not user_id:
            return render_template('error.html', message="Unable to recognize ID.")

        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # Fetch user information from the database
        user_query = f"""
            SELECT "USER_ID", "FIRST_NAME", "MIDDLE_NAME", "LAST_NAME", "EMAIL", "STREET_ADDRESS", "CITY", "STATE", "COUNTRY", "ZIP_CODE", "CELL_PHONE","WORK_PHONE"     
            FROM starrs."USER"
            WHERE "USER_ID" = '{user_id}'
        """

        cur.execute(user_query)
        user_data = cur.fetchone()

        # Fetch records from AttendSection table for the user ID
        attend_section_query = f"""
            SELECT a.*, c."COURSE_NO", c."TITLE", c."CREDITS", c."DEPARTMENT", s."SECTION_NO", s."SEMESTER", s."YEAR"
            FROM starrs."ATTENDS_SECTION" a
            INNER JOIN starrs."SECTION" s ON a."SECTION_NO" = s."SECTION_NO"
            INNER JOIN starrs."COURSE" c ON s."COURSE_NO" = c."COURSE_NO"
            WHERE a."STUDENT_ID" = '{user_id}'
        """

        cur.execute(attend_section_query)
        records = cur.fetchall()

        # Render the template with the fetched records and user information
        return render_template('registration_record.html', records=records, user=user_data)

    except psycopg2.Error as e:
        # Handle database errors
        print("Error executing SQL query:", e)
        traceback.print_exc()
        return render_template('error.html', message="An error occurred while fetching records.")

    finally:
        # Close database connection if applicable
        pass  # Adjust this according to your database handling

#GS/Faculty Grading--------------------------------------------------------------------------------------------------------------


@app.route('/student_academic_management')
def student_academic_management():
    return render_template('student_academic_management.html')

@app.route('/submit_student_academic', methods=['POST'])
def submit_student_academic():
    return render_template('student_academic_result.html')

# @app.route('/search_student_academic_records', methods=['POST'])
# def search_student_academic_records():
#     try:
#         # Access student ID and course number from the form data
#         student_id = request.form.get('student_id')
#         course_no = request.form.get('course_no')
#
#         if student_id and course_no:
#             conn = psycopg2.connect(**db_config)
#             cur = conn.cursor()
#
#             # Use parameterized query to prevent SQL injection
#             attend_section_query = """
#                 SELECT *
#                 FROM starrs."ATTENDS_SECTION"
#                 WHERE "STUDENT_ID" = %s AND "COURSE_NO" = %s
#             """
#
#             cur.execute(attend_section_query, (student_id, course_no))
#             records = cur.fetchall()
#
#             # Render the template with the fetched records
#             return render_template('student_academic_result.html', records=records)
#         else:
#             # If student ID or course number is not provided, display an error message
#             return render_template('student_academic_result.html', message="Please enter both student ID and course number.")
#
#     except psycopg2.Error as e:
#         # Handle database errors
#         print("Error executing SQL query:", e)
#         traceback.print_exc()
#         return render_template('error.html', message="An error occurred while fetching records.")
#     finally:
#         # Close cursor and connection
#         if cur:
#             cur.close()
#         if conn:
#             conn.close()
#

@app.route('/search_student_academic_records', methods=['POST'])
def search_student_academic_records():
    try:
        # Access student ID and course number from the form data
        student_id = request.form.get('student_id')
        course_no = request.form.get('course_no')

        if student_id and course_no:
            conn = psycopg2.connect(**db_config)
            cur = conn.cursor()

            # Use parameterized query to prevent SQL injection
            attend_section_query = """
                SELECT a.*, c."COURSE_NO", c."TITLE", c."CREDITS", c."DEPARTMENT", s."SECTION_NO", s."SEMESTER", s."YEAR",
                       u."FIRST_NAME" AS instructor_first_name, u."LAST_NAME" AS instructor_last_name
                FROM starrs."ATTENDS_SECTION" a
                INNER JOIN starrs."SECTION" s ON a."SECTION_NO" = s."SECTION_NO"
                INNER JOIN starrs."COURSE" c ON s."COURSE_NO" = c."COURSE_NO"
                INNER JOIN starrs."USER" u ON s."INSTRUCTOR_ID" = u."USER_ID"
                WHERE a."STUDENT_ID" = %s AND a."COURSE_NO" = %s
            """

            cur.execute(attend_section_query, (student_id, course_no))
            records = cur.fetchall()

            # Render the template with the fetched records
            return render_template('student_academic_result.html', records=records)
        else:
            # If student ID or course number is not provided, display an error message
            return render_template('student_academic_result.html', message="Please enter both student ID and course number.")

    except psycopg2.Error as e:
        # Handle database errors
        print("Error executing SQL query:", e)
        traceback.print_exc()
        return render_template('error.html', message="An error occurred while fetching records.")
    finally:
        # Close cursor and connection
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/update_record', methods=['POST'])
def update_record():
    try:
        # Establish connection to the database
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # Iterate over form data to update records
        for key, value in request.form.items():
            if key.startswith('grade_'):
                # Extract student_id, course_no, and section_no from the form field name
                prefix_length = len('grade_')
                identifiers = key[prefix_length:].split('_')
                if len(identifiers) == 3:
                    student_id, course_no, section_no = identifiers
                else:
                    continue

                # Get the registration status corresponding to the grade
                status_key = f"status_{student_id}_{course_no}_{section_no}"
                registration_status = request.form.get(status_key)

                # Ensure NULL values for grade if not "completed" or "dropped" status
                if registration_status not in ["Completed", "Dropped"]:
                    value = None

                print("Updating record with the following details:")
                print("Student ID:", student_id)
                print("Course Number:", course_no)
                print("Section Number:", section_no)
                print("Grade:", value)
                print("Registration Status:", registration_status)

                # Update the record in the database
                cur.execute("""
                    UPDATE starrs."ATTENDS_SECTION"
                    SET "Grade" = %s, "Registration Status" = %s
                    WHERE "STUDENT_ID" = %s AND "COURSE_NO" = %s AND "SECTION_NO" = %s
                """, (value, registration_status, student_id, course_no, section_no))

                print("Record updated successfully.")

        # Commit the transaction
        conn.commit()

        # Close cursor and connection
        cur.close()
        conn.close()

        # Return a success response
        return jsonify({'message': 'Records updated successfully'})

    except Exception as e:
        # Handle exceptions
        print("Error:", e)
        # Rollback the transaction in case of an error
        conn.rollback()
        # Optionally, return an error response
        return jsonify({'error': 'Failed to update records'}), 500

#--------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)

#--------------------------------------------------------------------------------------------------------------
