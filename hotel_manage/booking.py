from datetime import datetime
import time
class Booking:

    tableName = 'PalaceGardenBooking'
    
    # Initialize the variables
    def __init__(self, tableName):
        self.tableName = tableName
    
    # Generate unique booking id by current timestamp
    def generate_bookingId(self):
        timestamp = time.time()
        return "BN-" + str(timestamp)

    # Add new booking
    def create_booking(self, db, new_booking):
        try:
            # Get the current timestamp
            current_timestamp = datetime.now()
            # For example, converting it to ISO 8601 format can be useful.
            timestamp_str = current_timestamp.isoformat()  # Result: '2023-07-04T14:30:00.123456'
            
            # Use put_item() Method to Create the new_booking
            table_name = self.tableName
            response = db.put_item(
                TableName=table_name,
                Item={
                        "bookingId":{'S': new_booking['bookingId']},
                        "room_no": {'S': new_booking['room_no']}, 
                        "roomType": {'S': new_booking['roomType']},
                        "guestName": {'S': new_booking['guestName']},
                        "guestEmail": {'S': new_booking['guestEmail']},
                        "guestPhone": {'S': new_booking['guestPhone']},
                        "checkInDate": {'S': new_booking['checkInDate']},
                        "checkOutDate": {'S': new_booking['checkOutDate']},
                        "totalGuests": {'S': new_booking['totalGuests']},
                        "paymentStatus": {'S':new_booking['paymentStatus']},
                        "paymentAmount": {'S': new_booking['paymentAmount']},
                        'created_at': {'S': timestamp_str}
                }
            )
        
            # Check if the user was successfully created
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return {
                        "statusCode": 201,
                        "message": "New Booking added successfully!",
                    }
            else:
                return {
                        "statusCode": response['ResponseMetadata']['HTTPStatusCode'],
                        "message": "Booking not added!",
                    }
        except Exception as error:
            return {
                "statusCode": 500,
                "message": f"Something went wrong: {error}"
            }

    # Delete booking on based on booking ID
    def delete_booking(self, db, bookingId):
        try:    
            # Use delete_item() Method to Update the Booking
            table_name = self.tableName
            
            response = db.delete_item(
                TableName = table_name,
                Key={'bookingId': {'S': bookingId}},
            )

            # Check if the booking was successfully deleted
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return {
                        "statusCode": response['ResponseMetadata']['HTTPStatusCode'],
                        "message": "Booking deleted successfully!",
                    }
            else:
                return {
                        "statusCode": response['ResponseMetadata']['HTTPStatusCode'],
                        "message": "booking not deleted!",
                    }
        except Exception as error:
            return {
                    "statusCode": 500,
                    "message": f"Something went wrong: {error}"
                }
    
    # Update booking details
    def update_booking(self, db, updated_booking):
        try:
            # Get the current timestamp
            current_timestamp = datetime.now()
            # For example, converting it to ISO 8601 format can be useful.
            timestamp_str = current_timestamp.isoformat()  # Result: '2023-07-04T14:30:00.123456'
            
            # Use update_item() Method to Update the booking
            table_name = self.tableName
        
            updated_booking['updated_at'] = timestamp_str
            bookingId = updated_booking['bookingId']

            # Exclude the "bookingId" key from the updated_booking dictionary
            updated_booking = {k: v for k, v in updated_booking.items() if k != 'bookingId'}
            
            update_expression = 'SET ' + ', '.join([f'{k} = :{k}' for k in updated_booking])
            expression_attribute_values = {f':{k}': {'S': v} for k, v in updated_booking.items()}

            response = db.update_item(
                TableName=table_name,
                Key={
                    'bookingId': {'S':bookingId}
                },
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )
            #   Check the response to verify if the user was successfully updated
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return {
                    "statusCode": response['ResponseMetadata']['HTTPStatusCode'],
                    "message": "Booking updated successfully!"
                }
            else:
                return {
                    "statusCode": response['ResponseMetadata']['HTTPStatusCode'],
                    "message": "Failed to update booking!"
                }
        except Exception as error:
                return {
                    "statusCode": 500,
                    "message": f"Something went wrong: {error}"
                }
    
    # Get perticular booking details on based on booking ID
    def get_booking(self, db, bookingId):
        try:
            # Get user details from Dynamodb
            response = db.get_item(
                TableName=self.tableName,
                Key={
                    'bookingId': {'S': bookingId}
                }
            )

            booking = response.get('Item')

            if booking:
                # The booking was found in DynamoDB
                return {
                    "statusCode": 200,
                    "message": "Booking found!",
                    "data": booking
                }
            else:
                # The booking was not found in DynamoDB
                return {
                    "statusCode": 404,
                    "message": "Booking not found!",
                    "data": None
                }
        except Exception as e:
            return {
                    "statusCode": 500,
                    "message": f"Something went wrong: {e}",
                    "data": None
                }

    # Get all bookings
    def get_all_booking(self, db):
        # Perform the scan operation to get all items from the table
        response = db.scan(TableName=self.tableName)

        # Check if the scan operation was successful
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            # Access the items retrieved from the table
            items = response.items()
       
            booking = {k:v for k, v in items}
            #   Check the response to verify if the user was successfully updated
            if booking['ResponseMetadata']['HTTPStatusCode'] == 200:
                return {
                    "statusCode": booking['ResponseMetadata']['HTTPStatusCode'],
                    "message": "All booking retrieved!",
                    "data": booking
                }
            else:
                return {
                    "statusCode": booking['ResponseMetadata']['HTTPStatusCode'],
                    "message": "Failed to retrieve booking!"
                }
        else:
            return {
                "statusCode": booking['ResponseMetadata']['HTTPStatusCode'],
                "message": "Failed to retrieve booking!"
            }