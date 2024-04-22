from datetime import datetime
# Use to convert the string ("['a', 'b']") to list
import ast
class Room:
    tableName = 'PalaceGardenRooms'
    bucketName = 'x22245855uploadimage'
    
    # Initialize the variables
    def __init__(self, tableName, bucketName):
        self.tableName = tableName
        self.bucketName = bucketName

    # This function upload the room images to S3 bucket
    def upload_image_s3(self, request, s3):
        try:
        
            # Check if the POST request has a file part
            if 'image' not in request.files:
                return  {
                    "statusCode": 400,
                    "message": "No selected image",
                }

            file = request.files['image']
            # Check if the file is selected
            if file.filename == '':
                return  {
                    "statusCode": 400,
                    "message": "No selected image",
                }

            # Upload the file to S3
            s3.upload_fileobj(file, 'x22245855uploadimage', file.filename, ExtraArgs={'ACL': 'public-read'})

            # Get the public URL of the uploaded file
            public_url = f"https://{'x22245855uploadimage'}.s3.amazonaws.com/{file.filename}"
            return {
                "statusCode": 200,
                "message": "File uploaded successfully!",
                "image_url": public_url
            }
        except Exception as error:
            return {
                "statusCode": 400,
                "message":error,
                "image_url": None
            }

    # Add new room
    def create_room(self, db, new_room):
        try:
            # Get the current timestamp
            current_timestamp = datetime.now()
            # For example, converting it to ISO 8601 format can be useful.
            timestamp_str = current_timestamp.isoformat()  # Result: '2023-07-04T14:30:00.123456'
            # convert list to string
            amenities = str(new_room["amenities"])    
            
            # Use ast.literal_eval to convert the string to a Python list
            amenities_list = ast.literal_eval(amenities)
            for a in amenities_list:
                print(a)
            # Use put_item() Method to Create the room
            table_name = self.tableName
            response = db.put_item(
                TableName=table_name,
                Item={
                        "room_no": {'S': new_room["room_no"]},
                        "room_type": {'S': new_room["room_type"]},
                        "description":{'S': new_room["description"]},
                        "no_of_bed": {'S': new_room["no_of_bed"]},
                        "price": {'S': new_room["price"]},
                        "availability": {'S': new_room["availability"]},
                        "amenities": {'S': amenities},
                        "image_url": {'S': new_room['image_url']},
                        'created_at': {'S': timestamp_str}
                }
            )    
            # Check if the user was successfully created
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return {
                        "statusCode": 201,
                        "message": "Room added successfully!",
                    }
            else:
                return {
                        "statusCode": response['ResponseMetadata']['HTTPStatusCode'],
                        "message": "Room not added!",
                    }
        except Exception as error:
            return {
                "statusCode": 500,
                "message": f"Something went wrong: {error}"
            }
    
    # Delete Room on based on Room No
    def delete_room(self, db, room_no):
        try:    
            # Use delete_item() Method to Update the room
            table_name = self.tableName
            
            response = db.delete_item(
                TableName = table_name,
                Key={'room_no': {'S': room_no}},
            )

            # Check if the room was successfully deleted
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return {
                        "statusCode": response['ResponseMetadata']['HTTPStatusCode'],
                        "message": "Room deleted successfully!",
                    }
            else:
                return {
                        "statusCode": response['ResponseMetadata']['HTTPStatusCode'],
                        "message": "Room not deleted!",
                    }
        except Exception as error:
            return {
                    "statusCode": 500,
                    "message": f"Something went wrong: {error}"
                }
    
    # Update Room details
    def update_room(self, db, updated_room):
        try:
            # Get the current timestamp
            current_timestamp = datetime.now()
            # For example, converting it to ISO 8601 format can be useful.
            timestamp_str = current_timestamp.isoformat()  # Result: '2023-07-04T14:30:00.123456'
            
            # Use update_item() Method to Update the room
            table_name = self.tableName
        
            updated_room['updated_at'] = timestamp_str
            username = updated_room['room_no']

            # Exclude the "room_no" key from the updated_room dictionary
            updated_room = {k: v for k, v in updated_room.items() if k != 'room_no'}
            
            update_expression = 'SET ' + ', '.join([f'{k} = :{k}' for k in updated_room])
            expression_attribute_values = {f':{k}': {'S': v} for k, v in updated_room.items()}

            response = db.update_item(
                TableName=table_name,
                Key={
                    'room_no': {'S':username}
                },
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )
            #   Check the response to verify if the user was successfully updated
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return {
                    "statusCode": response['ResponseMetadata']['HTTPStatusCode'],
                    "message": "Room updated successfully!"
                }
            else:
                return {
                    "statusCode": response['ResponseMetadata']['HTTPStatusCode'],
                    "message": "Failed to update room!"
                }
        except Exception as error:
                return {
                    "statusCode": 500,
                    "message": f"Something went wrong: {error}"
                }
    
    # Get perticular Room details on based on Room ID
    def get_room(self, db, room_no):
        try:
            # Get user details from Dynamodb
            response = db.get_item(
                TableName=self.tableName,
                Key={
                    'room_no': {'S': room_no}
                }
            )

            room = response.get('Item')
            if room:
                # The room was found in DynamoDB
                return {
                    "statusCode": 200,
                    "message": "Room found!",
                    "data": room
                }
            else:
                # The room was not found in DynamoDB
                return {
                    "statusCode": 404,
                    "message": "Room not found!",
                    "data": None
                }
        except Exception as e:
            return {
                    "statusCode": 500,
                    "message": f"Something went wrong: {e}",
                    "data": None
                }

    # Get all Rooms
    def get_all_room(self, db):

        # Perform the scan operation to get all items from the table
        response = db.scan(TableName=self.tableName)

        # Check if the scan operation was successful
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            # Access the items retrieved from the table
            items = response.items()
        
            rooms = {k:v for k, v in items}
            if rooms['ResponseMetadata']['HTTPStatusCode'] == 200:
                return {
                    "statusCode": rooms['ResponseMetadata']['HTTPStatusCode'],
                    "message": "All rooms retrieved!",
                    "data": rooms
                }
            else:
                return {
                    "statusCode": rooms['ResponseMetadata']['HTTPStatusCode'],
                    "message": "Failed to retrieve rooms!"
                }
        else:
            return {
                "statusCode": rooms['ResponseMetadata']['HTTPStatusCode'],
                "message": "Failed to retrieve rooms!"
            }