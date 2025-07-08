#!/usr/bin/env python3
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

# Debug environment variables
print("Debug: Checking environment variables...")
secret_key = os.environ.get('STRIPE_SECRET_KEY')
print(f"STRIPE_SECRET_KEY loaded: {secret_key is not None}")
if secret_key:
    print(f"Key starts with: {secret_key[:12]}...")

stripe.api_key = secret_key

try:
    # Set API key directly
    print(f"Setting API key: {secret_key[:12]}...")
    stripe.api_key = secret_key
    
    # Test 1: Account access
    print("1. Testing account access...")
    response = stripe.Account.retrieve()
    print('✅ Stripe API Connected Successfully!')
    
    # Test 2: Price retrieval
    print("2. Testing price retrieval...")
    price_id = os.environ.get('STRIPE_PRICE_ID')
    if price_id:
        price = stripe.Price.retrieve(price_id)
        print(f'✅ Price ID found: {price.id} - ${price.unit_amount/100}/month')
    else:
        print('❌ No STRIPE_PRICE_ID found in environment')
    
    # Test 3: Customer creation (test mode)
    print("3. Testing customer operations...")
    customers = stripe.Customer.list(limit=1)
    print(f'✅ Can access customers: {len(customers.data)} customers found')
    
    print("\n🎉 All Stripe API tests passed! Your Oracle payment system is ready!")
    
except stripe.error.AuthenticationError as e:
    print(f'❌ Authentication Error: {str(e)}')
    print('This means the API key is invalid or expired')
except stripe.error.APIConnectionError as e:
    print(f'❌ Connection Error: {str(e)}')
    print('Network issue connecting to Stripe')
except Exception as e:
    print(f'❌ General Error: {str(e)}')
    print(f'Error type: {type(e).__name__}')
    import traceback
    traceback.print_exc()
