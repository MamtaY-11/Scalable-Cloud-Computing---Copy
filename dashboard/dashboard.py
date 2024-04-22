from flask import Blueprint, render_template, flash
#import os
#import boto3
#from database import dynamodb
<<<<<<< HEAD
from PalaceGarden.hotel_manage.booking import Booking
from PalaceGarden.hotel_manage.room import Room
from PalaceGarden.hotel_manage.user import User
from flask_login import login_required
from PalaceGarden.DynamoDBsettings import dynamodb

dashboard_blueprint = Blueprint('dashboard', __name__, static_folder="static", template_folder="templates")

# Initialize the DynamoDB client
# dynamodb =  boto3.client(
#                 'dynamodb',
#                  aws_access_key_id="ASIATUYJP7SUHZW6ODHZ",
#                  aws_secret_access_key="yu+othLPrqEzzZu1g3YlaRQCDcdBm8fJPbfizgO1",
#                  aws_session_token="IQoJb3JpZ2luX2VjEMj//////////wEaCXVzLWVhc3QtMSJHMEUCIG/Dsq8vV+F/Zxwf0W0/+d7beLHnIGQWu/0E9kwy8hfKAiEA5WilFLd4vZsHvpytSIK+Fgt3Z70mrIN/k7YKdRO3v9Iq+wMIERADGgwyNTA3Mzg2Mzc5OTIiDMRKKKMMpu6n9xKwlirYA7dZmLKAUZgcQVgOw53Wj/AuifCsNTH7nq2q7EIGxqw8PumHciJFwv/cX8GB6k5E5UuNy+FOe7i4X2J0oa8qoz4WmM644cmG6xqPHuu2m6Uz6KJf6oAs7OdSNPoe7P8bhGQ+C5F9N2XDV25Bj8rIipR35JjCbzM19OWJej5V8a80J7h07+pjGhUZUwaPREt3cefOBCk2NXBY7G1XKPaWwTVlWL5Jzh8qwdiCH+Ek800ii08oOheiZA6EX3G5T4uIQvQ4XnS+84papJjWAwpRdMb3Fa7c2XdreKSBWNTPDCa5Sxlt51I2RveGLjhdICrj98PY59Ae4ccFLaSph3XpXz0clLyaxjaHeTxptntnOkFsTn4aWCnumohOIUbTfeNe+iDgpQZUnXz1FOV1EclFdowZH1si89RCeBs+cClgqcMKgMew1jMdLy89y1wM9Hy7eBqAMMos7LDB7nPVDNPHWoXhvsj2pJxWILRbpnm58UvVoaA0Lr9yKahBKDgc8/ZxY0w3GkiWr0m8Wlt+24PSjwnW0SESBNZEnNbdP08a98N4jzjykYCwsjPmpzoWaorbZ7DygFneu/YI+TZ3QG15BMf/Z2QnNPgOPKDjwZ49fGZW65tTfiORYjsw7uq8qgY6pgGHWmgldeuN/F7uEVmfEIAhT4udJp4RQp53w79J5nxTO6Yi6UJkVmQwCKvPVYUFMLh3ttJWQ69PDmhCQuD8vkGRCX+jwiwVSLl6JRhXzoICW1+8yfi194sjMdCm3VO8lPKod+crTBOQZSfQXcXC3GRfsmIYq+riCQYyfiZRYlenFAqoPtp/U4Ej/EHWvjqVqxSUiGtquQyyBtjW82PtM6CEgEfRbyQj",
#                  region_name="eu-west-1"
#             )
=======
from hotel_manage.booking import Booking
from hotel_manage.room import Room
from hotel_manage.user import User
from flask_login import login_required
from DynamoDBsettings import dynamodb

dashboard_blueprint = Blueprint('dashboard', __name__, static_folder="static", template_folder="templates")

>>>>>>> dab37c022d0fffdccc0d6d09761c1bac4fd037bd

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