import ast
from flask import Flask, Blueprint, jsonify, request, render_template, flash, redirect
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user
import requests
from hotel_manage.booking import Booking
from hotel_manage.room import Room
from hotel_manage.user import User
from dashboard.dashboard import dashboard_blueprint
from dashboard.users import user_blueprint
from dashboard.rooms import room_blueprint
from dashboard.bookings import booking_blueprint
from DynamoDBsettings import dynamodb




   


application = Flask(__name__)
application.secret_key = "demo-dev"
userTable = 'PalaceGardenLogin'
user_obj = User(userTable)
room_obj = Room("PalaceGardenRooms", "x22245855pploads3image")
booking_obj = Booking("PalaceGardenBooking")
topic_arn = 'arn:aws:sns:eu-west-1:250738637992:demo'
# Register blueprints
application.register_blueprint(dashboard_blueprint, url_prefix="/dashboard")
application.register_blueprint(user_blueprint, url_prefix="/dashboard/users")
application.register_blueprint(booking_blueprint, url_prefix="/dashboard/booking")
application.register_blueprint(room_blueprint, url_prefix="/dashboard/rooms")

# Login Authentication
login_manager = LoginManager()
login_manager.init_app(application)

class UserAuth(UserMixin):
    def __init__(self, username):
        self.id = username
       

    def get_id(self):
        return str(self.id)
    
  

@application.route('/')
def hello_world():
    all_rooms = room_obj.get_all_room(dynamodb)
    # Convert the string amenities to list
    formated_all_room = []
    for room in all_rooms['data']['Items']:
        for key in room.keys():
            if key == 'amenities':
                room[key] = ast.literal_eval(room[key]['S'])
        formated_all_room.append(room)
    return render_template('index.html', data=formated_all_room)
    #return "hello"

@login_manager.user_loader
def load_user(username):
    # Get user details from the dynamodb
    get_user = user_obj.get_user(dynamodb, username)
    if get_user['data']:
        #role = get_user['data']['userRole']['S']
        return UserAuth(username)
    
    return None

@application.route('/login', methods=['GET', 'POST'])
def login():
    is_current_active = current_user.get_id()
    if is_current_active:
        return redirect('/dashboard')
    else:   
        if request.method == 'GET':
            return render_template("login.html")
    if request.method == 'POST':
        # Fetch login details from form
        username = request.form['username']
        password = request.form['password']
      
        # Check user exist or not
        user = user_obj.get_user(dynamodb, username)
    
        # If the username, role and password match then login to dashbaord
        if user['statusCode'] == 200 and user['data']['password']['S'] == password :
            
            # Create user session for authentication
            login_user(UserAuth(username))
            #cloudWatchLog.logFunction(user['data'])
            return redirect('/dashboard')
        
        else:
            # If login fails, store the error message using flash
            #flash('Invalid username or password. Please try again.', 'danger')
            flash(user , 'danger')
            return redirect('/login')
    else:
        return {"statuscode": 405, "message": "Method not allowd."}, 405

# Logout
@application.route('/logout', methods=['GET'])
def logout():
    logout_user()
    
    return redirect('/')

# Unauthorized Route
@application.route('/unauthorized', methods=['GET'])
def unauthorized():
    return render_template('/403.html')


# If the user is unauthorized then redirect user to login
@login_manager.unauthorized_handler
def unauthorized():
    # Redirect to the login page
    return redirect('/login')


# Booking Room
@application.route("/checkout", methods=['GET', 'POST'])
def book_now():

    # Get query parameter
    room_no = request.args.get('room_no')
    room = room_obj.get_room(dynamodb, room_no)
    room_type = room['data']['room_type']
    if request.method == 'GET':
        try:
            if room_no:
                return render_template('booking_form.html', room=room['data'])
            else:
                return render_template('404.html')
        except:
            return render_template('404.html')

    # If POST request
    if request.method == 'POST':
        # Generate unique booking id
        bookingId = booking_obj.generate_bookingId()
        new_booking = {
            "bookingId":bookingId,
            "room_no": str(room_no), 
            "roomType": str(room_type['S']),
            "guestName": request.form['guestName'],
            "guestEmail": request.form['guestEmail'],
            "guestPhone": request.form['guestPhone'],
            "checkInDate": request.form['checkInDate'],
            "checkOutDate": request.form['checkOutDate'],
            "totalGuests": request.form['totalGuests'],
            "paymentStatus": "Unpaid",
            "paymentAmount": request.form['paymentAmount'],
        }

         # Add new booking
        response = booking_obj.create_booking(dynamodb, new_booking)
        
        if response['statusCode'] == 201:
            # Send Email to Manager & Admin
            
            booking_details = {
                "bookingId":bookingId,
                "room_no": str(room_no),     
                "guestName": request.form['guestName'],
                "guestEmail": request.form['guestEmail'],
                "guestPhone": request.form['guestPhone'],
                "checkInDate": request.form['checkInDate'],
                "checkOutDate": request.form['checkOutDate'],
                "totalGuests": request.form['totalGuests'],
                "paymentAmount": request.form['paymentAmount']
            }

            #email_response = sendEmail(booking_details)
            #if email_response['statusCode'] == 200:
            #print("EMAIL SENT: ", email_response)
            flash('Thank you for booking, we will contact you soon!', 'success')
            return redirect(f'/checkout?room_no={room_no}')
            # else:
            #     #flash('Sorry!, failed booking, please try again!', 'danger')
            #     flash(email_response, 'danger')
            #     return redirect(f'/checkout?room_no={room_no}')
        else:
            flash('Sorry!, failed booking, please try again!', 'danger')
            return redirect(f'/checkout?room_no={room_no}')




if __name__ == "__main__":
    
    application.run(debug=True)