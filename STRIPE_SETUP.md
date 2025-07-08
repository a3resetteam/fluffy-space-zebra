# Stripe API Setup Guide

## Required Stripe Keys

To enable the seamless card collection and payment system, you need to set up your Stripe API keys:

### 1. Get Your Stripe Keys
1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Navigate to "Developers" → "API keys"
3. Copy your keys (use test keys for development)

### 2. Set Environment Variables

You can set these up in multiple ways:

#### Option A: Export in Terminal (Temporary)
```bash
export STRIPE_SECRET_KEY="sk_test_your_actual_secret_key_here"
export STRIPE_PUBLISHABLE_KEY="pk_test_your_actual_publishable_key_here"
export STRIPE_PRICE_ID="price_your_actual_price_id_here"
```

#### Option B: Create .env file (Recommended)
Create a `.env` file in the root directory:
```
STRIPE_SECRET_KEY=sk_test_your_actual_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_actual_publishable_key_here
STRIPE_PRICE_ID=price_your_actual_price_id_here
```

### 3. Create a Product and Price in Stripe

1. In Stripe Dashboard, go to "Products"
2. Click "Add product"
3. Set up a $19.99/month recurring subscription
4. Copy the Price ID and use it for `STRIPE_PRICE_ID`

### 4. Key Format Examples
- Secret Key: `sk_test_51ABC...` (starts with sk_test_ for test mode)
- Publishable Key: `pk_test_51ABC...` (starts with pk_test_ for test mode)
- Price ID: `price_1ABC...` (starts with price_)

### 5. Test Mode vs Live Mode
- **Test Mode**: Use test keys (sk_test_, pk_test_) for development
- **Live Mode**: Use live keys (sk_live_, pk_live_) for production

## How the Payment System Works

### Registration Flow:
1. **User enters card info** → Card details collected via Stripe Elements
2. **No immediate charge** → Payment method saved to customer for future use
3. **3-day free trial starts** → User gets full access immediately
4. **Automatic charge after trial** → Background process charges saved payment method

### Key Features:
- ✅ Seamless card collection (no Stripe checkout popup)
- ✅ No charges during trial period
- ✅ Automatic billing after 3 days
- ✅ Secure payment method storage
- ✅ Easy subscription management

## Testing with Test Cards

Use these test card numbers in development:

| Card Number | Description |
|-------------|-------------|
| 4242424242424242 | Visa - Succeeds |
| 4000000000000002 | Visa - Declined |
| 4000000000009995 | Visa - Insufficient funds |

**Test Details:**
- Any future expiry date (e.g., 12/25)
- Any 3-digit CVC (e.g., 123)
- Any cardholder name

## Important Notes

- **Never commit real API keys to version control**
- **Use test mode for development**
- **Set up webhooks for production** (optional for basic functionality)
- **The system stores payment methods securely via Stripe**

## Troubleshooting

If you see errors like "Invalid API key":
1. Check that your keys are set correctly
2. Ensure you're using the right test/live mode keys
3. Verify the keys haven't been regenerated in Stripe Dashboard

If payments aren't working:
1. Check the STRIPE_PRICE_ID matches your actual product price ID
2. Ensure your Stripe account is activated
3. Verify test cards are being used in test mode
