from flask import Blueprint, render_template, request, flash, redirect
from flask_login import login_required, current_user
import boto3

from statusCode import HTTP_200_OK, HTTP_201_CREATED
from hotel_manage.user import User
from DynamoDBsettings import dynamodb


user_blueprint = Blueprint('users', __name__, static_folder="static", template_folder="templates")
userTable = 'PalaceGardenLogin'
user_obj = User(userTable   )

@user_blueprint.route("/", methods=['GET'])
@login_required
def user():
    #current_user_role = current_user.get_role()
    # If the user is has admin permission then show users
    if 'Admin' == 'Admin':
        all_users = user_obj.get_all_user(dynamodb)
        return render_template('admin/users.html', users=all_users['data']['Items'])
    else:
        return redirect('/unauthorized')

# Add new users
@user_blueprint.route('/add', methods=['POST'])
@login_required
def add_user():
    # Get user details
    new_user={
        "username" : request.form['username'],
        "password" :request.form['password'],
        "fullName": request.form['fullName'],
        "email": request.form['email'],
        "phone": request.form['phone'],
    }
    # Check user exist or not
    user = user_obj.get_user(dynamodb, new_user['username'])
    
    # If the username already exist
    if user['statusCode'] == 200:

        flash(user['message'], 'danger')
        return redirect('/dashboard/users')
    
    else:
        # Create new user
        response = user_obj.create_user(dynamodb, new_user)

        if response['statusCode'] == HTTP_201_CREATED:
            flash(response['message'], 'success')
            return redirect('/dashboard/users')
        else:
            flash(response['message'], 'danger')
            return redirect('/dashboard/users')

# Update user
@user_blueprint.route("/edit", methods=['GET', 'POST'])
@login_required
def edit_user():
     # Get Query parameter
    username = request.args.get('username')

    # If not username then redirect to 404 page
    if username is None:
        return render_template('404.html')

    if request.method == 'GET':
        # Get user details and fill the edit form
        user = user_obj.get_user(dynamodb, username)
        
        # If the username exist
        if user['statusCode'] == 200:
           
            return render_template('admin/edit_user.html', user=user['data'])
        else:
            flash('User not exist!', 'danger')
            return redirect('users')

    if request.method == 'POST':
        # Get user details
        updated_user={
            "username" : username,
            "password" :request.form['password'],
            "fullName": request.form['fullName'],
            "email": request.form['email'],
            "phone": request.form['phone'],
        }
  
        # Check user exist or not
        user = user_obj.get_user(dynamodb, username)
  
        # If the username exist then update user
        if user['statusCode'] == 200:
            response = user_obj.update_user(dynamodb, updated_user)
            if response['statusCode'] == 200:
                flash(response['message'], 'success')
                return redirect('/dashboard/users')
            else:
                flash(response['message'], 'danger')
                return redirect('/dashboard/users')
        else:
            flash(user['message'], 'success')
            return redirect('/dashboard/users')

# Delete perticular user based on username
@user_blueprint.route('/remove/<username>')
@login_required
def delete_user(username):

    # Check user exist or not
    user = user_obj.get_user(dynamodb, username)
    print("USER TO DELETE: ", user)
    # If the username exist then update user
    if user['statusCode'] == 200:
        # Delete user
        response = user_obj.delete_user(dynamodb, username)
        if response['statusCode'] == 200:
            flash(response['message'], 'success')
            return redirect('/dashboard/users')
        else:
            flash(response['message'], 'danger')
            return redirect('/dashboard/users')
    else:
        flash(user['message'], 'danger')
        return redirect('/dashboard/users')