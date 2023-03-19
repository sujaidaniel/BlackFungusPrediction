import email
from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
from flask_mail import Mail
import json
from database import *
#import sqlalchemy as db

with open('config.json','r') as c:
    params = json.load(c)["params"]

# MY db connection
local_server= True
app = Flask(__name__)
app.secret_key='blackfungus'


# this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

# SMTP MAIL SERVER SETTINGS

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)
mail = Mail(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


''' USER = "root"
PASSWORD = "root"
HOST = "localhost"
DATABASE = "hmsdb"
url = 'mysql://%s:%s@%s' % (USER, PASSWORD, HOST)
engine = db.create_engine(url)  # connect to server

create_str = "CREATE DATABASE IF NOT EXISTS %s ;" % (DATABASE)
engine.execute(create_str)
engine.execute("USE hmsdb;")'''


# app.config['SQLALCHEMY_DATABASE_URL']='mysql://username:password@localhost/databas_table_name'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:root@localhost/hmsdb'
db=SQLAlchemy(app)
db.init_app(app)


# here we will create db models that is tables


class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    usertype=db.Column(db.String(50))
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))

class Patients(db.Model):
    pid=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50))
    name=db.Column(db.String(50))
    gender=db.Column(db.String(50))
    slot=db.Column(db.String(50))
    disease=db.Column(db.String(50))
    time=db.Column(db.String(50),nullable=False)
    date=db.Column(db.String(50),nullable=False)
    symptoms=db.Column(db.String(50))
    number=db.Column(db.String(50))

class Doctors(db.Model):
    did=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50))
    doctorname=db.Column(db.String(50))
    dept=db.Column(db.String(50))

class Trigr(db.Model):
    tid=db.Column(db.Integer,primary_key=True)
    pid=db.Column(db.Integer)
    email=db.Column(db.String(50))
    name=db.Column(db.String(50))
    action=db.Column(db.String(50))
    timestamp=db.Column(db.String(50))


class Prec(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    email=db.Column(db.String(100))
    date=db.Column(db.String(100))
    prec=db.Column(db.String(100))

class Bill(db.Model):
    bid=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    email=db.Column(db.String(100))
    confees=db.Column(db.String(100))
    othchrg=db.Column(db.String(100))
    total=db.Column(db.String(100))
    
class Payment(db.Model):
    oid=db.Column(db.Integer,primary_key=True)
    cname=db.Column(db.String(100),unique=True,nullable=False)
    email=db.Column(db.String(100),unique=True,nullable=False)
    ctype=db.Column(db.String(100),unique=True,nullable=False)
    camt=db.Column(db.String(100),unique=True,nullable=False)
  
    

db.create_all()
db.session.commit()





# here we will pass endpoints and run the fuction
@app.route('/')
def index():
    a=params['gmail-user']
    return render_template('index.html')
    


@app.route('/doctors',methods=['POST','GET'])
def doctors():

    if request.method=="POST":

        email=request.form.get('email')
        doctorname=request.form.get('doctorname')
        dept=request.form.get('dept')

        query=db.engine.execute(f"INSERT INTO `doctors` (`email`,`doctorname`,`dept`) VALUES ('{email}','{doctorname}','{dept}')")
        flash("Information is Stored","primary")

    return render_template('doctor.html')



@app.route('/patients',methods=['POST','GET'])
@login_required
def patient():
    doct=db.engine.execute("SELECT * FROM `doctors`")

    if request.method=="POST":
        email=request.form.get('email')
        name=request.form.get('name')
        gender=request.form.get('gender')
        slot=request.form.get('slot')
        disease=request.form.get('disease')
        time=request.form.get('time')
        date=request.form.get('date')
        symptoms=request.form.get('symptoms')
        number=request.form.get('number')
        
        subject="HOSPITAL MANAGEMENT SYSTEM"
        query=db.engine.execute(f"INSERT INTO `patients` (`email`,`name`,	`gender`,`slot`,`disease`,`time`,`date`,`symptoms`,`number`) VALUES ('{email}','{name}','{gender}','{slot}','{disease}','{time}','{date}','{symptoms}','{number}')")

# mail starts from here

        mail.send_message(subject, sender=params['gmail-user'], recipients=[email],body=f"YOUR bOOKING IS CONFIRMED THANKS FOR CHOOSING US \nYour Entered Details are :\nName: {name}\nSlot: {slot}\nTiming: {time}")



        flash("Booking Confirmed","info")


    return render_template('patient.html',doct=doct)


@app.route('/bookings')
@login_required
def bookings(): 
    em=current_user.email
    if current_user.usertype=="Doctor":
        query=db.engine.execute(f"SELECT * FROM `patients`")
        return render_template('booking.html',query=query)
    else:
        query=db.engine.execute(f"SELECT * FROM `patients` WHERE email='{em}'")
        return render_template('booking.html',query=query)
    
@app.route('/docpre2/<string:uemail>',methods=['GET'])
@login_required
def docpre2(uemail):
    ut=current_user.usertype
    if(ut=="Doctor"):
        print("Current user is doctor, checking prescription log of: ")
        print(uemail)
    data=db.engine.execute(f"select * from `prec` where email='{uemail}'")
    return render_template("docpre.html",data=data)

@app.route("/edit/<string:pid>",methods=['POST','GET'])
@login_required
def edit(pid):
    posts=Patients.query.filter_by(pid=pid).first()
    if request.method=="POST":
        email=request.form.get('email')
        name=request.form.get('name')
        gender=request.form.get('gender')
        slot=request.form.get('slot')
        disease=request.form.get('disease')
        time=request.form.get('time')
        date=request.form.get('date')
        symptoms=request.form.get('symptoms')
        number=request.form.get('number')
        db.engine.execute(f"UPDATE `patients` SET `email` = '{email}', `name` = '{name}', `gender` = '{gender}', `slot` = '{slot}', `disease` = '{disease}', `time` = '{time}', `date` = '{date}', `symptoms` = '{symptoms}', `number` = '{number}' WHERE `patients`.`pid` = {pid}")
        flash("Slot is Updated","success")
        return redirect('/bookings')
    
    return render_template('edit.html',posts=posts)


@app.route("/delete/<string:pid>",methods=['POST','GET'])
@login_required
def delete(pid):
    db.engine.execute(f"DELETE FROM `patients` WHERE `patients`.`pid`={pid}")
    flash("Slot Deleted Successful","danger")
    return redirect('/bookings')






@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == "POST":
        username=request.form.get('username')
        usertype=request.form.get('usertype')
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exist","warning")
            return render_template('/signup.html')
        encpassword=generate_password_hash(password)

        new_user=db.engine.execute(f"INSERT INTO `user` (`username`,`usertype`,`email`,`password`) VALUES ('{username}','{usertype}','{email}','{encpassword}')")

        # this is method 2 to save data in db
        # newuser=User(username=username,email=email,password=encpassword)
        # db.session.add(newuser)
        # db.session.commit()
        flash("Signup Success Please Login","success")
        return render_template('login.html')

          

    return render_template('signup.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","primary")
            return redirect(url_for('index'))
        else:
            flash("invalid credentials","danger")
            return render_template('login.html')    





    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))



    

@app.route('/details')
@login_required
def details():
    # posts=Trigr.query.all()
    posts=db.engine.execute("SELECT * FROM `trigr`")
    return render_template('trigers.html',posts=posts)


@app.route('/search',methods=['POST','GET'])
@login_required
def search():
    if request.method=="POST":
        query=request.form.get('search')
        dept=Doctors.query.filter_by(dept=query).first()
        name=Doctors.query.filter_by(doctorname=query).first()
        if name:

            flash("Doctor is Available","info")
        else:

            flash("Doctor is Not Available","danger")
    return render_template('index.html')


@app.route('/discharge',methods=['POST','GET'])
@login_required
def discharge():
    if request.method=="POST" and 'confees' in request.form and 'othchrg' in request.form:
        total=''
        name=request.form.get('name')
        email=request.form.get('email')
        confees=float(request.form.get('confees'))
        othchrg=float(request.form.get('othchrg'))
        total=total+str(confees+othchrg)
        print(total)
      
        newuser=Bill(name=name,email=email,confees=confees,othchrg=othchrg,total=total)
        db.session.add(newuser)
        db.session.commit()
        return render_template("discharge.html",total=total)
    return render_template("discharge.html")


@app.route('/docpre',methods=['GET'])
@login_required
def docpre():
    em=current_user.email
    data=db.engine.execute(f"select * from `prec` where email='{em}'")
    return render_template("docpre.html",data=data)

    
@app.route('/wpre',methods=['POST','GET'])
@login_required
def wpre():
    if request.method=="POST":
        name=request.form.get('name')
        email=request.form.get('email')
        date=request.form.get('date')
        prec=request.form.get('prec')
        newuser=Prec(name=name,email=email,date=date,prec=prec)
        db.session.add(newuser)
        db.session.commit()
        flash("Precription sent successfully","success")
    return render_template("wpre.html")


@app.route('/pbill')
@login_required
def pbill():
    em=current_user.email
    data=db.engine.execute(f"select * from `bill` where email='{em}'")
    return render_template("pbill.html",data1=data)

@app.route('/payment',methods=['POST','GET'])
@login_required
def payment():
    if request.method=="POST":
        cname=request.form.get('cname')
        print(cname)
        email=request.form.get('email')
        ctype=request.form.get('ctype')
        camt=request.form.get('camt')
        new_user=db.engine.execute(f"INSERT INTO `payment` (`cname`,`email`,`ctype`,`camt`) VALUES ('{cname}','{email}','{ctype}','{camt}')")
        flash("payment successfully done","success")
        return render_template("payment.html")
    return render_template("payment.html")
    



    

    
    
@app.route('/verify')
@login_required
def verify():
    return render_template("verify.html")



@app.route("/track")
def track():
    print("hiiiiiiiiiiiiii")
    
    disease = request.args.get('iname')
    print("111111111111111111111111111111111111111")
    print(disease)

   

    data = image_info(disease)
    
    print(data)
   
    
    #data = v_image(data)
    print(data)
    return render_template("booking.html",m1="sucess",users=data)
        


   


app.run(debug=True)    

