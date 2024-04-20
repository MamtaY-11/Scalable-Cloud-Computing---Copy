from flask import Blueprint, render_template, flash
#import os
#import boto3
#from database import dynamodb
from hotel_manage.booking import Booking
from hotel_manage.room import Room
from hotel_manage.user import User
from flask_login import login_required
from DynamoDBsettings import dynamodb

dashboard_blueprint = Blueprint('dashboard', __name__, static_folder="static", template_folder="templates")


# Initialize class object
tableName = 'PalaceGardenBooking'
booking_obj = Booking(tableName)
roomTableName = 'PalaceGardenRooms'
#bucketName = os.environ['BUCKET_NAME']
bucketName = ""
room_obj = Room(roomTableName, bucketName)
userTableName = 'PalaceGardenLogin'
user_obj = User(userTableName)

@dashboard_blueprint.route('/', methods=['GET'])
@login_required
def dashboard():
    all_booking=''
    #All Bookings
    all_booking = booking_obj.get_all_booking(dynamodb)
    total_booking = len(all_booking['data']['Items'])
        
    paid_bookings = [booking for booking in all_booking['data']['Items'] if booking['paymentStatus']['S'] == 'Paid']
    count_paid_bookings = len(paid_bookings)

    # # All Rooms
    all_rooms = room_obj.get_all_room(dynamodb)
    total_room = len(all_rooms['data']['Items'])

    # # All users
 

    # # current user
    #current_user_role = current_user.get_role()

    return render_template("admin/index.html", bookings=all_booking['data']['Items'], total_booking=total_booking, total_paid_invoices=count_paid_bookings,  total_room=total_room)
    #return render_template("admin/index.html",  total_booking=0, total_paid_invoices=0,  total_room=0 )