import requests

API_URL = 'http://localhost:5000/api/user'  # Adjust the URL if necessary

user_data = {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "contact": "1234567890",
    "address1": "123 Main St",
    "address2": "Apt 4B",
    "User": "user"  # Adjust the role as needed
}

response = requests.post(API_URL, json=user_data)
print(response.json())  # Print the response from the server
