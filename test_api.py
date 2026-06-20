import requests

url = "http://127.0.0.1:8000/api/v1/auth/register"
payload = {
  "username": "admin_test",
  "role": "Admin",
  "password": "my_secure_password123"
}
headers = {
  "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload)
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)
except Exception as e:
    print("Error:", e)
