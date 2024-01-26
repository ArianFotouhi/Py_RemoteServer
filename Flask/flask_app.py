from flask import Flask, request, jsonify , render_template
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



@app.route('/')
def index():
    return jsonify({'data': 'Hi'})



@app.route('/get_link', methods = ['GET', 'POST'])
def get_link():
    # Retrieve data from the request's JSON payload
    data = request.json
    username = data.get('username')
    phone_code = data.get('phone_code')
    phone_number = data.get('phone_number')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
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
            'phone_code': phone_code,
            'phone_number': phone_number,
            'first_name': first_name,
            'last_name': last_name,
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
                    ,
                    "invoice_data": {
                      "account_tax_ids": None,
                      "custom_fields": None,
                      "description": f'Access Purchase for Lounge {item} on {from_date}.',
                      "footer": 'Lounge Atlas powered by IEG',
                    #   "issuer": {},
                      "metadata": {},
                      "rendering_options": None
                    }
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
    #   session_id = session['id']

      invoice = stripe.Invoice.retrieve(session['invoice'])
      invoice_pdf_link = invoice['invoice_pdf']

      data = session['metadata']


      ######confirmation email#####

      customer_name = data['first_name'] + ' ' + data['last_name']
      item_name = data['item']
      amount = float(data['price'])/100
      customer_email = data['username']

      send_invoice_email(customer_name, item_name, amount, customer_email, invoice_pdf_link)
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
