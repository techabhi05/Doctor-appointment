from flask import Flask,render_template,request,redirect,url_for
import mysql.connector
import bcrypt

app = Flask(__name__)

db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "prashu@46",
    database = "clinic_management"
)

print("Database connected successfully")
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
                  return redirect(url_for)
             else:
                  return "Thapuuuuu"

    return render_template("patient_login.html")

@app.route("/doctor")
def doctor():
    return render_template("doctor_login.html")

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

@app.route("/book/<int:doctor_id>")
def book_appointment(doctor_id):

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

    
app.run(debug=True)