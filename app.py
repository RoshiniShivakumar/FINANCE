from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import time
from flask_socketio import SocketIO



today = None
target_date = None

balance=0
lock_amount = 0
app = Flask(__name__)
socketio = SocketIO(app)
CORS(app)

with open("profile.txt",'r') as file:
    lines = file.readlines()
    balance = lines[4].strip()
    balance = int(balance)

    savings = lines[3].strip()
    savings = int(savings)

# Home Route
@app.route("/home")
def home():
    return render_template("home.html")

# Add a Transaction
@app.route("/make_transaction", methods=["POST"])
def add_transaction():
    return "<h1>makinga transaction</h1>"

# Get All Transactions
@app.route("/transactions")
def get_transactions():
    with open("t_history.txt","r") as file:
        content = file.read()
    return render_template("transaction.html",content=content)


#SAVINGS PAGE
@app.route("/savings")
def savings():
    with open("savings.txt","r") as file:
        content = file.read()
    return render_template("savings.html",content=content,Total=lock_amount)

#USER AUTHENTICATION

@app.route("/signup")
def sign_up():
    return render_template("signup.html")

@app.route("/")
def login():
    return render_template("login.html")


@socketio.on("debit")
def debitted(data):
    global balance
    if data<=balance:
        print("amount to debit is greater than balance")
        balance-=data
        print("current balance is ",balance)
        with open("profile.txt",'r') as file:
            lines = file.readlines()
        with open("profile.txt",'w+') as file:
            lines[4]=str(balance)
            file.writelines(lines)

        with open("t_history.txt","a") as file:
            file.write("\n"+f"Amount: {data}, type: debit, balance: {balance}")
            
        socketio.emit("debit_true")
    else:
        socketio.emit("debit_false")

@socketio.on("credit")
def creditted(data):
    if data>0:
        global balance
        balance+=data

        with open("profile.txt",'r') as file:
            lines = file.readlines()
        with open("profile.txt",'w+') as file:
            lines[4]=str(balance)
            file.writelines(lines)

        with open("t_history.txt","a") as file:
            file.write("\n"+f"Amount: {data}, type: credit, balance: {balance}")

        socketio.emit("credit_true")
    else:
        socketio.emit("credit_false")

@socketio.on("a_lock")
def a_lock(data):
    global balance
    data[0]=int(data[0])
    data[1]=int(data[1])
    if data[0]<=0 or data[0]>balance or data[1]<0:
        socketio.emit("a_lock_false")
    else:
        balance-=data[0]

        with open("profile.txt",'r') as file:
            lines = file.readlines()
        with open("profile.txt",'w+') as file:
            lines[4]=str(balance)
            file.writelines(lines)

        with open("t_history.txt","a") as file:
            file.write("\n"+f"Amount: {data[0]}, type: savings, balance: {balance}, duration: {data[1]} days")

        with open("savings.txt","a") as file:
            file.write("\n"+f"Amount: {data[0]}, type: savings, balance: {balance}, duration: {data[1]} days")
        
        global lock_amount
        lock_amount+=data[0]
        
        socketio.emit("a_lock_true")
        timer(data[1],data[0])

#for days just remove the quotes for activation
'''def timer(data):
    today = datetime.today().date()
    target_date = today + timedelta(days=data)

    while True:
        today = datetime.today().date()
        if today == target_date:
            global lock_amount
            global balance
            balance+=lock_amount

            break  # Stop checking after execution
        else:
            print(f"Waiting... Today: {today}, Target: {target_date}")
            time.sleep(86400)  # Check once per day (86400 seconds = 1 day)'''

#for seconds or minutes
def timer(data1,data2):
    # Set target time (5 minutes from now)
    target_time = datetime.now() + timedelta(minutes=data1)

    # Sleep until the target time
    time_to_wait = (target_time - datetime.now()).total_seconds()
    time.sleep(time_to_wait)

    global balance
    balance+=data2

    with open("profile.txt",'r') as file:
            lines = file.readlines()
    with open("profile.txt",'w+') as file:
        lines[4]=str(balance)
        file.writelines(lines)


'''@socketio.on("pass_check")
def pass_check(data):

    print("pass ccheck is working")
    
    with open("login.txt",'r') as file:
        lines = file.readlines()
        if lines[0]==data[0] and lines[1]==data[1]:
            socketio.emit("pass_true")
        else:
            socketio.emit("pass_false")

@socketio.on("check_values")
def check_values(data):
    value1 = data["value1"]
    value2 = data["value2"]
    print("check_value function is working")
    # Check values in a file
    with open("login.txt", "r") as file:
        lines = file.readlines()
        if value1 == lines[0] and value2 == lines[1]:
            print(f"value1 :{value1} and lines[0]: {lines[0]}")
            socketio.emit("check_result", {"message": "Match found!"})
        else:
            print(f"value1 :{value1} and lines[0]: {lines[0]}")
            socketio.emit("check_result", {"message": "No match found!"})'''



@app.route("/")
def index():
    return render_template("login.html")

@socketio.on("login")
def handle_login(data):
    username = data["username"]+"\n"
    password = data["password"]

    print(username,password)


    try:
        with open("login.txt", "r") as file:
            lines = file.readlines()
            print(lines)

            file_username = lines[0]  # Read first line (username)
            file_password = lines[1]  # Read second line (password)

        if username == file_username and password == file_password:
            socketio.emit("login_response", {"message": "Login Successful!","flag":"true"})
        else:
            socketio.emit("login_response", {"message": "Invalid Username or Password","flag":"false"})
    
    except FileNotFoundError:
        socketio.emit("login_response", {"message": "Error: User data file not found!"})



if __name__ == "__main__":
    socketio.run(app, debug=True)
