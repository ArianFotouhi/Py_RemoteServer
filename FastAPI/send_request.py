import requests


url = 'http://127.0.0.1:8000/geo/'


payload_city = {
    "city_name" : "Boston",
}
response = requests.post(url, params={ "city_name" : "Boston",})
print(response.json())
