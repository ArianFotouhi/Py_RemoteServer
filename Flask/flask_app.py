from flask import Flask, request, jsonify , render_template
from geopy.geocoders import Nominatim
from utils import db_connector
import stripe


#########################stripe config#####################
import configparser
config = configparser.ConfigParser()
config.read('config/setting.ini')
# Access values from the INI file
secret_key = config['KEYS']['SECRET_KEY']
publish_key = config['KEYS']['PUBLISH_KEY']

stripe_keys = {
  'secret_key': secret_key,
  'publishable_key': publish_key
}
stripe.api_key = stripe_keys['secret_key']
###########################################################



app = Flask(__name__)


def get_city_info(city_name):
    geolocator = Nominatim(user_agent="city_info_app")



    try:
        location = geolocator.geocode(city_name)
        if location:
            city_info = {
                "city": city_name.capitalize(),
                "latitude": location.latitude,
                "longitude": location.longitude,
            }
            return city_info
    except Exception as e:
        return {"error": str(e)}

def purchase_lounge(card_num, exp_year, exp_month, cv2, amount, lounge):

    data = stripe.Token.create(
                card={
                    "number": str(card_num),
                    "exp_month": int(exp_month),
                    "exp_year": int(exp_year),
                    "cvc": str(cv2),
                })
    
    card_token = data['id']
    # Create a PaymentIntent with the token
    payment = stripe.Charge.create(
                amount= int(amount),                  # convert amount to cents
                currency='usd',
                description='Example charge',
                source=card_token,
                )

    payment_check = payment['paid']    # return True for successfull payment

    return payment_check



@app.route('/')
def index():
    return jsonify({'data': 'Hi'})


@app.route('/geo/', methods=['POST'])
def lang_lat_return():
    city_name = request.form['city_name']
    city_info = get_city_info(city_name)
    if "error" in city_info:
        return jsonify({"error": "City not found"})
    else:

        db_info = db_connector(fetch=True, name='Joe Elm', email='JE@gmail.com', lounge=city_name)
        city_info['db_info'] = db_info

        return jsonify(city_info)


@app.route('/lounge_reserve/')
def lounge_reserve():
    lounge_param = request.args.get('lounge')
    username_param = request.args.get('username')



    return render_template('index.html', key= stripe_keys['publishable_key'], username= username_param, lounge=lounge_param)

@app.route('/charge', methods=['POST'])
def charge():
    #in cents
    amount = 50

    customer = stripe.Customer.create(
        email='',
        source=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='cad',
        description='payment'
    )

    return render_template('charge.html', amount=amount)


if __name__ == "__main__":
    app.run()
