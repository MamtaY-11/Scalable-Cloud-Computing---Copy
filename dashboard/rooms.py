import datetime
from flask import Blueprint, render_template, request, flash, redirect
from flask_login import login_required, current_user
import os
import ast
import boto3
from botocore.exceptions import ClientError
from hotel_manage.room import Room
from DynamoDBsettings import dynamodb,s3
import json
from collections import OrderedDict
# from database import dynamodb, s3

room_blueprint = Blueprint('room', __name__, static_folder="static", template_folder="templates")

# Initialize class object
tableName= 'PalaceGardenRooms'
#room_obj = Room(tableName, os.environ['BUCKET_NAME'])
room_obj = Room(tableName, "x22245855pploads3image")

# def json_serializable(obj):
#     if isinstance(obj, datetime.date):
#         return obj.__str__()

# This route will show all rooms in dashboard
@room_blueprint.route("/")
@login_required
def room():
    all_rooms = room_obj.get_all_room(dynamodb)
    # Convert the string amenities to list
    formated_all_room = []
    for room in all_rooms['data']['Items']:
        # print("All rooms:", room)
        for key in room.keys():
            if key == 'amenities':
                room[key] = ast.literal_eval(room[key]['S'])
                # print("AMENITIES: ", room[key])
        formated_all_room.append(room)
    
    
    return render_template('admin/rooms.html', data=formated_all_room)

# This route can add new room
@room_blueprint.route("/add", methods=['POST'])


@login_required
def add_room():
    
    # Check the room exist or not
    room_no = request.form["room_no"]
    isRoomExist = room_obj.get_room(dynamodb, room_no)
 
    if isRoomExist['statusCode'] == 200:
        flash('Room already exist!', 'danger')
        return redirect('/dashboard/rooms')

    
    # Upload image to S3 bucket
    isUploaded = room_obj.upload_image_s3(request, s3)
  
    if isUploaded["statusCode"] == 200:
        # Get other details
        new_room = {
            "room_no": room_no,
            "room_type": request.form["room_type"],
            "description": request.form["description"],
            "no_of_bed": request.form["no_of_bed"],
            "price": request.form["price"],
            "availability": request.form["availability"],
            "amenities": request.form.getlist("amenities[]"),
            "image_url": isUploaded['image_url']
        }

        # Add new room
        isAdded = room_obj.create_room(dynamodb, new_room)
        
        if isAdded['statusCode'] == 201:
            flash(isAdded['message'], 'success')
            return redirect('/dashboard/rooms')
        else:
            flash(isAdded['message'], 'danger')
            return redirect('/dashboard/rooms')
    else:
        flash(isUploaded['message'], 'danger')
        return redirect('/dashboard/rooms')



# This route can update room
@room_blueprint.route("/edit", methods=['GET', 'POST'])
@login_required
def edit_room():

    # Get Query parameter
    room_no = request.args.get('room_no')

    # If not room_no then redirect to 404 page
    if room_no is None:
        return render_template('404.html')

    if request.method == 'GET':
        # Get room details and fill the edit form
        room = room_obj.get_room(dynamodb, room_no)
   
        # If the username exist
        if room['statusCode'] == 200:
            #current_user_role = current_user.get_role()
            return render_template('admin/edit_rooms.html', room=room['data'])
        else:
            flash(room['message'], 'danger')
            return redirect('rooms')
    amenities = str(request.form.getlist('amenities[]'))

    if request.method == 'POST':
        # Get room details
        updated_room={
            "room_no": room_no,
            "room_type": request.form["room_type"],
            "description": request.form["description"],
            "no_of_bed": request.form["no_of_bed"],
            "price": request.form["price"],
            "availability": request.form["availability"],
            "amenities": amenities
        }
   
        # Check room exist or not
        room = room_obj.get_room(dynamodb, room_no)
  
        # If the room_no exist then update room
        if room['statusCode'] == 200:
            response = room_obj.update_room(dynamodb, updated_room)
            flash(response['message'], 'success')
            return redirect('/dashboard/rooms')
        else:
            flash(room['message'], 'danger')
            return redirect('/dashboard/rooms')

# This route can remove room
@room_blueprint.route("/remove/<room_no>")
@login_required
def delete_room(room_no):
   
    # Check room exist or not
    room = room_obj.get_room(dynamodb, room_no)

    # If the room_no exist then update room
    if room['statusCode'] == 200:
        # Delete room based on room_no
        response = room_obj.delete_room(dynamodb, room_no)
        flash(response['message'], 'success')
        return redirect('/dashboard/rooms')
    else:
        flash(response['message'], 'danger')
        return redirect('/dashboard/rooms')