from flask import Flask, render_template,url_for,request,redirect,session,jsonify
from pymongo import MongoClient
import smtplib
import spacy
from email.mime.text import MIMEText
import logging 
import re
 
uname='NULL'
SMTP_SERVER = 'smtp.live.com'
SMTP_PORT = 587
SMTP_USERNAME = 'Akanksha.Akubathini@Chubb.com'
SMTP_PASSWORD = 'Akki@123'
SENDER_EMAIL = 'Akanksha.Akubathini@Chubb.com'

app=Flask(__name__)
app.config['SECRET_KEY']='a_secret_key'
app.logger.setLevel(logging.DEBUG)
client=MongoClient("mongodb://localhost:27017")
db=client.olms

nlp=spacy.load("en_core_web_sm")

def valid(email):
    pattern=r'^[a-zA-Z0-9._]+@[a-zA-Z]+\.[a-z]{2,3}$'
    is_valid = bool(re.match(pattern,email))
    return is_valid

#search
def search_data(keyword):
    # Create an empty list to store search results
    results = []
    # Build a query based on the provided search criteria
    query = {}
    # Check if a keyword is provided and add it to the query
    if keyword:
        query['name'] = {'$regex': f'.*{keyword}.*', '$options': 'i'}  # Case-insensitive partial match
    # Check if a category is provided and add it to the query
    # Execute the query and retrieve the results
    cursor = db.courses.find(query)
    # Convert the cursor to a list of dictionaries
    results = list(cursor)
    return results

#home
@app.route('/',methods=('GET','POST'))
def home():
    try:
        if request.method=='POST':
            return render_template("home.html")
        data=db.courses.find()
        data_list=[]
        for item in data:
            item_data={
                'name':item['name'],
                'desc':item['description'],
                'image':item['image'],
                'course':item['course']
            }
            if 'price' in item:  # check if 'price' key exists in 'item' dictionary
                item_data['price'] = item['price']
            data_list.append(item_data)
    except Exception as e:
                return f"Error: {str(e)}"
    return render_template("home.html",data=data_list)

#instructor_home
@app.route('/instructor_home')
def instructor_home():
    try:
        uname=session.get('user_name')
        data=db.courses.find({'iname':uname})
        app.logger.debug(uname)
        data_list=[]
        for item in data:
            item_data={
                'name':item['name'],
                'desc':item['description'],
                'image':item['image'],
                'course':item['course']
            }
            if 'price' in item:  # check if 'price' key exists in 'item' dictionary
                item_data['price'] = item['price']
            data_list.append(item_data)
    except Exception as e:
        return f"Error: {str(e)}"
    return render_template("instructor_home.html",data=data_list)

#chatbot
@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.json.get('user_message')
    chatbot_response = get_chatbot_response(user_message)
    return jsonify({"response": chatbot_response})

def get_chatbot_response(user_message):
    # chatbot logic 
    return "You said: " + user_message


#cart
@app.route('/cart',methods=('GET','POST'))
def cart():
    try:
        if 'user_name' not in session:
            logging.info('Session not started')
            return redirect(url_for('login'))
        if request.method=='POST':
            user_name=session['user_name']
            name=request.form['courses_name']
            is_item_already_present=db.cart.find_one({'username':user_name,'name':name})
            if not is_item_already_present and request.form['category']=="Premium":
                return redirect(url_for('payment',course_name=name))
            elif not is_item_already_present:
                db.cart.insert_one({'username':user_name,'name':name})
    except Exception as e:
        return f"Error: {str(e)}"
    return redirect(url_for('MyCourses'))

#signup
logging.basicConfig(filename='loggers.log', level=logging.INFO)
logger = logging.getLogger('email_validation')
@app.route('/signup',methods=('GET','POST'))
def signup():
    signup_message="Welcome to Guvi"
    try:
        if request.method=='POST':
            username=request.form['username']
            password=request.form['password']
            confirm_password=request.form['confirm_password']
            email=request.form['email']
            # valid
            if password!=confirm_password:
                signup_message="Passwords do not match"
                return render_template("signup.html",message=signup_message)
            if valid(email):
                logger.info(f'Valid email: {email}')
                db.login.insert_one({'email':email,'password':password,'name':username})
                app.logger.debug(f"User Signed in as: {username}")
                signup_message="Successfully Signedup"
                return redirect(url_for('home'))
            else:
                logger.warning(f'Invalid email: {email}')
                signup_message="Invalid Email"
    except Exception as e:
         return f"Error: {str(e)}"
    return render_template("signup.html",message=signup_message)

#login
@app.route('/login',methods=('GET','POST'))
def login():
    error_message="Enter your details"
    if request.method=='POST':
        rec_email=request.form['email']
        password=request.form['password']
        app.logger.debug(f"User Trying to log in with email: {rec_email}")
        user=db.login.find_one({'email':rec_email,'password':password})
        if user:
            session['logged_in'] = True
            session['user_name'] = user['name']
            uname=user['name']
            app.logger.debug(f"User logged in as: {user['name']}")
            # Create an SMTP connection
            try:
                smtp = smtplib.SMTP("smtp-mail.outlook.com", 587)
                smtp.starttls()
                # Log in to the email server
                smtp.login(SENDER_EMAIL ,SMTP_PASSWORD  )
                msg = MIMEText("Logged in successfully")
                msg["From"] = SENDER_EMAIL
                msg["To"] = rec_email
                msg["Subject"] = "You have logged in to Guvi"
                msg.set_payload("This is the body of the email")
                smtp.sendmail(SENDER_EMAIL, rec_email, msg.as_string())
                # Close the SMTP server connection
                smtp.quit()
                app.logger.debug(f"Email sent successfully.")
            except Exception as e:
                return f"Error: {str(e)}"
            if request.form['user']=='instructor':
                return redirect(url_for('instructor_dashboard'))
            return redirect(url_for('home'))
        else:
            error_message="Invalid email or password. Try again"
    return render_template("login.html" ,message=error_message)

#instructor_dashboard
@app.route('/instructor_dashboard',methods=('GET','POST'))
def instructor_dashboard():
    try:
        if request.method=='POST':
            name=request.form['name']
            description=request.form['desc']
            iname=request.form['iname']
            image_data = request.files['image']
            if image_data:
                image_data=url_for('static',filename='images/'+image_data.filename)
            course=request.form['course']
            if course=="free":
                db.courses.insert_one({'name':name,'description':description,'iname':iname,'image':image_data,'course':course})
            else:
                price=request.form['price']
                db.courses.insert_one({'name':name,'description':description,'iname':iname,'image':image_data,'course':course,'price':price})
            return "Course added Successfully"
    except Exception as e:
        return f"Error: {str(e)}"
    return render_template("instructor_dashboard.html",message="Course wasn't added.Try again")

#admin_dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    try:
        all_items_in_cart=db.cart.find()
    except Exception as e:
        return f"Error: {str(e)}"
    return render_template("admin_dashboard.html",data=all_items_in_cart)

#remove_course
@app.route('/remove_course',methods=['POST','GET'])
def remove_course():
    try:
        if request.method=='POST':
            name=request.form["name"]
            db.courses.delete_one({'name':name})
            db.cart.delete_one({'name':name})
            return "Course removed Successfully"
    except Exception as e:
        return f"Error: {str(e)}"

#admin_login
@app.route('/admin_login',methods=['GET','POST'])
def admin_login():
    try:
        if request.method=='POST':
            name=request.form['username']
            password=request.form['password']
            user=db.admin.find_one({'username':name,'password':password})
            if user:
                session['logged_in'] = True
                session['user_name'] = user['username']
                app.logger.debug(f"User logged in as: {user['username']}")
                return redirect(url_for('admin_dashboard'))
    except Exception as e:
        return f"Error: {str(e)}"
    return render_template("admin_login.html",message="Invalid")

#MyCourses
@app.route('/MyCourses',methods=['GET','POST'])
def MyCourses():
    try:
        if 'user_name' not in session:
            logging.info('Session not started')
            return redirect(url_for('login'))
        user_name=session['user_name']
        logging.info(f'Session started for {user_name}')
        cart_courses = db.cart.find({"username": user_name})
        data_list = []
        for course in cart_courses:
            course_name = course['name']
            course_data = db.courses.find_one({'name': course_name})
            logging.info(f'Course name {course_name}')
            if course_data:
                item_data = {
                    'name': course_data['name'],
                    'desc': course_data['description'],
                    'image': course_data['image'],
                    'course': course_data['course']
                }
            data_list.append(item_data)
    except Exception as e:
        return f"Error: {str(e)}"
    return render_template('MyCourses.html',data=data_list)

#search
@app.route('/search', methods=['POST','GET'])
def search():
    try:
        if request.method == 'POST':
            # Get the user's input from the form
            keyword = request.form['keyword']
            # Query your data source based on the search criteria
            results = search_data(keyword) 
            app.logger.debug(results)
            return render_template('search_results.html', results=results)
    except Exception as e:
        return f"Error: {str(e)}"
    return "not found"

#search_results
@app.route('/search_results')
def search_results():
    try:
        return render_template("search_results.html")
    except Exception as e:
        return f"Error: {str(e)}"

#payment
@app.route('/payment/<course_name>',methods=['GET','POST'])
def payment(course_name):
    try:
        return render_template("payment.html",course_name=course_name)
    except Exception as e:
        return f"Error: {str(e)}"

#payment_successful
@app.route('/payment_successful/<course_name>',methods=['GET','POST'])
def payment_successful(course_name):
    try:
        if request.method=='POST':
            user_name=session['user_name']
            db.cart.insert_one({'username':user_name,'name':course_name})
            return render_template("payment_successful.html")
    except Exception as e:
        return f"Error: {str(e)}"

#logout
@app.route('/logout')
def logout():
    session.clear()
    app.logger.debug("user logged out")
    return redirect(url_for('home'))

if __name__=="__main__":
    app.run(debug=True)