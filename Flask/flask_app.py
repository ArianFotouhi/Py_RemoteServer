from flask import Flask, request, jsonify , render_template
from geopy.geocoders import Nominatim
from utils import db_connector
import stripe
import json
import os
from confirm_sender import send_invoice_email
#########################stripe config#####################
import configparser
config = configparser.ConfigParser()
config.read('mysite/config/setting.ini')
# Access values from the INI file
secret_key = config['KEYS']['SECRET_KEY']
publish_key = config['KEYS']['PUBLISH_KEY']
endpoint_secret = config['KEYS']['ENDPOINT_KEY']

stripe_keys = {
  'secret_key': secret_key,
  'publishable_key': publish_key
}
stripe.api_key = stripe_keys['secret_key']


###########################################################



app = Flask(__name__)
server_address = 'https://iegapp.pythonanywhere.com'

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


# @app.route('/lounge_reserve/')
# def lounge_reserve():
#     lounge_param = request.args.get('lounge')
#     username_param = request.args.get('username')



#     return render_template('index.html', key= stripe_keys['publishable_key'], username= username_param, lounge= lounge_param)

# @app.route('/charge', methods=['POST'])
# def charge():
#     #in cents
#     amount = 50

#     customer = stripe.Customer.create(
#         email='',
#         source=request.form['stripeToken']
#     )

#     charge = stripe.Charge.create(
#         customer=customer.id,
#         amount=amount,
#         currency='cad',
#         description='payment'
#     )

#     return render_template('charge.html', amount=amount)


@app.route('/get_link', methods = ['GET', 'POST'])
def get_link():
    # Retrieve data from the request's JSON payload
    data = request.json
    username = data.get('username')
    lounge_id = data.get('lounge_id')
    from_date = data.get('from_date')
    to_date = data.get('to_date')
    price = data.get('price')
    item = data.get('item')
    currency = data.get('currency')

    prod_id = stripe.Product.create(name=item)
    price_id = stripe.Price.create(
        currency=currency,
        unit_amount=price,
        product=prod_id["id"],
    )

    metadata = {
            'username': username,
            'lounge_id': lounge_id,
            'from_date': from_date,
            'to_date': to_date,
            'price': price,
            'item': item,
            'currency': currency,
    }
    success_url = f"{server_address}/payment_success"
    cancel_url = f'{server_address}/payment_fail'

    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price": price_id["id"],
                "quantity": 1,
            }
        ],
        metadata=metadata,
        automatic_tax={"enabled": True},
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,

        customer_email = username,
        invoice_creation= {
                    "enabled": True
                    #,
                    #"invoice_data": {
                    #   "account_tax_ids": None,
                    #   "custom_fields": None,
                    #   "description": f'Access Purchase for Lounge {item} on {from_date}.',
                    #   "footer": 'Lounge Atlas powered by IEG',
                    #   "issuer": 'IEG America',
                    #   "metadata": {},
                    #   "rendering_options": None
                    # }
                  }
    )

    redirect_url = session.url
    return jsonify({'data': redirect_url})





@app.route('/payment_success', methods = ['GET', 'POST'])
def payment_success():

    username = request.args.get('username')
    lounge_id = request.args.get('lounge_id')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    item = request.args.get('item')
    price = request.args.get('price')


    return render_template('pay_success.html', username=username, lounge_id=lounge_id, from_date=from_date, to_date=to_date)



@app.route('/payment_fail', methods = ['GET', 'POST'])
def payment_fail():

    username = request.args.get('username')
    lounge_id = request.args.get('lounge_id')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')


    return render_template('pay_fail.html')




@app.route('/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.data

    sig_header = request.headers['STRIPE_SIGNATURE']



    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    # Handle the event
    if event['type'] == 'checkout.session.async_payment_failed':
      session = event['data']['object']


    elif event['type'] == 'checkout.session.async_payment_succeeded':
      session = event['data']['object']
      data = session['metadata']
      with open('example.txt','w') as file:

          file.write(str(data))

    elif event['type'] == 'checkout.session.completed':
      session = event['data']['object']
      data = session['metadata']
      
      ######confirmation email#####

      customer_name = "Jack Morales"
      item_name = data['item']
      amount = data['price']/100
      customer_email = data['username']
      send_invoice_email(customer_name, item_name, amount, customer_email)
      ############################

      with open('example.txt','w') as file:

        file.write(str(data))

    elif event['type'] == 'checkout.session.expired':
      session = event['data']['object']
    # ... handle other event types
    else:
      print('Unhandled event type {}'.format(event['type']))

    return jsonify(success=True)



if __name__ == "__main__":
    app.run()
