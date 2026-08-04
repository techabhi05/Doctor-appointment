from flask import Flask,render_template,request,redirect,url_for,session
from datetime import datetime,timedelta
import mysql.connector
import bcrypt

app = Flask(__name__)
app.secret_key = "clinic_secret_key"



db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "prashu@46",
    database = "clinic_management"
)

@app.route("/")
def home():
    return render_template("index.html")

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
                  return "Thapuuuuu"

    return render_template("patient_login.html")



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


@app.route("/about")
def about():
    return render_template("about.html")

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


@app.route("/patient/dashboard")
def patient_dashboard():
     print(session.get("patient_id"))
     return render_template("patient_dashboard.html")



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
              return "doctor illa kano vade nan magne"
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
                  return "this time slot is already booked"
             


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

         return "Appointment booked successfully!"


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

@app.route("/confirm_cancellation/<int:appointment_id>",methods = ["POST"])
def confirm_cancellation(appointment_id):
     appointment={"appointment_id":appointment_id}
     return render_template("confirm_cancellation.html",appointment=appointment)



app.run(debug=True)