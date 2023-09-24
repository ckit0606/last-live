import re
import boto3
import os
from pymysql import connections
from flask import Flask, redirect, url_for, request, render_template, session

from datetime import datetime
 
app = Flask(__name__)

bucket = "chunkit-s3-bucket"
region = "us-east-1"

db_conn = connections.Connection(
    host='database-2.cjdu7tfbjxtq.us-east-1.rds.amazonaws.com',
    port=3306,
    user='aws_user',
    password='Bait3273',
    db='test'

)


@app.route("/profile/")
def profile():
    cursor = db_conn.cursor()
    cursor.execute('SELECT * FROM student WHERE StudentID = 1')
    data = cursor.fetchone()

    return render_template("profile.html",data=data)

@app.route("/edit", methods=['GET', 'POST'])
def edit():
    resume_url = ''
    report_url = ''

    if request.method == 'POST':
        studentName = request.form.get("studentName")
        gender = request.form.get("gender")
        programme = request.form.get("programme")
        state = request.form.get("state_select_programme")
        contact = request.form.get("contact")
        studyYear = request.form.get("studyYear")
        method = request.form.get("method")
        resume = request.files.get("resume")
        report = request.files.get("report")
        status = 'Pending'
        studentID = 1

        if resume:    
            pdf_file_name_in_s3 = "Id-" + str(1) + "_resume_pdf"
            s3 = boto3.resource('s3')
            s3.Bucket(bucket).put_object(Key=pdf_file_name_in_s3, Body=resume)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=bucket)
            s3_location = (bucket_location['LocationConstraint'])
            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location
            resume_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                bucket,
                pdf_file_name_in_s3)
            
        if report:    
            pdf_file_name_in_s3 = "Id-" + str(1) + "_report_pdf"
            s3 = boto3.resource('s3')
            s3.Bucket(bucket).put_object(Key=pdf_file_name_in_s3, Body=resume)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=bucket)
            s3_location = (bucket_location['LocationConstraint'])
            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location
            report_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                bucket,
                pdf_file_name_in_s3)

        cursor = db_conn.cursor()
        update_sql = 'UPDATE student SET StudentName = %s, StudentGender = %s, StudentProgramme = %s, StudentState = %s,StudentPhoneNumber = %s,StudentYear = %s,StudentMethod = %s,StudentResume = %s,StudentReport = %s WHERE StudentID = 1'
        cursor.execute(update_sql, (studentName,gender,programme,state,contact,studyYear,method,resume_url,report_url))
        db_conn.commit()
        cursor.close()

        return redirect(url_for("profile"))

    return render_template("edit.html")

@app.route("/layout/")
def layout():
    return render_template("layout.html")

@app.route("/jobList/")
def jobList():
    # Fetch student data from the database where StudentApplyStatus is 'Pending'
    cursor = db_conn.cursor()
    select_sql = "SELECT JobID, JobTitle, JobSalary FROM jobs WHERE JobStatus = 'Accepted'"
    cursor.execute(select_sql)
    jobData = cursor.fetchall()
    cursor.close()
    return render_template("jobList.html", jobData=jobData)

@app.route("/jobDetail", methods=['GET', 'POST'])
@app.route("/jobDetail/<jobID>", methods=['GET', 'POST'])
def jobDetail(jobID=None):
    jobID=jobID
    if request.method == 'POST':
    # Retrieve data from the form
        StudentID = 1
        ApplicationStatus = "Pending"

        # Insert data into the application table
        cursor = db_conn.cursor()
        insert_sql = "INSERT INTO application (StudentID,JobID,ApplicationStatus) VALUES (%s, %s, %s)"
        cursor.execute(insert_sql, (StudentID, jobID, ApplicationStatus))
        db_conn.commit()
        cursor.close()


    # Fetch student data from the database where StudentApplyStatus is 'Pending'
    cursor = db_conn.cursor()
    select_sql = "SELECT JobID, JobTitle, JobSalary FROM jobs WHERE JobID = "+jobID
    cursor.execute(select_sql)
    jobData = cursor.fetchone()
    cursor.close()
    return render_template("jobDetail.html",jobData=jobData)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)


    #---------------------------------------------CKIT---------------------------------------------------------

@app.route("/")
def page():
    return render_template("Login.html")

@app.route("/Login/")
@app.route("/Login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve data from the form
        loginUserName = request.form.get('LoginEmail')
        loginPassword = request.form.get('LoginPassword')

        # Check if the login credentials exist in the student table
        cursor = db_conn.cursor()
        select_sql = "SELECT * FROM student WHERE StudentEmail = %s AND StudentPassword = %s"
        cursor.execute(select_sql, (loginUserName, loginPassword))
        studentData = cursor.fetchone()
        cursor.close()

 #       if studentData:
            # If the login credentials match a student, redirect to the student page
#            return redirect(url_for('profile'))

        # If not a student, check admin table
        cursor = db_conn.cursor()
        select_sql = "SELECT * FROM admin WHERE AdminEmail = %s AND AdminPassword = %s"
        cursor.execute(select_sql, (loginUserName, loginPassword))
        adminData = cursor.fetchone()
        cursor.close()

        if adminData:
            # If the login credentials match an admin, redirect to the admin page
            return redirect(url_for('companyList'))

        # If not an admin, check company table
        cursor = db_conn.cursor()
        select_sql = "SELECT * FROM company WHERE CompanyEmail = %s AND CompanyPassword = %s"
        cursor.execute(select_sql, (loginUserName, loginPassword))
        companyData = cursor.fetchone()
        cursor.close()

        if companyData:
            # If the login credentials match a company, redirect to the company page
            return redirect(url_for('viewCompanyProfile'))

        # If not a company, check supervisor table
        cursor = db_conn.cursor()
        select_sql = "SELECT * FROM supervisor WHERE SupervisorEmail = %s AND SuperVisorPassword = %s"
        cursor.execute(select_sql, (loginUserName, loginPassword))
        supervisorData = cursor.fetchone()
        cursor.close()

        if supervisorData:
            # If the login credentials match a supervisor, redirect to the supervisor page
            return redirect(url_for('markingReport'))

    # If no match is found or if the request method is GET, render the login page
    return render_template("Login.html")

    #---------------------------------------------ky---------------------------------------------------------

@app.route("/postAJob/")
def postAJob():
    return render_template("postAJob.html")

@app.route("/postJob", methods=['GET', 'POST'])
def postJob():
    if request.method == 'POST':
        # Retrieve data from the form
        CompanyID = 1
        jobTitle = request.form.get('jobTitle')
        jobDescription = request.form.get('jobDescription')
        jobNature = request.form.get('jobNature')
        jobSalary = request.form.get('jobSalary')

        # Insert data into the job table
        cursor = db_conn.cursor()
        insert_sql = "INSERT INTO jobs (CompanyID, jobTitle, jobDescription, jobNature, jobSalary) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_sql, (CompanyID, jobTitle, jobDescription, jobNature, jobSalary))
        db_conn.commit()
        cursor.close()

        return render_template("postAJob.html")
    else:
        return render_template("postAJob.html")

@app.route("/editCompanyProfile/")
@app.route("/editCompanyProfile", methods=['GET', 'POST'])
def editCompanyProfile():
    if request.method == 'POST':
        # Retrieve data from the form
        CompanyName = request.form.get('CompanyName')
        CompanyDetails = request.form.get('CompanyDetails')
        CompanyField = request.form.get('CompanyField')
        CompanyLocation = request.form.get('CompanyLocation')
        CompanySize = request.form.get('CompanySize')

        # Update data into company table
        cursor = db_conn.cursor()
        update_sql = "UPDATE company SET CompanyName = %s, CompanyDetails = %s, CompanyField = %s, CompanyLocation = %s, CompanySize = %s"
        cursor.execute(update_sql, (CompanyName, CompanyDetails, CompanyField, CompanyLocation, CompanySize))
        db_conn.commit()
        cursor.close()
        
        return render_template("editCompanyProfile.html")

@app.route("/viewCompanyProfile/")    
@app.route("/viewCompanyProfile", methods=['GET', 'POST'])
def viewCompanyProfile():
        
        # Fetch student data from the database where StudentApplyStatus is 'Pending'
        cursor = db_conn.cursor()
        select_sql = "SELECT CompanyName, CompanyDetails, CompanyField, CompanyLocation, CompanySize FROM company WHERE CompanyID = 1"
        cursor.execute(select_sql)
        companyData = cursor.fetchone()
        cursor.close()

        return render_template("viewCompanyProfile.html", companyData=companyData)


@app.route("/appliedStudent/<type>", methods=['GET', 'POST'])
def appliedStudent(type=None):
    type=type
    if request.method == 'POST':
        # Retrieve data from the form
        action = request.form.get('action')  # 'accept' or 'reject'
        student_id = request.form.get('student_id')  # Add a hidden input field for student_id
       

        # Update the StudentApplyStatus based on the action
        cursor = db_conn.cursor()
        update_sql = "UPDATE application SET ApplicationStatus = %s WHERE ApplicationID = %s"
        cursor.execute(update_sql, (action, student_id))
        db_conn.commit()
        cursor.close()


    # Fetch student data from the database where StudentApplyStatus is 'Pending'
    cursor = db_conn.cursor()
    select_sql = "SELECT A.ApplicationID, S.StudentName, S.StudentProgramme, J.JobTitle, A.ApplicationStatus FROM application A JOIN student S ON A.StudentID = S.StudentID JOIN jobs J ON A.JobID = J.JobID WHERE A.ApplicationStatus = '"+type+"'"
    cursor.execute(select_sql)
    appliedData = cursor.fetchall()
    cursor.close()

    return render_template("appliedStudent.html", appliedData=appliedData)

#---------------------------------------------chok---------------------------------------------------------

@app.route("/markingReport/")
def markingReport():
    # Fetch student data from the database
    cursor = db_conn.cursor()
    cursor.execute("SELECT StudentID, StudentName, StudentProgramme, StudentYear, StudyMethod, ReportMark, ReportDate FROM student WHERE ReportLink IS NOT NULL")
    students = cursor.fetchall()
    cursor.close()

    # Pass the student data to the template
    return render_template("markingReport.html", students=students)

@app.route("/submit_mark", methods=["POST"])
def submitMark():
    if request.method == "POST":
        student_id = request.form.get("student_id")
        mark = request.form.get("markInput")  # Use "markInput" as the field name

        try:
            # Create a cursor for database operations
            cursor = db_conn.cursor()

            # Construct and execute the SQL query to update the mark in the 'report' table
            sql = "UPDATE student SET ReportMark = %s, ReportDate = %s WHERE StudentID = %s"
            current_date = datetime.now().strftime('%Y-%m-%d')  # Get the current date
            cursor.execute(sql, (mark, current_date, student_id))
            
            # Commit the changes to the database
            db_conn.commit()

            # Close the cursor
            cursor.close()

            # Redirect back to the marking report page after submission
            return redirect(url_for("markingReport"))

        except Exception as e:
            # Handle any database errors here
            db_conn.rollback()
            return "Error: " + str(e)




@app.route("/teacherResume/<type>", methods=['GET', 'POST'])
def teacherResume(type=None):
    if request.method == 'POST':
        # Retrieve data from the form
        action = request.form.get('action')  # 'accept' or 'reject'
        studentID = request.form.get('studentID')  # Add a hidden input field for studentID


        # Update the StudentApplyStatus based on the action
        cursor = db_conn.cursor()
        update_sql = "UPDATE Student SET ResumeStatus = %s WHERE studentID = %s"
        cursor.execute(update_sql, (action, studentID))
        db_conn.commit()
        cursor.close()


    # Fetch student data from the database where StudentApplyStatus is 'Pending'
    cursor = db_conn.cursor()
    select_sql = f"SELECT StudentID, ResumeLink, ResumeStatus, StudentName, StudentProgramme, StudentYear, StudyMethod FROM Student WHERE ResumeStatus = '{type}' AND ResumeLink IS NOT NULL"
    cursor.execute(select_sql)
    studentdata = cursor.fetchall()
    cursor.close()

    return render_template("teacherResume.html", studentdata=studentdata)

#---------------------------------------------zhunHui---------------------------------------------------------

@app.route("/companyList/")
def companyList():
    # Fetch data from the 'company' table based on companyId 'C001'
    cursor = db_conn.cursor()
    select_sql = "SELECT CompanyName, CompanyLocation FROM company"
    cursor.execute(select_sql)
    company_data = cursor.fetchall()
    cursor.close()
    
    return render_template("companyList.html", company_data=company_data)

@app.route("/jobRequest/<type>", methods=['GET', 'POST'])
def jobRequest(type=None):
    type=type
    if request.method == 'POST':
        # Retrieve data from the form
        action = request.form.get('action')  # 'accept' or 'reject'
        job_id = request.form.get('job_id')  # Add a hidden input field for job_id

        # Update the JobStatus based on the action
        cursor = db_conn.cursor()
        update_sql = "UPDATE jobs SET JobStatus = %s WHERE JobID = %s"
        cursor.execute(update_sql, (action, job_id))
        db_conn.commit()
        cursor.close()


    # Fetch student data from the database where StudentApplyStatus is 'Pending'
    cursor = db_conn.cursor()
    select_sql = "SELECT j.JobID, j.JobTitle, j.JobSalary, j.JobStatus, c.CompanyLocation FROM jobs AS j INNER JOIN company AS c ON j.CompanyID = c.CompanyID WHERE JobStatus = '"+type+"'"
    cursor.execute(select_sql)
    jobData = cursor.fetchall()
    cursor.close()

    return render_template("jobRequest.html", jobData = jobData)

@app.route("/jobRequestDetails", methods=['GET', 'POST'])
@app.route("/jobRequestDetails/<jobID>", methods=['GET', 'POST'])
def jobRequestDetails(jobID=None):
    jobID=jobID

    # Fetch student data from the database where StudentApplyStatus is 'Pending'
    cursor = db_conn.cursor()
    select_sql = "SELECT j.JobID, j.JobTitle, j.JobSalary, c.CompanyLocation FROM jobs AS j INNER JOIN company AS c ON j.CompanyID = c.CompanyID WHERE JobID = "+jobID
    cursor.execute(select_sql)
    jobData = cursor.fetchone()
    cursor.close()
    return render_template("jobRequestDetails.html",jobData=jobData)
