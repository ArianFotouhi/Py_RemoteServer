import requests


# url = 'http://127.0.0.1:8000/geo/'
url= 'https://iegapp.pythonanywhere.com/geo/'

payload_city = {
    "city_name" : "Manchester",
}
response = requests.post(url, data={"city_name": payload_city['city_name']})
# response = requests.get(url)

print(response.json())
