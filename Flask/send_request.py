import requests


# url = 'http://127.0.0.1:8000/geo/'
# url= 'https://iegapp.pythonanywhere.com/geo/'
url = 'http://127.0.0.1:5000/purchase/'

payload = {
    "card_num":"4242424242424242",
    "exp_year":"24",
    "exp_month":"07",
    "cv2":"111" ,
    "lounge":"333",
    "amount": 100
}

response = requests.post(url, data=payload)
# response = requests.get(url)

print(response.json())
