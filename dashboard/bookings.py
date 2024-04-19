from flask import Blueprint, jsonify, render_template, request, flash, redirect
from flask_login import login_required, current_user
import os

import requests

# from database import dynamodb
from hotel_manage.booking import Booking
from hotel_manage.room import Room
from DynamoDBsettings import dynamodb
booking_blueprint = Blueprint('booking', __name__, static_folder="static", template_folder="templates")

#Initialize booking object
tableName = 'PalaceGardenBooking'
booking_obj = Booking(tableName)
roomTableName = 'PalaceGardenRooms'
bucketName = "x22245855pploads3image"
room_obj = Room(roomTableName, bucketName)

#Get all bookings
@booking_blueprint.route("/")
@login_required
def booking():
    # Get all bookings
    all_booking = booking_obj.get_all_booking(dynamodb)
  
    # Get all rooms
    all_rooms = room_obj.get_all_room(dynamodb)

   #current_user_role = current_user.get_role()
    return render_template('admin/booking.html', bookings=all_booking['data']['Items'], rooms=all_rooms['data']['Items'])

# Delete new booking
@booking_blueprint.route("/add", methods=['POST'])
@login_required
def add_booking():
    # If POST request
    if request.method == 'POST':
        # Generate unique booking id
        bookingId = booking_obj.generate_bookingId()
       
        new_booking = {
            "bookingId":bookingId,
            "room_no": request.form['room_no'],     
            "roomType": request.form['roomType'],
            "guestName": request.form['guestName'],
            "guestEmail": request.form['guestEmail'],
            "guestPhone": request.form['guestPhone'],
            "checkInDate": request.form['checkInDate'],
            "checkOutDate": request.form['checkOutDate'],
            "totalGuests": request.form['totalGuests'],
            "paymentStatus": request.form['paymentStatus'],
            "paymentAmount": request.form['paymentAmount']
        }

         # Add new booking
        response = booking_obj.create_booking(dynamodb, new_booking)
        
        if response['statusCode'] == 201:
            flash(response['message'], 'success')
            return redirect('/dashboard/booking')
        else:
            flash(response['message'], 'danger')
            return redirect('/dashboard/booking')

# Update perticular booking based on bookingID
@booking_blueprint.route("/edit", methods=['GET', 'POST'])
@login_required
def edit_booking():

    # Get Query parameter
    bookingId = request.args.get('bookingId')

    # If not bookingId then redirect to 404 page
    if bookingId is None:
        return render_template('404.html')

    # Get booking details and fill the edit form
    booking = booking_obj.get_booking(dynamodb, bookingId)
    if request.method == 'GET':

        # If the booking already exist
        if booking['statusCode'] == 200:
            #current_user_role = current_user.get_role()
            return render_template('admin/edit_booking.html', booking=booking['data'])
        else:
            flash('Booking not exist!', 'danger')
            return redirect('/edit')

    if request.method == 'POST':
        updated_booking={
            "bookingId": bookingId,
            "room_no":  request.form['room_no'], 
            "roomType":  request.form['roomType'],
            "guestName": request.form['guestName'],
            "guestEmail": request.form['guestEmail'],
            "guestPhone": request.form['guestPhone'],
            "checkInDate": request.form['checkInDate'],
            "checkOutDate": request.form['checkOutDate'],
            "totalGuests": request.form['totalGuests'],
            "paymentStatus": request.form['paymentStatus'],
            "paymentAmount": request.form['paymentAmount']
        }
   
        # If the bookingId exist then update room
        if booking['statusCode'] == 200:
            response = booking_obj.update_booking(dynamodb, updated_booking)
            flash(response['message'], 'success')
            return redirect('/dashboard/booking')
        else:
            flash(booking['message'], 'danger')
            return redirect('/dashboard/booking')

# Delete perticular booking based on bookingID
@booking_blueprint.route("/remove/<bookingId>", methods=['GET'])
@login_required
def delete_booking(bookingId):
       
    # Check booking exist or not
    room = booking_obj.get_booking(dynamodb, bookingId)

    # If the bookingId exist then update room
    if room['statusCode'] == 200:
        # Delete room based on bookingId
        response = booking_obj.delete_booking(dynamodb, bookingId)
        flash(response['message'], 'success')
        return redirect('/dashboard/booking')
    else:
        flash(response['room'], 'danger')
        return redirect('/dashboard/booking')
    

@booking_blueprint.route("/sort", methods=['POST'])
@login_required
def sort():
    try:
        # Extract form data from the request
        table_name = request.form.get('tableName')
        sort_key = request.form.get('sortBy')
        sort_order = request.form.get('sortOrder', 'asc').lower()

        # Validate parameters
        if not table_name or not sort_key:
            return jsonify({'message': 'Missing required parameters'}), 400

        # Construct the API URL with query parameters
        api_url = f'https://09q1ii462d.execute-api.eu-west-1.amazonaws.com/dev/x22245855SortingDemo?tableName={table_name}&sortBy={sort_key}&sortOrder={sort_order}'

        # Make a GET request to the API
        response = requests.get(api_url)

        # Check if the request was successful
        if response.status_code == 200:
            api_data = response.json()
            all_rooms = room_obj.get_all_room(dynamodb)
            if response.status_code == 200:
               return render_template('admin/booking.html', bookings=api_data, rooms=all_rooms['data']['Items'])
            #return jsonify(api_data), 200
        else:
            return jsonify({'message': 'Failed to fetch data from API'}), response.status_code

    except Exception as e:
        return jsonify({'message': 'Internal Server Error'}), 500