import stripe
stripe.api_key = "sk_test_51NvMVHBvm3XTcAsU3BjobBAa74TwYeO7GivG7ewBYtGGxBRLvdH8TNfL70WioSIPQbMi67oX1mV1hV3mvx32MULj00yXHYKib0"

stripe.Token.create(
  card={
    "number": "4242424242424242",
    "exp_month": 10,
    "exp_year": 2024,
    "cvc": "314",
  },
)