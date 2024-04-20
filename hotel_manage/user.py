from datetime import datetime
class User:
    tableName = 'PalaceGardenLogin'
    
    # Initialize the variables
    def __init__(self, tableName):
        self.tableName = tableName

    # Add new room
    def create_user(self, db, user):
        try:
            # Get the current timestamp
            current_timestamp = datetime.now()
            # For example, converting it to ISO 8601 format can be useful.
            timestamp_str = current_timestamp.isoformat()  # Result: '2023-07-04T14:30:00.123456'
            
            # Use put_item() Method to Create the user
            table_name = self.tableName
            response = db.put_item(
                TableName=table_name,
                Item={
                    'username': {'S': user['username']},
                    'fullName': {'S': user['fullName']},
                    'email': {'S': user['email']},
                    'phone': {'S': user['phone']},
                    'password': {'S': user['password']},
                    'created_at': {'S': timestamp_str}
                }
            )
          
            # Check if the user was successfully created
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return {
                        "statusCode": 201,
                        "message": "User created successfully!",
                    }
            else:
                return {
                        "statusCode": response['ResponseMetadata']['HTTPStatusCode'],
                        "message": "User not created!",
                    }
        except Exception as error:
                return {
                    "statusCode": 500,
                    "message": f"Something went wrong: {error}"
                }
          
    # Delete User on based on username
    def delete_user(self, db, username):
        try:    
            # Use delete_item() Method to Update the user
            table_name = self.tableName
            
            response = db.delete_item(
                TableName = table_name,
                Key={'username': {'S': username}},
            )

            # Check if the user was successfully deleted
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return {
                        "statusCode": response['ResponseMetadata']['HTTPStatusCode'],
                        "message": "User deleted successfully!",
                    }
            else:
                return {
                        "statusCode": response['ResponseMetadata']['HTTPStatusCode'],
                        "message": "User not deleted!",
                    }
        except Exception as error:
            return {
                    "statusCode": 500,
                    "message": f"Something went wrong: {error}"
                }
    
    # Update User details
    def update_user(self, db, updated_user):
        try:
            # Get the current timestamp
            current_timestamp = datetime.now()
            # For example, converting it to ISO 8601 format can be useful.
            timestamp_str = current_timestamp.isoformat()  # Result: '2023-07-04T14:30:00.123456'
            
            # Use update_item() Method to Update the user
            table_name = self.tableName
        
            updated_user['updated_at'] = timestamp_str
            username = updated_user['username']

            # Step 4: Exclude the "username" key from the updated_user dictionary
            updated_user = {k: v for k, v in updated_user.items() if k != 'username'}
            
            update_expression = 'SET ' + ', '.join([f'{k} = :{k}' for k in updated_user])
            expression_attribute_values = {f':{k}': {'S': v} for k, v in updated_user.items()}

            response = db.update_item(
                TableName=table_name,
                Key={
                    'username': {'S':username}
                },
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )
            #   Check the response to verify if the user was successfully updated
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                print('User updated successfully!')
                return {
                    "statusCode": response['ResponseMetadata']['HTTPStatusCode'],
                    "message": "User updated successfully!"
                }
            else:
                print('Failed to update user!')
                return {
                    "statusCode": response['ResponseMetadata']['HTTPStatusCode'],
                    "message": "Failed to update user!"
                }
        except Exception as error:
                return {
                    "statusCode": 500,
                    "message": f"Something went wrong: {error}"
                }

    # Get perticular User details on based on username
    def get_user(self, db, username):

        try:
            # Get user details from Dynamodb
            response = db.get_item(
                TableName=self.tableName,
                Key={
                    'username': {'S': username}
                }
            )

            user = response.get('Item')

            if user:
                # The user was found in DynamoDB
                return {
                    "statusCode": 200,
                    "message": "User found!",
                    "data": user
                }
            else:
                # The user was not found in DynamoDB
                return {
                    "statusCode": 404,
                    "message": "User not found!",
                    "data": None
                }
        except Exception as e:
            return {
                    "statusCode": 500,
                    "message": f"Something went wrong: {e}",
                    "data": None
                }
    
    # Get all Users
    def get_all_user(self, db):

        # Perform the scan operation to get all items from the table
        response = db.scan(TableName=self.tableName)

        # Check if the scan operation was successful
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            # Access the items retrieved from the table
            items = response.items()
        
            users = {k:v for k, v in items}
            if users['ResponseMetadata']['HTTPStatusCode'] == 200:
                return {
                    "statusCode": users['ResponseMetadata']['HTTPStatusCode'],
                    "message": "All users retrieved!",
                    "data": users
                }
            else:
                return {
                    "statusCode": users['ResponseMetadata']['HTTPStatusCode'],
                    "message": "Failed to retrieve users!"
                }
        else:
            return {
                "statusCode": response['ResponseMetadata']['HTTPStatusCode'],
                "message": "Failed to retrieve users!"
            }