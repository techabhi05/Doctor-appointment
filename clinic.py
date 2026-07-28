from flask import Flask,render_template,request

app = Flask(__name__)

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

app.run(debug=True)