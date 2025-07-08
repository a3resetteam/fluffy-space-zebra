# Stripe Setup Instructions for MYA3Reset: The Oracle

## 🎯 Seamless Card Collection System

Your Oracle platform now features a **seamless card collection system** that:
- ✅ Collects payment information at signup WITHOUT showing Stripe checkout
- ✅ Stores payment methods securely with Stripe
- ✅ Provides immediate access with a 3-day FREE trial
- ✅ Automatically charges $19.99/month ONLY after the trial ends
- ✅ No upfront charges - truly seamless experience

## 🔧 Setup Instructions

### 1. Get Your Stripe Keys
1. Go to [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Copy your **Publishable key** (starts with `pk_test_`)
3. Copy your **Secret key** (starts with `sk_test_`)

### 2. Create a Product and Price
1. Go to [Stripe Products](https://dashboard.stripe.com/products)
2. Click "Add product"
3. Name: "MYA3Reset: The Oracle - Premium Plan"
4. Description: "Elite transformation platform with AI coaching"
5. Set price: $19.99 USD, recurring monthly
6. Copy the **Price ID** (starts with `price_`)

### 3. Configure Environment Variables
Copy `.env.template` to `.env` and fill in your keys:

```bash
cp .env.template .env
```

Edit `.env` with your actual Stripe keys:
```
STRIPE_PUBLISHABLE_KEY=pk_test_your_actual_key_here
STRIPE_SECRET_KEY=sk_test_your_actual_key_here  
STRIPE_PRICE_ID=price_your_actual_price_id_here
```

### 4. Test the System
1. Restart the Flask app: `python app.py`
2. Go to `/register`
3. Fill out the form with test card: `4242 4242 4242 4242`
4. User gets immediate access with 3-day trial
5. No charge occurs until trial ends

## 🔄 How It Works

### Registration Flow:
1. **Step 1**: User fills form → Creates Stripe customer → Returns setup intent
2. **Step 2**: Frontend creates payment method → Attaches to customer → Completes registration
3. **Result**: User has full access, card is stored, no charge yet

### Trial Management:
- Users get 3 days of full access
- Payment method is stored securely with Stripe
- After 3 days, automatic charge of $19.99/month begins
- Admin endpoint `/process-trial-charges` can manually trigger billing

### Features:
- ✅ **Seamless UX**: No Stripe checkout overlay
- ✅ **Secure**: Uses Stripe's Payment Methods API
- ✅ **Compliant**: PCI-compliant card storage
- ✅ **Flexible**: Easy cancellation and management
- ✅ **Professional**: Chrome/glass theme throughout

## 🛠️ Admin Features

### Manual Billing Processing
```bash
curl -X POST http://localhost:5000/process-trial-charges \
  -H "Cookie: session=your_admin_session"
```

### Monitoring
- Check database for trial statuses
- Monitor Stripe dashboard for payment methods
- View billing history in user profiles

## 🎨 UI Features

The system includes:
- **Modern Design**: Chrome, glass-morphism, and accent colors
- **Responsive**: Works on all devices  
- **Consistent**: All pages match the Oracle theme
- **Intuitive**: Clear trial messaging and billing management
- **Professional**: Emojis and color pops for engagement

## 🔐 Security

- All payment data handled by Stripe (PCI compliant)
- No card numbers stored in your database
- Secure tokenization and payment method storage
- HTTPS required for production

## 🚀 Ready to Launch!

Your Oracle platform now has enterprise-grade payment processing with a seamless user experience. Users can sign up and start their transformation journey immediately!
