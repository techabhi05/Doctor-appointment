from flask import Flask,render_template,request,redirect,url_for,session
from datetime import datetime,timedelta
from urllib.parse import urlparse,unquote
import mysql.connector
import bcrypt
import os

app = Flask(__name__)
app.secret_key = "clinic_secret_key"

db_url = os.getenv("MYSQL_PUBLIC_URL")

url = urlparse(db_url)

db = mysql.connector.connect(
    host=url.hostname,
    port=url.port,
    user=unquote(url.username),
    password=unquote(url.password),
    database=url.path.lstrip("/")
)

# Home route
@app.route("/")
def home():
    return render_template("index.html")


# Doctor Login Page
@app.route("/doctor", methods=["GET", "POST"])
def doctor():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        cursor = db.cursor(dictionary=True)

        sql = "SELECT * FROM doctors WHERE email = %s"
        cursor.execute(sql, (email,))

        doctor = cursor.fetchone()

        if doctor:

            if bcrypt.checkpw(
                password.encode("utf-8"),
                doctor["password"].encode("utf-8")
            ):

                session["doctor_id"] = doctor["doctor_id"]

                return redirect(url_for("doctor_dashboard"))

            else:
                return "Wrong password"

        else:
            return redirect(url_for("doctor_register"))

    return render_template("doctor_login.html")


# Doctor Register
@app.route("/doctor/register", methods=["GET", "POST"])
def doctor_register():

    if request.method == "POST":

        name = request.form["name"]
        specialization = request.form["specialization"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        cursor = db.cursor()

        sql = """
        INSERT INTO doctors
        (name, specialization, email, password)
        VALUES (%s, %s, %s, %s)
        """

        values = (
            name,
            specialization,
            email,
            hashed_password
        )

        cursor.execute(sql, values)
        db.commit()

        return "Doctor Registered Successfully!"

    return render_template("doctor_registration.html")

# Doctor Dashboard
@app.route("/doctor/dashboard")
def doctor_dashboard():

    if "doctor_id" not in session:
        return redirect(url_for("doctor"))

    cursor = db.cursor(dictionary=True)

    sql = "SELECT * FROM doctors WHERE doctor_id = %s"
    cursor.execute(sql, (session["doctor_id"],))

    doctor = cursor.fetchone()

    return render_template(
        "doctor_dashboard.html",
        doctor=doctor
    )

# Doctor Availability
@app.route("/doctor/my-availability")
def my_availability():

    if "doctor_id" not in session:
        return redirect(url_for("doctor"))

    cursor = db.cursor(dictionary=True)

    sql = """
    SELECT *
    FROM doctor_availability
    WHERE doctor_id = %s
    ORDER BY available_date, start_time
    """

    cursor.execute(sql, (session["doctor_id"],))

    availability = cursor.fetchall()
    print(availability)
    print(session.get("doctor_id"))

    return render_template(
        "my_availability.html",
        availability=availability
    )

# Adding Doctor Avaliability
@app.route("/doctor/add-availability", methods=["GET", "POST"])
def add_availability():

    if "doctor_id" not in session:
        return redirect(url_for("doctor"))

    if request.method == "POST":

        available_date = request.form["available_date"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]

        cursor = db.cursor()

        sql = """
        INSERT INTO doctor_availability
        (doctor_id, available_date, start_time, end_time)
        VALUES (%s, %s, %s, %s)
        """

        values = (
            session["doctor_id"],
            available_date,
            start_time,
            end_time
        )

        cursor.execute(sql, values)
        db.commit()

        return redirect(url_for("my_availability"))

    return render_template("add_availability.html")

# Cancelling the doctor availability
@app.route("/doctor/cancel_availability/<int:availability_id>",methods=["POST"])
def cancel_availability(availability_id):
        cursor = db.cursor()
    
        sql = """
        DELETE FROM doctor_availability
        WHERE availability_id = %s
        """
    
        cursor.execute(sql,(availability_id,))
        db.commit()
    
        return redirect(url_for("my_availability"))

# Doctor viewing his client's appointments
@app.route("/doctor/view_appointments")
def view_appointments():

    if "doctor_id" not in session:
        return redirect(url_for("doctor"))

    cursor = db.cursor(dictionary=True)

    sql = """
    SELECT
        appointments.appointment_id,
        patients.name AS patient_name,
        appointments.appointment_date,
        appointments.start_time,
        appointments.end_time,
        appointments.status
    FROM appointments
    JOIN patients
        ON appointments.patient_id = patients.patient_id
    WHERE appointments.doctor_id = %s
    ORDER BY appointments.appointment_date,
             appointments.start_time
    """

    cursor.execute(sql, (session["doctor_id"],))

    appointments = cursor.fetchall()

    return render_template(
        "view_appointments.html",
        appointments=appointments
    )



# Doctor marking the appointment as completed
@app.route("/doctor/complete_appointment/<int:appointment_id>", methods=["POST"])
def complete_appointment(appointment_id):

    if "doctor_id" not in session:
        return redirect(url_for("doctor"))

    cursor = db.cursor()

    sql = """
    UPDATE appointments
    SET status = 'Completed'
    WHERE appointment_id = %s
    AND doctor_id = %s
    """

    values = (
        appointment_id,
        session["doctor_id"]
    )

    cursor.execute(sql, values)
    db.commit()

    return redirect(url_for("view_appointments"))


# Patient Home
@app.route("/patient", methods=["GET", "POST"])
def patient():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        cursor = db.cursor(dictionary=True)

        sql = "SELECT * FROM patients WHERE email = %s"

        cursor.execute(sql, (email,))

        patient = cursor.fetchone()

        print(patient)
        print(patient.keys() if patient else "No patient")

        if patient:
             if bcrypt.checkpw(password.encode("utf-8"),patient["Password"].encode("utf-8")):
                  session["patient_id"] = patient["patient_id"]
                  return redirect(url_for("patient_dashboard"))
             else:
                  return render_template(
                    "wrong_password.html",
                    message="Thapu thapuu thapuu",message_type="wrong_password",
                    url="/patient"
                )

    return render_template("patient_login.html")

# Patient forgot password
@app.route("/patient/forgot_password_p", methods=["GET", "POST"])
def forgot_password_p():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]

        cursor = db.cursor(dictionary=True)

        sql = """
            SELECT * FROM patients
            WHERE name = %s AND email = %s
        """

        cursor.execute(sql, (name, email))

        patient = cursor.fetchone()

        if patient:

            return render_template(
                "reset_password.html",
                patient_id = patient["patient_id"]
            )

        else:

            return render_template(
                "forgot_password.html",
                message="Name and email do not match."
            )

    return render_template("forgot_password.html")

# Resetting the patient password
@app.route("/patient/reset_password/<int:patient_id>", methods=["POST"])
def reset_password(patient_id):

    password = request.form["password"]
    confirm_password = request.form["confirm_password"]

    if password != confirm_password:

        return render_template(
            "reset_password.html",
            patient_id=patient_id,
            message="Passwords do not match."
        )

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    cursor = db.cursor()

    sql = """
        UPDATE patients
        SET password = %s
        WHERE patient_id = %s
    """

    cursor.execute(
        sql,
        (hashed_password, patient_id)
    )

    db.commit()

    return render_template(
        "wrong_password1.html",
        message="Password changed successfully",
        url="/patient"
    )

# Patient Registering 
@app.route("/patient/register", methods = ["GET","POST"])
def patient_registers():
        if request.method == "POST":
            name = request.form["name"]
            email = request.form["email"]
            password = request.form["password"]
            hashed_password=bcrypt.hashpw(password.encode("utf-8"),bcrypt.gensalt())

            cursor = db.cursor()

            sql = """
                INSERT INTO PATIENTS (NAME,EMAIL,PASSWORD) 
                VALUES(%s,%s,%s)    """

            values = (name,email,hashed_password)

            cursor.execute(sql,values)
            db.commit()

            return "Patients register successfully"

        return render_template("patient_register.html") 

# Patient Dashboard
@app.route("/patient/dashboard")
def patient_dashboard():
     print(session.get("patient_id"))
     return render_template("patient_dashboard.html")

# Patient viewing the doctors
@app.route("/doctors")
def view_doctors():

    cursor = db.cursor(dictionary=True)

    sql = "SELECT * FROM doctors"

    cursor.execute(sql)

    doctors = cursor.fetchall()

    return render_template(
        "doctors.html",
        doctors=doctors
    )


# Patient booking the appointment
@app.route("/book/<int:doctor_id>",methods = ["GET","POST"])
def book_appointment(doctor_id):

    if request.method == "POST":
         patient_id = session["patient_id"]
         availability_id = request.form["availability_id"]
         start_time = request.form["start_time"]

         cursor = db.cursor(dictionary=True)

         sql = """
             SELECT * FROM doctor_availability
             WHERE availability_id = %s
             """

         cursor.execute(sql,(availability_id,))

         slot = cursor.fetchone()

         appointment_date = slot["available_date"]

         availability_start=slot["start_time"]
         availability_end=slot["end_time"]
         availability_start = (datetime.min + availability_start).time()
         availability_end = (datetime.min + availability_end).time()

         start_datetime = datetime.strptime(start_time,"%H:%M")
         end_datetime = start_datetime + timedelta(minutes=30)

         appointment_start=start_datetime.time()
         appointment_end=end_datetime.time()

         if appointment_start < availability_start or appointment_end > availability_end:
                  return render_template(
                              "time_slot_booked.html",
                              message="Doctor is not available",message_type="doctor_unavailable",
                              url=f"/book/{doctor_id}"
                  )
         sql="""
                select start_time,end_time
                from appointments
                where doctor_id = %s
                and appointment_date = %s"""
         
         cursor.execute(sql,(doctor_id,appointment_date))
         book_appointments = cursor.fetchall()

         for booked in book_appointments:
             booked_start= (datetime.min+booked["start_time"]).time()
             booked_end= (datetime.min+booked["end_time"]).time()
             if appointment_start<booked_end and appointment_end>booked_start:
                  return render_template(
                              "time_slot_booked.html",
                              message="Time slot is already booked",message_type="time_slot",
                              url=f"/book/{doctor_id}"
                  )
             


         end_time = end_datetime.time()

         sql = """
            INSERT INTO appointments
            (patient_id, doctor_id, appointment_date, start_time, end_time)
            VALUES (%s, %s, %s, %s, %s)
            """

         values = (
                patient_id,
                doctor_id,
                appointment_date,
                start_time,
                end_time
            )

         cursor.execute(sql, values)

         db.commit()

         return render_template(
            "wrong_password.html",
            message="Appointment booked successfully",message_type="appointment_booked",
            url="/my_appointments"
            )


    cursor = db.cursor(dictionary=True)

    sql = "SELECT * FROM doctors WHERE doctor_id = %s"
    cursor.execute(sql, (doctor_id,))
    doctor = cursor.fetchone()

    sql = """
    SELECT * FROM doctor_availability
    WHERE doctor_id = %s
    """
    cursor.execute(sql, (doctor_id,))
    availability = cursor.fetchall()

    return render_template(
        "book_appointment.html",
        doctor=doctor,
        availability=availability
    )



# Patient viewing his appointments
@app.route("/my_appointments")
def my_appointments():

    patient_id = session["patient_id"]

    cursor = db.cursor(dictionary=True)

    sql = """
    SELECT
        appointments.appointment_id,
        appointments.appointment_date,
        appointments.start_time,
        appointments.end_time,
        appointments.status,
        doctors.name AS doctor_name,
        doctors.specialization
    FROM appointments
    JOIN doctors
    ON appointments.doctor_id = doctors.doctor_id
    WHERE appointments.patient_id = %s
    """

    cursor.execute(sql, (patient_id,))

    appointments = cursor.fetchall()

    return render_template(
        "my_appointments.html",
        appointments=appointments
    )

# Patient cancelling his appointment
@app.route("/cancel_appointment/<int:appointment_id>", methods=["POST"])
def cancel_appointment(appointment_id):

    patient_id = session["patient_id"]

    cursor = db.cursor()

    sql = """
    DELETE FROM appointments
    WHERE appointment_id = %s
    """

    cursor.execute(sql, (appointment_id,))
    db.commit()

    return redirect(url_for("my_appointments"))


# Patient confirming his cancellation
@app.route("/confirm_cancellation/<int:appointment_id>",methods = ["POST"])
def confirm_cancellation(appointment_id):
     appointment={"appointment_id":appointment_id}
     return render_template("confirm_cancellation.html",appointment=appointment)





# About the clinic route
@app.route("/about")
def about():
    return render_template("about.html")

app.run(debug=True)