# Hotel Booking System

A premium, production-ready Django web application for search, booking, and management of hotel reservations, featuring customer booking flows, vendor dash panels, and automated payment processing with Razorpay integration.

---

## Features

### For Customers:
* **Interactive Search**: Browse hotels by location, pricing, and availability.
* **Detail Views**: Check room options, descriptions, and premium amenities (WiFi, Pool, AC, etc.).
* **Wishlist**: Add favorite hotels to a personal wishlist for quick booking later.
* **OTP Verification**: Secure login and sign-up using dynamic OTP verification codes.
* **Payment Gateway Integration**: Secure checkouts and instant booking verification powered by **Razorpay**.
* **Booking History**: Keep track of upcoming and completed stays directly from the user profile.

### For Hotel Owners (Vendors):
* **Vendor Dashboard**: Complete business analytics showing active listings, reservations, and earnings.
* **Listing Manager**: Create, edit, or delete hotel listings.
* **Image Uploads**: Upload high-quality hotel images directly to the server.
* **Reservation Tracker**: View active bookings and track guest stays.

---

## Technology Stack

* **Backend**: Django 6.0 (Python)
* **Frontend**: HTML5, Vanilla CSS, JavaScript
* **Database**: PostgreSQL (Production) / SQLite (Local fallback option)
* **Production Server**: Gunicorn
* **Static Assets**: WhiteNoise (compresses and serves assets in production)
* **Payments**: Razorpay API
* **Environment Configuration**: Python-Decouple, Python-Dotenv

---

## Local Setup Instructions

Follow these steps to run the application locally on your computer:

### 1. Clone the Repository
```bash
git clone https://github.com/Lokesh8039/Hotel_Booking_system.git
cd Hotel_Booking_system
```

### 2. Create and Activate a Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate it (Mac/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory based on the `.env.example` template:
```env
SECRET_KEY='your-local-development-secret-key'
DEBUG=True

# Database Configuration (leave empty to fall back to default local postgres parameters)
# DATABASE_URL=

# Local Postgres Parameters
NAME='oyo_clone'
USER='postgres'
PASSWORD='your-local-postgres-password'
HOST='localhost'
PORT='5432'

# Email settings for OTP/Alerts
EMAIL_HOST_USER='your-email@gmail.com'
EMAIL_HOST_PASSWORD='your-gmail-app-password'

# Razorpay credentials
RAZORPAY_KEY_ID='your-razorpay-key-id'
RAZORPAY_KEY_SECRET='your-razorpay-key-secret'
```

### 5. Run Database Migrations
```bash
python manage.py migrate
```

### 6. Start the Development Server
```bash
python manage.py runserver
```
Visit the local website at `http://127.0.0.1:8000/`.

---

## Deploying on Render (Free Tier)

This application is pre-configured for seamless production hosting on **Render** (for the web app) and **Neon.tech** (for a permanent free PostgreSQL database).

### Step 1: Connect your GitHub Account
1. Push your local Git repository to GitHub.
2. Register/Log in on [Render](https://render.com/).

### Step 2: Create a Web Service
1. Click **New +** and select **Web Service**.
2. Select your GitHub repository.
3. Configure the following service settings:
   - **Name**: `hotel-booking-system`
   - **Runtime**: `Python`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn hotel_booking_system.wsgi:application`
   - **Instance Type**: **Free**

### Step 3: Configure Render Environment Variables
Add the following key-value pairs under the **Environment** tab in Render:

| Key | Value | Description |
| :--- | :--- | :--- |
| `SECRET_KEY` | *A secure random secret key* | Used for cryptographic signing in production |
| `DEBUG` | `False` | Disables debug mode for performance and safety |
| `DATABASE_URL` | *Your Postgres Connection String* | Obtained from Neon.tech / Render DB |
| `EMAIL_HOST_USER` | *Your Gmail Address* | For automated communications |
| `EMAIL_HOST_PASSWORD` | *Your Gmail App Password* | Generated from Google security portal |
| `RAZORPAY_KEY_ID` | *Your Razorpay Key ID* | Payment gateway identification token |
| `RAZORPAY_KEY_SECRET` | *Your Razorpay Key Secret* | Payment gateway verification token |

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
