from flask import Flask,render_template,request
import mysql.connector

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

@app.route("/patient",methods=["GET","POST"])
def patient():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]


        print("Email: ",email)
        print("Password :",password)

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

            print("Name: ",name)
            print("Email: ",email)
            print("Password :",password)

        return render_template("patient_register.html")

    
app.run(debug=True)