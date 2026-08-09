import logging
import requests
import time
import random
import uuid
from flask import session
from flask_login import logout_user, current_user
import razorpay
from flask import send_file
import random
import subprocess
import smtplib
import secrets
import resend
from email.mime.text import MIMEText
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, session, url_for, flash
import os
from datetime import datetime,date
import pandas as pd
from openpyxl import Workbook
from flask import send_file
import io
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from flask import jsonify
from push_notification import send_push_notification
from datetime import datetime, timedelta, date
from sqlalchemy import case
from flask_mail import Mail, Message
from flask import render_template
from weasyprint import HTML, CSS
from io import BytesIO
from functools import wraps

IST = ZoneInfo("Asia/Kolkata")

def india_time():
    return datetime.now(IST)

import os
from werkzeug.utils import secure_filename
from sqlalchemy import func
from math import ceil
import re

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

from datetime import timedelta
import secrets

app = Flask(__name__)

def admin_required(f):
    @login_required
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return "Access Denied", 403
        return f(*args, **kwargs)

    return decorated_function

PRODUCT_UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "uploads",
    "products"
)

os.makedirs(
    PRODUCT_UPLOAD_FOLDER,
    exist_ok=True
)

app.config["MAIL_SERVER"] = "smtp.hostinger.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USE_TLS"] = False

app.config["MAIL_USERNAME"] = "info@recrootearn.com"
app.config["MAIL_PASSWORD"] = "Manojcycle@95"

app.config["MAIL_DEFAULT_SENDER"] = (
    "RecrootEarn",
    "info@recrootearn.com"
)

mail = Mail(app)

# ==========================
# MSG91 OTP CONFIGURATION
# ==========================

MSG91_AUTH_KEY = "546033ACbxg22rJeDi6a53304fP1"

MSG91_TEMPLATE_ID = "6a586d4c8aa5f75205015ec2"

MSG91_SENDER_ID = "RCRTRN"

OTP_EXPIRY = 600

app.secret_key = "7sf7rth515t4h8ljyyj151577rgnmd62vlkg81bmej96cnsv365fvvdsebn"

app.permanent_session_lifetime = timedelta(days=365)

app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=365)
app.config["REMEMBER_COOKIE_SECURE"] = True
app.config["REMEMBER_COOKIE_HTTPONLY"] = True
app.config["REMEMBER_COOKIE_SAMESITE"] = "Lax"
app.config["REMEMBER_COOKIE_REFRESH_EACH_REQUEST"] = True

app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

resend.api_key = "re_QT3qQPqz_Ngn6WAnA4A2ykKbH9CZEs6Fz"

RAZORPAY_KEY = "rzp_live_SukwF35NxDKD1h"
RAZORPAY_SECRET = "ctp74whaDCaF5omzFqoEg6Ya"

client = razorpay.Client(
    auth=(RAZORPAY_KEY, RAZORPAY_SECRET)
)

def generate_referral_code():

    while True:
        code = "RR" + str(random.randint(100000, 999999))

        if not User.query.filter_by(referral_code=code).first():
            return code

def generate_candidate_referral_code():

    while True:
        code = "RC" + str(random.randint(100000, 999999))

        if not CandidateUser.query.filter_by(
            candidate_referral_code=code
        ).first():
            return code

def save_image(file, folder):
    if not file or not file.filename:
        return None

    upload_folder = os.path.join(
        app.config["UPLOAD_FOLDER"],
        folder
    )

    os.makedirs(upload_folder, exist_ok=True)

    filename = (
        str(uuid.uuid4())
        + "_"
        + secure_filename(file.filename)
    )

    filepath = os.path.join(
        upload_folder,
        filename
    )

    file.save(filepath)

    return filename

# =========================
# CONFIG & DB SETUP
# =========================
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://recrootearn:Kymore%4095@localhost/recrootearn'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
VIDEO_EXTENSIONS = {
    "mp4",
    "mov",
    "webm",
    "mkv"
}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

db = SQLAlchemy(app)

# =========================
# MODELS
# =========================
class User(UserMixin, db.Model):
    __table_args__ = {'sqlite_autoincrement': True}

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    mobile = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(120))
    company = db.Column(db.String(200))
    hr_type = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(300))
    profile_photo = db.Column(db.String(300))
    credits = db.Column(db.Integer, default=0)
    paid_credits = db.Column(db.Integer, default=0)
    wallet_balance = db.Column(db.Float, default=0)
    upi_id = db.Column(db.String(200))
    bank_name = db.Column(db.String(200))
    account_number = db.Column(db.String(200))
    ifsc_code = db.Column(db.String(100))
    session_token = db.Column(db.String(200))
    fcm_token = db.Column(db.Text)
    company_house = db.Column(db.String(200))
    company_road = db.Column(db.String(200))
    company_area = db.Column(db.String(200))
    company_state = db.Column(db.String(100))
    company_pincode = db.Column(db.String(20))
    company_country = db.Column(db.String(100), default="India")
    app_token = db.Column(db.String(128), unique=True, nullable=True)
    last_streak_reset = db.Column(db.Date, nullable=True)
    welcome_email_sent = db.Column(db.Boolean, default=False)

    is_shop_promoted = db.Column(
        db.Boolean,
        default=False
    )

    is_verified_seller = db.Column(
        db.Boolean,
        default=False
    )

    is_shop_active = db.Column(
        db.Boolean,
        default=True
    )

    verification_status = db.Column(
        db.String(30),
        default="Pending"
    )

    verification_date = db.Column(
        db.DateTime
    )

    verification_remarks = db.Column(
        db.Text
    )

    shop_promotion_expires_at = db.Column(
        db.DateTime
    )

    shop_promotion_priority = db.Column(
        db.Integer,
        default=0
    )

    boost_posts = db.relationship(
        "BoostPost",
        backref="hr",
        lazy=True
    )

    seller_coupons = db.relationship(
        "Coupon",
        foreign_keys="Coupon.seller_id",
        lazy=True
    )

    wishlist = db.relationship(
        "Wishlist",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    account_holder_name = db.Column(db.String(200))
    trust_score = db.Column(db.Integer, default=100)
    is_admin = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    failed_logins = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime)

    is_deleted = db.Column(
        db.Boolean,
        default=False
    )

    referral_code = db.Column(
        db.String(20),
        unique=True
    )

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

    daily_referral_rewards = db.Column(
        db.Integer,
        default=0
    )

    last_referral_reward_date = db.Column(
        db.Date
    )

    about_company = db.Column(db.Text)

    product_reviews = db.relationship(
        "ProductReview",
        foreign_keys="ProductReview.customer_id",
        backref="customer",
        lazy=True
    )

    company_logo = db.Column(
        db.String(300)
    )

    company_city = db.Column(
        db.String(100)
    )

    company_website = db.Column(
        db.String(300)
    )

    company_photos = db.Column(
        db.Text
    )

    company_city = db.Column(
        db.String(100)
    )

    full_company_address = db.Column(
        db.Text
    )

    company_website = db.Column(
        db.String(200)
    )

    referred_by = db.Column(
        db.String(20)
    )

    total_referrals = db.Column(
        db.Integer,
        default=0
    )

    msme_certificate = db.Column(
        db.String(255)
    )

    gumasta_certificate = db.Column(
        db.String(255)
    )

    successful_referrals = db.Column(
        db.Integer,
        default=0
    )

    referral_earnings = db.Column(
        db.Float,
        default=0
    )

    pending_marketplace_balance = db.Column(
        db.Float,
        default=0
    )

    marketplace_earnings = db.Column(
        db.Float,
        default=0
    )

    marketplace_withdrawn = db.Column(
        db.Float,
        default=0
    )

    shipping_addresses = db.relationship(
        "ShippingAddress",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    products = db.relationship(
        "Product",
        backref="seller",
        lazy=True,
        cascade="all, delete-orphan"
    )

    profile_completion = db.Column(
        db.Integer,
        default=0
    )

    last_profile_reminder = db.Column(
        db.DateTime
    )

    profile_reminders_today = db.Column(
        db.Integer,
        default=0
    )

    pickup_address = db.relationship(
        "SellerPickupAddress",
        backref="seller",
        uselist=False,
        cascade="all, delete-orphan"
    )

    referral_purchase_reward_given = db.Column(
        db.Boolean,
        default=False
    )

class SellerVerification(db.Model):

    __tablename__ = "seller_verification"

    id = db.Column(db.Integer, primary_key=True)

    seller_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    gst_number = db.Column(db.String(30))

    pan_number = db.Column(db.String(20))

    aadhaar_number = db.Column(db.String(20))

    business_name = db.Column(db.String(200))

    gst_certificate = db.Column(db.String(255))

    pan_image = db.Column(db.String(255))

    aadhaar_front = db.Column(db.String(255))

    aadhaar_back = db.Column(db.String(255))

    status = db.Column(
        db.String(20),
        default="Pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class ShopFollower(db.Model):
    __tablename__ = "shop_followers"

    id = db.Column(db.Integer, primary_key=True)

    seller_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    follower_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

    __table_args__ = (
        db.UniqueConstraint(
            "seller_id",
            "follower_id",
            name="unique_shop_follow"
        ),
    )

class CandidateUser(UserMixin, db.Model):

    __table_args__ = {'sqlite_autoincrement': True}

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(150))

    mobile = db.Column(db.String(20), unique=True)

    email = db.Column(db.String(150), unique=True)

    username = db.Column(db.String(100), unique=True)

    password = db.Column(db.String(300))

    dob = db.Column(db.Date)

    qualification = db.Column(db.String(100))

    city = db.Column(db.String(100))

    experience = db.Column(db.String(100))

    current_company = db.Column(db.String(200))

    current_ctc = db.Column(db.String(50))

    expected_ctc = db.Column(db.String(50))

    profile_photo = db.Column(db.String(300))

    resume_file = db.Column(db.String(300))

    designation = db.Column(db.String(200))

    skills = db.Column(db.Text)

    about_me = db.Column(db.Text)

    resume_file = db.Column(db.String(255))

    is_deleted = db.Column(db.Boolean, default=False)

    session_token = db.Column(db.String(200))

    fcm_token = db.Column(db.Text)

    welcome_email_sent = db.Column(db.Boolean, default=False)

    career_level = db.Column(db.String(20))

    company_name = db.Column(db.String(200))

    experience_from = db.Column(db.String(20))

    experience_to = db.Column(db.String(20))

    education = db.Column(db.Text)

    interested_fields = db.Column(db.Text)

    app_token = db.Column(db.String(128), unique=True, nullable=True)

    profile_completion = db.Column(db.Integer, default=0)

    last_profile_reminder = db.Column(db.DateTime)
    profile_reminders_today = db.Column(db.Integer, default=0)

    daily_reward_claimed = db.Column(
        db.Boolean,
        default=False
    )

    daily_bonus_completed = db.Column(
        db.Boolean,
        default=False
    )

    # Candidate XP
    candidate_xp = db.Column(db.Integer, default=0)

    # Daily Streaks
    daily_login_completed = db.Column(db.Boolean, default=False)
    daily_apply_completed = db.Column(db.Boolean, default=False)
    daily_follow_completed = db.Column(db.Boolean, default=False)
    daily_referral_completed = db.Column(db.Boolean, default=False)

    # Date for resetting streaks
    last_streak_reset = db.Column(db.Date, nullable=True)
    
    upi_id = db.Column(db.String(100))
    bank_name = db.Column(db.String(100))
    account_holder = db.Column(db.String(100))
    account_number = db.Column(db.String(50))
    ifsc_code = db.Column(db.String(30))

    referred_by_hr_code = db.Column(db.String(50))
    referred_by_hr_id = db.Column(db.Integer)

    candidate_referral_code = db.Column(
        db.String(20),
        unique=True
    )

    referred_by_candidate_code = db.Column(
        db.String(20)
    )

    referred_by_candidate_id = db.Column(
        db.Integer
    )

    candidate_referral_reward_given = db.Column(
        db.Boolean,
        default=False
    )

    wallet_balance = db.Column(
        db.Float,
        default=0
    )

    referral_earnings = db.Column(
        db.Float,
        default=0
    )

    successful_referrals = db.Column(
        db.Integer,
        default=0
    )

    hr_referral_reward_given = db.Column(
        db.Boolean,
        default=False
    )

    revenue_owner_type = db.Column(
        db.String(20),
        default="admin"
    )

    revenue_owner_id = db.Column(
        db.Integer
    )

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

    last_login = db.Column(db.DateTime)

class CreditPurchase(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer)

    package_name = db.Column(db.String(100))

    package_price = db.Column(db.Integer)

    package_credits = db.Column(db.Integer)

    amount_paid = db.Column(db.Float)

    credits_bought = db.Column(db.Integer)

    credits_remaining = db.Column(db.Integer)

    price_per_credit = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=india_time)

    invoice_number = db.Column(db.String(50), unique=True)
    invoice_file = db.Column(db.String(255))
    payment_id = db.Column(db.String(100))
    payment_status = db.Column(db.String(20), default="Paid")

class NotificationQueue(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer)

    user_type = db.Column(db.String(20))

    template_id = db.Column(db.Integer)

    send_at = db.Column(db.DateTime)

    status = db.Column(
        db.String(20),
        default="Pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class ReferralRewardHistory(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    reward_type = db.Column(db.String(20))

    mobile = db.Column(
        db.String(20),
        unique=True
    )

    rewarded = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class DeletedAccount(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    account_type = db.Column(db.String(20))

    full_name = db.Column(db.String(200))

    mobile = db.Column(db.String(20), nullable=False)

    email = db.Column(db.String(150))

    username = db.Column(db.String(100))

    referral_reward_used = db.Column(
        db.Boolean,
        default=False
    )

    deleted_by = db.Column(
        db.String(20)
    )

    deleted_at = db.Column(
        db.DateTime,
        default=india_time
    )

class JobPost(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    hr_id = db.Column(db.Integer)

    company_name = db.Column(db.String(200))

    job_title = db.Column(db.String(200))

    location = db.Column(db.String(200))

    salary = db.Column(db.String(100))

    incentive = db.Column(db.String(100))

    job_timing = db.Column(db.String(100))

    working_days = db.Column(db.String(100))

    job_type = db.Column(db.String(100))

    employment_type = db.Column(db.String(50))

    eligibility = db.Column(db.String(100))

    experience_required = db.Column(db.String(100))

    education = db.Column(db.String(100))

    gender = db.Column(db.String(20))

    interview_from = db.Column(db.String(20))

    interview_to = db.Column(db.String(20))

    interview_time = db.Column(db.String(50))

    interview_instructions = db.Column(db.Text)

    description = db.Column(db.Text)

    image = db.Column(db.Text)

    office_address = db.Column(db.String(255))  

    images = db.Column(db.Text)

    post_type = db.Column(db.String(20), default="hiring")
    video_caption = db.Column(db.Text)
    hashtags = db.Column(db.String(300))
    cta_type = db.Column(db.String(20), default="none")
    cta_url = db.Column(db.String(500))

    boosts = db.relationship(
        "BoostPost",
        backref="job",
        lazy=True,
        cascade="all, delete-orphan"
    )

    comments = db.relationship(
        "Comment",
        backref="job",
        lazy=True,
        cascade="all, delete-orphan"
    )

    sparks = db.relationship(
        "Spark",
        backref="job",
        lazy=True,
        cascade="all, delete-orphan"
    )

    enquiries = db.relationship(
        "PostEnquiry",
        backref="job",
        lazy=True,
        cascade="all, delete-orphan"
    )

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    candidate_id = db.Column(
        db.Integer,
        db.ForeignKey('candidate_user.id')
    )

    job_id = db.Column(
        db.Integer,
        db.ForeignKey('job_post.id')
    )

    applicant_hr_id = db.Column(
        db.Integer,
        nullable=True
    )

    status = db.Column(
    db.String(50),
    nullable=True,
    default=None
    )

    applied_at = db.Column(
        db.DateTime,
        default=india_time
    )

class Notification(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)

    message = db.Column(db.Text)

    link = db.Column(db.String(300))

    image = db.Column(db.String(300))

    is_read = db.Column(db.Boolean, default=False)

    type = db.Column(db.String(30))
   
    user_type = db.Column(db.String(20))

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class CandidateWithdrawal(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    candidate_id = db.Column(db.Integer)

    amount = db.Column(db.Float)

    upi_id = db.Column(db.String(100))

    status = db.Column(
        db.String(20),
        default="Pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class PostEnquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    post_id = db.Column(db.Integer, db.ForeignKey("job_post.id"))
    hr_id = db.Column(db.Integer, db.ForeignKey("user.id"))  # Owner of the post

    enquiry_hr_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    enquiry_candidate_id = db.Column(db.Integer, db.ForeignKey("candidate_user.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=india_time)

class Follow(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    follower_candidate_id = db.Column(
        db.Integer
    )

    follower_hr_id = db.Column(
        db.Integer
    )

    followed_candidate_id = db.Column(
        db.Integer
    )

    followed_hr_id = db.Column(
        db.Integer
    )

    followed_hr_id = db.Column(
        db.Integer
    )

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class NotificationAutomation(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(200), nullable=False)

    template_id = db.Column(
        db.Integer,
        db.ForeignKey("notification_template.id")
    )

    trigger = db.Column(db.String(100))

    delay_hours = db.Column(db.Integer, default=0)

    enabled = db.Column(db.Boolean, default=True)

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

    template = db.relationship(
        "NotificationTemplate"
    )

class JobImage(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    job_id = db.Column(db.Integer)

    image = db.Column(db.String(300))

class PlatformEarning(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )

    candidate_id = db.Column(
        db.Integer,
        db.ForeignKey('candidate.id')
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    purchase_id = db.Column(
        db.Integer,
    db.ForeignKey("credit_purchase.id")
    )

    reason = db.Column(
        db.String(200)
    )

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class BusinessSettings(db.Model):
    __tablename__ = "business_settings"

    id = db.Column(db.Integer, primary_key=True)

    # -------------------------
    # HR Referral
    # -------------------------
    hr_to_hr_reward = db.Column(db.Integer, default=200)
    hr_to_candidate_reward = db.Column(db.Integer, default=25)
    candidate_to_candidate_reward = db.Column(db.Integer, default=25)

    product_promotion_price = db.Column(
        db.Integer,
        default=100
    )

    shop_promotion_price = db.Column(
        db.Integer,
        default=500
    )

    # Marketplace

    marketplace_enabled = db.Column(db.Boolean, default=True)

    marketplace_commission = db.Column(db.Float, default=10)

    seller_payment_hold_days = db.Column(db.Integer, default=7)

    minimum_order_amount = db.Column(db.Float, default=0)

    maximum_order_amount = db.Column(db.Float, default=100000)

    # Shipping

    free_shipping_amount = db.Column(db.Float, default=999)

    shipping_tax_percent = db.Column(db.Float, default=0)

    cod_enabled = db.Column(db.Boolean, default=True)

    # Returns

    return_window_days = db.Column(db.Integer, default=7)

    exchange_window_days = db.Column(db.Integer, default=7)

    # Wallet

    minimum_withdrawal = db.Column(db.Float, default=500)

    maximum_daily_withdrawal = db.Column(db.Float, default=50000)

    # Promotions

    product_promotion_price = db.Column(db.Integer, default=100)

    shop_promotion_price = db.Column(db.Integer, default=500)

    homepage_banner_price = db.Column(db.Integer, default=1000)

    promotion_duration_days = db.Column(db.Integer, default=7)

    # Search

    maximum_products_per_page = db.Column(db.Integer, default=20)

    enable_related_products = db.Column(db.Boolean, default=True)

    # Maintenance

    marketplace_maintenance = db.Column(db.Boolean, default=False)

    homepage_banner_price = db.Column(
        db.Integer,
        default=1000
    )

    promotion_duration_days = db.Column(
        db.Integer,
        default=7
    )

    daily_candidate_upload_limit = db.Column(
        db.Integer,
        default=100
    )

    hr_minimum_purchase = db.Column(db.Integer, default=500)

    hr_daily_referral_limit = db.Column(db.Integer, default=10)
    candidate_daily_referral_limit = db.Column(db.Integer, default=10)

    # ==========================
    # Daily Candidate Reward
    # ==========================

    enable_daily_candidate_reward = db.Column(
        db.Boolean,
        default=True
    )

    daily_candidate_reward = db.Column(
        db.Integer,
        default=5
    )

    daily_reward_login = db.Column(
        db.Boolean,
        default=True
    )

    daily_reward_apply = db.Column(
        db.Boolean,
        default=True
    )

    daily_reward_follow = db.Column(
        db.Boolean,
        default=True
    )

    daily_reward_referral = db.Column(
        db.Boolean,
        default=True
    )

    daily_referral_target = db.Column(
        db.Integer,
        default=10
    )

    # -------------------------
    # Revenue Sharing
    # -------------------------
    discover_hr_share = db.Column(db.Integer, default=50)
    discover_admin_share = db.Column(db.Integer, default=50)

    leads_hr_share = db.Column(db.Integer, default=50)
    leads_admin_share = db.Column(db.Integer, default=50)

    self_candidate_admin_share = db.Column(db.Integer, default=100)

    # -------------------------
    # Unlock Credits
    # -------------------------
    discover_unlock_credits = db.Column(db.Integer, default=2)
    leads_unlock_credits = db.Column(db.Integer, default=2)

    # -------------------------
    # Wallet
    # -------------------------
    minimum_withdrawal = db.Column(db.Integer, default=500)
    maximum_daily_withdrawal = db.Column(db.Integer, default=5000)

    # -------------------------
    # Feature Toggles
    # -------------------------
    enable_hr_referral = db.Column(db.Boolean, default=True)
    enable_candidate_referral = db.Column(db.Boolean, default=True)
    enable_revenue_sharing = db.Column(db.Boolean, default=True)

    enable_discover = db.Column(db.Boolean, default=True)
    enable_leads = db.Column(db.Boolean, default=True)

    enable_wallet = db.Column(db.Boolean, default=True)
    enable_withdrawals = db.Column(db.Boolean, default=True)

    # Lead Unlock Credits
    lead_fresher_paid = db.Column(db.Integer, default=1)
    lead_fresher_free = db.Column(db.Integer, default=2)

    lead_experienced_paid = db.Column(db.Integer, default=2)
    lead_experienced_free = db.Column(db.Integer, default=4)

    # Discover Unlock Credits
    discover_unlock_cost = db.Column(db.Integer, default=2)

    # -------------------------
    # Audit
    # -------------------------
    updated_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    updated_at = db.Column(
        db.DateTime,
        default=india_time,
        onupdate=india_time
    )

    # ==========================
    # Boost Promotion
    # ==========================

    enable_boost_posts = db.Column(db.Boolean, default=True)

    boost_city_price = db.Column(db.Integer, default=5)
    boost_pan_india_price = db.Column(db.Integer, default=50)

    boost_min_days = db.Column(db.Integer, default=1)
    boost_max_days = db.Column(db.Integer, default=30)

    boost_max_active_posts = db.Column(db.Integer, default=5)

    boost_max_impressions = db.Column(db.Integer, default=10000)

    boost_credits_per_day = db.Column(db.Integer, default=5)

    shiprocket_email = db.Column(db.String(120))
    shiprocket_password = db.Column(db.String(255))

    shiprocket_pickup_location = db.Column(db.String(100))

    marketplace_commission = db.Column(
        db.Float,
        default=10
    )

    seller_payment_hold_days = db.Column(
        db.Integer,
        default=7
    )

    platform_commission = db.Column(
        db.Float,
        default=10
    )

    seller_payment_hold_days = db.Column(
        db.Integer,
        default=7
    )

class BoostCity(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    boost_id = db.Column(
        db.Integer,
        db.ForeignKey("boost_post.id", ondelete="CASCADE")
    )

    city = db.Column(db.String(100))

class MarketplaceFee(db.Model):
    __tablename__ = "marketplace_fees"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("product_categories.id"),
        nullable=True
    )

    commission_percent = db.Column(
        db.Float,
        default=0
    )

    shipping_fee = db.Column(
        db.Float,
        default=0
    )

    return_fee = db.Column(
        db.Float,
        default=0
    )

    cod_fee = db.Column(
        db.Float,
        default=0
    )

    promotion_discount = db.Column(
        db.Float,
        default=0
    )

class HomepageBanner(db.Model):
    __tablename__ = "homepage_banners"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200))

    subtitle = db.Column(db.String(255))

    image = db.Column(db.String(255))

    button_text = db.Column(db.String(50))

    button_link = db.Column(db.String(255))

    display_order = db.Column(
        db.Integer,
        default=1
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class HomepageSection(db.Model):

    __tablename__="homepage_sections"

    id=db.Column(db.Integer,primary_key=True)

    section_name=db.Column(db.String(100))

    title=db.Column(db.String(200))

    is_enabled=db.Column(
        db.Boolean,
        default=True
    )

    display_order=db.Column(
        db.Integer,
        default=1
    )

class CategoryBanner(db.Model):

    id=db.Column(db.Integer,primary_key=True)

    category_id=db.Column(

        db.Integer,

        db.ForeignKey("product_categories.id")

    )

    image=db.Column(db.String(255))

    active=db.Column(

        db.Boolean,

        default=True

    )

    icon = db.Column(db.String(255))

    banner_image = db.Column(db.String(255))

    mobile_banner = db.Column(db.String(255))

    seo_title = db.Column(db.String(255))

    seo_description = db.Column(db.Text)

    display_order = db.Column(db.Integer, default=0)

    show_on_homepage = db.Column(db.Boolean, default=False)

    is_trending = db.Column(db.Boolean, default=False)

class CMSPage(db.Model):

    __tablename__ = "cms_pages"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200))

    slug = db.Column(
        db.String(100),
        unique=True
    )

    content = db.Column(db.Text)

    meta_title = db.Column(db.String(255))

    meta_description = db.Column(db.Text)

    is_published = db.Column(
        db.Boolean,
        default=True
    )

    updated_at = db.Column(
        db.DateTime,
        default=india_time,
        onupdate=india_time
    )

class SocialLink(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    platform = db.Column(db.String(50))

    url = db.Column(db.String(255))

    icon = db.Column(db.String(100))

    active = db.Column(
        db.Boolean,
        default=True
    )

class SEOSettings(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    site_title = db.Column(db.String(255))

    meta_description = db.Column(db.Text)

    meta_keywords = db.Column(db.Text)

    favicon = db.Column(db.String(255))

    logo = db.Column(db.String(255))

    og_image = db.Column(db.String(255))

class ContactSettings(db.Model):

    __tablename__ = "contact_settings"

    id = db.Column(db.Integer, primary_key=True)

    company_name = db.Column(db.String(255))

    email = db.Column(db.String(255))

    support_email = db.Column(db.String(255))

    phone = db.Column(db.String(50))

    whatsapp = db.Column(db.String(50))

    address = db.Column(db.Text)

    business_hours = db.Column(db.String(255))

    google_map = db.Column(db.Text)

class Brand(db.Model):

    __tablename__="brands"

    id=db.Column(db.Integer,primary_key=True)

    name=db.Column(db.String(120))

    logo=db.Column(db.String(255))

    active=db.Column(db.Boolean,default=True)

    created_at=db.Column(

        db.DateTime,

        default=india_time

    )

class BoostPost(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    job_id = db.Column(db.Integer, db.ForeignKey("job_post.id"))

    hr_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    boost_type = db.Column(db.String(20))
    # city
    # state
    # pan_india

    state = db.Column(db.String(100))

    cities = db.Column(db.Text)
    # JSON string

    days = db.Column(db.Integer)

    total_credits = db.Column(db.Integer)

    status = db.Column(db.String(20), default="Active")

    impressions = db.Column(db.Integer, default=0)

    clicks = db.Column(db.Integer, default=0)

    applications = db.Column(db.Integer, default=0)

    starts_at = db.Column(db.DateTime, default=india_time)

    expires_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=india_time)

    credits_used = db.Column(db.Integer, default=0)

    credits_remaining = db.Column(db.Integer, default=0)

    days_completed = db.Column(db.Integer, default=0)

    last_credit_deduction = db.Column(db.Date)

class ShopPromotion(db.Model):
    __tablename__ = "shop_promotions"

    id = db.Column(db.Integer, primary_key=True)

    seller_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    credits_used = db.Column(db.Integer)

    amount = db.Column(db.Float)

    start_date = db.Column(
        db.DateTime,
        default=india_time
    )

    end_date = db.Column(db.DateTime)

    status = db.Column(
        db.String(20),
        default="Active"
    )

class ProductPromotion(db.Model):

    __tablename__ = "product_promotions"

    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id")
    )

    seller_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    credits_used = db.Column(db.Integer)

    amount = db.Column(db.Float)

    start_date = db.Column(
        db.DateTime,
        default=india_time
    )

    end_date = db.Column(db.DateTime)

    status = db.Column(
        db.String(20),
        default="Active"
    )

class BroadcastNotification(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)

    message = db.Column(db.Text, nullable=False)

    send_to = db.Column(db.String(30), nullable=False)
    # hr
    # candidate
    # both

    send_mode = db.Column(db.String(20), default="all")
    # all
    # selected

    selected_users = db.Column(db.Text)

    status = db.Column(db.String(20), default="Pending")
    # Pending
    # Sent

    schedule_time = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=india_time)

    is_paused = db.Column(db.Boolean, default=False)

    sent_at = db.Column(db.DateTime)

    updated_at = db.Column(
        db.DateTime,
        default=india_time,
        onupdate=india_time
    )

class NotificationTemplate(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)

    title = db.Column(db.String(200), nullable=False)

    message = db.Column(db.Text, nullable=False)

    audience = db.Column(db.String(30), default="both")
    # hr
    # candidate
    # both

    link = db.Column(db.String(300), default="/")

    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=india_time)

class CreditPackage(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    package_name = db.Column(db.String(100), nullable=False)

    credits = db.Column(db.Integer, nullable=False)

    price = db.Column(db.Float, nullable=False)

    badge = db.Column(db.String(50), default="")

    color = db.Column(db.String(30), default="primary")

    description = db.Column(db.String(200), default="")

    display_order = db.Column(db.Integer, default=0)

    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20), unique=True)
    experience = db.Column(db.String(50))
    designation = db.Column(db.String(200))
    city = db.Column(db.String(100))
    category = db.Column(db.String(100))
    uploaded_by = db.Column(db.Integer)
    is_platform_candidate = db.Column(
        db.Boolean,
        default=False
    )
    revenue_owner_type = db.Column(
        db.String(20),
        default="admin"
    )

    revenue_owner_id = db.Column(
        db.Integer
    )
    created_at = db.Column(db.DateTime, default=india_time)
    is_fake = db.Column(db.Boolean, default=False)
    report_count = db.Column(db.Integer, default=0)
    wrong_experience_reports = db.Column(db.Integer, default=0)

class Unlock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    candidate_id = db.Column(db.Integer)
    created_at = db.Column(
    db.DateTime,
    default=india_time
    )

class CandidateWalletHistory(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    candidate_id = db.Column(db.Integer)

    amount = db.Column(db.Float)

    action = db.Column(db.String(200))

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class CreditHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    amount = db.Column(db.Integer)
    action = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=india_time)

class Earnings(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer)

    amount = db.Column(db.Float)

    reason = db.Column(db.String(300))

    purchase_id = db.Column(
        db.Integer,
    db.ForeignKey("credit_purchase.id")
    )

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class Spark(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    job_id = db.Column(
        db.Integer,
        db.ForeignKey("job_post.id"),
        nullable=False
    )

    hr_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True
    )

    candidate_id = db.Column(
        db.Integer,
        db.ForeignKey("candidate_user.id"),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

class CandidateReview(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    candidate_id = db.Column(db.Integer)

    user_id = db.Column(db.Integer)

    rating = db.Column(db.Integer)

    review = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class ProductReport(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id")
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    reason = db.Column(db.String(200))

    description = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class ProductAnalytics(db.Model):
    __tablename__ = "product_analytics"

    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    total_views = db.Column(
        db.Integer,
        default=0
    )

    unique_views = db.Column(
        db.Integer,
        default=0
    )

    wishlist_count = db.Column(
        db.Integer,
        default=0
    )

    cart_count = db.Column(
        db.Integer,
        default=0
    )

    purchase_count = db.Column(
        db.Integer,
        default=0
    )

    revenue = db.Column(
        db.Float,
        default=0
    )

    last_updated = db.Column(
        db.DateTime,
        default=india_time
    )

class LeadView(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    hr_id = db.Column(db.Integer, nullable=False)

    candidate_id = db.Column(db.Integer, nullable=False)

    viewed_at = db.Column(
        db.DateTime,
        default=india_time
    )

class HiddenFeed(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    post_id = db.Column(
        db.Integer,
        db.ForeignKey("job_post.id", ondelete="CASCADE")
    )

    hr_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True
    )

    candidate_id = db.Column(
        db.Integer,
        db.ForeignKey("candidate_user.id"),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class FeedReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    post_id = db.Column(
        db.Integer,
        db.ForeignKey("job_post.id", ondelete="CASCADE"),
        nullable=False
    )

    hr_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True
    )

    candidate_id = db.Column(
        db.Integer,
        db.ForeignKey("candidate_user.id"),
        nullable=True
    )

    reason = db.Column(db.String(100))

    comment = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class HRFollower(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    hr_id = db.Column(db.Integer)

    candidate_id = db.Column(db.Integer)

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class CandidateContactUnlock(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    hr_id = db.Column(db.Integer)

    candidate_user_id = db.Column(db.Integer)

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class AdminLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=india_time)

class SupportReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    ticket_id = db.Column(db.Integer)

    sender = db.Column(db.String(50))

    message = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=india_time)

class SupportTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer)

    user_type = db.Column(
        db.String(20),
        default='hr'
    )

    subject = db.Column(db.String(300))

    message = db.Column(db.Text)

    status = db.Column(
        db.String(50),
        default='Open'
    )

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class SeenLead(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer)

    candidate_id = db.Column(db.Integer)

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class Withdrawal(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    status = db.Column(
        db.String(50),
        default="Pending"
    )

    payment_method = db.Column(
        db.String(50)
    )

    payment_details = db.Column(
        db.Text
    )

    utr_number = db.Column(
        db.String(100)
    )

    admin_remark = db.Column(
        db.Text
    )

    approved_at = db.Column(
        db.DateTime
    )

    paid_at = db.Column(
        db.DateTime
    )

    rejected_at = db.Column(
        db.DateTime
    )

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

    withdrawal_type = db.Column(
        db.String(30),
        default="marketplace"
    )

    order_id = db.Column(
        db.Integer,
        nullable=True
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "withdrawals",
            lazy=True
        )
    )

class PasswordReset(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120))

    otp = db.Column(db.String(10))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    job_id = db.Column(
        db.Integer,
        db.ForeignKey("job_post.id", ondelete="CASCADE"),
        nullable=False
    )

    hr_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True
    )

    candidate_id = db.Column(
        db.Integer,
        db.ForeignKey("candidate_user.id"),
        nullable=True
    )

    parent_comment_id = db.Column(
        db.Integer,
        db.ForeignKey("comment.id"),
        nullable=True
    )

    comment = db.Column(db.Text, nullable=False)

    edited = db.Column(db.Boolean, default=False)

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

    replies = db.relationship(
        "Comment",
        backref=db.backref(
            "parent",
            remote_side=[id]
        ),
        lazy=True,
        cascade="all, delete-orphan"
    )

class CommentLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    comment_id = db.Column(
        db.Integer,
        db.ForeignKey("comment.id", ondelete="CASCADE"),
        nullable=False
    )

    hr_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True
    )

    candidate_id = db.Column(
        db.Integer,
        db.ForeignKey("candidate_user.id"),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class CommentReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(
        db.Integer,
        db.ForeignKey("comment.id", ondelete="CASCADE"),
        nullable=False
    )
    hr_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True
    )
    candidate_id = db.Column(
        db.Integer,
        db.ForeignKey("candidate_user.id"),
        nullable=True
    )
    reason = db.Column(db.String(100))
    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class ProductCategory(db.Model):
    __tablename__ = "product_categories"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False, unique=True)

    image = db.Column(db.String(255))

    is_active = db.Column(db.Boolean, default=True)

    coupons = db.relationship(
        "Coupon",
        backref="category",
        lazy=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

# =========================================================
# RECROOTEARN SHOP - DEFAULT CATEGORIES
# =========================================================

DEFAULT_SHOP_CATEGORIES = [

    "Mobiles & Tablets",
    "Electronics",
    "Computers & Laptops",
    "Computer Accessories",
    "TV, Audio & Video",
    "Cameras & Photography",

    "Home Appliances",
    "Kitchen Appliances",

    "Fashion",
    "Men's Clothing",
    "Women's Clothing",
    "Kids' Clothing",
    "Footwear",
    "Bags & Luggage",
    "Jewellery & Accessories",

    "Beauty & Personal Care",
    "Health & Wellness",

    "Home & Kitchen",
    "Furniture",
    "Home Decor",
    "Home Improvement",
    "Kitchen & Dining",

    "Grocery & Gourmet Food",

    "Baby Products",
    "Toys & Games",

    "Books",
    "Stationery & Office",

    "Sports & Fitness",

    "Pet Supplies",

    "Automotive",

    "Tools & Hardware",
    "Garden & Outdoor",

    "Arts, Crafts & Hobbies",

    "Gifts & Custom Products",

    "Musical Instruments",

    "Travel & Travel Accessories",

    "Other Products"
]


def create_default_shop_categories():

    for category_name in DEFAULT_SHOP_CATEGORIES:

        existing = ProductCategory.query.filter_by(
            name=category_name
        ).first()

        if not existing:

            db.session.add(
                ProductCategory(
                    name=category_name,
                    is_active=True
                )
            )

    db.session.commit()

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)

    seller_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("product_categories.id")
    )

    name = db.Column(db.String(200), nullable=False)

    is_promoted = db.Column(
        db.Boolean,
        default=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    promotion_expires_at = db.Column(
        db.DateTime
    )

    promotion_type = db.Column(
        db.String(30)
    )

    promotion_priority = db.Column(
        db.Integer,
        default=0
    )

    promotion_amount = db.Column(
        db.Float,
        default=0
    )

    # Analytics
    total_views = db.Column(db.Integer, default=0)

    unique_views = db.Column(db.Integer, default=0)

    wishlist_count = db.Column(db.Integer, default=0)

    cart_count = db.Column(db.Integer, default=0)

    purchase_count = db.Column(db.Integer, default=0)

    revenue = db.Column(db.Float, default=0)

    conversion_rate = db.Column(db.Float, default=0)

    last_viewed_at = db.Column(db.DateTime)

    last_purchased_at = db.Column(db.DateTime)

    analytics = db.relationship(
        "ProductAnalytics",
        backref="product",
        uselist=False,
        cascade="all, delete-orphan"
    )

    wishlist_users = db.relationship(
        "Wishlist",
        backref="product",
        lazy=True,
        cascade="all, delete-orphan"
    )

    slug = db.Column(db.String(255), unique=True)

    description = db.Column(db.Text)

    price = db.Column(db.Float, nullable=False)

    sale_price = db.Column(db.Float)

    stock = db.Column(db.Integer, default=0)

    status = db.Column(
        db.String(20),
        default="active"
    )

    is_promoted = db.Column(
        db.Boolean,
        default=False
    )

    promotion_end = db.Column(db.DateTime)

    views = db.Column(db.Integer, default=0)

    sold = db.Column(db.Integer, default=0)

    order_items = db.relationship(
        "OrderItem",
        backref="product",
        lazy=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    images = db.relationship(
        "ProductImage",
        backref="product",
        lazy=True,
        cascade="all, delete-orphan"
    )

    category = db.relationship(
        "ProductCategory",
        backref="products",
        lazy=True
    )

    average_rating = db.Column(
        db.Float,
        default=0
    )

    total_reviews = db.Column(
        db.Integer,
        default=0
    )

    cart_items = db.relationship(
        "CartItem",
        backref="product",
        lazy=True
    )

    variants = db.relationship(
        "ProductVariant",
        backref="product",
        lazy=True,
        cascade="all, delete-orphan"
    )

    reviews = db.relationship(
        "ProductReview",
        backref="product",
        lazy=True,
        cascade="all, delete-orphan"
    )

    cart_items = db.relationship(
        "CartItem",
        backref="product",
        lazy=True
    )

    average_rating = db.Column(
        db.Float,
        default=0
    )

    total_reviews = db.Column(
        db.Integer,
        default=0
    )

    sold = db.Column(
        db.Integer,
        default=0
    )

    views = db.Column(
        db.Integer,
        default=0
    )

    product_type = db.Column(
        db.String(20),
        default="simple"
    )

    badge = db.Column(
        db.String(50)
    )

    average_rating = db.Column(
        db.Float,
        default=0
    )

    total_reviews = db.Column(
        db.Integer,
        default=0
    )

    reviews = db.relationship(
        "ProductReview",
        backref="product",
        lazy=True,
        cascade="all, delete-orphan"
    )

    weight = db.Column(db.Float)        # in kg
    length = db.Column(db.Float)        # cm
    width = db.Column(db.Float)         # cm
    height = db.Column(db.Float)        # cm
    hsn_code = db.Column(db.String(20))
    gst_percentage = db.Column(db.Float, default=0)

    # ==========================================
    # SHOP HOME SETTINGS
    # ==========================================

    show_on_home = db.Column(
        db.Boolean,
        default=False
    )

    home_section = db.Column(
        db.String(100),
        default="Trending Now"
    )

    home_tagline = db.Column(
        db.String(255)
    )

    home_display_order = db.Column(
        db.Integer,
        default=0
    )

class ProductImage(db.Model):
    __tablename__ = "product_images"

    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    image = db.Column(
        db.String(255),
        nullable=False
    )

    sort_order = db.Column(
        db.Integer,
        default=0
    )

class Cart(db.Model):
    __tablename__ = "cart"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    seller_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    items = db.relationship(
        "CartItem",
        backref="cart",
        lazy=True,
        cascade="all, delete-orphan"
    )

class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)

    cart_id = db.Column(
        db.Integer,
        db.ForeignKey("cart.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    variant_option_id = db.Column(
        db.Integer,
        db.ForeignKey("product_variant_options.id")
    )

    quantity = db.Column(
        db.Integer,
        default=1
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    variant_option = db.relationship(
        "ProductVariantOption",
    )

class ProductVariant(db.Model):
    __tablename__ = "product_variants"

    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    options = db.relationship(
        "ProductVariantOption",
        backref="variant",
        lazy=True,
        cascade="all, delete-orphan"
    )

class ProductVariantOption(db.Model):
    __tablename__ = "product_variant_options"

    id = db.Column(db.Integer, primary_key=True)

    variant_id = db.Column(
        db.Integer,
        db.ForeignKey("product_variants.id"),
        nullable=False
    )

    value = db.Column(
        db.String(100),
        nullable=False
    )

    extra_price = db.Column(
        db.Float,
        default=0
    )

    stock = db.Column(
        db.Integer,
        default=0
    )

    sku = db.Column(
        db.String(100)
    )

    cart_items = db.relationship(
        "CartItem",
        backref="variant",
        lazy=True
    )

    order_items = db.relationship(
        "OrderItem",
        backref="variant_option",
        lazy=True
    )

class ShippingAddress(db.Model):
    __tablename__ = "shipping_addresses"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    full_name = db.Column(
        db.String(120),
        nullable=False
    )

    mobile = db.Column(
        db.String(20),
        nullable=False
    )

    alternate_mobile = db.Column(
        db.String(20)
    )

    address_line1 = db.Column(
        db.String(255),
        nullable=False
    )

    address_line2 = db.Column(
        db.String(255)
    )

    landmark = db.Column(
        db.String(255)
    )

    city = db.Column(
        db.String(100),
        nullable=False
    )

    state = db.Column(
        db.String(100),
        nullable=False
    )

    pincode = db.Column(
        db.String(10),
        nullable=False
    )

    country = db.Column(
        db.String(50),
        default="India"
    )

    is_default = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    orders = db.relationship(
        "Order",
        lazy=True
    )

class OrderStatusHistory(db.Model):
    __tablename__ = "order_status_history"

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id"),
        nullable=False
    )

    status = db.Column(
        db.String(100),
        nullable=False
    )

    remarks = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    variant_option_id = db.Column(
        db.Integer,
        db.ForeignKey("product_variant_options.id")
    )

    quantity = db.Column(
        db.Integer,
        default=1
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    total = db.Column(
        db.Float,
        nullable=False
    )

    product_name = db.Column(
        db.String(255)
    )

    product_image = db.Column(
        db.String(255)
    )

    variant_name = db.Column(
        db.String(100)
    )

    return_request = db.relationship(
        "ReturnRequest",
        backref="order_item",
        uselist=False
    )

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    order_number = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    seller_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    address_id = db.Column(
        db.Integer,
        db.ForeignKey("shipping_addresses.id"),
        nullable=False
    )

    payment_method = db.Column(
        db.String(50)
    )

    payment_status = db.Column(
        db.String(30),
        default="Pending"
    )

    order_status = db.Column(
        db.String(30),
        default="Pending"
    )

    razorpay_order_id = db.Column(
        db.String(120)
    )

    razorpay_payment_id = db.Column(
        db.String(120)
    )

    subtotal = db.Column(
        db.Float,
        default=0
    )

    shipping_charge = db.Column(
        db.Float,
        default=0
    )

    total_amount = db.Column(
        db.Float,
        default=0
    )

    platform_commission = db.Column(
        db.Float,
        default=0
    )

    seller_amount = db.Column(
        db.Float,
        default=0
    )

    wallet_released = db.Column(
        db.Boolean,
        default=False
    )

    # ==================================
    # SHIPPING
    # ==================================

    shipping_provider = db.Column(
        db.String(30),
        default="shiprocket"
    )

    shipment_id = db.Column(
        db.String(120)
    )

    shipment_reference = db.Column(
        db.String(120)
    )

    tracking_id = db.Column(
        db.String(100)
    )

    awb_code = db.Column(
        db.String(100)
    )

    courier_name = db.Column(
        db.String(100)
    )

    shipping_status = db.Column(
        db.String(50),
        default="Pending"
    )

    estimated_delivery = db.Column(
        db.DateTime
    )

    shipped_at = db.Column(
        db.DateTime
    )

    out_for_delivery_at = db.Column(
        db.DateTime
    )

    delivered_at = db.Column(
        db.DateTime
    )

    cancelled_at = db.Column(
        db.DateTime
    )

    returned_at = db.Column(
        db.DateTime
    )

    pickup_request_id = db.Column(
        db.String(120)
    )

    label_url = db.Column(
        db.Text
    )

    manifest_url = db.Column(
        db.Text
    )

    tracking_url = db.Column(
        db.Text
    )

    tracking_json = db.Column(
        db.Text
    )

    last_tracking_sync = db.Column(
        db.DateTime
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    seller = db.relationship(
        "User",
        foreign_keys=[seller_id],
        backref="seller_orders"
    )

    customer = db.relationship(
        "User",
        foreign_keys=[user_id],
        backref="customer_orders"
    )

    # ==================================
    # RELATIONSHIPS
    # ==================================

    shipping_address = db.relationship(
        "ShippingAddress",
    )

    items = db.relationship(
        "OrderItem",
        backref="order",
        lazy=True,
        cascade="all, delete-orphan"
    )

    seller_remarks = db.Column(db.Text)

    customer_notes = db.Column(db.Text)

    invoice_number = db.Column(db.String(100))

import requests

BASE_URL = "https://apiv2.shiprocket.in/v1/external"


class ShiprocketService:

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.token = None

    # ==========================================
    # LOGIN
    # ==========================================

    def login(self):

        response = requests.post(
            BASE_URL + "/auth/login",
            json={
                "email": self.email,
                "password": self.password
            },
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("token"):
            raise Exception(
                f"Shiprocket login failed: {data}"
            )

        self.token = data["token"]

        return self.token

    # ==========================================
    # HEADERS
    # ==========================================

    def headers(self):

        if not self.token:
            self.login()

        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    # ==========================================
    # CREATE SHIPMENT / ORDER
    # ==========================================

    def create_shipment(self, order):

        pickup = order.seller.pickup_address
        address = order.shipping_address

        if not pickup:
            raise Exception(
                "Seller pickup address is not configured."
            )

        if not address:
            raise Exception(
                "Customer shipping address is missing."
            )

        items = []

        for item in order.items:

            items.append({
                "name": item.product_name,
                "sku": str(item.product_id),
                "units": item.quantity,
                "selling_price": item.price,
                "discount": "",
                "tax": "",
                "hsn": (
                    item.product.hsn_code
                    if item.product and item.product.hsn_code
                    else ""
                )
            })

        # ------------------------------------------
        # PACKAGE DIMENSIONS
        # ------------------------------------------

        lengths = []
        widths = []
        heights = []

        total_weight = 0

        for item in order.items:

            product = item.product

            if not product:
                continue

            lengths.append(product.length or 1)
            widths.append(product.width or 1)

            heights.append(
                (product.height or 1) * item.quantity
            )

            total_weight += (
                (product.weight or 0.1)
                * item.quantity
            )

        package_length = max(lengths) if lengths else 1
        package_width = max(widths) if widths else 1
        package_height = sum(heights) if heights else 1

        if total_weight <= 0:
            total_weight = 0.1

        # ------------------------------------------
        # PAYMENT METHOD
        # ------------------------------------------

        payment_method = "Prepaid"

        if getattr(order, "payment_method", "").lower() == "cod":
            payment_method = "COD"

        # ------------------------------------------
        # PAYLOAD
        # ------------------------------------------

        payload = {

            "order_id": order.order_number,

            "order_date":
                order.created_at.strftime(
                    "%Y-%m-%d %H:%M"
                ),

            "pickup_location":
                pickup.pickup_name,

            "billing_customer_name":
                address.full_name,

            "billing_last_name": "",

            "billing_address":
                address.address_line1,

            "billing_address_2":
                address.address_line2 or "",

            "billing_city":
                address.city,

            "billing_pincode":
                str(address.pincode),

            "billing_state":
                address.state,

            "billing_country":
                address.country or "India",

            "billing_email":
                order.customer.email or "",

            "billing_phone":
                address.mobile,

            "shipping_is_billing":
                True,

            "order_items":
                items,

            "payment_method":
                payment_method,

            "sub_total":
                order.subtotal,

            "length":
                package_length,

            "breadth":
                package_width,

            "height":
                package_height,

            "weight":
                total_weight
        }

        # ------------------------------------------
        # API REQUEST
        # ------------------------------------------

        response = requests.post(

            BASE_URL + "/orders/create/adhoc",

            headers=self.headers(),

            json=payload,

            timeout=30
        )

        try:
            response.raise_for_status()

        except requests.HTTPError:

            raise Exception(
                "Shiprocket shipment creation failed: "
                + response.text
            )

        return response.json()

    # ==========================================
    # CHECK SERVICEABILITY
    # ==========================================

    def check_serviceability(
        self,
        pickup_pincode,
        delivery_pincode,
        weight,
        cod=False
    ):

        response = requests.get(

            BASE_URL + "/courier/serviceability",

            headers=self.headers(),

            params={

                "pickup_postcode":
                    pickup_pincode,

                "delivery_postcode":
                    delivery_pincode,

                "weight":
                    weight,

                "cod":
                    1 if cod else 0
            },

            timeout=30
        )

        response.raise_for_status()

        return response.json()

    # ==========================================
    # TRACK SHIPMENT
    # ==========================================

    def track_shipment(self, awb):

        response = requests.get(

            BASE_URL
            + f"/courier/track/awb/{awb}",

            headers=self.headers(),

            timeout=30
        )

        response.raise_for_status()

        return response.json()


# ==================================================
# GET SHIPROCKET INSTANCE
# IMPORTANT: OUTSIDE ShiprocketService CLASS
# ==================================================

def get_shiprocket():

    settings = get_business_settings()

    if not settings:
        raise Exception(
            "Business settings not configured."
        )

    if not settings.shiprocket_email:
        raise Exception(
            "Shiprocket email is not configured."
        )

    if not settings.shiprocket_password:
        raise Exception(
            "Shiprocket password is not configured."
        )

    shiprocket = ShiprocketService(
        settings.shiprocket_email,
        settings.shiprocket_password
    )

    shiprocket.login()

    return shiprocket

class SellerPickupAddress(db.Model):
    __tablename__ = "seller_pickup_addresses"

    id = db.Column(db.Integer, primary_key=True)

    seller_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        unique=True
    )

    pickup_name = db.Column(
        db.String(120),
        nullable=False
    )

    contact_person = db.Column(
        db.String(120),
        nullable=False
    )

    mobile = db.Column(
        db.String(20),
        nullable=False
    )

    email = db.Column(
        db.String(120)
    )

    address_line1 = db.Column(
        db.String(255),
        nullable=False
    )

    address_line2 = db.Column(
        db.String(255)
    )

    city = db.Column(
        db.String(100),
        nullable=False
    )

    state = db.Column(
        db.String(100),
        nullable=False
    )

    pincode = db.Column(
        db.String(10),
        nullable=False
    )

    country = db.Column(
        db.String(50),
        default="India"
    )

    gst_number = db.Column(
        db.String(30)
    )

    company_name = db.Column(
        db.String(150)
    )

    alternate_mobile = db.Column(
        db.String(20)
    )

    landmark = db.Column(
        db.String(255)
    )

    pickup_location_code = db.Column(
        db.String(120),
        unique=True
    )

    is_default = db.Column(
        db.Boolean,
        default=True
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    is_verified = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

class MarketplaceWalletHistory(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    seller_id = db.Column(db.Integer)

    order_id = db.Column(db.Integer)

    amount = db.Column(db.Float)

    action = db.Column(db.String(50))

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class ProductReview(db.Model):
    __tablename__ = "product_reviews"

    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    seller_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id"),
        nullable=False
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    title = db.Column(
        db.String(150)
    )

    review = db.Column(
        db.Text
    )

    images = db.Column(
        db.Text
    )

    is_verified_purchase = db.Column(
        db.Boolean,
        default=True
    )

    is_approved = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class CouponUsage(db.Model):
    __tablename__ = "coupon_usage"

    id = db.Column(db.Integer, primary_key=True)

    coupon_id = db.Column(
        db.Integer,
        db.ForeignKey("coupons.id")
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id")
    )

    discount_amount = db.Column(db.Float)

    used_at = db.Column(
        db.DateTime,
        default=india_time
    )

class Coupon(db.Model):
    __tablename__ = "coupons"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    code = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    title = db.Column(
        db.String(150)
    )

    description = db.Column(
        db.Text
    )

    discount_type = db.Column(
        db.String(20),
        default="percentage"
    )

    discount_value = db.Column(
        db.Float,
        default=0
    )

    minimum_order = db.Column(
        db.Float,
        default=0
    )

    minimum_order_amount = db.Column(
        db.Float,
        default=0
    )

    maximum_discount = db.Column(
        db.Float
    )

    usage_limit = db.Column(
        db.Integer
    )

    used_count = db.Column(
        db.Integer,
        default=0
    )

    seller_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("product_categories.id"),
        nullable=True
    )

    start_date = db.Column(
        db.DateTime
    )

    expiry_date = db.Column(
        db.DateTime
    )

    first_order_only = db.Column(
        db.Boolean,
        default=False
    )

    active = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

class Wishlist(db.Model):
    __tablename__ = "wishlist"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "product_id",
            name="unique_wishlist_product"
        ),
    )

class ReturnRequest(db.Model):
    __tablename__ = "return_requests"

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id"),
        nullable=False
    )

    order_item_id = db.Column(
        db.Integer,
        db.ForeignKey("order_items.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    seller_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    reason = db.Column(db.String(255))

    description = db.Column(db.Text)

    status = db.Column(
        db.String(30),
        default="Pending"
    )

    refund_amount = db.Column(
        db.Float,
        default=0
    )

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

    approved_at = db.Column(db.DateTime)

    completed_at = db.Column(db.DateTime)

    pickup_awb = db.Column(db.String(100))

    pickup_status = db.Column(
        db.String(50),
        default="Pending"
    )

    pickup_scheduled_at = db.Column(db.DateTime)

    exchange_requested = db.Column(
        db.Boolean,
        default=False
    )

    exchange_product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id")
    )

    refund_mode = db.Column(
        db.String(30),
        default="Original Payment"
    )

    images = db.relationship(
        "ReturnImage",
        backref="return_request",
        cascade="all, delete-orphan"
    )

class ReturnImage(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    return_id = db.Column(
        db.Integer,
        db.ForeignKey("return_requests.id")
    )

    image = db.Column(
        db.String(255)
    )

class ReturnHistory(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    return_id = db.Column(
        db.Integer,
        db.ForeignKey("return_requests.id")
    )

    status = db.Column(db.String(50))

    remarks = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=india_time
    )

# =========================
# LOGIN MANAGER
# =========================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_only():

    if (
        not current_user.is_authenticated
        or current_user.mobile != "6261568334"
    ):
        return False

    return True

def get_business_settings():

    settings = BusinessSettings.query.first()

    if not settings:

        settings = BusinessSettings()

        db.session.add(settings)

        db.session.commit()

    return settings

def check_daily_reward(candidate):

    settings = get_business_settings()

    if not settings.enable_daily_candidate_reward:
        return

    if candidate.daily_reward_claimed:
        return

    login_ok = (
        not settings.daily_reward_login
        or candidate.daily_login_completed
    )

    apply_ok = (
        not settings.daily_reward_apply
        or candidate.daily_apply_completed
    )

    follow_ok = (
        not settings.daily_reward_follow
        or candidate.daily_follow_completed
    )

    referral_ok = (
        not settings.daily_reward_referral
        or candidate.daily_referral_completed
    )

    if login_ok and apply_ok and follow_ok and referral_ok:

        candidate.wallet_balance += settings.daily_candidate_reward

        candidate.daily_reward_claimed = True

        db.session.add(

            CandidateWalletHistory(

                candidate_id=candidate.id,

                amount=settings.daily_candidate_reward,

                action="Daily Task Reward"

            )

        )

        send_notification(

            user_id=candidate.id,

            user_type="candidate",

            message=f"🎉 You earned ₹{settings.daily_candidate_reward} for completing today's tasks.",

            link="/candidate-wallet",

            type="daily_reward"

        )

def safe_wallet_credit(user, amount):

    if not user:
        return False

    if amount <= 0:
        return False

    user.wallet_balance += amount

    return True

def safe_wallet_debit(user, amount):

    if not user:
        return False

    if amount <= 0:
        return False

    if user.wallet_balance < amount:
        return False

    user.wallet_balance -= amount

    return True

# ==========================
# SEND OTP USING MSG91
# ==========================

def send_msg91_otp(mobile):

    print("===== CALLING MSG91 =====")
    print("AUTH:", MSG91_AUTH_KEY)
    print("TEMPLATE:", MSG91_TEMPLATE_ID)
    print("SENDER:", MSG91_SENDER_ID)
    print("MOBILE:", mobile)

    url = "https://control.msg91.com/api/v5/otp"

    headers = {
        "authkey": MSG91_AUTH_KEY
    }

    payload = {
        "mobile": "91" + mobile,
        "template_id": MSG91_TEMPLATE_ID,
        "sender": MSG91_SENDER_ID,
        "otp_length": 6,
        "otp_expiry": 10
    }

    response = requests.post(url, headers=headers, data=payload)

    print("STATUS:", response.status_code)
    print("BODY:", response.text)

    return response.json()

# ==========================
# VERIFY OTP
# ==========================

def verify_msg91_otp(mobile, otp):

    url = "https://control.msg91.com/api/v5/otp/verify"

    headers = {

        "authkey": MSG91_AUTH_KEY

    }

    payload = {

        "mobile": "91" + mobile,

        "otp": otp

    }

    response = requests.post(

        url,

        headers=headers,

        data=payload

    )

    return response.json()

def send_notification(
    user_id,
    user_type,
    message,
    link="",
    image="",
    type="general",
    extra=None
):

    try:
        if user_type == "hr":
            user = User.query.get(user_id)
        else:
            user = CandidateUser.query.get(user_id)

        message = replace_notification_variables(
            message,
            user,
            extra
        )

    except Exception as e:
        print("Variable replacement error:", e)
        user = None

    # Automatically use RecrootEarn logo for system notifications
    # Use app logo whenever no image is provided
    if not image:
        image = "../images/recrootearn_logo.png"   # Place this file in static/uploads/

    db.session.add(
        Notification(
            user_id=user_id,
            user_type=user_type,
            message=message,
            link=link,
            image=image,
            type=type
        )
    )

    db.session.commit()

    try:
        if user and user.fcm_token:
            send_push_notification(
                user.fcm_token,
                "",
                message
            )
    except Exception as e:
        print("Push notification error:", e)

def replace_notification_variables(message, user=None, extra=None):

    if extra is None:
        extra = {}

    if user:

        # Common
        message = message.replace(
            "{{first_name}}",
            getattr(user, "first_name", "") or getattr(user, "full_name", "")
        )

        message = message.replace(
            "{{last_name}}",
            getattr(user, "last_name", "")
        )

        message = message.replace(
            "{{full_name}}",
            getattr(user, "full_name", (
                (getattr(user, "first_name", "") + " " +
                 getattr(user, "last_name", "")).strip()
            ))
        )

        message = message.replace(
            "{{wallet_balance}}",
            str(getattr(user, "wallet_balance", 0))
        )

        message = message.replace(
            "{{city}}",
            str(getattr(user, "city", ""))
        )

        message = message.replace(
            "{{state}}",
            str(getattr(user, "state", ""))
        )

        message = message.replace(
            "{{company}}",
            str(getattr(user, "company_name", ""))
        )

        message = message.replace(
            "{{credits}}",
            str(
                getattr(user, "paid_credits", 0)
                +
                getattr(user, "free_credits", 0)
            )
        )

        message = message.replace(
            "{{paid_credits}}",
            str(getattr(user, "paid_credits", 0))
        )

        message = message.replace(
            "{{free_credits}}",
            str(getattr(user, "free_credits", 0))
        )

    for key, value in extra.items():

        message = message.replace(
            "{{" + key + "}}",
            str(value)
        )

    return message

from datetime import timedelta

def run_notification_automation(trigger, user_id, user_type):

    rule = NotificationAutomation.query.filter_by(
        trigger=trigger,
        enabled=True
    ).first()

    if not rule:
        return

    queue = NotificationQueue(

        user_id=user_id,

        user_type=user_type,

        template_id=rule.template_id,

        send_at=india_time() + timedelta(
            hours=rule.delay_hours
        )

    )

    db.session.add(queue)

    db.session.commit()

def process_notification_queue():

    pending = NotificationQueue.query.filter(

        NotificationQueue.status == "Pending",

        NotificationQueue.send_at <= india_time()

    ).all()

    for item in pending:

        template = NotificationTemplate.query.get(
            item.template_id
        )

        if template:

            send_notification(

                user_id=item.user_id,

                user_type=item.user_type,

                message=f"{template.title}\n\n{template.message}",

                link=template.link,

                type="automation"

            )

        item.status = "Sent"

    db.session.commit()

def send_welcome_email(email, name):
    msg = Message(
        "Welcome to RecrootEarn",
        recipients=[email]
    )

    msg.body = f"""
Hello {name},

Welcome to RecrootEarn!

Your account has been created successfully.

Thank you for joining us.

Regards,
RecrootEarn Team
"""

    mail.send(msg)

def generate_invoice_pdf(user, purchase, payment_id):

    html = render_template(
        "invoice.html",

        logo_path="static/images/invoice_logo.png",

        invoice_no=f"INV-{purchase.created_at.strftime('%Y%m%d')}-{purchase.id:06d}",

        invoice_date=purchase.created_at.strftime("%d %b %Y"),

        payment_id=payment_id,

        customer_name=f"{user.first_name} {user.last_name}",

        company=user.company or "-",

        email=user.email,

        mobile=user.mobile,

        package=purchase.package_name,

        credits=purchase.credits_bought,

        amount=f"{purchase.amount_paid:.2f}"
    )

    pdf = BytesIO()

    HTML(
        string=html,
        base_url=app.root_path
    ).write_pdf(
        target=pdf
    )

    invoice_no = f"INV-{purchase.created_at.strftime('%Y%m%d')}-{purchase.id:06d}"

    invoice_folder = os.path.join(
        app.root_path,
        "static",
        "invoices"
    )

    os.makedirs(invoice_folder, exist_ok=True)

    invoice_path = os.path.join(
        invoice_folder,
        invoice_no + ".pdf"
    )

    with open(invoice_path, "wb") as f:
        f.write(pdf.getvalue())

    return (
        pdf.getvalue(),
        invoice_no,
        invoice_path
    )

def send_invoice_email(user, purchase, payment_id):
    try:

        pdf, invoice_no, invoice_path = generate_invoice_pdf(
            user,
            purchase,
            payment_id
        )

        msg = Message(
            subject=f"Payment Invoice - #{purchase.id}",
            recipients=[user.email]
        )

        msg.body = f"""
Hello {user.first_name},

Thank you for your purchase on RecrootEarn.

Your payment has been received successfully.

Amount Paid : ₹{purchase.amount_paid}
Credits Purchased : {purchase.credits_bought}
Package : {purchase.package_name}

Please find your invoice attached.

Regards,
RecrootEarn Team
"""

        msg.attach(
            filename=f"Invoice_{invoice_no}.pdf",
            content_type="application/pdf",
            data=pdf
        )

        mail.send(msg)

        purchase.invoice_number = invoice_no
        purchase.invoice_file = f"static/invoices/{invoice_no}.pdf"
        purchase.payment_id = payment_id
        purchase.payment_status = "Paid"

        db.session.commit()

    except Exception as e:
        print("Invoice Email Error:", e)

def check_daily_bonus(candidate):

    if (
        candidate.daily_login_completed and
        candidate.daily_apply_completed and
        candidate.daily_follow_completed and
        candidate.daily_referral_completed
    ):

        if not getattr(candidate, "daily_bonus_completed", False):

            candidate.candidate_xp += 15
            candidate.daily_bonus_completed = True

def get_candidate_level(xp):

    levels = [

        ("🌱 Beginner", 0),
        ("🚀 Explorer", 100),
        ("💼 Job Seeker", 300),
        ("⭐ Rising Talent", 700),
        ("🔥 Professional", 1500),
        ("💎 Elite Candidate", 3000),
        ("👑 Career Champion", 6000)

    ]

    current_level = levels[0][0]
    next_level = "MAX"
    progress = 100
    remaining = 0

    for i in range(len(levels)):

        level_name, level_xp = levels[i]

        if xp >= level_xp:
            current_level = level_name

            if i < len(levels) - 1:

                next_level_name, next_level_xp = levels[i + 1]

                remaining = next_level_xp - xp

                progress = (
                    (xp - level_xp)
                    /
                    (next_level_xp - level_xp)
                ) * 100

                next_level = next_level_name

            else:

                remaining = 0
                progress = 100
                next_level = "MAX"

    return {
        "level": current_level,
        "next_level": next_level,
        "remaining": remaining,
        "progress": round(progress),
    }

def process_boosts():
    current_time = india_time().replace(tzinfo=None)

    boosts = BoostPost.query.filter_by(status="Active").all()

    for boost in boosts:

        # Expire only after end date
        if current_time >= boost.expires_at:
            boost.status = "Expired"

    db.session.commit()

@app.before_request
def process_boost_system():

    if request.endpoint == "static":
        return

    process_boosts()

@app.before_request
def check_candidate_session():

    if "candidate_id" in session:

        candidate = CandidateUser.query.get(
            session["candidate_id"]
        )

        if not candidate:
            session.clear()
            return redirect("/candidate-login")

        if session.get("candidate_session_token") != candidate.session_token:

            session.clear()

            flash(
                "Your account was logged in on another device.",
                "warning"
            )

            return redirect("/candidate-login")

@app.context_processor
def inject_notifications():

    unread_notifications = 0

    try:

        if current_user.is_authenticated:

            unread_notifications = Notification.query.filter_by(
                user_id=current_user.id,
                user_type='hr',
                is_read=False
            ).count()

        elif 'candidate_id' in session:

            unread_notifications = Notification.query.filter_by(
                user_id=session['candidate_id'],
                user_type='candidate',
                is_read=False
            ).count()

    except:
        pass

    return dict(
        unread_notifications=unread_notifications
    )

@app.before_request
def check_hr_profile():

    # Not logged in
    if not current_user.is_authenticated:
        return

    # Admin can access everything
    if current_user.is_admin:
        return

    # Routes allowed without profile completion
    allowed_routes = [

        "home",

        "profile",

        "edit_profile",

        "logout",

        "notifications",

        "notification_redirect",

        "mark_notifications_read",

        "static"

    ]

    if request.endpoint in allowed_routes:
        return

    # Check profile completion
    if (current_user.profile_completion or 0) < 80:

        flash(
            "Complete at least 80% of your profile to unlock all features.",
            "warning"
        )

        return redirect(
            url_for("edit_profile")
        )

@app.before_request
def check_candidate_profile():

    # Candidate not logged in
    if "candidate_id" not in session:
        return

    # Routes allowed even if profile is incomplete
    allowed_routes = [

        "candidate_dashboard",

        "candidate_profile",

        "edit_candidate_profile",

        "candidate_logout",

        "static"

    ]

    if request.endpoint in allowed_routes:
        return

    candidate = CandidateUser.query.get(
        session["candidate_id"]
    )

    if not candidate:
        return

    if (candidate.profile_completion or 0) < 80:

        flash(
            "Complete at least 80% of your profile to unlock all features.",
            "warning"
        )

        return redirect(
            url_for("edit_candidate_profile")
        )

@app.before_request
def update_last_login():
    if request.endpoint is None:
        return

    # HR
    if current_user.is_authenticated:
        today = india_time()
        if (
            current_user.last_login is None or
            current_user.last_login.date() != today.date()
        ):
            current_user.last_login = today
            db.session.commit()

    # Candidate
    elif session.get("candidate_id"):
        candidate = CandidateUser.query.get(session["candidate_id"])
        if candidate:
            today = india_time()
            if (
                candidate.last_login is None or
                candidate.last_login.date() != today.date()
            ):
                candidate.last_login = today
                db.session.commit()

    def allowed_product_file(filename):

        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower()
            in ALLOWED_PRODUCT_EXTENSIONS
        )

def get_cart_count(user_id):

    cart = Cart.query.filter_by(
        user_id=user_id
    ).first()

    if not cart:
        return 0

    total = 0

    for item in cart.items:
        total += item.quantity

    return total

@app.context_processor
def inject_cart():

    if current_user.is_authenticated:

        return dict(
            cart_count=get_cart_count(current_user.id)
        )

    return dict(cart_count=0)

def headers(self):

    return{

        "Authorization":"Bearer "+self.token,

        "Content-Type":"application/json"

    }

def check_serviceability(

        self,

        pickup_pincode,

        delivery_pincode,

        weight

):

    response=requests.get(

        BASE_URL+"/courier/serviceability/",

        headers=self.headers(),

        params={

            "pickup_postcode":pickup_pincode,

            "delivery_postcode":delivery_pincode,

            "weight":weight

        }

    )

    return response.json()

def create_order(self,data):

    response=requests.post(

        BASE_URL+"/orders/create/adhoc",

        headers=self.headers(),

        json=data

    )

    return response.json()

def track(self,awb):

    response=requests.get(

        BASE_URL+

        f"/courier/track/awb/{awb}",

        headers=self.headers()

    )

    return response.json()

def label(self,shipment_id):

    response=requests.post(

        BASE_URL+"/courier/generate/label",

        headers=self.headers(),

        json={

            "shipment_id":[shipment_id]

        }

    )

    return response.json()

from datetime import datetime, timedelta

def release_wallet_amount():
    settings = get_business_settings()

    orders = Order.query.filter_by(
        wallet_released=False,
        order_status="Delivered"
    ).all()

    for order in orders:
        if not order.delivered_at:
            continue

        days = (
            datetime.utcnow() -
            order.delivered_at
        ).days

        if days >= settings.seller_payment_hold_days:
            seller = User.query.get(order.seller_id)

            if seller:
                seller.wallet_balance += order.seller_amount
                order.wallet_released = True

    db.session.commit()
# =========================
# USER ROUTES
# =========================

@app.route('/')
def landing():

    return render_template(
        'index.html'
    )

@app.route('/home')
def home_page():

    return render_template(
        'index.html'
    )

@app.route('/splash')
def splash():

    next_page = request.args.get('next', '/home')

    return render_template(
        'splash.html',
        next_page=next_page
    )

@app.route('/dashboard')
@login_required
def home():

    # ==========================
    # Update Last Login
    # ==========================
    current_user.last_login = india_time()

    # ==========================
    # Reset Daily Streaks
    # ==========================
    today = india_time().date()

    if current_user.last_streak_reset != today:
        current_user.daily_login_completed = False
        current_user.daily_upload_completed = False
        current_user.daily_referral_completed = False

        current_user.last_streak_reset = today

    # Today's login completed
    current_user.daily_login_completed = True

    db.session.commit()

    from datetime import date

    industry = request.args.get('industry')
    designation = request.args.get('designation')
    city = request.args.get('city')
    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)

    unlocked_ids = [
        u.candidate_id
        for u in Unlock.query.filter_by(
            user_id=current_user.id
        ).all()
    ]

    # ==========================
    # RECRUITER RANK SYSTEM
    # ==========================

    total_uploads = Candidate.query.filter_by(
        uploaded_by=current_user.id
    ).count()

    if total_uploads <= 100:

        recruiter_rank = "🌱 Beginner Recruiter"
        recruiter_icon = "🌱"
        rank_color = "#22c55e"

        next_rank = "Bronze Recruiter"
        uploads_remaining = 101 - total_uploads

    elif total_uploads <= 500:

        recruiter_rank = "🥉 Bronze Recruiter"
        recruiter_icon = "🥉"
        rank_color = "#cd7f32"

        next_rank = "Silver Recruiter"
        uploads_remaining = 501 - total_uploads

    elif total_uploads <= 1500:

        recruiter_rank = "🥈 Silver Recruiter"
        recruiter_icon = "🥈"
        rank_color = "#9ca3af"

        next_rank = "Gold Recruiter"
        uploads_remaining = 1501 - total_uploads

    elif total_uploads <= 5000:

        recruiter_rank = "🥇 Gold Recruiter"
        recruiter_icon = "🥇"
        rank_color = "#eab308"

        next_rank = "Platinum Recruiter"
        uploads_remaining = 5001 - total_uploads

    elif total_uploads <= 10000:

        recruiter_rank = "💎 Platinum Recruiter"
        recruiter_icon = "💎"
        rank_color = "#06b6d4"

        next_rank = "Elite Recruiter"
        uploads_remaining = 10001 - total_uploads

    else:

        recruiter_rank = "👑 Elite Recruiter"
        recruiter_icon = "👑"
        rank_color = "#7c3aed"

        next_rank = "Maximum Level Reached"
        uploads_remaining = 0

    # ==========================
    # DAILY STREAKS
    # ==========================

    today = india_time().date()

    daily_login_completed = current_user.daily_login_completed

    today_uploads = Candidate.query.filter(
        Candidate.uploaded_by == current_user.id,
        db.func.date(Candidate.created_at) == today
    ).count()

    current_user.daily_upload_completed = (today_uploads >= 10)

    today_referrals = User.query.filter(
        User.referred_by == current_user.referral_code,
        db.func.date(User.created_at) == today
    ).count()

    current_user.daily_referral_completed = (today_referrals > 0)

    db.session.commit()

    daily_upload_completed = current_user.daily_upload_completed
    daily_referral_completed = current_user.daily_referral_completed

    # ==========================
    # CANDIDATE LIST
    # ==========================

    query = Candidate.query.filter(
        Candidate.is_fake == False,
        Candidate.uploaded_by != current_user.id
    )

    if industry:
        query = query.filter_by(category=industry)

    if designation:
        query = query.filter(
            Candidate.designation.contains(designation)
        )

    if city:
        query = query.filter(
            Candidate.city.contains(city)
        )

    if search:
        query = query.filter(
            or_(
                Candidate.name.contains(search),
                Candidate.designation.contains(search),
                Candidate.city.contains(search)
            )
        )

    candidates = query.order_by(
        Candidate.created_at.desc()
    ).paginate(
        page=page,
        per_page=10
    )

    # ==========================
    # DASHBOARD
    # ==========================

    return render_template(
        'dashboard.html',

        candidates=candidates,

        unlocked_ids=unlocked_ids,

        my_uploads_count=total_uploads,
        my_unlocks_count=len(unlocked_ids),

        recruiter_rank=recruiter_rank,
        recruiter_icon=recruiter_icon,
        rank_color=rank_color,

        total_uploads=total_uploads,
        next_rank=next_rank,
        uploads_remaining=uploads_remaining,

        daily_login_completed=daily_login_completed,
        daily_upload_completed=daily_upload_completed,
        daily_referral_completed=daily_referral_completed,

        today_uploads=today_uploads,

        CandidateReview=CandidateReview,
        User=User
    )

@app.route('/admin/notification-center')
@login_required
def admin_notification_center():

    if not current_user.is_admin:
        return redirect('/dashboard')

    notifications = BroadcastNotification.query.order_by(
        BroadcastNotification.created_at.desc()
    ).all()

    templates = NotificationTemplate.query.filter_by(
        is_active=True
    ).order_by(
        NotificationTemplate.name.asc()
    ).all()

    return render_template(
        "admin_notification_center.html",
        notifications=notifications,
        templates=templates
    )

@app.route('/admin/notification-automation')
@login_required
def notification_automation():

    rules = NotificationAutomation.query.all()

    templates = NotificationTemplate.query.filter_by(
        is_active=True
    ).all()

    return render_template(

        "notification_automation.html",

        rules=rules,

        templates=templates

    )

@app.route('/admin/business-settings', methods=['GET', 'POST'])
@login_required
def admin_business_settings():

    if not admin_only():
        return "Access Denied"

    settings = get_business_settings()

    if request.method == "POST":

        try:

            # ======================================
            # HR REFERRAL
            # ======================================

            settings.hr_to_hr_reward = int(request.form.get("hr_to_hr_reward", 200))
            settings.hr_minimum_purchase = int(request.form.get("hr_minimum_purchase", 500))
            settings.hr_daily_referral_limit = int(request.form.get("hr_daily_referral_limit", 10))

            # ======================================
            # CANDIDATE REFERRAL
            # ======================================

            settings.hr_to_candidate_reward = int(request.form.get("hr_to_candidate_reward", 25))
            settings.candidate_to_candidate_reward = int(request.form.get("candidate_to_candidate_reward", 25))
            settings.candidate_daily_referral_limit = int(request.form.get("candidate_daily_referral_limit", 10))

            # ======================================
            # REVENUE SHARING
            # ======================================

            settings.discover_hr_share = int(request.form.get("discover_hr_share", 50))
            settings.discover_admin_share = int(request.form.get("discover_admin_share", 50))

            settings.leads_hr_share = int(request.form.get("leads_hr_share", 50))
            settings.leads_admin_share = int(request.form.get("leads_admin_share", 50))

            settings.self_candidate_admin_share = int(request.form.get("self_candidate_admin_share", 100))

            # ======================================
            # UNLOCK SETTINGS
            # ======================================

            settings.discover_unlock_credits = int(request.form.get("discover_unlock_credits", 2))
            settings.leads_unlock_credits = int(request.form.get("leads_unlock_credits", 2))

            # ======================================
            # WALLET
            # ======================================

            settings.minimum_withdrawal = int(request.form.get("minimum_withdrawal", 500))
            settings.maximum_daily_withdrawal = int(request.form.get("maximum_daily_withdrawal", 5000))

            settings.lead_fresher_paid = int(request.form.get("lead_fresher_paid", 1))
            settings.lead_fresher_free = int(request.form.get("lead_fresher_free", 2))

            settings.lead_experienced_paid = int(request.form.get("lead_experienced_paid", 2))
            settings.lead_experienced_free = int(request.form.get("lead_experienced_free", 4))

            settings.discover_unlock_cost = int(request.form.get("discover_unlock_cost", 2))

            settings.enable_daily_candidate_reward = "enable_daily_candidate_reward" in request.form

            settings.daily_candidate_reward = int(
                request.form.get("daily_candidate_reward", 5)
            )

            settings.daily_reward_login = "daily_reward_login" in request.form

            settings.daily_reward_apply = "daily_reward_apply" in request.form

            settings.daily_reward_follow = "daily_reward_follow" in request.form

            settings.daily_reward_referral = "daily_reward_referral" in request.form

            settings.daily_referral_target = int(
                request.form.get("daily_referral_target", 10)
            )

            settings.daily_candidate_upload_limit = int(
                request.form.get(
                    "daily_candidate_upload_limit",
                    100
                )
            )

            # ======================================
            # FEATURE TOGGLES
            # ======================================

            settings.enable_hr_referral = "enable_hr_referral" in request.form
            settings.enable_candidate_referral = "enable_candidate_referral" in request.form
            settings.enable_revenue_sharing = "enable_revenue_sharing" in request.form
            settings.enable_discover = "enable_discover" in request.form
            settings.enable_leads = "enable_leads" in request.form
            settings.enable_wallet = "enable_wallet" in request.form
            settings.enable_withdrawals = "enable_withdrawals" in request.form

            # ======================================
            # VALIDATIONS
            # ======================================

            if settings.discover_hr_share + settings.discover_admin_share != 100:
                flash("Discover Revenue Share must total 100%.", "danger")
                return redirect(url_for("admin_business_settings"))

            if settings.leads_hr_share + settings.leads_admin_share != 100:
                flash("Leads Revenue Share must total 100%.", "danger")
                return redirect(url_for("admin_business_settings"))

            if settings.self_candidate_admin_share != 100:
                flash("Self Registered Candidate revenue must remain 100% for Admin.", "danger")
                return redirect(url_for("admin_business_settings"))

            if settings.hr_to_hr_reward < 0:
                flash("HR Referral Reward cannot be negative.", "danger")
                return redirect(url_for("admin_business_settings"))

            if settings.hr_to_candidate_reward < 0:
                flash("HR to Candidate Reward cannot be negative.", "danger")
                return redirect(url_for("admin_business_settings"))

            if settings.candidate_to_candidate_reward < 0:
                flash("Candidate Referral Reward cannot be negative.", "danger")
                return redirect(url_for("admin_business_settings"))

            if settings.discover_unlock_credits < 1:
                flash("Discover Unlock Credits must be at least 1.", "danger")
                return redirect(url_for("admin_business_settings"))

            if settings.leads_unlock_credits < 1:
                flash("Lead Unlock Credits must be at least 1.", "danger")
                return redirect(url_for("admin_business_settings"))

            if settings.hr_daily_referral_limit < 1:
                flash("HR Daily Referral Limit must be at least 1.", "danger")
                return redirect(url_for("admin_business_settings"))

            if settings.candidate_daily_referral_limit < 1:
                flash("Candidate Daily Referral Limit must be at least 1.", "danger")
                return redirect(url_for("admin_business_settings"))

            if settings.minimum_withdrawal > settings.maximum_daily_withdrawal:
                flash("Minimum Withdrawal cannot exceed Maximum Daily Withdrawal.", "danger")
                return redirect(url_for("admin_business_settings"))

            # ======================================
            # AUDIT
            # ======================================

            settings.updated_by = current_user.id

            db.session.commit()

            flash("Business Settings Updated Successfully.", "success")

            return redirect(url_for("admin_business_settings"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for("admin_business_settings"))

    return render_template(
        "admin_business_settings.html",
        settings=settings
    )

import requests

@app.route('/verify-otp-backend', methods=['POST'])
def verify_otp_backend():
    req_id = request.form.get('msg91_req_id')
    otp = request.form.get('otp')
    
    # Call MSG91 API to verify
    url = f"https://control.msg91.com/api/v5/otp/verify?otp={otp}&request_id={req_id}"
    headers = {"authkey": "546033TFUN4xUNi6a436063P1"} # Use your actual auth key
    response = requests.get(url, headers=headers)
    
    if response.json().get('type') == 'success':
        return jsonify({"status": "verified"})
    return jsonify({"status": "failed"}), 400

@app.route("/api/save-fcm-token", methods=["POST"])
def save_fcm_token():

    print("FCM API CALLED")

    data = request.get_json()

    token = data.get("token")

    if not token:
        return jsonify({
            "success": False,
            "message": "Token missing"
        }), 400

    # ===========================
    # HR Logged In
    # ===========================
    if current_user.is_authenticated:

        # Remove this token from every other HR
        User.query.filter(
            User.fcm_token == token,
            User.id != current_user.id
        ).update(
            {"fcm_token": None},
            synchronize_session=False
        )

        # Remove this token from every candidate
        CandidateUser.query.filter(
            CandidateUser.fcm_token == token
        ).update(
            {"fcm_token": None},
            synchronize_session=False
        )

        current_user.fcm_token = token

        db.session.commit()

        return jsonify({
            "success": True,
            "user": "hr"
        })

    # ===========================
    # Candidate Logged In
    # ===========================
    if "candidate_id" in session:

        candidate = CandidateUser.query.get(
            session["candidate_id"]
        )

        if candidate:

            # Remove this token from every HR
            User.query.filter(
                User.fcm_token == token
            ).update(
                {"fcm_token": None},
                synchronize_session=False
            )

            # Remove this token from every other Candidate
            CandidateUser.query.filter(
                CandidateUser.fcm_token == token,
                CandidateUser.id != candidate.id
            ).update(
                {"fcm_token": None},
                synchronize_session=False
            )

            candidate.fcm_token = token

            db.session.commit()

            return jsonify({
                "success": True,
                "user": "candidate"
            })

    return jsonify({
        "success": False,
        "message": "Not logged in"
    }), 401

@app.route("/test-push")
def test_push():

    token = "f771DnBkRs6QjmXrAIHLaL:APA91bGm9x_99JYNDV_q1uwvNmuR38h_vrux2G3WX5p-zvXPX-HNohyPO2oL6rzhN0bUx1lyE9LEvMovCviVq_pRL68gxBPAmaao7sqU3jPW3nuFql3ohQY"

    response = send_push_notification(
        token,
        "RecrootEarn",
        "🎉 Push Notifications are working!"
    )

    return {
        "success": True,
        "response": response
    }

@app.route("/candidate-send-otp", methods=["POST"])
def candidate_send_otp():

    mobile = request.form.get("mobile", "").strip()

    if len(mobile) != 10:
        return jsonify({
            "success": False,
            "message": "Enter a valid mobile number."
        })

    # Duplicate check
    if CandidateUser.query.filter_by(mobile=mobile).first():
        return jsonify({
            "success": False,
            "message": "❌ Mobile number already registered."
        })

    try:
        result = send_msg91_otp(mobile)

        return jsonify({
            "success": True,
            "message": "✅ OTP sent successfully."
        })

    except Exception as e:

        print(e)

        return jsonify({
            "success": False,
            "message": "Unable to send OTP."
        })

@app.route("/candidate-verify-otp", methods=["POST"])
def candidate_verify_otp():

    mobile = request.form.get("mobile", "").strip()
    otp = request.form.get("otp", "").strip()

    try:

        result = verify_msg91_otp(mobile, otp)

        if result.get("type") == "success":

            session["candidate_otp_verified"] = True
            session["candidate_mobile"] = mobile

            return jsonify({
                "success": True,
                "message": "✅ Mobile verified successfully."
            })

        return jsonify({
            "success": False,
            "message": "❌ Invalid OTP."
        })

    except Exception as e:

        print(e)

        return jsonify({
            "success": False,
            "message": "OTP verification failed."
        })

@app.route("/candidate-resend-otp", methods=["POST"])
def candidate_resend_otp():

    mobile = request.form.get("mobile", "").strip()

    try:

        send_msg91_otp(mobile)

        return jsonify({
            "success": True,
            "message": "✅ OTP resent successfully."
        })

    except Exception:

        return jsonify({
            "success": False,
            "message": "Unable to resend OTP."
        })

@app.route("/send-otp", methods=["POST"])
def send_otp():

    print("===== SEND OTP ROUTE CALLED =====")

    mobile = request.form.get("mobile", "").strip()

    print("Mobile:", mobile)

    response = send_msg91_otp(mobile)

    print("MSG91 RESPONSE:", response)

    if response.get("type") == "success":

        session["otp_mobile"] = mobile
        session["otp_verified"] = False

        return jsonify({
            "success": True,
            "message": "OTP sent successfully."
        })

    return jsonify({
        "success": False,
        "message": str(response)
    })

@app.route("/verify-otp", methods=["POST"])
def verify_otp():

    mobile = request.form.get("mobile", "").strip()

    otp = request.form.get("otp", "").strip()

    if mobile != session.get("otp_mobile"):

        return jsonify({
            "success": False,
            "message": "Mobile number mismatch."
        })

    response = verify_msg91_otp(mobile, otp)

    if response.get("type") == "success":

        session["otp_verified"] = True

        return jsonify({
            "success": True,
            "message": "Mobile verified successfully."
        })

    return jsonify({
        "success": False,
        "message": "Invalid OTP."
    })

@app.route("/resend-otp", methods=["POST"])
def resend_otp():

    mobile = request.form.get("mobile", "").strip()

    response = send_msg91_otp(mobile)

    if response.get("type") == "success":

        return jsonify({
            "success": True,
            "message": "OTP resent successfully."
        })

    return jsonify({
        "success": False,
        "message": "Unable to resend OTP."
    })

@app.route('/admin/add-automation-rule', methods=['GET', 'POST'])
@login_required
def add_automation_rule():

    templates = NotificationTemplate.query.filter_by(
        is_active=True
    ).all()

    if request.method == "POST":

        rule = NotificationAutomation(

            name=request.form.get("name"),

            template_id=request.form.get("template_id"),

            trigger=request.form.get("trigger"),

            delay_hours=int(
                request.form.get("delay_hours", 0)
            ),

            enabled=True

        )

        db.session.add(rule)

        db.session.commit()

        flash(
            "Automation Rule Created Successfully.",
            "success"
        )

        return redirect(
            "/admin/notification-automation"
        )

    return render_template(
        "add_automation_rule.html",
        templates=templates
    )

@app.route('/admin/notification-templates')
@login_required
def notification_templates():

    templates = NotificationTemplate.query.order_by(
        NotificationTemplate.id.desc()
    ).all()

    return render_template(
        "notification_templates.html",
        templates=templates
    )

@app.route('/admin/delete-template/<int:id>')
@login_required
def delete_notification_template(id):

    template = NotificationTemplate.query.get_or_404(id)

    db.session.delete(template)

    db.session.commit()

    flash("Template Deleted.","success")

    return redirect("/admin/notification-templates")

@app.route('/admin/get-template/<int:id>')
@login_required
def get_notification_template(id):

    template = NotificationTemplate.query.get_or_404(id)

    return jsonify({

        "title": template.title,

        "message": template.message,

        "audience": template.audience,

        "link": template.link

    })

@app.route('/admin/edit-template/<int:id>', methods=['GET','POST'])
@login_required
def edit_notification_template(id):

    template = NotificationTemplate.query.get_or_404(id)

    if request.method == "POST":

        template.name = request.form.get("name")
        template.title = request.form.get("title")
        template.message = request.form.get("message")
        template.audience = request.form.get("audience")
        template.link = request.form.get("link")

        db.session.commit()

        flash("Template Updated Successfully.","success")

        return redirect("/admin/notification-templates")

    return render_template(
        "edit_notification_template.html",
        template=template
    )

@app.route('/admin/edit-candidate/<int:candidate_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_candidate(candidate_id):

    if not current_user.is_admin:
        abort(403)

    candidate = CandidateUser.query.get_or_404(candidate_id)

    if request.method == "POST":

        candidate.full_name = request.form.get("full_name")
        candidate.email = request.form.get("email")
        candidate.mobile = request.form.get("mobile")
        candidate.gender = request.form.get("gender")
        candidate.dob = request.form.get("dob")
        candidate.city = request.form.get("city")
        candidate.state = request.form.get("state")
        candidate.address = request.form.get("address")
        candidate.qualification = request.form.get("qualification")
        candidate.experience = request.form.get("experience")
        candidate.skills = request.form.get("skills")
        candidate.about_me = request.form.get("about_me")

        db.session.commit()

        flash("Candidate details updated successfully.", "success")
        return redirect(url_for("admin_candidate_users"))

    return render_template(
        "admin_edit_candidate.html",
        candidate=candidate
    )

@app.route('/admin/edit-hr/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_hr(user_id):

    if not current_user.is_admin:
        abort(403)

    user = User.query.get_or_404(user_id)

    if request.method == "POST":

        user.first_name = request.form.get("first_name")
        user.last_name = request.form.get("last_name")
        user.username = request.form.get("username")
        user.company = request.form.get("company")
        user.mobile = request.form.get("mobile")
        user.email = request.form.get("email")
        user.hr_type = request.form.get("hr_type")

        user.company_house = request.form.get("company_house")
        user.company_road = request.form.get("company_road")
        user.company_area = request.form.get("company_area")
        user.company_city = request.form.get("company_city")
        user.company_state = request.form.get("company_state")
        user.company_pincode = request.form.get("company_pincode")
        user.company_country = request.form.get("company_country")

        db.session.commit()

        flash("HR details updated successfully.", "success")
        return redirect(url_for("admin_users"))

    return render_template(
        "admin_edit_hr.html",
        user=user
    )

@app.route('/my-uploads')
@login_required
def my_uploads():

    page = request.args.get('page', 1, type=int)

    candidates = Candidate.query.filter_by(
        uploaded_by=current_user.id
    ).order_by(
        Candidate.created_at.desc()
    ).paginate(
        page=page,
        per_page=10,
        error_out=False
    )

    return render_template(
        'my_uploads.html',
        candidates=candidates,
        CandidateReview=CandidateReview,
        User=User,
        Unlock=Unlock
    )

@app.route("/otp-success", methods=["POST"])
def otp_success():

    data = request.get_json()

    session["otp_verified"] = True
    session["otp_mobile"] = data.get("mobile")

    return jsonify({
        "success": True
    })

@app.route('/general-info')
@login_required
def general_info():
    return render_template('general_info.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/admin/referrals')
@login_required
def admin_referrals():

    if not current_user.is_admin:
        return "Access Denied"

    users = User.query.filter(
        User.referred_by != None
    ).all()

    referral_data = []

    for user in users:

        referrer = User.query.filter_by(
            referral_code=user.referred_by
        ).first()

        referral_data.append({
            "user": user,
            "referrer": referrer
        })

    return render_template(
        'admin_referrals.html',
        referral_data=referral_data
    )

@app.route('/admin/install-default-notification-templates')
@login_required
def install_default_notification_templates():

    defaults = [

        {
            "name":"👋 Welcome HR",
            "title":"Welcome to RecrootEarn",
            "message":"Welcome {{first_name}}! Complete your profile and start earning by recruiting candidates.",
            "audience":"hr",
            "link":"/dashboard"
        },

        {
            "name":"👋 Welcome Candidate",
            "title":"Welcome to RecrootEarn",
            "message":"Welcome {{first_name}}! Complete your profile to unlock better job opportunities.",
            "audience":"candidate",
            "link":"/candidate-profile"
        },

        {
            "name":"🔥 Complete Today's Streak",
            "title":"Daily Streak Reminder",
            "message":"Hi {{first_name}}, complete today's streak and earn exciting rewards!",
            "audience":"both",
            "link":"/dashboard"
        },

        {
            "name":"📝 Complete Profile",
            "title":"Complete Your Profile",
            "message":"Your profile is {{profile_completion}}% complete. Finish it to improve visibility.",
            "audience":"candidate",
            "link":"/candidate-profile"
        },

        {
            "name":"💳 Buy Credits",
            "title":"Running Low on Credits",
            "message":"Hi {{first_name}}, purchase more credits to continue unlocking candidates.",
            "audience":"hr",
            "link":"/credits"
        },

        {
            "name":"🎉 Referral Reward",
            "title":"Congratulations!",
            "message":"₹{{amount}} has been credited to your wallet for your successful referral.",
            "audience":"both",
            "link":"/wallet"
        },

        {
            "name":"💰 Wallet Credited",
            "title":"Wallet Updated",
            "message":"₹{{amount}} has been added to your wallet.",
            "audience":"both",
            "link":"/wallet"
        },

        {
            "name":"📈 Upload Candidates",
            "title":"Upload More Candidates",
            "message":"Upload candidates today and increase your earnings.",
            "audience":"hr",
            "link":"/upload-candidate"
        },

        {
            "name":"💼 Apply for Jobs",
            "title":"New Jobs Waiting",
            "message":"New jobs matching your profile are available. Apply now!",
            "audience":"candidate",
            "link":"/jobs"
        },

        {
            "name":"🎊 Festival Wishes",
            "title":"Best Wishes",
            "message":"Wishing you and your family happiness and success.",
            "audience":"both",
            "link":"/"
        }

    ]

    added = 0

    for item in defaults:

        exists = NotificationTemplate.query.filter_by(
            name=item["name"]
        ).first()

        if not exists:

            db.session.add(
                NotificationTemplate(
                    name=item["name"],
                    title=item["title"],
                    message=item["message"],
                    audience=item["audience"],
                    link=item["link"],
                    is_active=True
                )
            )

            added += 1

    db.session.commit()

    flash(f"{added} default templates installed successfully.","success")

    return redirect("/admin/notification-templates")

@app.route('/admin/delete-user/<int:user_id>')
@login_required
def admin_delete_user(user_id):

    user = User.query.get_or_404(user_id)

    db.session.add(
        DeletedAccount(
            account_type="hr",
            full_name=f"{user.first_name} {user.last_name}",
            mobile=user.mobile,
            email=user.email,
            username=user.username,
            referral_reward_used=True,
            deleted_by="admin"
        )
    )

    db.session.delete(user)

    db.session.commit()

    flash("HR deleted successfully")

    return redirect(url_for('admin_users'))

from werkzeug.security import generate_password_hash

@app.route('/admin/reset-password/<int:user_id>')
@login_required
def admin_reset_password(user_id):

    user = User.query.get_or_404(user_id)

    user.password = generate_password_hash("123456")

    db.session.commit()

    flash("Password reset to 123456")

    return redirect(url_for('admin_users'))

# =========================
# LOCKED CANDIDATES
# =========================

@app.route('/locked')
@login_required
def locked():

    designation = request.args.get('designation')
    city = request.args.get('city')
    industry = request.args.get('industry')
    experience = request.args.get('experience')
    lead_filter = request.args.get('lead_filter')

    page = request.args.get('page', 1, type=int)

    # Already unlocked candidates

    unlocked_ids = [

        u.candidate_id

        for u in Unlock.query.filter_by(
            user_id=current_user.id
        ).all()

    ]

    # Base Query

    query = Candidate.query.filter(

        ~Candidate.id.in_(unlocked_ids),

        Candidate.uploaded_by != current_user.id

    )

    # Designation Filter

    if designation:

        query = query.filter(
            Candidate.designation.contains(designation)
        )

    # City Filter

    if city:

        query = query.filter(
            Candidate.city.contains(city)
        )

    # Industry Filter

    if industry:

        query = query.filter_by(
            category=industry
        )

    # Experience Filter

    if experience:

        query = query.filter_by(
            experience=experience
        )

    # Read / Unread Filter

    seen_ids = [

        s.candidate_id

        for s in SeenLead.query.filter_by(
            user_id=current_user.id
        ).all()

    ]

    if lead_filter == "read":

        query = query.filter(
            Candidate.id.in_(seen_ids)
        )

    elif lead_filter == "unread":

        query = query.filter(
            ~Candidate.id.in_(seen_ids)
        )

    # Get all matching candidates

    candidate_list = query.all()

    # Shuffle every refresh

    random.shuffle(candidate_list)

    # Manual pagination

    from math import ceil

    per_page = 10

    start = (page - 1) * per_page

    end = start + per_page

    page_items = candidate_list[start:end]

    class Pagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = ceil(total / per_page)

        @property
        def has_prev(self):
            return self.page > 1

        @property
        def has_next(self):
            return self.page < self.pages

        @property
        def prev_num(self):
            return self.page - 1

        @property
        def next_num(self):
            return self.page + 1

    candidates = Pagination(
        page_items,
        page,
        per_page,
        len(candidate_list)
    )

    # Auto Mark as Read

    for candidate in candidates.items:

        already_seen = SeenLead.query.filter_by(

            user_id=current_user.id,

            candidate_id=candidate.id

        ).first()

        if not already_seen:

            db.session.add(

                SeenLead(

                    user_id=current_user.id,

                    candidate_id=candidate.id

                )

            )

    db.session.commit()

    # Dynamic Filter Values

    cities = [

        c[0]

        for c in db.session.query(
            Candidate.city
        ).filter(

            Candidate.city.isnot(None),

            Candidate.city != ""

        ).distinct().order_by(
            Candidate.city
        ).all()

    ]

    industries = [

        i[0]

        for i in db.session.query(
            Candidate.category
        ).filter(

            Candidate.category.isnot(None),

            Candidate.category != ""

        ).distinct().order_by(
            Candidate.category
        ).all()

    ]

    designations = [

        d[0]

        for d in db.session.query(
            Candidate.designation
        ).filter(

            Candidate.designation.isnot(None),

            Candidate.designation != ""

        ).distinct().order_by(
            Candidate.designation
        ).all()

    ]

    experiences = [

        e[0]

        for e in db.session.query(
            Candidate.experience
        ).filter(

            Candidate.experience.isnot(None),

            Candidate.experience != ""

        ).distinct().order_by(
            Candidate.experience
        ).all()

    ]

    return render_template(

        "locked.html",

        candidates=candidates,

        unlocked_ids=unlocked_ids,

        CandidateReview=CandidateReview,

        User=User,

        cities=cities,

        industries=industries,

        designations=designations,

        experiences=experiences

    )

@app.route("/admin-credit-packages")
@login_required
def admin_credit_packages():

    packages = CreditPackage.query.order_by(
        CreditPackage.display_order.asc()
    ).all()

    return render_template(
        "admin_credit_packages.html",
        packages=packages
    )

@app.route("/send-forgot-otp", methods=["POST"])
def send_forgot_otp():

    mobile = request.form.get("mobile", "").strip()

    if len(mobile) != 10:
        return jsonify({
            "success": False,
            "message": "Enter valid mobile number."
        })

    # Search HR
    user = User.query.filter_by(
        mobile=mobile,
        is_deleted=False
    ).first()

    # Search Candidate
    if not user:
        user = CandidateUser.query.filter_by(
            mobile=mobile,
            is_deleted=False
        ).first()

    if not user:

        return jsonify({
            "success": False,
            "message": "No account found with this mobile number."
        })

    result = send_msg91_otp(mobile)

    if result.get("type") == "success":

        session["forgot_mobile"] = mobile
        session["forgot_verified"] = False

        return jsonify({
            "success": True,
            "message": "OTP sent successfully."
        })

    return jsonify({
        "success": False,
        "message": "Unable to send OTP."
    })

@app.route("/verify-forgot-otp", methods=["POST"])
def verify_forgot_otp():

    mobile = request.form.get("mobile", "").strip()
    otp = request.form.get("otp", "").strip()

    if mobile != session.get("forgot_mobile"):

        return jsonify({
            "success": False,
            "message": "Mobile number mismatch."
        })

    result = verify_msg91_otp(mobile, otp)

    if result.get("type") == "success":

        session["forgot_verified"] = True

        return jsonify({
            "success": True,
            "message": "OTP verified successfully."
        })

    return jsonify({
        "success": False,
        "message": "Invalid OTP."
    })

@app.route("/change-password", methods=["GET", "POST"])
def change_password():

    if "forgot_mobile" not in session:

        flash(
            "Please verify your mobile number first.",
            "warning"
        )

        return redirect(url_for("forgot_password"))

    mobile = session["forgot_mobile"]

    user = User.query.filter_by(
        mobile=mobile,
        is_deleted=False
    ).first()

    if not user:

        user = CandidateUser.query.filter_by(
            mobile=mobile,
            is_deleted=False
        ).first()

    if not user:

        flash(
            "Account not found.",
            "danger"
        )

        session.pop("forgot_mobile", None)

        return redirect(url_for("forgot_password"))

    if request.method == "POST":

        password = request.form.get("password")
        confirm = request.form.get("confirm_password")

        if password != confirm:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect(url_for("change_password"))

        user.password = generate_password_hash(password)

        db.session.commit()

        session.pop("forgot_mobile", None)

        flash(
            "Password changed successfully.",
            "success"
        )

        return redirect(url_for("login"))

    return render_template("change_password.html")

@app.route('/admin/add-notification-template', methods=['GET', 'POST'])
@login_required
def add_notification_template():

    if request.method == "POST":

        template = NotificationTemplate(
            name=request.form.get("name"),
            title=request.form.get("title"),
            message=request.form.get("message"),
            audience=request.form.get("audience"),
            link=request.form.get("link"),
            is_active=True
        )

        db.session.add(template)
        db.session.commit()

        flash("Notification Template Added Successfully.", "success")

        return redirect("/admin/notification-templates")

    return render_template("add_notification_template.html")

@app.route("/report-post/<int:post_id>", methods=["POST"])
def report_post(post_id):

    reason = request.form.get("reason")
    comment = request.form.get("comment")

    # Must be logged in
    if not current_user.is_authenticated and "candidate_id" not in session:
        return jsonify(success=False)

    # Prevent duplicate reports
    existing = None

    if current_user.is_authenticated:

        existing = FeedReport.query.filter_by(
            post_id=post_id,
            hr_id=current_user.id
        ).first()

    else:

        existing = FeedReport.query.filter_by(
            post_id=post_id,
            candidate_id=session["candidate_id"]
        ).first()

    if existing:
        return jsonify(
            success=False,
            message="Already reported."
        )

    report = FeedReport(
        post_id=post_id,
        reason=reason,
        comment=comment
    )

    hidden = HiddenFeed(
        post_id=post_id
    )

    if current_user.is_authenticated:

        report.hr_id = current_user.id
        hidden.hr_id = current_user.id

    else:

        report.candidate_id = session["candidate_id"]
        hidden.candidate_id = session["candidate_id"]

    db.session.add(report)
    db.session.add(hidden)

    db.session.commit()

    return jsonify(success=True)

from sqlalchemy import func

@app.route("/admin/reported-posts")
@login_required
def admin_reported_posts():

    if not admin_only():
        return "Access Denied"

    reports = db.session.query(

        JobPost,

        func.count(FeedReport.id).label("total_reports")

    ).join(

        FeedReport,
        FeedReport.post_id == JobPost.id

    ).group_by(

        JobPost.id

    ).order_by(

        func.count(FeedReport.id).desc()

    ).all()

    return render_template(

        "admin_reported_posts.html",

        reports=reports

    )

@app.route("/admin/invoices")
@login_required
def admin_invoices():

    if not current_user.is_admin:
        flash("Unauthorized", "danger")
        return redirect("/dashboard")

    invoices = CreditPurchase.query.order_by(
        CreditPurchase.created_at.desc()
    ).all()

    return render_template(
        "admin_invoices.html",
        invoices=invoices,
        User=User
    )

@app.route("/admin/view-report/<int:post_id>")
@login_required
def admin_view_report(post_id):

    if not admin_only():
        return "Access Denied"

    post = JobPost.query.get_or_404(post_id)

    reports = FeedReport.query.filter_by(
        post_id=post_id
    ).order_by(
        FeedReport.created_at.desc()
    ).all()

    return render_template(

        "admin_view_report.html",

        post=post,

        reports=reports

    )

@app.route("/admin/delete-reported-post/<int:post_id>")
@login_required
def delete_reported_post(post_id):

    if not admin_only():
        return "Access Denied"

    post = JobPost.query.get_or_404(post_id)

    FeedReport.query.filter_by(
        post_id=post.id
    ).delete()

    HiddenFeed.query.filter_by(
        post_id=post.id
    ).delete()

    Spark.query.filter_by(
        job_id=post.id
    ).delete()

    # Delete uploaded files
    if post.images:

        for file in post.images.split(","):

            path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                file
            )

            if os.path.exists(path):
                os.remove(path)

    db.session.delete(post)

    db.session.commit()

    flash(
        "Reported post deleted successfully.",
        "success"
    )

    return redirect("/admin/reported-posts")

@app.route("/add-credit-package", methods=["GET","POST"])
@login_required
def add_credit_package():

    if request.method == "POST":

        package = CreditPackage(

            package_name=request.form["package_name"],

            credits=int(request.form["credits"]),

            price=float(request.form["price"]),

            badge=request.form["badge"],

            color=request.form["color"],

            description=request.form["description"],

            display_order=int(request.form["display_order"]),

            is_active=bool(int(request.form["is_active"]))

        )

        db.session.add(package)

        db.session.commit()

        flash("Package Added Successfully","success")

        return redirect("/admin-credit-packages")

    return render_template("add_credit_package.html")

@app.route("/edit-credit-package/<int:id>",methods=["GET","POST"])
@login_required
def edit_credit_package(id):

    package = CreditPackage.query.get_or_404(id)

    if request.method=="POST":

        package.package_name = request.form["package_name"]

        package.credits = int(request.form["credits"])

        package.price = float(request.form["price"])

        package.badge = request.form["badge"]

        package.color = request.form["color"]

        package.description = request.form["description"]

        package.display_order = int(request.form["display_order"])

        package.is_active = bool(int(request.form["is_active"]))

        db.session.commit()

        flash("Package Updated","success")

        return redirect("/admin-credit-packages")

    return render_template(
        "edit_credit_package.html",
        package=package
    )

@app.route("/delete-credit-package/<int:id>")
@login_required
def delete_credit_package(id):

    package=CreditPackage.query.get_or_404(id)

    db.session.delete(package)

    db.session.commit()

    flash("Package Deleted","success")

    return redirect("/admin-credit-packages")

@app.route("/toggle-credit-package/<int:id>")
@login_required
def toggle_credit_package(id):

    package=CreditPackage.query.get_or_404(id)

    package.is_active=not package.is_active

    db.session.commit()

    flash("Package Updated","success")

    return redirect("/admin-credit-packages")

@app.route("/package-order/<int:id>",methods=["POST"])
@login_required
def package_order(id):

    package=CreditPackage.query.get_or_404(id)

    package.display_order=int(request.form["display_order"])

    db.session.commit()

    return redirect("/admin-credit-packages")

@app.route('/leads')
@login_required
def leads():

    designation = request.args.get('designation')
    city = request.args.get('city')
    industry = request.args.get('industry')
    experience = request.args.get('experience')
    sort = request.args.get('sort')
    page = request.args.get('page', 1, type=int)
    tab = request.args.get('tab', 'locked')

    # =========================
    # UNLOCKED IDS
    # =========================

    unlocked = Unlock.query.filter_by(
        user_id=current_user.id
    ).all()

    unlocked_ids = [
        u.candidate_id
        for u in unlocked
    ]

    # =========================
    # FILTER OPTIONS
    # =========================

    cities = sorted({

        c[0].strip().title()

        for c in db.session.query(
            func.lower(Candidate.city)
        ).filter(

            Candidate.city.isnot(None),

            Candidate.city != ""

        ).distinct().all()

    })

    designations = sorted({

        d[0].strip().title()

        for d in db.session.query(
            func.lower(Candidate.designation)
        ).filter(

            Candidate.designation.isnot(None),

            Candidate.designation != ""

        ).distinct().all()

    })

    industries = sorted({

        i[0].strip().title()

        for i in db.session.query(
            func.lower(Candidate.category)
        ).filter(

            Candidate.category.isnot(None),

            Candidate.category != ""

        ).distinct().all()

    })

    experiences = sorted({

        e[0]

        for e in db.session.query(
            Candidate.experience
        ).filter(

            Candidate.experience.isnot(None),

            Candidate.experience != ""

        ).distinct().all()

    })

    # =========================
    # MAIN QUERY
    # =========================

    if tab == 'unlocked':

        query = Candidate.query.filter(

            Candidate.id.in_(unlocked_ids),

            Candidate.uploaded_by != current_user.id

        )

    else:

        query = Candidate.query.filter(

            Candidate.id.notin_(unlocked_ids),

            Candidate.uploaded_by != current_user.id

        )

    # =========================
    # FILTERS
    # =========================

    if designation:

        query = query.filter(

            func.lower(Candidate.designation) == designation.lower()

        )

    if city:

        query = query.filter(

            func.lower(Candidate.city) == city.lower()

        )

    if industry:

        query = query.filter(

            func.lower(Candidate.category) == industry.lower()

        )

    if experience:

        query = query.filter(

            Candidate.experience == experience

        )

    # =========================
    # SORTING
    # =========================

    if tab == "locked":

        query = query.order_by(func.random())

    else:

        if sort == "old":
            query = query.order_by(Candidate.id.asc())
        else:
            query = query.order_by(Candidate.id.desc())

    # =========================
    # PAGINATION
    # =========================

    candidates = query.all()

    random.shuffle(candidates)

    per_page = 10
    start = (page - 1) * per_page
    end = start + per_page

    page_items = candidates[start:end]

    class Pagination:
        pass

    pagination = Pagination()
    pagination.items = page_items
    pagination.page = page
    pagination.per_page = per_page
    pagination.total = len(candidates)
    pagination.pages = ceil(len(candidates) / per_page)
    pagination.has_prev = page > 1
    pagination.has_next = page < pagination.pages
    pagination.prev_num = page - 1
    pagination.next_num = page + 1

    candidates = pagination

    # =========================
    # RENDER
    # =========================

    return render_template(

        'leads.html',

        candidates=candidates,

        unlocked_ids=unlocked_ids,

        CandidateReview=CandidateReview,

        User=User,

        tab=tab,

        cities=cities,

        designations=designations,

        industries=industries,

        experiences=experiences

    )

@app.route('/candidate-withdraw', methods=['GET', 'POST'])
def candidate_withdraw():

    if 'candidate_id' not in session:
        return redirect('/candidate-login')

    candidate = CandidateUser.query.get_or_404(
        session['candidate_id']
    )

    settings = get_business_settings()

    if request.method == "POST":

        amount = float(request.form["amount"])
        upi = request.form["upi"]

        if amount < settings.minimum_withdrawal:

            flash(
                f"Minimum withdrawal is ₹{settings.minimum_withdrawal}",
                "danger"
            )

            return redirect("/candidate-withdraw")

        if amount > candidate.wallet_balance:

            flash(
                "Insufficient wallet balance.",
                "danger"
            )

            return redirect("/candidate-withdraw")

        withdrawal = CandidateWithdrawal(

            candidate_id=candidate.id,

            amount=amount,

            upi_id=upi,

            status="Pending"

        )

        db.session.add(withdrawal)

        # Reserve wallet amount immediately
        candidate.wallet_balance -= amount

        db.session.add(

            CandidateWalletHistory(

                candidate_id=candidate.id,

                amount=-amount,

                action="Withdrawal Requested"

            )

        )

        db.session.commit()

        flash(
            "Withdrawal request submitted successfully.",
            "success"
        )

        return redirect("/candidate-withdraw")

    withdrawals = CandidateWithdrawal.query.filter_by(
        candidate_id=candidate.id
    ).order_by(
        CandidateWithdrawal.created_at.desc()
    ).all()

    return render_template(
        "candidate_withdraw.html",
        candidate=candidate,
        withdrawals=withdrawals,
        settings=settings
    )

@app.route('/approve-withdrawal/<int:id>')
@login_required
def approve_withdrawal(id):

    if not current_user.is_admin:
        return "Access Denied"

    withdrawal = Withdrawal.query.get_or_404(id)

    if withdrawal.status != "Pending":

        flash(
            "This withdrawal request has already been processed.",
            "warning"
        )

        return redirect("/admin/withdrawals")

    withdrawal.status = "Approved"

    withdrawal.approved_at = india_time()

    db.session.commit()

    flash(
        "Withdrawal approved successfully.",
        "success"
    )

    return redirect("/admin/withdrawals")

@app.route('/reject-withdrawal/<int:id>')
@login_required
def reject_withdrawal(id):

    if not current_user.is_admin:

        flash(
            "Access Denied.",
            "danger"
        )

        return redirect("/dashboard")

    withdrawal = Withdrawal.query.get_or_404(id)

    if withdrawal.status != "Pending":

        flash(
            "This withdrawal request has already been processed.",
            "warning"
        )

        return redirect("/admin/withdrawals")

    # Refund wallet balance
    user = User.query.get(withdrawal.user_id)

    if user:

        user.wallet_balance += withdrawal.amount

        # Optional: Add wallet history
        history = CreditHistory(

            user_id=user.id,

            amount=withdrawal.amount,

            action=f"Withdrawal Rejected - Amount Refunded ₹{withdrawal.amount}"

        )

        db.session.add(history)

    withdrawal.status = "Rejected"

    withdrawal.rejected_at = india_time()

    db.session.commit()

    flash(
        "Withdrawal rejected and amount refunded successfully.",
        "success"
    )

    return redirect("/admin/withdrawals")

@app.route('/admin-candidate-withdrawals')
@login_required
def admin_candidate_withdrawals():

    withdrawals = CandidateWithdrawal.query.order_by(
        CandidateWithdrawal.created_at.desc()
    ).all()

    return render_template(
        "admin_candidate_withdrawals.html",
        withdrawals=withdrawals
    )

@app.route('/admin/template/<int:id>')
@login_required
def get_notification_template_old(id):

    template = NotificationTemplate.query.get_or_404(id)

    return jsonify({

        "title": template.title,

        "message": template.message,

        "audience": template.audience,

        "link": template.link

    })

@app.route('/admin/send-notification', methods=['POST'])
@login_required
def admin_send_notification():

    title = request.form.get("title")
    message = request.form.get("message")
    send_to = request.form.get("send_to")
    selected_users = request.form.get("selected_users", "")
    schedule_date = request.form.get("schedule_date")
    schedule_time = request.form.get("schedule_time")

    if not title or not message:
        flash("Please fill all fields.", "danger")
        return redirect("/admin/notification-center")

    # Save notification history
    from datetime import datetime

    schedule_datetime = None
    status = "Sent"

    if schedule_date and schedule_time:

        schedule_datetime = datetime.strptime(
            f"{schedule_date} {schedule_time}",
            "%Y-%m-%d %H:%M"
        )

        status = "Scheduled"

    broadcast = BroadcastNotification(

        title=title,
        message=message,
        send_to=send_to,
        selected_users=selected_users,
        status=status,
        schedule_time=schedule_datetime

    )

    db.session.add(broadcast)

    if status == "Scheduled":

        db.session.commit()

        flash(
            "Notification scheduled successfully.",
            "success"
        )

        return redirect("/admin/notification-center")

    full_message = f"{title}\n\n{message}"

    # ===========================
    # SEND TO SELECTED HR
    # ===========================
    if send_to == "selected_hr":

        ids = [
            int(x)
            for x in selected_users.split(",")
            if x.strip()
        ]

        users = User.query.filter(
            User.id.in_(ids)
        ).all()

        for user in users:

            send_notification(
                user_id=user.id,
                user_type="hr",
                message=full_message,
                link="/dashboard",
                type="admin_broadcast"
            )

    # ===========================
    # SEND TO ALL HR
    # ===========================
    elif send_to == "hr":

        users = User.query.all()

        for user in users:

            send_notification(
                user_id=user.id,
                user_type="hr",
                message=full_message,
                link="/dashboard",
                type="admin_broadcast"
            )

    # ===========================
    # SEND TO SELECTED CANDIDATES
    # ===========================
    elif send_to == "selected_candidate":

        ids = [
            int(x)
            for x in selected_users.split(",")
            if x.strip()
        ]

        candidates = CandidateUser.query.filter(
            CandidateUser.id.in_(ids)
        ).all()

        for candidate in candidates:

            send_notification(
                user_id=candidate.id,
                user_type="candidate",
                message=full_message,
                link="/candidate-home",
                type="admin_broadcast"
            )

    # ===========================
    # SEND TO ALL CANDIDATES
    # ===========================
    elif send_to == "candidate":

        candidates = CandidateUser.query.all()

        for candidate in candidates:

            send_notification(
                user_id=candidate.id,
                user_type="candidate",
                message=full_message,
                link="/candidate-home",
                type="admin_broadcast"
            )

    # ===========================
    # SEND TO BOTH
    # ===========================
    elif send_to == "both":

        users = User.query.all()

        for user in users:

            send_notification(
                user_id=user.id,
                user_type="hr",
                message=full_message,
                link="/dashboard",
                type="admin_broadcast"
            )

        candidates = CandidateUser.query.all()

        for candidate in candidates:

            send_notification(
                user_id=candidate.id,
                user_type="candidate",
                message=full_message,
                link="/candidate-home",
                type="admin_broadcast"
            )

    broadcast.sent_at = datetime.now(IST)
    broadcast.status = "Sent"

    db.session.commit()

    flash("Push notification sent successfully.", "success")

    return redirect("/admin/notification-center")

@app.route('/admin/search-users')
@login_required
def admin_search_users():

    q = request.args.get("q", "").strip()

    user_type = request.args.get("type")

    results = []

    if len(q) < 2:
        return jsonify(results)

    if user_type == "hr":

        users = User.query.filter(
            db.or_(
                User.first_name.ilike(f"%{q}%"),
                User.last_name.ilike(f"%{q}%"),
                User.username.ilike(f"%{q}%"),
                User.mobile.ilike(f"%{q}%")
            )
        ).limit(20).all()

        for u in users:

            results.append({
                "id": u.id,
                "name": f"{u.first_name} {u.last_name}",
                "username": u.username,
                "mobile": u.mobile
            })

    elif user_type == "candidate":

        candidates = CandidateUser.query.filter(
            db.or_(
                CandidateUser.full_name.ilike(f"%{q}%"),
                CandidateUser.mobile.ilike(f"%{q}%")
            )
        ).limit(20).all()

        for c in candidates:

            results.append({
                "id": c.id,
                "name": c.full_name,
                "username": "",
                "mobile": c.mobile
            })

    return jsonify(results)

@app.route('/approve-candidate-withdrawal/<int:id>')
@login_required
def approve_candidate_withdrawal(id):

    withdrawal = CandidateWithdrawal.query.get_or_404(id)

    if withdrawal.status != "Pending":
        return redirect('/admin-candidate-withdrawals')

    candidate = CandidateUser.query.get(
        withdrawal.candidate_id
    )

    if candidate:

        withdrawal.status = "Approved"

        db.session.add(

            CandidateWalletHistory(

                candidate_id=candidate.id,

                amount=0,

                action="Withdrawal Approved"

            )

        )

        send_notification(
            user_id=candidate.id,
            user_type="candidate",
            message=f"Your withdrawal request of ₹{withdrawal.amount} has been approved.",
            link="/candidate-withdraw",
            type="withdraw_approved"
        )

    db.session.commit()

    flash(
        "Withdrawal Approved.",
        "success"
    )

    return redirect('/admin-candidate-withdrawals')

@app.route('/reject-candidate-withdrawal/<int:id>')
@login_required
def reject_candidate_withdrawal(id):

    withdrawal = CandidateWithdrawal.query.get_or_404(id)

    if withdrawal.status != "Pending":
        return redirect('/admin-candidate-withdrawals')

    candidate = CandidateUser.query.get(
        withdrawal.candidate_id
    )

    if candidate:

        candidate.wallet_balance += withdrawal.amount

        db.session.add(

            CandidateWalletHistory(

                candidate_id=candidate.id,

                amount=withdrawal.amount,

                action="Withdrawal Rejected - Amount Refunded"

            )

        )

        send_notification(
            user_id=candidate.id,
            user_type="candidate",
            message=f"Your withdrawal request of ₹{withdrawal.amount} was rejected. The amount has been refunded to your wallet.",
            link="/candidate-withdraw",
            type="withdraw_rejected"
        )

    withdrawal.status = "Rejected"

    db.session.commit()

    flash(
        "Withdrawal Rejected.",
        "warning"
    )

    return redirect('/admin-candidate-withdrawals')

@app.route('/candidate-payment-info', methods=['GET', 'POST'])
def candidate_payment_info():

    if 'candidate_id' not in session:
        return redirect('/candidate-login')

    candidate = CandidateUser.query.get_or_404(
        session['candidate_id']
    )

    if request.method == "POST":

        candidate.upi_id = request.form.get("upi_id")

        candidate.bank_name = request.form.get("bank_name")

        candidate.account_holder = request.form.get("account_holder")

        candidate.account_number = request.form.get("account_number")

        candidate.ifsc_code = request.form.get("ifsc_code")

        db.session.commit()

        flash(
            "Payment information updated successfully.",
            "success"
        )

        return redirect("/candidate-withdraw")

    return render_template(
        "candidate_payment_info.html",
        candidate=candidate
    )

@app.route('/candidate-wallet')
def candidate_wallet():

    if 'candidate_id' not in session:
        return redirect('/candidate-login')

    candidate = CandidateUser.query.get_or_404(
        session['candidate_id']
    )

    history = CandidateWalletHistory.query.filter_by(
        candidate_id=candidate.id
    ).order_by(
        CandidateWalletHistory.created_at.desc()
    ).all()

    return render_template(
        "candidate_wallet.html",
        candidate=candidate,
        history=history
    )

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        mobile = request.form['mobile'].strip()

        password = request.form['password']

        entered_referral = request.form.get(
            "referral_code",
            ""
        ).strip().upper()

        # VALIDATE MOBILE

        if not re.fullmatch(r"[6-9]\d{9}", mobile):

            flash(
                "Please enter a valid 10-digit Indian mobile number.",
                "danger"
            )

            return redirect('/register')

        # OTP CHECK

        if not session.get("otp_verified"):

            flash(
                "Please verify your mobile number using OTP.",
                "danger"
            )

            return redirect('/register')

        if session.get("otp_mobile") != mobile:

            flash(
                "OTP verification does not match the entered mobile number.",
                "danger"
            )

            return redirect('/register')

        # MOBILE EXISTS

        existing_hr = User.query.filter_by(
            mobile=mobile
        ).first()

        existing_candidate = CandidateUser.query.filter_by(
            mobile=mobile
        ).first()

        if existing_hr or existing_candidate:

            deleted = DeletedAccount.query.filter_by(
                mobile=mobile
            ).first()

            if not deleted:

                flash(
                    "Mobile number already exists.",
                    "danger"
                )

                return redirect('/register')

        # REFERRAL

        referrer = None

        if entered_referral:

            referrer = User.query.filter_by(
                referral_code=entered_referral
            ).first()

        # CREATE USER

        user = User(

            mobile=mobile,

            password=generate_password_hash(password),

            referral_code=generate_referral_code(),

            referred_by=(
                referrer.referral_code
                if referrer
                else None
            ),

            is_approved=True,

            profile_photo="default.png"

        )

        # ADMIN ACCOUNT
        # Replace with your mobile number

        if mobile == "6261568334":

            user.is_admin = True

        db.session.add(user)

        if referrer:

            referrer.total_referrals += 1

        db.session.commit()

        # CLEAR OTP SESSION

        session.pop("otp_verified", None)
        session.pop("otp_mobile", None)

        return render_template(
            "register_success.html"
        )

    return render_template(
        "register.html"
    )

@app.route("/candidate-otp-success", methods=["POST"])
def candidate_otp_success():

    data = request.get_json()

    session["candidate_otp_verified"] = True
    session["candidate_mobile"] = data.get("mobile")

    return jsonify({
        "success": True
    })

@app.route('/candidate-register', methods=['GET', 'POST'])
def candidate_register():

    if request.method == 'POST':

        # ==========================
        # OTP VERIFICATION CHECK
        # ==========================
        if not session.get("candidate_otp_verified"):

            flash(
                "Please verify your mobile number first.",
                "danger"
            )

            return redirect('/candidate-register')

        # ==========================
        # BASIC DETAILS
        # ==========================

        mobile = request.form['mobile'].strip()
        password = request.form['password']

        entered_code = request.form.get(
            "referral_code",
            ""
        ).strip().upper()

        # ==========================
        # FIND REFERRER
        # ==========================

        referred_hr = User.query.filter_by(
            referral_code=entered_code
        ).first()

        referred_candidate = None

        if not referred_hr:

            referred_candidate = CandidateUser.query.filter_by(
                candidate_referral_code=entered_code
            ).first()

        # ==========================
        # VALIDATE MOBILE
        # ==========================

        if not re.fullmatch(r"[6-9]\d{9}", mobile):

            flash(
                "Please enter a valid 10-digit Indian mobile number.",
                "danger"
            )

            return redirect('/candidate-register')

        # ==========================
        # CHECK MOBILE
        # ==========================

        existing_hr_mobile = User.query.filter_by(
            mobile=mobile
        ).first()

        existing_candidate_mobile = CandidateUser.query.filter_by(
            mobile=mobile
        ).first()

        if existing_hr_mobile or existing_candidate_mobile:

            deleted = DeletedAccount.query.filter_by(
                mobile=mobile
            ).first()

            if not deleted:

                flash(
                    "Mobile number already exists.",
                    "danger"
                )

                return redirect('/candidate-register')

        # ==========================
        # CREATE CANDIDATE
        # ==========================

        candidate = CandidateUser(

            mobile=mobile,

            password=generate_password_hash(password),

            candidate_referral_code=generate_candidate_referral_code(),

            referred_by_hr_id=(
                referred_hr.id
                if referred_hr
                else None
            ),

            referred_by_hr_code=(
                referred_hr.referral_code
                if referred_hr
                else None
            ),

            referred_by_candidate_code=(
                referred_candidate.candidate_referral_code
                if referred_candidate
                else None
            ),

            referred_by_candidate_id=(
                referred_candidate.id
                if referred_candidate
                else None
            )

        )

        db.session.add(candidate)

        db.session.commit()

        # ==========================
        # CLEAR OTP SESSION
        # ==========================

        session.pop("candidate_otp_mobile", None)
        session.pop("candidate_otp_verified", None)
        session.pop("candidate_mobile", None)

        flash(
            "Registration Successful. Please Login.",
            "success"
        )

        return redirect('/candidate-login')

    ref = request.args.get("ref", "").upper()

    return render_template(
        "candidate_register.html",
        referral_code=ref
    )

@app.route('/candidate-login', methods=['GET', 'POST'])
def candidate_login():

    if request.method == 'POST':

        import uuid
        from datetime import date

        mobile = request.form['mobile'].strip()
        password = request.form['password']

        user = CandidateUser.query.filter_by(
            mobile=mobile
        ).first()

        # (Optional) If candidates can also login with mobile
        # if not user:
        #     user = CandidateUser.query.filter_by(
        #         mobile=login_id
        #     ).first()

        # Candidate blocked by admin
        if user and user.is_deleted:

            flash(
                'This account has been disabled by Admin. Please create a new account.',
                'danger'
            )

            return redirect('/candidate-register')

        # Normal login
        if user and check_password_hash(
            user.password,
            password
        ):

            today = date.today()

            # Reset daily tasks on a new day
            if user.last_streak_reset != today:

                user.daily_login_completed = False
                user.daily_apply_completed = False
                user.daily_follow_completed = False
                user.daily_referral_completed = False
                user.daily_reward_claimed = False

                user.last_streak_reset = today

            # Mark daily login completed
            if not user.daily_login_completed:

                user.daily_login_completed = True

            # Check daily reward
            check_daily_reward(user)

            # Single device login
            token = str(uuid.uuid4())

            user.session_token = token

            # Generate App Token if not already present
            if not user.app_token:
                user.app_token = secrets.token_hex(64)

            user.last_login = india_time()

            db.session.commit()

            session.clear()

            is_app = request.headers.get("X-App") == "RecrootEarn"

            if is_app:
                session.permanent = True

            session["candidate_id"] = user.id
            session["candidate_session_token"] = token

            flash(
                "Login Successful",
                "success"
            )

            return redirect("/candidate-feed")

        flash(
            "Invalid Mobile Number or Password",
            "danger"
        )

    return render_template("candidate_login.html")

@app.route('/candidate-dashboard')
def candidate_dashboard():

    if 'candidate_id' not in session:
        return redirect('/candidate-login')

    candidate = CandidateUser.query.get_or_404(
        session['candidate_id']
    )

    # ==========================
    # Update Last Login
    # ==========================
    candidate.last_login = india_time()
    db.session.commit()

    # ==========================
    # Candidate Level
    # ==========================

    level = get_candidate_level(
        candidate.candidate_xp
    )

    # ==========================
    # Top Cards
    # ==========================

    applied_jobs = JobApplication.query.filter_by(
        candidate_id=candidate.id
    ).count()

    interviews = JobApplication.query.filter(
        JobApplication.candidate_id == candidate.id,
        JobApplication.status == "Interviewed"
    ).count()

    referrals = candidate.successful_referrals

    wallet_balance = candidate.wallet_balance

    # ==========================
    # Daily Streaks
    # ==========================

    daily_login_completed = candidate.daily_login_completed

    daily_apply_completed = candidate.daily_apply_completed

    daily_follow_completed = candidate.daily_follow_completed

    daily_referral_completed = candidate.daily_referral_completed

    settings = get_business_settings()

    return render_template(

        "candidate_dashboard.html",

        candidate=candidate,

        wallet_balance=wallet_balance,

        applied_jobs=applied_jobs,

        interviews=interviews,

        settings=settings,

        referrals=referrals,

        candidate_xp=candidate.candidate_xp,

        candidate_level=level["level"],

        next_level=level["next_level"],

        remaining_xp=level["remaining"],

        progress=level["progress"],

        daily_login_completed=daily_login_completed,

        daily_apply_completed=daily_apply_completed,

        daily_follow_completed=daily_follow_completed,

        daily_referral_completed=daily_referral_completed

    )

@app.route('/candidate-support', methods=['GET','POST'])
def candidate_support():

    if 'candidate_id' not in session:
        return redirect('/candidate-login')

    candidate = CandidateUser.query.get(
        session['candidate_id']
    )

    if request.method == 'POST':

        ticket = SupportTicket(
            user_id=candidate.id,
            user_type='candidate',
            subject=request.form['subject'],
            message=request.form['message']
        )

        db.session.add(ticket)

        db.session.flush()  # generates ticket.id

        # NOTIFICATION

        send_notification(
            user_id=candidate.id,
            user_type="candidate",
            message="Support ticket submitted successfully",
            link="/candidate-support",
            type="support"
        )

        db.session.commit()

        flash(
            "Support ticket submitted successfully",
            "success"
        )

        return redirect('/candidate-support')

    page = request.args.get(
        'page',
        1,
        type=int
    )

    tickets = SupportTicket.query.filter_by(
        user_id=candidate.id,
        user_type='candidate'
    ).order_by(
        SupportTicket.created_at.desc()
    ).paginate(
        page=page,
        per_page=10
    )

    return render_template(
        'support.html',
        tickets=tickets,
        SupportReply=SupportReply
    )

@app.route('/candidate-general-info')
def candidate_general_info():

    if 'candidate_id' not in session:
        return redirect('/candidate-login')

    return render_template('general_info.html')

@app.route('/admin/send-now/<int:id>')
@login_required
def send_now_notification(id):

    notification = BroadcastNotification.query.get_or_404(id)

    full_message = f"{notification.title}\n\n{notification.message}"

    # ==========================
    # Selected HR
    # ==========================
    if notification.send_to == "selected_hr":

        ids = [
            int(x)
            for x in notification.selected_users.split(",")
            if x.strip()
        ]

        users = User.query.filter(
            User.id.in_(ids)
        ).all()

        for user in users:

            send_notification(

                user_id=user.id,

                user_type="hr",

                message=full_message,

                link="/dashboard",

                type="admin_broadcast"

            )

    # ==========================
    # All HR
    # ==========================
    elif notification.send_to == "hr":

        users = User.query.all()

        for user in users:

            send_notification(

                user_id=user.id,

                user_type="hr",

                message=full_message,

                link="/dashboard",

                type="admin_broadcast"

            )

    # ==========================
    # Selected Candidate
    # ==========================
    elif notification.send_to == "selected_candidate":

        ids = [
            int(x)
            for x in notification.selected_users.split(",")
            if x.strip()
        ]

        candidates = CandidateUser.query.filter(
            CandidateUser.id.in_(ids)
        ).all()

        for candidate in candidates:

            send_notification(

                user_id=candidate.id,

                user_type="candidate",

                message=full_message,

                link="/candidate-home",

                type="admin_broadcast"

            )

    # ==========================
    # All Candidate
    # ==========================
    elif notification.send_to == "candidate":

        candidates = CandidateUser.query.all()

        for candidate in candidates:

            send_notification(

                user_id=candidate.id,

                user_type="candidate",

                message=full_message,

                link="/candidate-home",

                type="admin_broadcast"

            )

    # ==========================
    # Both
    # ==========================
    elif notification.send_to == "both":

        users = User.query.all()

        for user in users:

            send_notification(

                user_id=user.id,

                user_type="hr",

                message=full_message,

                link="/dashboard",

                type="admin_broadcast"

            )

        candidates = CandidateUser.query.all()

        for candidate in candidates:

            send_notification(

                user_id=candidate.id,

                user_type="candidate",

                message=full_message,

                link="/candidate-home",

                type="admin_broadcast"

            )

    notification.status = "Sent"

    notification.sent_at = india_time()

    db.session.commit()

    flash(
        "Notification sent successfully.",
        "success"
    )

    return redirect("/admin/notification-center")

@app.route('/admin/edit-notification/<int:id>', methods=['GET','POST'])
@login_required
def edit_notification(id):

    notification = BroadcastNotification.query.get_or_404(id)

    if request.method == "POST":

        notification.title = request.form.get("title")

        notification.message = request.form.get("message")

        notification.send_to = request.form.get("send_to")

        schedule_date = request.form.get("schedule_date")
        schedule_time = request.form.get("schedule_time")

        if schedule_date and schedule_time:

            from datetime import datetime

            notification.schedule_time = datetime.strptime(
                f"{schedule_date} {schedule_time}",
                "%Y-%m-%d %H:%M"
            )

            notification.status = "Scheduled"

        db.session.commit()

        flash(
            "Notification updated successfully.",
            "success"
        )

        return redirect("/admin/notification-center")

    return render_template(
        "edit_notification.html",
        notification=notification
    )

@app.route('/admin/pause-notification/<int:id>')
@login_required
def pause_notification(id):

    notification = BroadcastNotification.query.get_or_404(id)

    notification.is_paused = not notification.is_paused

    db.session.commit()

    flash(
        "Notification status updated.",
        "success"
    )

    return redirect("/admin/notification-center")

@app.route('/admin/delete-notification/<int:id>')
@login_required
def delete_notification(id):

    notification = BroadcastNotification.query.get_or_404(id)

    db.session.delete(notification)

    db.session.commit()

    flash(
        "Notification deleted successfully.",
        "success"
    )

    return redirect("/admin/notification-center")

@app.route('/candidate-profile')
def candidate_profile():

    if 'candidate_id' not in session:
        return redirect('/candidate-login')

    candidate = CandidateUser.query.get(
        session['candidate_id']
    )
  
    # ----------------------------
    # PROFILE REMINDER
    # ----------------------------

    today = date.today()

    # Reset daily count
    if (
        candidate.last_profile_reminder is None or
        candidate.last_profile_reminder.date() != today
    ):
        candidate.profile_reminders_today = 0

    followers_count = Follow.query.filter_by(
        followed_candidate_id=candidate.id
    ).count()

    following_count = Follow.query.filter_by(
        follower_candidate_id=candidate.id
    ).count()

    # ----------------------------
    # PROFILE COMPLETION
    # ----------------------------

    completion = 0

    if candidate.profile_photo:
        completion += 10

    if candidate.resume_file:
        completion += 10

    if candidate.about_me:
        completion += 10

    if candidate.skills:
        completion += 10

    if candidate.city:
        completion += 10

    if candidate.qualification:
        completion += 10

    if candidate.dob:
        completion += 10

    if candidate.education:
        completion += 10

    if candidate.interested_fields:
        completion += 10

    if candidate.career_level == "Experienced":

        if (
            candidate.company_name
            and candidate.designation
        ):
            completion += 10

    if completion < 100:

        if (
            candidate.profile_reminders_today < 4 and
            (
                candidate.last_profile_reminder is None or
                datetime.utcnow() - candidate.last_profile_reminder >= timedelta(hours=3)
            )
        ):

            messages = [
                f"🚀 Your profile is {completion}% complete. Complete it to unlock more job opportunities.",
                "📄 Add your resume to increase your chances of getting hired.",
                "⭐ Complete your profile to become more visible to recruiters.",
                "🎯 You're just a few steps away from a 100% profile. Complete it today!"
            ]

            send_notification(
                user_id=candidate.id,
                user_type="candidate",
                message=random.choice(messages),
                link="/candidate-profile",
                type="profile_completion"
            )

            candidate.last_profile_reminder = datetime.utcnow()
            candidate.profile_reminders_today += 1

            db.session.commit()

    else:

        completion += 10

    return render_template(

        'candidate_profile_view.html',

        candidate=candidate,

        followers_count=followers_count,

        following_count=following_count,

        profile_completion=completion

    )

@app.route('/edit-candidate-profile', methods=['GET', 'POST'])
def edit_candidate_profile():

    if 'candidate_id' not in session:
        return redirect('/candidate-login')

    candidate = CandidateUser.query.get(
        session['candidate_id']
    )

    if request.method == 'POST':

        candidate.full_name = request.form['full_name']
        candidate.email = request.form['email']

        dob = request.form.get("dob")

        if dob:
            candidate.dob = datetime.strptime(
                dob,
                "%Y-%m-%d"
            ).date()

        candidate.city = request.form['city']
        candidate.qualification = request.form['qualification']
        candidate.career_level = request.form['career_level']

        candidate.company_name = request.form.get(
            'company_name',
            ''
        )

        candidate.designation = request.form.get(
            'designation',
            ''
        )

        candidate.experience_from = request.form.get(
            'experience_from',
            ''
        )

        candidate.experience_to = request.form.get(
            'experience_to',
            ''
        )

        candidate.education = request.form['education']
        candidate.skills = request.form['skills']
        candidate.about_me = request.form['about_me']

        candidate.interested_fields = ",".join(
            request.form.getlist(
                "interested_fields"
            )
        )

        # ----------------------------
        # PROFILE PHOTO
        # ----------------------------

        profile_photo = request.files.get(
            "profile_photo"
        )

        if profile_photo and profile_photo.filename:

            filename = secure_filename(
                profile_photo.filename
            )

            profile_photo.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )
            )

            candidate.profile_photo = filename

        # ----------------------------
        # RESUME
        # ----------------------------

        resume = request.files.get(
            "resume_file"
        )

        if resume and resume.filename:

            filename = secure_filename(
                resume.filename
            )

            resume.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )
            )

            candidate.resume_file = filename

    # ----------------------------
    # PROFILE COMPLETION
    # ----------------------------

    completion = 0

    if candidate.profile_photo:
        completion += 10

    if candidate.resume_file:
        completion += 10

    if candidate.about_me:
        completion += 10

    if candidate.skills:
        completion += 10

    if candidate.city:
        completion += 10

    if candidate.qualification:
        completion += 10

    if candidate.dob:
        completion += 10

    if candidate.education:
        completion += 10

    if candidate.interested_fields:
        completion += 10

    if candidate.career_level == "Experienced":

        if (
            candidate.company_name
            and candidate.designation
        ):
            completion += 10

    else:

        completion += 10

    # Save profile completion
    candidate.profile_completion = completion

    db.session.commit()

    if candidate.email and not candidate.welcome_email_sent:
        send_welcome_email(
            candidate.email,
            candidate.full_name
        )
        candidate.welcome_email_sent = True
        db.session.commit()

    if request.method == 'POST':

        flash(
            "Profile Updated",
            "success"
        )

        return redirect(
            url_for("edit_candidate_profile")
        )

    return render_template(

        'edit_candidate_profile.html',

        candidate=candidate,

        profile_completion=completion

    )

@app.route('/candidate-forgot-password', methods=['GET', 'POST'])
def candidate_forgot_password():

    if request.method == "POST":

        email = request.form["email"].strip()
        mobile = request.form["mobile"].strip()

        candidate = CandidateUser.query.filter_by(
            email=email,
            mobile=mobile
        ).first()

        if not candidate:

            flash(
                "Invalid Email or Mobile Number.",
                "danger"
            )

            return redirect("/candidate-forgot-password")

        session["candidate_reset_id"] = candidate.id

        return redirect("/candidate-reset-password")

    return render_template(
        "candidate_forgot_password.html"
    )

@app.route('/candidate-reset-password', methods=['GET', 'POST'])
def candidate_reset_password():

    if "candidate_reset_id" not in session:

        return redirect("/candidate-login")

    candidate = CandidateUser.query.get(
        session["candidate_reset_id"]
    )

    if request.method == "POST":

        candidate.password = generate_password_hash(
            request.form["password"]
        )

        db.session.commit()

        session.pop(
            "candidate_reset_id",
            None
        )

        flash(
            "Password Updated Successfully.",
            "success"
        )

        return redirect("/candidate-login")

    return render_template(
        "candidate_reset_password.html"
    )

@app.route('/hr/<int:id>')
def hr_profile(id):

    hr = User.query.get_or_404(id)

    jobs = JobPost.query.filter_by(
        hr_id=hr.id
    ).order_by(
        JobPost.created_at.desc()
    ).all()

    return render_template(
        'hr_profile.html',
        hr=hr,
        jobs=jobs
    )

@app.route('/job-view/<int:job_id>')
def job_view(job_id):

    job = JobPost.query.get_or_404(job_id)

    hr = User.query.get(job.hr_id)

    applied_jobs = []

    # Candidate
    if 'candidate_id' in session:

        applications = JobApplication.query.filter_by(
            candidate_id=session['candidate_id']
        ).all()

        applied_jobs = [a.job_id for a in applications]

    # HR
    elif current_user.is_authenticated:

        applications = JobApplication.query.filter_by(
            applicant_hr_id=current_user.id
        ).all()

        applied_jobs = [a.job_id for a in applications]

    return render_template(
        "job_view.html",
        job=job,
        hr=hr,
        applied_jobs=applied_jobs
    )

@app.route('/candidate-referral')
def candidate_referral():

    if not session.get("candidate_id"):
        return redirect("/candidate-login")

    settings = get_business_settings()

    candidate = CandidateUser.query.get_or_404(
        session["candidate_id"]
    )

    # Generate referral code if it doesn't exist
    if not candidate.candidate_referral_code:

        candidate.candidate_referral_code = generate_candidate_referral_code()
        db.session.commit()

    # Candidates referred by this candidate
    referrals = CandidateUser.query.filter_by(
        referred_by_candidate_id=candidate.id
    ).order_by(
        CandidateUser.id.desc()
    ).all()

    # Referral link
    referral_link = (
        request.host_url.rstrip("/")
        + "/candidate-register?ref="
        + candidate.candidate_referral_code
    )

    return render_template(
        "candidate_referral.html",
        candidate=candidate,
        referrals=referrals,
        settings=settings,
        referral_link=referral_link
    )

@app.route("/boost-post/<int:job_id>", methods=["GET", "POST"])
@login_required
def boost_post(job_id):

    job = JobPost.query.get_or_404(job_id)

    # Only owner can boost
    if job.hr_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("feed"))

    settings = get_business_settings()

    existing_boost = BoostPost.query.filter(
        BoostPost.job_id == job.id,
        BoostPost.status == "Active"
    ).first()

    if existing_boost:
        flash(
            "This post is already boosted.",
            "warning"
        )
        return redirect(url_for("boost_post", job_id=job.id))

    if request.method == "POST":

        boost_type = request.form.get("boost_type")
        state = request.form.get("state", "")
        selected_cities = request.form.getlist("cities")
        days = int(request.form.get("days", 1))

        # -----------------------
        # Validation
        # -----------------------

        if days < settings.boost_min_days:
            flash(
                f"Minimum boost duration is {settings.boost_min_days} day(s).",
                "danger"
            )
            return redirect(request.url)

        if days > settings.boost_max_days:
            flash(
                f"Maximum boost duration is {settings.boost_max_days} day(s).",
                "danger"
            )
            return redirect(request.url)

        total_credits = 0

        # -----------------------
        # Credit Calculation
        # -----------------------

        if boost_type == "city":

            if len(selected_cities) == 0:
                flash("Please select at least one city.", "danger")
                return redirect(request.url)

            total_credits = (
                len(selected_cities)
                * days
                * settings.boost_city_price
            )

        elif boost_type == "state":

            total_credits = (
                days
                * settings.boost_state_price
            )

        elif boost_type == "pan_india":

            total_credits = (
                days
                * settings.boost_pan_india_price
            )

        else:

            flash("Invalid boost type.", "danger")
            return redirect(request.url)

        # -----------------------
        # Credit Check
        # -----------------------

        if current_user.paid_credits < total_credits:

            flash(
                "You don't have enough paid credits.",
                "danger"
            )

            return redirect(request.url)

        # -----------------------
        # Deduct Credits
        # -----------------------

        current_user.paid_credits -= total_credits

        db.session.add(
            CreditHistory(
                user_id=current_user.id,
                amount=-total_credits,
                action="Boost Promotion"
            )
        )

        # -----------------------
        # Save Boost
        # -----------------------

        boost = BoostPost(
            job_id=job.id,
            hr_id=current_user.id,
            boost_type=boost_type,
            state=state,
            days=days,
            total_credits=total_credits,

            starts_at=india_time(),
            expires_at=india_time() + timedelta(days=days),

            status="Active",

            impressions=0,
            clicks=0,
            applications=0,

            credits_used=0,
            credits_remaining=total_credits,

            days_completed=0,
            last_credit_deduction=None
        )

        db.session.add(boost)
        db.session.flush()

        # -----------------------
        # Save Cities
        # -----------------------

        if boost_type == "city":

            for city in selected_cities:

                db.session.add(
                    BoostCity(
                        boost_id=boost.id,
                        city=city
                    )
                )

        db.session.commit()

        flash(
            f"Your post has been boosted successfully using {total_credits} credits.",
            "success"
        )

        return redirect(url_for("feed"))

    locations = (

        db.session.query(
            func.lower(JobPost.location)
        )

        .filter(
            JobPost.location.isnot(None),
            JobPost.location != ""
        )

        .distinct()

        .order_by(
            func.lower(JobPost.location)
        )

        .all()

    )

    locations = [
        loc[0].title()
        for loc in locations
    ]

    return render_template(
        "boost_post.html",
        job=job,
        settings=settings,
        locations=locations
    )

@app.route("/manage-boost/<int:job_id>")
@login_required
def manage_boost(job_id):

    job = JobPost.query.get_or_404(job_id)

    boost = BoostPost.query.filter(
        BoostPost.job_id == job.id,
        BoostPost.status.in_(["Active", "Paused"])
    ).order_by(
        BoostPost.id.desc()
    ).first()

    if not boost:
        flash("No active boost found.")
        return redirect(url_for("feed"))

    # Analytics
    ctr = 0
    if boost.impressions > 0:
        ctr = round(
            (boost.clicks / boost.impressions) * 100,
            2
        )

    application_rate = 0
    if boost.clicks > 0:
        application_rate = round(
            (boost.applications / boost.clicks) * 100,
            2
        )

    days_remaining = max(
        0,
        boost.days - boost.days_completed
    )

    return render_template(
        "manage_boost.html",
        job=job,
        boost=boost,
        ctr=ctr,
        application_rate=application_rate,
        days_remaining=days_remaining
    )

@app.route("/pause-boost/<int:boost_id>")
@login_required
def pause_boost(boost_id):

    boost = BoostPost.query.get_or_404(boost_id)

    if boost.hr_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("feed"))

    if boost.status != "Active":
        flash("Only active boosts can be paused.", "warning")
        return redirect(url_for("manage_boost", job_id=boost.job_id))

    boost.status = "Paused"

    db.session.commit()

    flash("Boost paused successfully.", "success")

    return redirect(url_for("manage_boost", job_id=boost.job_id))

@app.route("/resume-boost/<int:boost_id>")
@login_required
def resume_boost(boost_id):

    boost = BoostPost.query.get_or_404(boost_id)

    if boost.hr_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("feed"))

    if boost.status != "Paused":
        flash("Only paused boosts can be resumed.", "warning")
        return redirect(url_for("manage_boost", job_id=boost.job_id))

    boost.status = "Active"

    db.session.commit()

    flash("Boost resumed successfully.", "success")

    return redirect(url_for("manage_boost", job_id=boost.job_id))

@app.route("/end-boost/<int:boost_id>")
@login_required
def end_boost(boost_id):

    boost = BoostPost.query.get_or_404(boost_id)

    if boost.hr_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("feed_post"))

    if boost.status == "Ended":
        flash("Boost is already ended.", "warning")
        return redirect(url_for("manage_boost", job_id=boost.job_id))

    boost.status = "Ended"

    db.session.commit()

    flash("Boost ended successfully.", "success")

    return redirect(url_for("feed_post"))

@app.route("/admin/boost-settings", methods=["GET", "POST"])
@login_required
def admin_boost_settings():

    if not admin_only():
        return redirect(url_for("feed"))

    settings = get_business_settings()

    if request.method == "POST":

        settings.enable_boost_posts = "enable_boost_posts" in request.form

        settings.boost_city_price = int(
            request.form["boost_city_price"]
        )

        settings.boost_pan_india_price = int(
            request.form["boost_pan_india_price"]
        )

        settings.boost_min_days = int(
            request.form["boost_min_days"]
        )

        settings.boost_max_days = int(
            request.form["boost_max_days"]
        )

        settings.boost_max_active_posts = int(
            request.form["boost_max_active_posts"]
        )

        settings.boost_max_impressions = int(
            request.form["boost_max_impressions"]
        )

        settings.boost_credits_per_day = int(
            request.form["boost_credits_per_day"]
        )

        db.session.commit()

        flash(
            "Boost settings updated successfully.",
            "success"
        )

        return redirect(url_for("admin_boost_settings"))

    return render_template(
        "admin_boost_settings.html",
        settings=settings
    )

@app.route("/admin/boosts")
@login_required
def admin_boosts():

    if not admin_only():
        return redirect(url_for("feed"))

    boosts = (
        BoostPost.query
        .order_by(
            BoostPost.created_at.desc()
        )
        .all()
    )

    return render_template(
        "admin_boosts.html",
        boosts=boosts
    )

@app.route('/company/<int:id>')
def company_profile(id):

    hr = User.query.get_or_404(id)

    jobs = JobPost.query.filter_by(
        hr_id=id
    ).order_by(
        JobPost.created_at.desc()
    ).all()

    followers_count = Follow.query.filter_by(
        followed_hr_id=id
    ).count()

    is_following = False

    if 'candidate_id' in session:

        existing_follow = Follow.query.filter_by(
            follower_candidate_id=session['candidate_id'],
            followed_hr_id=id
        ).first()

        if existing_follow:
            is_following = True

    elif current_user.is_authenticated:

        existing_follow = Follow.query.filter_by(
            follower_hr_id=current_user.id,
            followed_hr_id=id
        ).first()

        if existing_follow:
            is_following = True

    return render_template(
        'company_profile.html',
        hr=hr,
        jobs=jobs,
        followers_count=followers_count,
        is_following=is_following
    )

@app.route('/update-application-status/<int:id>', methods=['POST'])
@login_required
def update_application_status(id):

    print("UPDATE APPLICATION STATUS ROUTE CALLED")

    settings = get_business_settings()

    application = JobApplication.query.get_or_404(id)
    job = JobPost.query.get_or_404(application.job_id)

    if job.hr_id != current_user.id:
        return "Access Denied"

    new_status = request.form.get("status")
    application.status = new_status

    # ==========================================
    # HR -> CANDIDATE REFERRAL REWARD
    # ==========================================

    if (
        settings.enable_hr_referral
        and new_status == "Interviewed"
    ):

        candidate = CandidateUser.query.get(
            application.candidate_id
        )

        if (
            candidate
            and candidate.referred_by_hr_id
            and not candidate.hr_referral_reward_given
        ):

            # Profile completion
            completion = 0

            if candidate.profile_photo:
                completion += 10

            if candidate.resume_file:
                completion += 10

            if candidate.about_me:
                completion += 10

            if candidate.skills:
                completion += 10

            if candidate.city:
                completion += 10

            if candidate.qualification:
                completion += 10

            if candidate.dob:
                completion += 10

            if candidate.education:
                completion += 10

            if candidate.interested_fields:
                completion += 10

            if candidate.career_level == "Experienced":

                if candidate.company_name and candidate.designation:
                    completion += 10

            else:
                completion += 10

            print("STATUS =", new_status)

            candidate = CandidateUser.query.get(application.candidate_id)

            print("Candidate =", candidate.full_name)
            print("HR ID =", candidate.referred_by_hr_id)
            print("Candidate ID =", candidate.referred_by_candidate_id)
            print("HR Reward Given =", candidate.hr_referral_reward_given)
            print("Candidate Reward Given =", candidate.candidate_referral_reward_given)

            print("Completion =", completion)
            print("HR ID =", candidate.referred_by_hr_id)
            print("Candidate ID =", candidate.referred_by_candidate_id)

            if completion >= 100:

                referring_hr = User.query.get(
                    candidate.referred_by_hr_id
                )

                if referring_hr:

                    already_rewarded = ReferralRewardHistory.query.filter_by(
                        mobile=candidate.mobile,
                        reward_type="hr"
                    ).first()

                    if not already_rewarded:

                        safe_wallet_credit(
                            referring_hr,
                            settings.hr_to_candidate_reward
                        )

                        referring_hr.referral_earnings += (
                            settings.hr_to_candidate_reward
                        )

                        referring_hr.successful_referrals += 1

                        candidate.hr_referral_reward_given = True

                        candidate.revenue_owner_type = "hr"
                        candidate.revenue_owner_id = referring_hr.id

                        db.session.add(
                            ReferralRewardHistory(

                        mobile=candidate.mobile,
                                reward_type="hr"
                            )
                        )

                        db.session.add(
                            Earnings(
                                user_id=referring_hr.id,
                                amount=settings.hr_to_candidate_reward,
                                reason=f"Candidate Referral Reward - {candidate.full_name}"
                            )
                        )

                        send_notification(
                            user_id=referring_hr.id,
                            user_type="hr",
                            message=f"Congratulations! ₹{settings.hr_to_candidate_reward} has been credited to your wallet for referring {candidate.full_name}.",
                            link="/wallet",
                            image=candidate.profile_photo,
                            type="referral_reward"
                        )

    # ==========================================
    # CANDIDATE -> CANDIDATE REFERRAL REWARD
    # ==========================================

    if (
        settings.enable_candidate_referral
        and candidate.referred_by_candidate_id
        and not candidate.candidate_referral_reward_given
    ):

        referring_candidate = CandidateUser.query.get(
            candidate.referred_by_candidate_id
        )

        if referring_candidate:

           already_rewarded = ReferralRewardHistory.query.filter_by(
               mobile=candidate.mobile,
               reward_type="candidate"
           ).first()

           if not already_rewarded:

               safe_wallet_credit(
                   referring_candidate,
                   settings.candidate_to_candidate_reward
               )

               referring_candidate.referral_earnings += (
                   settings.candidate_to_candidate_reward
               )

               referring_candidate.successful_referrals += 1

               candidate.candidate_referral_reward_given = True

               db.session.add(
                   ReferralRewardHistory(       
                       mobile=candidate.mobile,
                       reward_type="candidate"
                   )
               )

               db.session.add(
                   CandidateWalletHistory(
                       candidate_id=referring_candidate.id,
                       amount=settings.candidate_to_candidate_reward,
                       action=f"Referral Reward - {candidate.full_name}"
                   )
               )

               db.session.add(
                   Notification(
                       user_id=referring_candidate.id,
                       user_type="candidate",
                       message=f"You earned ₹{settings.candidate_to_candidate_reward} because {candidate.full_name} completed Interview.",
                       link="/candidate-wallet",
                       image=candidate.profile_photo,
                       type="candidate_referral_reward"
                   )
               )

               send_notification(
                   user_id=referring_candidate.id,
                   user_type="candidate",
                   message=f"🎉 Congratulations! ₹{settings.candidate_to_candidate_reward} has been credited to your wallet for referring {candidate.full_name}.",
                   link="/candidate-wallet",
                   image=candidate.profile_photo,
                   type="candidate_referral_reward"
               )

    db.session.commit()

    flash(
        "Candidate status updated successfully.",
        "success"
    )

    return redirect(request.referrer)

@app.route('/admin/deleted-accounts')
@login_required
def admin_deleted_accounts():

    if not admin_only():
        return "Access Denied"

    search = request.args.get("search", "").strip()

    query = DeletedAccount.query

    if search:

        query = query.filter(
            db.or_(
                DeletedAccount.full_name.contains(search),
                DeletedAccount.mobile.contains(search),
                DeletedAccount.username.contains(search),
                DeletedAccount.email.contains(search)
            )
        )

    deleted_accounts = query.order_by(
        DeletedAccount.id.desc()
    ).all()

    return render_template(
        "admin_deleted_accounts.html",
        deleted_accounts=deleted_accounts,
        total_deleted=len(deleted_accounts)
    )

from flask_login import login_user
from flask import request, jsonify

@app.route("/api/app-auto-login", methods=["POST"])
def app_auto_login():

    data = request.get_json()

    token = data.get("app_token")

    if not token:
        return jsonify({
            "success": False
        }), 401

    # HR
    user = User.query.filter_by(app_token=token).first()

    if user:

        login_user(user, remember=True)

        session["session_token"] = user.session_token

        return jsonify({
            "success": True,
            "role": "hr"
        })

    # Candidate
    candidate = CandidateUser.query.filter_by(app_token=token).first()

    if candidate:

        session["candidate_id"] = candidate.id
        session["candidate_session_token"] = candidate.session_token

        return jsonify({
            "success": True,
            "role": "candidate"
        })

    return jsonify({
        "success": False
    }), 401

@app.route('/admin/referral-history')
@login_required
def admin_referral_history():

    if not admin_only():
        return "Access Denied"

    referral_data = []

    # =====================================
    # HR REFERRALS
    # =====================================

    hrs = User.query.all()

    for hr in hrs:

        # HRs referred by this HR
        hr_referred = User.query.filter_by(
            referred_by=hr.referral_code
        ).count()

        # Candidates referred by this HR
        candidate_referred = CandidateUser.query.filter_by(
            referred_by_hr_id=hr.id
        ).count()

        active = CandidateUser.query.filter_by(
            referred_by_hr_id=hr.id,
            is_deleted=False
        ).count()

        deleted = CandidateUser.query.filter_by(
            referred_by_hr_id=hr.id,
            is_deleted=True
        ).count()

        interviewed = JobApplication.query.join(
            CandidateUser,
            CandidateUser.id == JobApplication.candidate_id
        ).filter(
            CandidateUser.referred_by_hr_id == hr.id,
            JobApplication.status == "Interviewed"
        ).count()

        referral_data.append({

            "type": "HR",

            "name": f"{hr.first_name} {hr.last_name}",

            "mobile": hr.mobile,

            "referral_code": hr.referral_code,

            "hr_referred": hr_referred,

            "candidate_referred": candidate_referred,

            "active": active,

            "deleted": deleted,

            "interviewed": interviewed,

            "earned": hr.referral_earnings,

            "wallet": hr.wallet_balance

        })

    # =====================================
    # CANDIDATE REFERRALS
    # =====================================

    candidates = CandidateUser.query.all()

    for c in candidates:

        candidate_referred = CandidateUser.query.filter_by(
            referred_by_candidate_id=c.id
        ).count()

        active = CandidateUser.query.filter_by(
            referred_by_candidate_id=c.id,
            is_deleted=False
        ).count()

        deleted = CandidateUser.query.filter_by(
            referred_by_candidate_id=c.id,
            is_deleted=True
        ).count()

        interviewed = JobApplication.query.join(
            CandidateUser,
            CandidateUser.id == JobApplication.candidate_id
        ).filter(
            CandidateUser.referred_by_candidate_id == c.id,
            JobApplication.status == "Interviewed"
        ).count()

        referral_data.append({

            "type": "Candidate",

            "name": c.full_name,

            "mobile": c.mobile,

            "referral_code": c.candidate_referral_code,

            "hr_referred": 0,

            "candidate_referred": candidate_referred,

            "active": active,

            "deleted": deleted,

            "interviewed": interviewed,

            "earned": c.referral_earnings,

            "wallet": c.wallet_balance

        })

    # =====================================
    # SEARCH
    # =====================================

    search = request.args.get("search", "").strip().lower()

    if search:

        referral_data = [

            r for r in referral_data

            if (
                search in (r["name"] or "").lower()
                or search in (r["mobile"] or "").lower()
                or search in (r["referral_code"] or "").lower()
            )

        ]

    # =====================================
    # SORT
    # =====================================

    referral_data.sort(
        key=lambda x: x["earned"] or 0,
        reverse=True
    )

    return render_template(
        "admin_referral_history.html",
        referral_data=referral_data
    )

@app.route('/check-email')
def check_email():

    email = request.args.get("email", "").strip().lower()

    exists = (
        User.query.filter_by(email=email).first()
        or
        CandidateUser.query.filter_by(email=email).first()
    )

    return jsonify({
        "exists": bool(exists)
    })

@app.route('/candidate/<int:id>')
@login_required
def view_candidates(id):

    settings = get_business_settings()

    candidate = CandidateUser.query.get_or_404(id)

    followers_count = Follow.query.filter_by(
        followed_candidate_id=id
    ).count()

    is_following = Follow.query.filter_by(
        follower_hr_id=current_user.id,
        followed_candidate_id=id
    ).first()

    contact_unlocked = CandidateContactUnlock.query.filter_by(
        hr_id=current_user.id,
        candidate_user_id=id
    ).first()

    has_applied = JobApplication.query.join(
        JobPost,
        JobPost.id == JobApplication.job_id
    ).filter(
        JobApplication.candidate_id == candidate.id,
        JobPost.hr_id == current_user.id
    ).first()

    return render_template(
        "candidate_view.html",
        candidate=candidate,
        followers_count=followers_count,
        is_following=is_following,
        contact_unlocked=contact_unlocked,
        has_applied=has_applied,
        settings=settings
    )

@app.route('/follow-hr/<int:id>')
def follow_hr(id):

    from datetime import date

    if 'candidate_id' not in session:
        return redirect('/candidate-login')

    hr_id = id

    existing = Follow.query.filter_by(
        follower_candidate_id=session['candidate_id'],
        followed_hr_id=hr_id
    ).first()

    candidate = CandidateUser.query.get(session['candidate_id'])

    if existing:

        db.session.delete(existing)

        send_notification(
            user_id=hr_id,
            user_type="hr",
            message=f"{candidate.full_name} unfollowed you",
            link=f"/candidate/{candidate.id}",
            image=candidate.profile_photo,
            type="unfollow"
        )

    else:

        db.session.add(
            Follow(
                follower_candidate_id=session['candidate_id'],
                followed_hr_id=hr_id
            )
        )

        send_notification(
            user_id=hr_id,
            user_type="hr",
            message=f"{candidate.full_name} started following you",
            link=f"/candidate/{candidate.id}",
            image=candidate.profile_photo,
            type="follow"
        )

        # ==========================
        # DAILY FOLLOW TASK
        # ==========================

        today = date.today()

        if candidate.last_streak_reset != today:

            candidate.daily_login_completed = False
            candidate.daily_apply_completed = False
            candidate.daily_follow_completed = False
            candidate.daily_referral_completed = False
            candidate.daily_reward_claimed = False

            candidate.last_streak_reset = today

        if not candidate.daily_follow_completed:
            candidate.daily_follow_completed = True

        # Check if all daily tasks are completed
        check_daily_reward(candidate)

    db.session.commit()

    # Return to the same page
    next_page = request.args.get("next")

    if next_page:
        return redirect(next_page)

    return redirect(request.referrer or "/discover-hr")

@app.route('/admin-revenue-dashboard')
@login_required
def admin_revenue_dashboard():

    total_platform = db.session.query(
        db.func.sum(PlatformEarning.amount)
    ).scalar() or 0

    total_hr_wallet = db.session.query(
        db.func.sum(User.wallet_balance)
    ).scalar() or 0

    total_candidate_wallet = db.session.query(
        db.func.sum(CandidateUser.wallet_balance)
    ).scalar() or 0

    total_hr_referrals = db.session.query(
        db.func.sum(User.referral_earnings)
    ).scalar() or 0

    total_candidate_referrals = db.session.query(
        db.func.sum(CandidateUser.referral_earnings)
    ).scalar() or 0

    pending_candidate = CandidateWithdrawal.query.filter_by(
        status="Pending"
    ).count()

    approved_candidate = CandidateWithdrawal.query.filter_by(
        status="Approved"
    ).count()

    total_leads_unlock = Unlock.query.count()

    total_discover_unlock = CandidateContactUnlock.query.count()

    total_hr = User.query.count()

    total_candidates = CandidateUser.query.count()

    return render_template(

        "admin_revenue_dashboard.html",

        total_platform=total_platform,

        total_hr_wallet=total_hr_wallet,

        total_candidate_wallet=total_candidate_wallet,

        total_hr_referrals=total_hr_referrals,

        total_candidate_referrals=total_candidate_referrals,

        pending_candidate=pending_candidate,

        approved_candidate=approved_candidate,

        total_leads_unlock=total_leads_unlock,

        total_discover_unlock=total_discover_unlock,

        total_hr=total_hr,

        total_candidates=total_candidates

    )

from flask import jsonify

@app.route("/spark/<int:job_id>", methods=["POST"])
@login_required
def spark(job_id):

    job = JobPost.query.get_or_404(job_id)

    # -----------------------------
    # HR Spark
    # -----------------------------
    if current_user.is_authenticated:

        existing = Spark.query.filter_by(
            job_id=job.id,
            hr_id=current_user.id
        ).first()

        if existing:

            db.session.delete(existing)
            sparked = False

        else:

            db.session.add(
                Spark(
                    job_id=job.id,
                    hr_id=current_user.id
                )
            )

            sparked = True

            if job.hr_id != current_user.id:

                send_notification(
                    user_id=job.hr_id,
                    user_type="hr",
                    message=f"{current_user.first_name} {current_user.last_name} sparked your video.",
                    link=f"/job-view/{job.id}",
                    image=current_user.profile_photo,
                    type="spark"
                )

        db.session.commit()

        # Refresh job to get updated spark count
        db.session.refresh(job)

        return jsonify({
            "success": True,
            "count": len(job.sparks),
            "sparked": sparked
        })

    return jsonify({
        "success": False
    })

@app.route("/candidate-spark/<int:job_id>", methods=["POST"])
def candidate_spark(job_id):

    if "candidate_id" not in session:
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    job = JobPost.query.get_or_404(job_id)

    candidate = CandidateUser.query.get_or_404(
        session["candidate_id"]
    )

    existing = Spark.query.filter_by(
        job_id=job.id,
        candidate_id=candidate.id
    ).first()

    if existing:

        db.session.delete(existing)
        sparked = False

    else:

        db.session.add(
            Spark(
                job_id=job.id,
                candidate_id=candidate.id
            )
        )

        sparked = True

        send_notification(
            user_id=job.hr_id,
            user_type="hr",
            message=f"{candidate.full_name} sparked your video.",
            link=f"/job-view/{job.id}",
            image=candidate.profile_photo,
            type="spark"
        )

    db.session.commit()

    db.session.refresh(job)

    return jsonify({
        "success": True,
        "count": len(job.sparks),
        "sparked": sparked
    })

@app.route('/follow-hr-user/<int:id>')
@login_required
def follow_hr_user(id):

    # Prevent self-follow

    if current_user.id == id:
        return redirect(f'/company/{id}')

    existing = Follow.query.filter_by(
        follower_hr_id=current_user.id,
        followed_hr_id=id
    ).first()

    if existing:

        db.session.delete(existing)

        send_notification(
            user_id=id,
            user_type="hr",
            message=f"{current_user.first_name} {current_user.last_name} unfollowed you",
            link=f"/company/{current_user.id}",
            image=current_user.profile_photo,
            type="unfollow"
        )

    else:

        db.session.add(
            Follow(
                follower_hr_id=current_user.id,
                followed_hr_id=id
            )
        )

        send_notification(
            user_id=id,
            user_type="hr",
            message=f"{current_user.first_name} {current_user.last_name} started following you",
            link=f"/company/{current_user.id}",
            image=current_user.profile_photo,
            type="follow"
        )

    db.session.commit()

    return redirect(request.referrer)

@app.route('/follow-candidate/<int:id>')
@login_required
def follow_candidate(id):

    existing = Follow.query.filter_by(
        follower_hr_id=current_user.id,
        followed_candidate_id=id
    ).first()

    if existing:

        db.session.delete(existing)

    else:

        follow = Follow(
            follower_hr_id=current_user.id,
            followed_candidate_id=id
        )

        db.session.add(follow)

    db.session.commit()

    return redirect(request.referrer)

@app.route('/unlock-contact/<int:id>')
@login_required
def unlock_contact(id):

    settings = get_business_settings()

    existing = CandidateContactUnlock.query.filter_by(
        hr_id=current_user.id,
        candidate_user_id=id
    ).first()

    if existing:
        flash("Already unlocked")
        return redirect(request.referrer)

    candidate = CandidateUser.query.get_or_404(id)

    cost = settings.discover_unlock_credits

    paid_credit_used = False
    purchase = None

    # =====================================
    # USE PAID CREDITS FIRST
    # =====================================

    if current_user.paid_credits >= cost:

        paid_credit_used = True

        current_user.paid_credits -= cost

        purchase = CreditPurchase.query.filter(
            CreditPurchase.user_id == current_user.id,
            CreditPurchase.credits_remaining > 0
        ).order_by(
            CreditPurchase.created_at.asc()
        ).first()

        if purchase:
            purchase.credits_remaining -= cost

    # =====================================
    # OTHERWISE USE FREE CREDITS
    # =====================================

    elif current_user.credits >= cost:

        current_user.credits -= cost

    # =====================================
    # NOT ENOUGH CREDITS
    # =====================================

    else:

        flash(f"Need {cost} credits")

        return redirect(request.referrer)

    # =====================================
    # SAVE UNLOCK
    # =====================================

    db.session.add(
        CandidateContactUnlock(
            hr_id=current_user.id,
            candidate_user_id=id
        )
    )

    db.session.add(
        CreditHistory(
            user_id=current_user.id,
            amount=-cost,
            action="Unlocked Candidate Contact"
        )
    )

    # =====================================
    # REVENUE SHARING ONLY FOR PAID CREDITS
    # =====================================

    if (
        paid_credit_used
        and purchase
        and settings.enable_revenue_sharing
    ):

        revenue = purchase.price_per_credit * cost

        if candidate.referred_by_hr_id:

            owner = User.query.get(candidate.referred_by_hr_id)

            if owner:

                hr_share = revenue * settings.discover_hr_share / 100

                admin_share = revenue * settings.discover_admin_share / 100

                owner.wallet_balance += hr_share

                db.session.add(
                    Earnings(
                        user_id=owner.id,
                        amount=hr_share,
                        purchase_id=purchase.id,
                        reason="Discover Candidate Unlock"
                    )
                )

                db.session.add(
                    PlatformEarning(
                        user_id=current_user.id,
                        amount=admin_share,
                        purchase_id=purchase.id,
                        reason="Discover Candidate Unlock"
                    )
                )

            else:

                db.session.add(
                    PlatformEarning(
                        user_id=current_user.id,
                        amount=revenue,
                        purchase_id=purchase.id,
                        reason="Deleted HR Owner"
                    )
                )

        else:

            db.session.add(
                PlatformEarning(
                    user_id=current_user.id,
                    amount=revenue,
                    purchase_id=purchase.id,
                    reason="Self Registered Candidate"
                )
            )

    db.session.commit()

    flash("Contact unlocked successfully")

    return redirect(request.referrer)

@app.route('/notifications')
@login_required
def notifications():

    notifications = Notification.query.filter_by(
        user_id=current_user.id,
        user_type="hr"
    ).order_by(
        Notification.created_at.desc()
    ).all()

    return render_template(
        'notifications.html',
        notifications=notifications
    )

@app.route('/candidate-notifications')
def candidate_notifications():

    if 'candidate_id' not in session:
        return redirect('/candidate-login')

    notifications = Notification.query.filter_by(
        user_id=session['candidate_id'],
        user_type='candidate'
    ).order_by(
        Notification.created_at.desc()
    ).all()

    return render_template(
        'notifications.html',
        notifications=notifications
    )

@app.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():

    if request.method == 'POST':

        files = request.files.getlist("images")

        saved_images = []

        import uuid

        for file in files:

            if file and file.filename:

                ext = file.filename.rsplit(".", 1)[1].lower()

                filename = f"{uuid.uuid4().hex}.{ext}"

                filepath = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )

                file.save(filepath)

                # Generate thumbnail for videos
                if ext in VIDEO_EXTENSIONS:

                    thumbnail = f"{os.path.splitext(filename)[0]}.jpg"

                    thumbnail_path = os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        thumbnail
                    )

                    try:

                        result = subprocess.run(
                            [
                                "ffmpeg",
                                "-y",
                                "-i", filepath,
                                "-ss", "00:00:01",
                                "-vframes", "1",
                                thumbnail_path
                            ],
                            capture_output=True,
                            text=True
                        )

                        print(result.stderr)

                    except Exception as e:
                        print("Thumbnail Error:", e)

                saved_images.append(filename)

        job_timing = (
            f"{request.form.get('working_from')} - "
            f"{request.form.get('working_to')}"
        )

        interview_time = (
            f"{request.form.get('interview_time_from')} - "
            f"{request.form.get('interview_time_to')}"
        )

        job = JobPost(

            hr_id=current_user.id,

            company_name=current_user.company,

            job_title=request.form["job_title"],

            # City selected from dropdown
            location=request.form["location"].strip().title(),

            # Office address
            office_address=request.form.get("office_address"),

            salary=request.form["salary"],

            incentive=request.form.get("incentive"),

            job_timing=job_timing,

            working_days=request.form.get("working_days"),

            job_type=request.form.get("job_type"),

            employment_type=request.form.get("employment_type"),

            eligibility=request.form.get("eligibility"),

            experience_required=request.form.get("experience_required"),

            education=request.form.get("education"),

            gender=request.form.get("gender"),

            interview_from=request.form.get("interview_from"),

            interview_to=request.form.get("interview_to"),

            interview_time=interview_time,

            interview_instructions=request.form.get("interview_instructions"),

            description=request.form["description"],

            images=",".join(saved_images)

        )

        db.session.add(job)
        db.session.commit()

        # ===========================
        # NOTIFY FOLLOWERS
        # ===========================

        followers = Follow.query.filter_by(
            followed_hr_id=current_user.id
        ).all()

        first_image = (
            saved_images[0]
            if saved_images
            else ""
        )

        for f in followers:

            if not f.follower_candidate_id:
                continue

            candidate = CandidateUser.query.get(
                f.follower_candidate_id
            )

            if not candidate:
                continue

            send_notification(

                user_id=candidate.id,

                user_type="candidate",

                message=f"{current_user.company} posted a new job: {job.job_title}",

                link=f"/job/{job.id}",

                image=first_image,

                type="job_post"

            )

        db.session.commit()

        flash(
            "Job posted successfully.",
            "success"
        )

        return redirect("/my-jobs")

    return render_template("post_job.html")

import os
import uuid
import subprocess
from flask import request, flash, redirect, render_template
from flask_login import login_required, current_user

# Helper function for compression
def compress_video(input_path, output_path):
    # 1. Compress the video
    command = [
        '/usr/bin/ffmpeg', '-i', input_path,
        '-vf', 'scale=-2:1080',
        '-c:v', 'libx264',
        '-crf', '28',
        '-preset', 'veryfast',
        '-c:a', 'aac',
        '-y', output_path
    ]
    subprocess.run(command, check=True)
    
    # 2. Extract a thumbnail (the poster frame)
    # This creates a .jpg file in the same folder with the same name
    thumb_path = output_path.rsplit('.', 1)[0] + '.jpg'
    thumb_command = [
        '/usr/bin/ffmpeg', '-i', output_path,
        '-ss', '00:00:01',  # Takes a snapshot at 1 second
        '-vframes', '1',
        '-y', thumb_path
    ]
    subprocess.run(thumb_command, check=True)

@app.route("/post-video", methods=["GET", "POST"])
@login_required
def post_video():
    if request.method == "POST":
        video = request.files.get("company_video")
        if not video or video.filename == "":
            flash("Please select a video.", "danger")
            return redirect("/post-video")

        ext = video.filename.rsplit(".", 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Define temporary path for processing
        temp_filepath = os.path.join(app.config["UPLOAD_FOLDER"], f"temp_{filename}")
        final_filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        # Save and compress
        video.save(temp_filepath)
        try:
            compress_video(temp_filepath, final_filepath)
        finally:
            # Always remove the temporary uncompressed file[span_2](start_span)[span_2](end_span)
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)

        job = JobPost(
            hr_id=current_user.id,
            company_name=current_user.company,
            location=request.form.get("location"),
            description=request.form.get("description"),
            images=filename,
            post_type="video",
            cta_type=request.form.get("cta_type"),
            cta_url=request.form.get("cta_url")
        )

        db.session.add(job)
        db.session.commit()

        flash("Company video posted successfully.", "success")
        return redirect("/feed")

    return render_template("post_video.html")

@app.route("/post-enquiries/<int:post_id>")
@login_required
def post_enquiries(post_id):

    job = JobPost.query.get_or_404(post_id)

    if job.hr_id != current_user.id:
        abort(403)

    enquiries = (
        PostEnquiry.query
        .filter_by(post_id=post_id)
        .order_by(PostEnquiry.created_at.desc())
        .all()
    )

    return render_template(
        "post_enquiries.html",
        enquiries=enquiries,
        job=job,
        User=User,
        CandidateUser=CandidateUser
    )

@app.route("/enquire-post/<int:post_id>", methods=["POST"])
def enquire_post(post_id):

    job = JobPost.query.get_or_404(post_id)

    # HR enquiry
    if current_user.is_authenticated:

        already = PostEnquiry.query.filter_by(
            post_id=post_id,
            enquiry_hr_id=current_user.id
        ).first()

        if already:
            return jsonify(success=False, message="You have already enquired.")

        enquiry = PostEnquiry(
            post_id=job.id,
            hr_id=job.hr_id,
            enquiry_hr_id=current_user.id,
            enquiry_candidate_id=None
        )

    # Candidate enquiry
    elif "candidate_id" in session:

        candidate_id = session["candidate_id"]

        already = PostEnquiry.query.filter_by(
            post_id=post_id,
            enquiry_candidate_id=candidate_id
        ).first()

        if already:
            return jsonify(success=False, message="You have already enquired.")

        enquiry = PostEnquiry(
            post_id=job.id,
            hr_id=job.hr_id,
            enquiry_hr_id=None,
            enquiry_candidate_id=candidate_id
        )
        
        # Fetch candidate details to send to the HR post owner
        candidate = CandidateUser.query.get(candidate_id)
        if candidate and job.hr_id:
            send_notification(
                user_id=job.hr_id,
                user_type="hr",
                message=f"📩 New Enquiry from Candidate: {candidate.full_name} ({candidate.mobile})",
                link=f"/candidate/{candidate.id}",
                image=candidate.profile_photo,
                type="enquiry"
            )

    else:
        return jsonify(success=False, message="Please login first.")

    db.session.add(enquiry)
    db.session.commit()

    return jsonify(success=True)

@app.route("/candidate-enquire-post/<int:post_id>", methods=["POST"])
def candidate_enquire_post(post_id):

    if "candidate_id" not in session:
        return jsonify(success=False, message="Please login as Candidate.")

    candidate_id = session["candidate_id"]

    job = JobPost.query.get_or_404(post_id)

    already = PostEnquiry.query.filter_by(
        post_id=post_id,
        enquiry_candidate_id=candidate_id
    ).first()

    if already:
        return jsonify(success=False, message="Already enquired.")

    enquiry = PostEnquiry(
        post_id=job.id,
        hr_id=job.hr_id,
        enquiry_candidate_id=candidate_id
    )

    db.session.add(enquiry)
    db.session.commit()

    return jsonify(success=True)

@app.route('/job/<int:id>')
def view_job(id):

    job = JobPost.query.get_or_404(id)

    hr = User.query.get(job.hr_id)

    return render_template(
        'job_details.html',
        job=job,
        hr=hr
    )

@app.route('/my-jobs')
@login_required
def my_jobs():

    jobs = JobPost.query.filter_by(
        hr_id=current_user.id
    ).order_by(
        JobPost.created_at.desc()
    ).all()

    return render_template(
        'my_jobs.html',
        jobs=jobs
    )

from sqlalchemy import func

@app.route('/candidate-feed')
def candidate_feed():

    selected_location = request.args.get('location', '').strip()

    selected_content = request.args.get(
        'content',
        'all'
    )

    # -----------------------------
    # Hidden Posts
    # -----------------------------
    hidden_post_ids = []

    if "candidate_id" in session:

        hidden_post_ids = [

            h.post_id

            for h in HiddenFeed.query.filter_by(
                candidate_id=session["candidate_id"]
            ).all()

        ]

    # -----------------------------
    # Feed Query
    # -----------------------------
    jobs_query = JobPost.query

    # Hide reported posts
    if hidden_post_ids:

        jobs_query = jobs_query.filter(
            ~JobPost.id.in_(hidden_post_ids)
        )

    # -----------------------------
    # Location Filter
    # -----------------------------
    if selected_location:

        jobs_query = jobs_query.filter(
            func.lower(JobPost.location)
            == selected_location.lower()
        )

    # -----------------------------
    # Content Filter
    # -----------------------------
    if selected_content == "videos":

        jobs_query = jobs_query.filter(
            JobPost.post_type == "video"
        )

    elif selected_content == "jobs":

        jobs_query = jobs_query.filter(
            JobPost.post_type != "video"
        )

    # -----------------------------
    # Fetch Jobs
    # -----------------------------
    jobs = (
        jobs_query
        .outerjoin(
            BoostPost,
            db.and_(
                BoostPost.job_id == JobPost.id,
                BoostPost.status == "Active"
            )
        )
        .order_by(
            case((BoostPost.id == None, 1), else_=0),
            BoostPost.created_at.desc(),
            JobPost.created_at.desc()
        )
        .all()
    )

    # -----------------------------
    # Mark Boosted Posts
    # -----------------------------
    for job in jobs:
        job.active_boost = any(
            boost.status == "Active"
            for boost in job.boosts
        )

    # -----------------------------
    # Available Locations
    # -----------------------------
    locations = (

        db.session.query(
            func.lower(JobPost.location)
        )

        .filter(
            JobPost.location.isnot(None),
            JobPost.location != ""
        )

        .distinct()

        .order_by(
            func.lower(JobPost.location)
        )

        .all()

    )

    locations = [
        loc[0].title()
        for loc in locations
    ]

    selected_id = request.args.get(
        'selected',
        type=int
    )

    applied_jobs = []

    sparked_jobs = []

    if 'candidate_id' in session:

        applications = JobApplication.query.filter_by(
            candidate_id=session['candidate_id']
        ).all()

        applied_jobs = [
            app.job_id
            for app in applications
        ]

        sparked_jobs = [
            s.job_id
            for s in Spark.query.filter_by(
                candidate_id=session["candidate_id"]
            ).all()
        ]

        enquired_jobs = [
            e.post_id
            for e in PostEnquiry.query.filter_by(
                enquiry_candidate_id=session["candidate_id"]
            ).all()
        ]

    else:

        enquired_jobs = []

    return render_template(

        'candidate_feed.html',

        jobs=jobs,

        applied_jobs=applied_jobs,

        sparked_jobs=sparked_jobs,

        enquired_jobs=enquired_jobs,

        selected_id=selected_id,

        locations=locations,

        selected_location=selected_location,

        selected_content=selected_content

    )

from sqlalchemy import func

@app.route('/discover-hr')
def discover_hr():

    city = request.args.get('city', '').strip()

    # Get all unique cities (case-insensitive)
    cities = (
        db.session.query(func.lower(User.company_city))
        .filter(
            User.is_approved == True,
            User.company_city.isnot(None),
            User.company_city != ""
        )
        .distinct()
        .order_by(func.lower(User.company_city))
        .all()
    )

    cities = [c[0].title() for c in cities]

    query = User.query.filter_by(is_approved=True)

    if city:
        query = query.filter(
            func.lower(User.company_city) == city.lower()
        )

    hrs = query.order_by(
        User.id.desc()
    ).all()

    following_ids = []

    if 'candidate_id' in session:

        following_ids = [
            f.followed_hr_id
            for f in Follow.query.filter_by(
                follower_candidate_id=session['candidate_id']
            ).all()
        ]

    return render_template(
        "discover_hr.html",
        hrs=hrs,
        city=city,
        cities=cities,
        following_ids=following_ids
    )

from sqlalchemy import func

@app.route('/discover-candidates')
@login_required
def discover_candidates():

    city = request.args.get('city', '').strip()

    # Available Cities (case-insensitive)
    cities = (
        db.session.query(func.lower(CandidateUser.city))
        .filter(
            CandidateUser.city.isnot(None),
            CandidateUser.city != ""
        )
        .distinct()
        .order_by(func.lower(CandidateUser.city))
        .all()
    )

    cities = [c[0].title() for c in cities]

    # CANDIDATES
    candidate_query = CandidateUser.query

    if city:
        candidate_query = candidate_query.filter(
            func.lower(CandidateUser.city) == city.lower()
        )

    candidates = candidate_query.order_by(
        CandidateUser.id.desc()
    ).all()

    # HRS
    hr_query = User.query.filter(
        User.id != current_user.id
    )

    if city:
        hr_query = hr_query.filter(
            func.lower(User.company_city) == city.lower()
        )

    hrs = hr_query.order_by(
        User.id.desc()
    ).all()

    return render_template(
        'discover_candidates.html',
        candidates=candidates,
        hrs=hrs,
        city=city,
        cities=cities,
        Follow=Follow
    )

@app.route('/apply-job/<int:job_id>')
def apply_job(job_id):

    if 'candidate_id' not in session:
        return redirect('/candidate-login')

    existing = JobApplication.query.filter_by(
        job_id=job_id,
        candidate_id=session['candidate_id']
    ).first()

    if existing:
        return "Already Applied"

    application = JobApplication(
        job_id=job_id,
        candidate_id=session['candidate_id'],
        status=None
    )

    db.session.add(application)

    job = JobPost.query.get(job_id)

    candidate = CandidateUser.query.get(
        session['candidate_id']
    )

    send_notification(
        user_id=job.hr_id,
        user_type="hr",
        message=f"{candidate.full_name} applied for {job.job_title}",
        link=f"/candidate/{candidate.id}",
        image=candidate.profile_photo,
        type="job_apply"
    )

    # ==========================
    # DAILY APPLY TASK
    # ==========================

    from datetime import date

    today = date.today()

    if candidate.last_streak_reset != today:

        candidate.daily_login_completed = False
        candidate.daily_apply_completed = False
        candidate.daily_follow_completed = False
        candidate.daily_referral_completed = False
        candidate.daily_reward_claimed = False

        candidate.last_streak_reset = today

    if not candidate.daily_apply_completed:

        candidate.daily_apply_completed = True

    # Check if all daily tasks are completed
    check_daily_reward(candidate)

    boost = BoostPost.query.filter_by(
        job_id=job_id,
        status="Active"
    ).first()

    if boost:
        boost.applications += 1

    db.session.commit()

    next_page = request.args.get('next')

    if next_page:
        return redirect(next_page)

    return redirect(request.referrer)

@app.route('/apply-job-hr/<int:id>')
@login_required
def apply_job_hr(id):

    existing = JobApplication.query.filter_by(
        applicant_hr_id=current_user.id,
        job_id=id
    ).first()

    if existing:
        return redirect('/feed')

    application = JobApplication(
        applicant_hr_id=current_user.id,
        job_id=id,
        status=None
    )

    db.session.add(application)

    job = JobPost.query.get(id)

    send_notification(
        user_id=job.hr_id,
        user_type="hr",
        message=f"{current_user.first_name} applied for your job",
        link=f"/job-applicants/{id}",
        image=current_user.profile_photo,
        type="job_application"
    )

    boost = BoostPost.query.filter_by(
        job_id=id,
        status="Active"
    ).first()

    if boost:
        boost.applications += 1

    db.session.commit()

    return redirect(request.referrer)

@app.route('/job-applicants/<int:job_id>')
@login_required
def job_applicants(job_id):

    applications = JobApplication.query.filter_by(
        job_id=job_id
    ).all()

    for app in applications:
        print(
            "ID:", app.id,
            "candidate_id:", app.candidate_id,
            "applicant_hr_id:", app.applicant_hr_id
        )

    return render_template(
        'job_applicants.html',
        applications=applications,
        CandidateUser=CandidateUser,
        User=User
    )

@app.route('/applied-jobs')
def applied_jobs():

    if 'candidate_id' not in session:
        return redirect('/candidate-login')

    applications = JobApplication.query.filter_by(
        candidate_id=session['candidate_id']
    ).all()

    return render_template(
        'applied_jobs.html',
        applications=applications,
        JobPost=JobPost,
        User=User
    )

@app.route('/feed')
@login_required
def feed():

    selected_location = request.args.get(
        "location",
        ""
    ).strip()

    selected_content = request.args.get(
        "content",
        "all"
    )

    # -----------------------------
    # Hidden Posts
    # -----------------------------
    hidden_post_ids = [

        h.post_id

        for h in HiddenFeed.query.filter_by(
            hr_id=current_user.id
        ).all()

    ]

    # -----------------------------
    # Feed Query
    # -----------------------------
    query = JobPost.query.filter(
        JobPost.hr_id != current_user.id
    )

    # Hide reported posts
    if hidden_post_ids:

        query = query.filter(
            ~JobPost.id.in_(hidden_post_ids)
        )

    # -----------------------------
    # Location Filter
    # -----------------------------
    if selected_location:

        query = query.filter(
            func.lower(JobPost.location)
            == selected_location.lower()
        )

    # -----------------------------
    # Content Filter
    # -----------------------------
    if selected_content == "videos":

        query = query.filter(
            JobPost.post_type == "video"
        )

    elif selected_content == "jobs":

        query = query.filter(
            JobPost.post_type != "video"
        )

    # -----------------------------
    # Fetch Feed
    # -----------------------------
    jobs = (
        query
        .outerjoin(
            BoostPost,
            db.and_(
                BoostPost.job_id == JobPost.id,
                BoostPost.status == "Active"
            )
        )
        .order_by(
            case((BoostPost.id == None, 1), else_=0),
            BoostPost.created_at.desc(),
            JobPost.created_at.desc()
        )
        .all()
    )

    # -----------------------------
    # Mark Boosted Posts
    # -----------------------------
    for job in jobs:
        job.active_boost = any(
            boost.status == "Active"
            for boost in job.boosts
        )

    # -----------------------------
    # Applied Jobs
    # -----------------------------
    applications = JobApplication.query.filter_by(
        applicant_hr_id=current_user.id
    ).all()

    applied_jobs = [
        app.job_id
        for app in applications
    ]

    # -----------------------------
    # Sparked Jobs
    # -----------------------------
    sparked_jobs = [

        s.job_id

        for s in Spark.query.filter_by(
            hr_id=current_user.id
        ).all()

    ]

    enquired_jobs = [

        e.post_id

        for e in PostEnquiry.query.filter_by(
            enquiry_hr_id=current_user.id
        ).all()

    ]

    # -----------------------------
    # Available Locations
    # -----------------------------
    locations = (

        db.session.query(
            func.lower(JobPost.location)
        )

        .filter(
            JobPost.location.isnot(None),
            JobPost.location != ""
        )

        .distinct()

        .order_by(
            func.lower(JobPost.location)
        )

        .all()

    )

    locations = [
        loc[0].title()
        for loc in locations
    ]

    return render_template(

        "feed.html",

        jobs=jobs,

        applied_jobs=applied_jobs,

        sparked_jobs=sparked_jobs,

        enquired_jobs=enquired_jobs,

        locations=locations,

        selected_location=selected_location,

        selected_content=selected_content

    )

@app.route('/applied-jobs-hr')
@login_required
def applied_jobs_hr():

    applications = JobApplication.query.filter_by(
        applicant_hr_id=current_user.id
    ).order_by(
        JobApplication.applied_at.desc()
    ).all()

    return render_template(
        "applied_jobs_hr.html",
        applications=applications,
        JobPost=JobPost,
        User=User
    )

@app.route("/record-impression/<int:job_id>", methods=["POST"])
@login_required
def record_impression(job_id):

    boost = BoostPost.query.filter_by(
        job_id=job_id,
        status="Active"
    ).first()

    if not boost:
        return "", 204

    boost.impressions += 1
    db.session.commit()

    return "", 204

@app.route('/my-applicants')
@login_required
def my_applicants():

    jobs = JobPost.query.filter_by(
        hr_id=current_user.id
    ).all()

    return render_template(
        'my_applicants.html',
        jobs=jobs,
        JobApplication=JobApplication,
        CandidateUser=CandidateUser,
        User=User
    )

@app.route('/edit-company-profile')
@login_required
def edit_company_profile():

    return render_template(
        'edit_company_profile.html'
    )

@app.route('/followers')
@login_required
def followers():

    return render_template(
        'followers.html'
    )

@app.route('/notification/<int:id>')
@login_required
def open_notification(id):

    n = Notification.query.get_or_404(id)

    if n.user_id != current_user.id:
        return redirect('/notifications')

    n.is_read = True
    db.session.commit()

    if n.link:
        return redirect(n.link)

    return redirect('/notifications')

@app.route('/edit-job/<int:job_id>', methods=['GET','POST'])
@login_required
def edit_job(job_id):

    job = JobPost.query.get_or_404(job_id)

    # only owner can edit
    if job.hr_id != current_user.id:
        return "Access Denied"

    if request.method == 'POST':

        job.job_title = request.form['job_title']
        job.salary = request.form['salary']
        job.location = request.form['location']
        job.description = request.form['description']

        image = request.files.get('image')

        if image and image.filename:

            filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )
            )

            job.image = filename

        db.session.commit()

        flash("Job updated successfully")

        return redirect('/my-jobs')

    return render_template(
        'edit_job.html',
        job=job
    )

@app.route("/account-deletion-policy", methods=["GET"])
def account_deletion_policy():
    return render_template("account_deletion_policy.html")

@app.route('/delete-account')
@login_required
def delete_account():

    user_id = current_user.id

    # Mark uploaded candidates as Platform Candidates

    Candidate.query.filter_by(
        uploaded_by=user_id
    ).update({

        "is_platform_candidate": True,

        "revenue_owner_type": "admin",

        "revenue_owner_id": None

    })

    # Delete jobs
    JobPost.query.filter_by(
        hr_id=user_id
    ).delete()

    # Delete unlocks
    Unlock.query.filter_by(
        user_id=user_id
    ).delete()

    # Delete notifications
    Notification.query.filter_by(
        user_id=user_id
    ).delete()

    # Delete follows
    Follow.query.filter(
        (Follow.follower_hr_id == user_id) |
        (Follow.followed_hr_id == user_id)
    ).delete()

    # Delete credit history
    CreditHistory.query.filter_by(
        user_id=user_id
    ).delete()

    # Delete earnings
    Earnings.query.filter_by(
        user_id=user_id
    ).delete()

    # Delete withdrawals
    Withdrawal.query.filter_by(
        user_id=user_id
    ).delete()

    # Delete support tickets
    SupportTicket.query.filter_by(
        user_id=user_id,
        user_type='hr'
    ).delete()

    # Delete unlocked contacts
    CandidateContactUnlock.query.filter_by(
        hr_id=user_id
    ).delete()

    user = User.query.get(user_id)

    logout_user()

    db.session.add(
        DeletedAccount(
            account_type="hr",
            full_name=f"{user.first_name} {user.last_name}",
            mobile=user.mobile,
            email=user.email,
            username=user.username,
            referral_reward_used=True
        )
    )

    db.session.flush()      # Save DeletedAccount first

    db.session.delete(user)

    db.session.commit()

    session.clear()

    return redirect('/')

@app.route('/delete-candidate-account')
def delete_candidate_account():

    if 'candidate_id' not in session:
        return redirect('/candidate-login')

    candidate_id = session['candidate_id']

    # Delete job applications
    JobApplication.query.filter_by(
        candidate_id=candidate_id
    ).delete()

    # Delete notifications
    Notification.query.filter_by(
        user_id=candidate_id,
        user_type='candidate'
    ).delete()

    # Delete follows
    Follow.query.filter(
        (Follow.follower_candidate_id == candidate_id) |
        (Follow.followed_candidate_id == candidate_id)
    ).delete()

    # Delete support tickets
    SupportTicket.query.filter_by(
        user_id=candidate_id,
        user_type='candidate'
    ).delete()

    candidate = CandidateUser.query.get(
        candidate_id
    )

    db.session.add(
        DeletedAccount(
            account_type="candidate",
            full_name=candidate.full_name,
            mobile=candidate.mobile,
            email=candidate.email,
            username=candidate.username,
            referral_reward_used=True
        )
    )

    db.session.flush()      # Save DeletedAccount first

    db.session.delete(candidate)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return str(e)

    session.clear()

    return redirect('/')

@app.route('/candidate-notification/<int:id>')
def open_candidate_notification(id):

    if 'candidate_id' not in session:
        return redirect('/candidate-login')

    n = Notification.query.get_or_404(id)

    if (
        n.user_id != session['candidate_id']
        or n.user_type != 'candidate'
    ):
        return redirect('/candidate-notifications')

    n.is_read = True

    db.session.commit()

    if n.link:
        return redirect(n.link)

    return redirect('/candidate-notifications')

@app.template_filter("timeago")
def timeago(dt):

    if not dt:
        return ""

    now = india_time()

    if dt.tzinfo is None:
        dt = now.replace(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second,
            microsecond=dt.microsecond
        )

    seconds = int((now - dt).total_seconds())

    if seconds < 60:
        return "Just now"

    elif seconds < 3600:
        return f"{seconds // 60}m ago"

    elif seconds < 86400:
        return f"{seconds // 3600}h ago"

    elif seconds < 604800:
        return f"{seconds // 86400}d ago"

    return dt.strftime("%d %b %Y")

@app.route('/feed/<int:id>')
@login_required
def feed_post(id):

    jobs = JobPost.query.filter_by(
        hr_id=current_user.id
    ).order_by(
        JobPost.created_at.desc()
    ).all()

    sparked_jobs = [
        s.job_id
        for s in Spark.query.filter_by(
            hr_id=current_user.id
        ).all()
    ]

    return render_template(
        'feed_post.html',
        jobs=jobs,
        selected_id=id,
        sparked_jobs=sparked_jobs
    )

@app.route('/candidate-logout')
def candidate_logout():

    session.clear()

    return redirect('/candidate-login')

@app.route('/referrals')
@login_required
def referrals():

    settings = get_business_settings()

    if not current_user.referral_code:

        current_user.referral_code = generate_referral_code()

        db.session.commit()

    referral_link = (
        request.host_url.rstrip("/")
        + "/register?ref="
        + current_user.referral_code
    )

    referred_users = User.query.filter_by(
        referred_by=current_user.referral_code
    ).all()

    return render_template(
        'referrals.html',
        referral_link=referral_link,
        referred_users=referred_users,
        settings=settings
    )

from flask import jsonify

@app.route('/check-username')
def check_username():

    username = request.args.get(
        'username',
        ''
    ).strip().upper()

    hr = User.query.filter_by(
        username=username
    ).first()

    candidate = CandidateUser.query.filter_by(
        username=username
    ).first()

    return jsonify({
        "exists": bool(hr or candidate)
    })

@app.route('/check-mobile')
def check_mobile():

    mobile = request.args.get(
        'mobile',
        ''
    ).strip()

    hr = User.query.filter_by(
        mobile=mobile
    ).first()

    candidate = CandidateUser.query.filter_by(
        mobile=mobile
    ).first()

    return jsonify({
        "exists": bool(hr or candidate)
    })

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        login_id = request.form['mobile'].strip()

        password = request.form['password'].strip()

        # LOGIN USING MOBILE ONLY

        user = User.query.filter_by(
            mobile=login_id
        ).first()

        print("LOGIN =", login_id)

        if user:
            print("APPROVED =", user.is_approved)
            print("FAILED LOGINS =", user.failed_logins)
        else:
            logging.warning("USER NOT FOUND")

        if not user:
            flash("Invalid Mobile Number or Password", "danger")
            return redirect(url_for("login"))

        if user.is_deleted:
            flash("Your account has been deleted.", "danger")
            return redirect(url_for("login"))

        if user.failed_logins >= 5:
            flash("Your account has been blocked. Contact Admin.", "danger")
            return redirect(url_for("login"))

        # ADMIN CAN LOGIN EVEN IF NOT APPROVED

        if not user.is_approved and not user.is_admin:

            flash(
                "Your account is pending approval.",
                "warning"
            )

            return redirect(url_for("login"))

        if check_password_hash(user.password, password):

            user.failed_logins = 0

            user.last_login = datetime.utcnow()

            # SINGLE DEVICE LOGIN

            token = str(uuid.uuid4())

            user.session_token = token

            # APP TOKEN

            if not user.app_token:

                user.app_token = secrets.token_hex(64)

            db.session.commit()

            login_user(user, remember=True)

            is_app = (
                request.headers.get("X-App")
                == "RecrootEarn"
            )

            if is_app:
                session.permanent = True

            session["session_token"] = token

            # ADMIN REDIRECT

            if user.is_admin:

                return redirect(
                    url_for("admin")
                )

            # NORMAL HR

            return redirect(
                url_for("feed")
            )

        user.failed_logins += 1

        db.session.commit()

        flash(
            "Invalid Mobile Number or Password",
            "danger"
        )

        return redirect(url_for("login"))

    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():

    if request.method == 'POST':

        # UPLOAD LIMIT

        settings = get_business_settings()

        if Candidate.query.filter_by(
            uploaded_by=current_user.id
        ).count() >= settings.daily_candidate_upload_limit:

            flash(
                "Upload limit reached",
                "danger"
            )

            return redirect(
                url_for('upload')
            )

        # GET FORM DATA

        name = request.form['name']
        phone = request.form['phone']
        experience = request.form['experience']
        designation = request.form['designation']
        city = request.form['city']
        category = request.form['category']

        # CHECK DUPLICATE PHONE

        existing = Candidate.query.filter_by(
            phone=phone
        ).first()

        if existing:

            uploader = User.query.get(
                existing.uploaded_by
            )

            uploader_name = (
                uploader.first_name
                if uploader
                else "Another HR"
            )

            flash(
                f"{phone} already uploaded by {uploader_name}",
                "warning"
            )

            return redirect(
                url_for('upload')
            )

        # CREATE CANDIDATE

        candidate = Candidate(

            name=name,

            phone=phone,

            experience=experience,

            designation=designation,

            city=city,

            category=category,

            uploaded_by=current_user.id,

            revenue_owner_type="hr",

            revenue_owner_id=current_user.id

        )

        db.session.add(candidate)

        # REWARD CREDIT

        current_user.credits += 1

        db.session.add(

            CreditHistory(

                user_id=current_user.id,

                amount=1,

                action=f"Uploaded: {name}"

            )

        )

        db.session.commit()

        flash(
            "Candidate uploaded successfully",
            "success"
        )

        return redirect(
            url_for('home')
        )

    settings = get_business_settings()

    return render_template(
        'upload.html',
        settings=settings
    )

@app.route('/bulk-upload', methods=['POST'])
@login_required
def bulk_upload():

    file = request.files['file']

    df = pd.read_excel(file)

    uploaded_count = 0
    duplicate_count = 0
    invalid_count = 0

    for _, row in df.iterrows():

        try:

            # PHONE
            phone = str(row['Phone']).strip()

            # REMOVE .0 FROM EXCEL
            if phone.endswith('.0'):
                phone = phone[:-2]

            # REMOVE SPACES
            phone = phone.replace(" ", "")

            # VALIDATE PHONE
            if len(phone) != 10 or not phone.isdigit():
                invalid_count += 1
                continue

            # DUPLICATE CHECK
            existing = Candidate.query.filter_by(
                phone=phone
            ).first()

            if existing:
                duplicate_count += 1
                continue

            # EXPERIENCE FIX
            experience_raw = str(
                row['Experience']
            ).strip().lower()

            if (
                "exp" in experience_raw
                or "experience" in experience_raw
            ):
                experience_value = "Experienced"
            else:
                experience_value = "Fresher"

            # CREATE CANDIDATE
            candidate = Candidate(

                name=str(
                    row['Name']
                ).strip(),

                phone=phone,

                experience=experience_value,

                designation=str(
                    row['Designation']
                ).strip(),

                city=str(
                    row['City']
                ).strip(),

                category=str(
                    row['Industry']
                ).strip(),

                uploaded_by=current_user.id,

                # Revenue Owner
                revenue_owner_type="hr",

                revenue_owner_id=current_user.id

            )

            db.session.add(candidate)

            uploaded_count += 1

        except Exception as e:

            print(e)

            invalid_count += 1
            continue

    # CREDIT REWARD
    current_user.credits += uploaded_count

    db.session.add(

        CreditHistory(

            user_id=current_user.id,

            amount=uploaded_count,

            action=f'Bulk uploaded {uploaded_count} candidates'

        )

    )

    db.session.commit()

    # SUCCESS MESSAGE
    if uploaded_count > 0:

        flash(
            f'{uploaded_count} Candidates uploaded successfully.',
            'success'
        )

    # DUPLICATE MESSAGE
    if duplicate_count > 0:

        flash(
            f'{duplicate_count} Candidates are already uploaded by some other HR.',
            'warning'
        )

    # INVALID MESSAGE
    if invalid_count > 0:

        flash(
            f'{invalid_count} Invalid rows skipped.',
            'danger'
        )

    return redirect(url_for('home'))

@app.route('/unlock/<int:id>')
@login_required
def unlock(id):

    candidate = Candidate.query.get_or_404(id)

    # -----------------------------------------
    # Prevent unlocking own candidate
    # -----------------------------------------

    if candidate.uploaded_by == current_user.id:

        flash(
            "You cannot unlock your own candidate.",
            "danger"
        )

        return redirect(request.referrer)

    # -----------------------------------------
    # Already unlocked?
    # -----------------------------------------

    existing = Unlock.query.filter_by(
        user_id=current_user.id,
        candidate_id=id
    ).first()

    if existing:

        flash(
            "Candidate already unlocked.",
            "warning"
        )

        return redirect(request.referrer)

    # -----------------------------------------
    # Credit Calculation
    # -----------------------------------------

    settings = get_business_settings()

    is_experienced = (
    candidate.experience.strip().lower() == "experienced"
    )

    if is_experienced:

        paid_cost = settings.lead_experienced_paid

        free_cost = settings.lead_experienced_free

    else:

        paid_cost = settings.lead_fresher_paid

        free_cost = settings.lead_fresher_free

    # -----------------------------------------
    # Total Credit Check
    # -----------------------------------------

    if (
        current_user.paid_credits < paid_cost
        and
        current_user.credits < free_cost
    ):

        flash(
            f"You need {paid_cost} paid credits or {free_cost} free credits to unlock this candidate.",
            "warning"
        )

        return redirect("/buy-credits")

    # -----------------------------------------
    # Create Unlock Record
    # -----------------------------------------

    unlock = Unlock(

        user_id=current_user.id,

        candidate_id=id

    )

    db.session.add(unlock)

    uploader = User.query.get(candidate.uploaded_by)

    # -----------------------------------------
    # Paid Credits First
    # -----------------------------------------

    if current_user.paid_credits >= paid_cost:

        current_user.paid_credits -= paid_cost

        credit_used = paid_cost

        credits_to_use = paid_cost

        purchases = CreditPurchase.query.filter(

            CreditPurchase.user_id == current_user.id,

            CreditPurchase.credits_remaining > 0

        ).order_by(

            CreditPurchase.created_at.asc()

        ).all()

        remaining_paid = sum(
            purchase.credits_remaining
            for purchase in purchases
        )

        if remaining_paid < paid_cost:

            flash(
                "Paid credit records are out of sync. Please contact support.",
                "danger"
            )

            return redirect("/buy-credits")

        for purchase in purchases:

            if credits_to_use == 0:
                break

            used = min(
                purchase.credits_remaining,
                credits_to_use
            )

            purchase.credits_remaining -= used

            if purchase.credits_remaining < 0:
                purchase.credits_remaining = 0

            credits_to_use -= used

            settings = get_business_settings()

            uploader_share = round(
                purchase.price_per_credit *
                used *
                settings.leads_hr_share / 100,
                2
            )

            platform_share = round(
                purchase.price_per_credit *
                used *
                settings.leads_admin_share / 100,
                2
            )

            # ==========================================
            # REVENUE OWNER LOGIC
            # ==========================================

            if settings.enable_revenue_sharing:

                # HR-owned lead
                if (
                    candidate.revenue_owner_type == "hr"
                    and candidate.revenue_owner_id
                ):

                    owner = User.query.get(
                        candidate.revenue_owner_id
                    )

                    if owner:

                        safe_wallet_credit(
                            owner,
                            uploader_share
                        )

                        db.session.add(
                            Earnings(
                                user_id=owner.id,
                                purchase_id=purchase.id,
                                amount=uploader_share,
                                reason=f"Lead Unlock Revenue - {candidate.name}"
                            )
                        )

                    else:

                        # HR deleted
                        platform_share += uploader_share
                        uploader_share = 0

                else:

                    # Platform/Admin owned
                    platform_share += uploader_share
                    uploader_share = 0

            else:

                # Revenue sharing disabled
                platform_share += uploader_share
                uploader_share = 0

            platform = PlatformEarning(
                user_id=current_user.id,
                candidate_id=candidate.id,
                purchase_id=purchase.id,
                amount=platform_share,
                reason=f"Platform share from unlocking {candidate.name}"
            )

            db.session.add(platform)

    else:

        if current_user.credits < free_cost:

            flash(
                f"You need {free_cost} free credits or {paid_cost} paid credits to unlock this candidate.",
                "warning"
            )

            return redirect("/buy-credits")

        current_user.credits -= free_cost

        credit_used = free_cost

    # -----------------------------------------
    # CREDIT HISTORY
    # -----------------------------------------

    history = CreditHistory(

        user_id=current_user.id,

        amount=-credit_used,

        action=(
            f"Unlocked {candidate.name} "
            f"({'Paid Credits' if credit_used == paid_cost else 'Free Credits'})"
        )

    )

    db.session.add(history)

    db.session.commit()

    flash(
        "Lead transferred to Unlocked Candidates successfully.",
        "success"
    )

    return redirect(request.referrer)

# =========================
# REPORTING
# =========================
@app.route('/report-fake/<int:id>')
@login_required
def report_fake(id):
    candidate = Candidate.query.get(id)
    candidate.report_count += 1
    if candidate.report_count >= 3:
        candidate.is_fake = True
        uploader = User.query.get(candidate.uploaded_by)
        if uploader: uploader.trust_score -= 10
    db.session.commit()
    return redirect('/leads')

@app.route('/wrong-experience/<int:id>')
@login_required
def wrong_experience(id):

    candidate = Candidate.query.get(id)

    candidate.wrong_experience_reports += 1

    db.session.commit()

    return redirect('/leads')

# =========================
# ADMIN ROUTES (Fixed Indentations)
# =========================
@app.route('/admin')
@login_required
def admin():
    if not admin_only():
        return "Access Denied", 403

    today = india_time().date()

    return render_template(
        'admin.html',
        total_users=User.query.count(),
        total_candidates=Candidate.query.count(),
        total_candidate_users=CandidateUser.query.count(),
        total_unlocks=Unlock.query.count(),

        today_active_hr=User.query.filter(
            db.func.date(User.last_login) == today
        ).count(),

        today_active_candidates=CandidateUser.query.filter(
            db.func.date(CandidateUser.last_login) == today
        ).count(),

        recent_candidates=Candidate.query.order_by(
            Candidate.created_at.desc()
        ).limit(10).all()
    )

@app.route('/admin/users')
@login_required
def admin_users():
    if not admin_only():
        return "Access Denied"

    return render_template(
        'admin_users.html',
        users=User.query.filter_by(is_deleted=False).all()
    )

@app.route('/export-users')
@login_required
def export_users():

    if not current_user.is_admin:
        return "Access Denied"

    users = db.session.query(User).all()

    data = []

    for u in users:

        row = {
            "ID": u.id,
            "First Name": str(u.first_name),
            "Last Name": str(u.last_name),
            "Company": str(u.company),
            "Mobile": str(u.mobile),
            "Username": str(u.username),
            "Credits": str(u.credits),
            "Trust Score": str(u.trust_score)
        }

        data.append(row)

    df = pd.DataFrame(data)

    file_name = "hr_users.xlsx"

    df.to_excel(file_name, index=False)

    return send_file(
        file_name,
        as_attachment=True
    )

@app.route('/delete-candidate/<int:id>')
@login_required
def delete_candidate(id):
    if not admin_only(): return "Access Denied"
    c = Candidate.query.get(id)
    db.session.add(AdminLog(action=f"Deleted candidate: {c.name}"))
    db.session.delete(c)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/ban-user/<int:id>')
@login_required
def ban_user(id):
    if not admin_only(): return "Access Denied"
    u = User.query.get(id)
    db.session.add(AdminLog(action=f"Banned user: {u.first_name}"))
    db.session.delete(u)
    db.session.commit()
    return redirect(url_for('admin_users'))

@app.route('/admin/support')
@login_required
def admin_support():

    if not admin_only():
        return "Access Denied"

    user_type = request.args.get("user_type")
    user_name = request.args.get("user_name")
    day = request.args.get("day")

    tickets = SupportTicket.query

    # ======================
    # USER TYPE FILTER
    # ======================

    if user_type:
        tickets = tickets.filter(
            SupportTicket.user_type == user_type
        )

    # ======================
    # NAME FILTER
    # ======================

    if user_name:

        if user_type == "hr":

            tickets = tickets.join(
                User,
                SupportTicket.user_id == User.id
            ).filter(
                User.first_name == user_name
            )

        elif user_type == "candidate":

            tickets = tickets.join(
                CandidateUser,
                SupportTicket.user_id == CandidateUser.id
            ).filter(
                CandidateUser.full_name == user_name
            )

    # ======================
    # DATE FILTER
    # ======================

    today = datetime.utcnow().date()

    if day == "today":

        tickets = tickets.filter(
            db.func.date(
                SupportTicket.created_at
            ) == today
        )

    elif day == "yesterday":

        tickets = tickets.filter(
            db.func.date(
                SupportTicket.created_at
            ) == today - timedelta(days=1)
        )

    elif day == "last7":

        tickets = tickets.filter(
            SupportTicket.created_at >=
            datetime.utcnow() - timedelta(days=7)
        )

    elif day == "last30":

        tickets = tickets.filter(
            SupportTicket.created_at >=
            datetime.utcnow() - timedelta(days=30)
        )

    tickets = tickets.order_by(
        SupportTicket.created_at.desc()
    ).all()

    # ======================
    # DROPDOWNS
    # ======================

    hr_names = [
        x[0] for x in db.session.query(
            User.first_name
        ).distinct().order_by(
            User.first_name
        ).all()
    ]

    candidate_names = [
        x[0] for x in db.session.query(
            CandidateUser.full_name
        ).distinct().order_by(
            CandidateUser.full_name
        ).all()
    ]

    return render_template(
        "admin_support.html",
        tickets=tickets,
        hr_names=hr_names,
        candidate_names=candidate_names,
        User=User,
        CandidateUser=CandidateUser,
        SupportReply=SupportReply
    )

@app.route('/user-reply/<int:id>', methods=['POST'])
@login_required
def user_reply(id):

    reply = request.form['reply']

    r = SupportReply(
        ticket_id=id,
        sender=current_user.first_name,
        message=reply
    )

    db.session.add(r)

    ticket = SupportTicket.query.get(id)

    if ticket:
        ticket.status = "User Replied"

    db.session.commit()

    return redirect('/support')

@app.route('/reply-ticket/<int:id>', methods=['POST'])
@login_required
def reply_ticket(id):

    if not admin_only():
        return "Access Denied"

    reply = request.form['reply']

    r = SupportReply(
        ticket_id=id,
        sender="Admin",
        message=reply
    )

    db.session.add(r)

    ticket = SupportTicket.query.get(id)

    if ticket:

        ticket.status = "Answered"

        # NOTIFICATION

        send_notification(
            user_id=ticket.user_id,
            user_type=ticket.user_type,
            message=f"Support replied to your ticket: {ticket.subject}",
            link="/support",
            type="support"
        )

        db.session.commit()

    flash(
        "Reply sent successfully",
        "success"
    )

    return redirect('/admin/support')

@app.route('/admin/candidates')
@login_required
def admin_candidates():

    if not admin_only():
        return "Access Denied"

    candidates = Candidate.query.all()

    return render_template(
        'admin_candidates.html',
        candidates=candidates
    )

@app.route('/export-candidates')

@login_required
def export_candidates():

    if not admin_only():

        return "Access Denied"

    candidates = Candidate.query.all()

    data = []

    for c in candidates:

        data.append({

            'Name': c.name,
            'Phone': c.phone,
            'Experience': c.experience,
            'Designation': c.designation,
            'City': c.city,
            'Category': c.category

        })

    df = pd.DataFrame(data)

    file_path = 'all_candidates.xlsx'

    df.to_excel(file_path, index=False)

    return send_file(
        file_path,
        as_attachment=True
    )

    candidates = Candidate.query.order_by(
        Candidate.created_at.desc()
    ).all()

    return render_template(
        'admin_candidates.html',
        candidates=candidates,
        User=User
    )

@app.route('/admin/unlocks')
@login_required
def admin_unlocks():

    if not admin_only():
        return "Access Denied"

    unlocks = Unlock.query.all()

    return render_template(
        'admin_unlocks.html',
        unlocks=unlocks,
        User=User,
        Candidate=Candidate
    )

    unlocks = Unlock.query.all()

    return render_template(
        'admin_unlocks.html',
        unlocks=unlocks
    )

@app.route('/admin/credits')
@login_required
def admin_credits():

    if not current_user.is_admin:
        return "Access Denied"

    history = CreditHistory.query.order_by(
        CreditHistory.created_at.desc()
    ).all()

    return render_template(
        'admin_credits.html',
        history=history,
        User=User
    )

@app.route('/admin-revenue')
@login_required
def admin_revenue():

    if not current_user.is_admin:
        return redirect("/dashboard")

    period = request.args.get("period")
    hr_id = request.args.get("hr")
    package = request.args.get("package")
    search = request.args.get("search")

    today = datetime.now()

    start_date = None
    end_date = None

    if period == "today":

        start_date = today.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

    elif period == "yesterday":

        start_date = (
            today - timedelta(days=1)
        ).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        end_date = today.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

    elif period == "week":

        start_date = today - timedelta(days=7)

    elif period == "month":

        start_date = today.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

    elif period == "year":

        start_date = today.replace(
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

    # ----------------------------------
    # DASHBOARD SUMMARY
    # ----------------------------------

    sales_query = CreditPurchase.query

    platform_query = PlatformEarning.query

    earnings_query = Earnings.query

    unlock_query = Unlock.query

    if hr_id:

        sales_query = sales_query.filter(
            CreditPurchase.user_id == int(hr_id)
        )

        platform_query = platform_query.filter(
            PlatformEarning.user_id == int(hr_id)
        )

    if package:

        sales_query = sales_query.filter(
            CreditPurchase.credits_bought == int(package)
        )

    if start_date:

        if period == "yesterday":

            sales_query = sales_query.filter(
                CreditPurchase.created_at >= start_date,
                CreditPurchase.created_at < end_date
            )

            platform_query = platform_query.filter(
                PlatformEarning.created_at >= start_date,
                PlatformEarning.created_at < end_date
            )

            earnings_query = earnings_query.filter(
                Earnings.created_at >= start_date,
                Earnings.created_at < end_date
            )

            unlock_query = unlock_query.filter(
                Unlock.created_at >= start_date,
                Unlock.created_at < end_date
            )

        else:

            sales_query = sales_query.filter(
                CreditPurchase.created_at >= start_date
            )

            platform_query = platform_query.filter(
                PlatformEarning.created_at >= start_date
            )

            earnings_query = earnings_query.filter(
                Earnings.created_at >= start_date
            )

            unlock_query = unlock_query.filter(
                Unlock.created_at >= start_date
            )

    total_sales = sum(
        p.amount_paid
        for p in sales_query.all()
    )

    platform_earnings = sum(
        p.amount
        for p in platform_query.all()
    )

    uploader_earnings = sum(
        e.amount
        for e in earnings_query.all()
    )

    total_unlocks = unlock_query.count()

    # ----------------------------------
    # HR REPORT
    # ----------------------------------

    hrs_query = User.query.filter_by(
        is_admin=False
    )

    if hr_id:

        hrs_query = hrs_query.filter(
            User.id == int(hr_id)
        )

    if search:

        hrs_query = hrs_query.filter(

            db.or_(

                User.first_name.ilike(f"%{search}%"),

                User.last_name.ilike(f"%{search}%"),

                User.company.ilike(f"%{search}%")

            )

        )

    hrs = hrs_query.all()

    hr_data = []

    for hr in hrs:

        candidate_query = Candidate.query.filter_by(
            uploaded_by=hr.id
        )

        if search:

            candidate_query = candidate_query.filter(

                Candidate.name.ilike(
                    f"%{search}%"
                )

            )

        uploaded = candidate_query.all()

        uploaded_count = len(uploaded)

        candidate_ids = [c.id for c in uploaded]

        unlock_count = Unlock.query.filter(
            Unlock.candidate_id.in_(candidate_ids)
        ).count() if candidate_ids else 0

        total_earning = db.session.query(
            db.func.sum(Earnings.amount)
        ).filter(
            Earnings.user_id == hr.id
        ).scalar() or 0

        hr_data.append({

            "hr": hr,
            "uploaded": uploaded_count,
            "unlocks": unlock_count,
            "earnings": round(total_earning, 2)

        })

    # ----------------------------------
    # PURCHASE HISTORY
    # ----------------------------------

    purchases_query = CreditPurchase.query

    if hr_id:

        purchases_query = purchases_query.filter(
            CreditPurchase.user_id == int(hr_id)
        )

    if package:

        purchases_query = purchases_query.filter(
            CreditPurchase.credits_bought == int(package)
        )

    if start_date:

        if period == "yesterday":

            purchases_query = purchases_query.filter(
                CreditPurchase.created_at >= start_date,
                CreditPurchase.created_at < end_date
            )

        else:

            purchases_query = purchases_query.filter(
                CreditPurchase.created_at >= start_date
            )

    purchases = purchases_query.order_by(
        CreditPurchase.created_at.desc()
    ).all()

    # ----------------------------------
    # CANDIDATE REPORT
    # ----------------------------------

    candidates_query = Candidate.query

    if hr_id:

        candidates_query = candidates_query.filter(
            Candidate.uploaded_by == int(hr_id)
        )

    if search:

        candidates_query = candidates_query.filter(
            Candidate.name.ilike(
                f"%{search}%"
            )
        )

    candidates = candidates_query.all()

    candidate_data = []

    for candidate in candidates:

        unlock_query = Unlock.query.filter_by(
            candidate_id=candidate.id
        )

        if start_date:

            if period == "yesterday":

                unlock_query = unlock_query.filter(
                    Unlock.created_at >= start_date,
                    Unlock.created_at < end_date
                )

            else:

                unlock_query = unlock_query.filter(
                    Unlock.created_at >= start_date
                )

        unlocks = unlock_query.count()

        earnings_query = db.session.query(
            db.func.sum(Earnings.amount)
        ).filter(
            Earnings.reason.like(
                f"%{candidate.name}%"
            )
        )

        if start_date:

            if period == "yesterday":

                earnings_query = earnings_query.filter(
                    Earnings.created_at >= start_date,
                    Earnings.created_at < end_date
                )

            else:

                earnings_query = earnings_query.filter(
                    Earnings.created_at >= start_date
                )

        total_earned = earnings_query.scalar() or 0

        candidate_data.append({

            "candidate": candidate,
            "unlocks": unlocks,
            "earnings": round(total_earned, 2)

        })

    # ----------------------------------
    # TRANSACTION LEDGER
    # ----------------------------------

    transactions_query = PlatformEarning.query

    if hr_id:

        transactions_query = transactions_query.filter(
            PlatformEarning.user_id == int(hr_id)
        )

    if start_date:

        if period == "yesterday":

            transactions_query = transactions_query.filter(
                PlatformEarning.created_at >= start_date,
                PlatformEarning.created_at < end_date
            )

        else:

            transactions_query = transactions_query.filter(
                PlatformEarning.created_at >= start_date
            )

    transactions = transactions_query.order_by(
        PlatformEarning.created_at.desc()
    ).all()

    if search:

        filtered_transactions = []

        for t in transactions:

            candidate = Candidate.query.get(t.candidate_id)

            if candidate and search.lower() in candidate.name.lower():

                filtered_transactions.append(t)

        transactions = filtered_transactions

    if package:

        filtered_transactions = []

        for t in transactions:

            purchase = CreditPurchase.query.get(t.purchase_id)

            if purchase and purchase.credits_bought == int(package):

                filtered_transactions.append(t)

        transactions = filtered_transactions

    return render_template(

        "admin_revenue.html",

        total_sales=round(total_sales, 2),

        platform_earnings=round(platform_earnings, 2),

        uploader_earnings=round(uploader_earnings, 2),

        total_unlocks=total_unlocks,

        hr_data=hr_data,

        purchases=purchases,

        candidate_data=candidate_data,

        transactions=transactions,

        User=User,

        Candidate=Candidate,

        CreditPurchase=CreditPurchase

    )

@app.route('/admin/logs')
@login_required
def admin_logs():

    if not admin_only():
        return "Access Denied"

    logs = AdminLog.query.order_by(
        AdminLog.created_at.desc()
    ).all()

    return render_template(
        'admin_logs.html',
        logs=logs
    )

@app.route('/admin/candidate-users')
@login_required
def admin_candidate_users():

    if not admin_only():
        return "Access Denied"

    name = request.args.get('name', '')
    city = request.args.get('city', '')
    mobile = request.args.get('mobile', '')
    page = request.args.get('page', 1, type=int)

    query = CandidateUser.query.filter_by(
        is_deleted=False
    )

    if name:
        query = query.filter(
            CandidateUser.full_name.contains(name)
        )

    if city:
        query = query.filter(
            CandidateUser.city.contains(city)
        )

    if mobile:
        query = query.filter(
            CandidateUser.mobile.contains(mobile)
        )

    candidates = query.order_by(
        CandidateUser.id.desc()
    ).paginate(
        page=page,
        per_page=20,
        error_out=False
    )

    total_candidates = CandidateUser.query.count()
    total_applications = JobApplication.query.count()

    return render_template(
        'admin_candidate_users.html',
        candidates=candidates,
        total_candidates=total_candidates,
        total_applications=total_applications,
        User=User,
        CandidateUser=CandidateUser,
        JobApplication=JobApplication
    )

@app.route('/admin/candidate-users/export')
@login_required
def export_candidate_users():

    if not admin_only():
        return "Access Denied"

    wb = Workbook()
    ws = wb.active
    ws.title = "Candidate Users"

    ws.append([
        "ID",
        "Name",
        "Email",
        "Mobile",
        "Username",
        "City",
        "Wallet Balance",
        "Career Level",
        "Designation",
        "Qualification",
        "Applied Jobs",
        "Joined Date"
    ])

    candidates = CandidateUser.query.order_by(
        CandidateUser.id.desc()
    ).all()

    for c in candidates:

        ws.append([
            c.id,
            c.full_name,
            c.email,
            c.mobile,
            c.username,
            c.city,
            c.wallet_balance or 0,
            c.career_level,
            c.designation,
            c.qualification,
            JobApplication.query.filter_by(candidate_id=c.id).count(),
            c.created_at.strftime('%d-%m-%Y') if c.created_at else ""
        ])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="candidate_users.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route('/admin/candidate/<int:id>/delete')
@login_required
def admin_delete_candidate(id):

    if not admin_only():
        return "Access Denied"

    candidate = CandidateUser.query.get_or_404(id)

    db.session.add(
        DeletedAccount(
            account_type="candidate",
            full_name=candidate.full_name,
            mobile=candidate.mobile,
            email=candidate.email,
            username=candidate.username,
            referral_reward_used=True,
            deleted_by="admin"
        )
    )

    db.session.delete(candidate)

    db.session.commit()

    flash(
        "Candidate marked as deleted successfully",
        "success"
    )

    return redirect('/admin/candidate-users')

@app.route('/job/<int:job_id>')
def job_share(job_id):
    return redirect(f'/job-details/{job_id}')

from urllib.parse import quote

@app.route('/share-job/<int:job_id>')
def share_job(job_id):

    job = JobPost.query.get_or_404(job_id)

    share_link = request.host_url.rstrip("/") + f"/job-view/{job.id}"

    text = f"""📢 {job.job_title}

Apply here:
{share_link}
"""

    return redirect(
        "https://wa.me/?text=" + quote(text)
    )

@app.route('/job/<int:job_id>')
def public_job(job_id):

    job = JobPost.query.get_or_404(job_id)

    return render_template(
        'public_job.html',
        job=job
    )

# =========================
# START APP
# =========================

@app.route('/make-admin')
def make_admin():

    user = User.query.filter_by(
        mobile="6261568334"
    ).first()

    if user:

        user.is_admin = True
        user.is_approved = True

        db.session.commit()

        return "6261568334 is now admin"

    return "User not found"

# =========================
# UNLOCKED CANDIDATES
# =========================

@app.route('/unlocked')
@login_required
def unlocked():

    page = request.args.get('page', 1, type=int)

    candidates = Candidate.query.join(
        Unlock,
        Unlock.candidate_id == Candidate.id
    ).filter(
        Unlock.user_id == current_user.id
    ).order_by(
        Candidate.created_at.desc()
    ).paginate(
        page=page,
        per_page=10
    )

    return render_template(
        'unlocked.html',
        candidates=candidates,
        CandidateReview=CandidateReview,
        User=User
    )

@app.route('/export-unlocked')
@login_required
def export_unlocked():

    import pandas as pd
    from flask import send_file

    unlocked = Unlock.query.filter_by(
        user_id=current_user.id
    ).all()

    data = []

    for u in unlocked:

        c = Candidate.query.get(u.candidate_id)

        if c:

            data.append({

                "Name": c.name,
                "Phone": c.phone,
                "City": c.city,
                "Category": c.category,
                "Designation": c.designation,
                "Experience": c.experience

            })

    df = pd.DataFrame(data)

    file_name = "unlocked_candidates.xlsx"

    df.to_excel(file_name, index=False)

    return send_file(
        file_name,
        as_attachment=True
    )

# =========================
# PROFILE
# =========================

@app.route('/profile')
@login_required
def profile():

    jobs = JobPost.query.filter_by(
        hr_id=current_user.id
    ).order_by(
        JobPost.created_at.desc()
    ).all()

    products = Product.query.filter_by(
        seller_id=current_user.id
    ).order_by(
        Product.created_at.desc()
    ).all()

    followers_count = Follow.query.filter_by(
        followed_hr_id=current_user.id
    ).count()

    following_count = Follow.query.filter_by(
        follower_hr_id=current_user.id
    ).count()

    return render_template(
        'profile.html',
        jobs=jobs,
        products=products,
        posts_count=len(jobs),
        products_count=len(products),
        followers_count=followers_count,
        following_count=following_count
    )

# =========================
# CREDIT HISTORY
# =========================

@app.route('/credits')
@login_required
def credits():

    history = CreditHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(
        CreditHistory.created_at.desc()
    ).all()

    return render_template(
        "buy_credits.html",
        history=history,
    packages=CreditPackage.query.filter_by(is_active=True)
            .order_by(CreditPackage.display_order.asc())
            .all()
    )

@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():

    if request.method == 'POST':

        # ----------------------------
        # PERSONAL DETAILS
        # ----------------------------

        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.email = request.form.get('email')

        # ----------------------------
        # COMPANY DETAILS
        # ----------------------------

        current_user.company = request.form.get('company')
        current_user.hr_type = request.form.get('hr_type')
        current_user.company_city = request.form.get('company_city')
        current_user.full_company_address = request.form.get('full_company_address')
        current_user.company_website = request.form.get('company_website')
        current_user.about_company = request.form.get('about_company')
        current_user.company_house = request.form.get("company_house")
        current_user.company_road = request.form.get("company_road")
        current_user.company_area = request.form.get("company_area")
        current_user.company_city = request.form.get("company_city")
        current_user.company_state = request.form.get("company_state")
        current_user.company_pincode = request.form.get("company_pincode")
        current_user.company_country = request.form.get("company_country")

        # ----------------------------
        # BANK DETAILS
        # ----------------------------

        current_user.account_holder_name = request.form.get('account_holder_name')
        current_user.bank_name = request.form.get('bank_name')
        current_user.account_number = request.form.get('account_number')
        current_user.ifsc_code = request.form.get('ifsc_code')
        current_user.upi_id = request.form.get('upi_id')

        # ----------------------------
        # PROFILE PHOTO
        # ----------------------------

        photo = request.files.get("photo")

        if photo and photo.filename:

            filename = secure_filename(photo.filename)

            photo.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )
            )

            current_user.profile_photo = filename

        # ----------------------------
        # MSME CERTIFICATE
        # ----------------------------

        msme = request.files.get("msme_certificate")

        if msme and msme.filename:

            filename = secure_filename(msme.filename)

            msme.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )
            )

            current_user.msme_certificate = filename

        # ----------------------------
        # GUMASTA CERTIFICATE
        # ----------------------------

        gumasta = request.files.get("gumasta_certificate")

        if gumasta and gumasta.filename:

            filename = secure_filename(gumasta.filename)

            gumasta.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )
            )

            current_user.gumasta_certificate = filename

        # ----------------------------
        # PROFILE COMPLETION
        # ----------------------------

        completion = 0

        if current_user.profile_photo:
            completion += 10

        if current_user.first_name:
            completion += 10

        if current_user.last_name:
            completion += 10

        if current_user.email:
            completion += 10

        if current_user.company:
            completion += 10

        if current_user.company_city:
            completion += 10

        if (
            current_user.company_house and
            current_user.company_road and
            current_user.company_area and
            current_user.company_city and
            current_user.company_state and
            current_user.company_pincode
        ):
            completion += 10

        if current_user.company_website:
            completion += 10

        if current_user.hr_type:
            completion += 10

        if (
            current_user.msme_certificate
            or current_user.gumasta_certificate
        ):
            completion += 10

        current_user.profile_completion = completion

        db.session.commit()

        if current_user.email and not current_user.welcome_email_sent:
            send_welcome_email(
                current_user.email,
                current_user.first_name
            )
            current_user.welcome_email_sent = True
            db.session.commit()

        flash(
            "Profile Updated Successfully",
            "success"
        )

        return redirect(url_for("profile"))

    cities = [
        "Indore",
        "Bhopal",
        "Dewas",
    ]
    return render_template(
        "edit_profile.html",
        profile_completion=current_user.profile_completion or 0,
        cities=cities
    )

# =========================
# SUPPORT
# =========================

@app.route('/support', methods=['GET', 'POST'])
@login_required
def support():

    if request.method == 'POST':

        ticket = SupportTicket(
            user_id=current_user.id,
            user_type='hr',
            subject=request.form['subject'],
            message=request.form['message']
        )

        db.session.add(ticket)

        db.session.flush()  # generates ticket.id

        # NOTIFICATION

        send_notification(
            user_id=current_user.id,
            user_type="hr",
            message="Support ticket submitted successfully",
            link=f"/ticket/{ticket.id}",
            type="support"
        )

        db.session.commit()

        flash(
            "Support ticket submitted successfully",
            "success"
        )

        return redirect('/support')

    page = request.args.get(
        'page',
        1,
        type=int
    )

    tickets = SupportTicket.query.filter_by(
        user_id=current_user.id
    ).order_by(
        SupportTicket.created_at.desc()
    ).paginate(
        page=page,
        per_page=10
    )

    return render_template(
        'support.html',
        tickets=tickets,
        SupportReply=SupportReply
    )

@app.route('/test-export')
def test_export():
    print("EXPORT ROUTE WORKING")
    return "WORKING"

@app.route('/ticket/<int:id>', methods=['GET', 'POST'])
@login_required
def ticket_chat(id):

    ticket = SupportTicket.query.get(id)

    replies = SupportReply.query.filter_by(
        ticket_id=id
    ).all()

    if request.method == 'POST':

        msg = request.form['message']

        sender = current_user.username

        reply = SupportReply(
            ticket_id=id,
            sender=sender,
            message=msg
        )

        db.session.add(reply)

        db.session.commit()

        return redirect(url_for(
            'ticket_chat',
            id=id
        ))

    return render_template(
        'ticket_chat.html',
        ticket=ticket,
        replies=replies
    )

@app.route('/buy-credits')
@login_required
def buy_credits_page():

    packages = CreditPackage.query.filter_by(
        is_active=True
    ).order_by(
        CreditPackage.display_order.asc()
    ).all()

    return render_template(
        "buy_credits.html",
        packages=packages
    )

@app.route('/buy-credits/<int:package_id>')
@login_required
def buy_credits(package_id):

    package = CreditPackage.query.filter_by(
        id=package_id,
        is_active=True
    ).first()

    if not package:
        flash(
            "Invalid Package",
            "danger"
        )
        return redirect("/buy-credits")

    credits = package.credits

    order = client.order.create({
        "amount": int(float(package.price) * 100),
        "currency": "INR",
        "payment_capture": 1
    })

    # Save purchase info
    session["buy_credits"] = credits
    session["buy_amount"] = package.price
    session["package_name"] = package.package_name
    session["package_id"] = package.id

    return render_template(
        "payment.html",
        order=order,
        amount=package.price,
        credits=credits,
        package=package,
        razorpay_key=RAZORPAY_KEY
    )

@app.route("/delete-job/<int:id>")
@login_required
def delete_job(id):

    job = JobPost.query.get_or_404(id)

    if job.hr_id != current_user.id:
        flash("Unauthorized", "danger")
        return redirect("/feed")

    db.session.delete(job)
    db.session.commit()

    flash("Job deleted successfully.", "success")
    return redirect("/profile")

@app.route('/payment-success')
@login_required
def payment_success():

    settings = get_business_settings()

    credits = session.get('buy_credits', 0)
    amount = session.get('buy_amount', 0)

    razorpay_payment_id = request.args.get("payment_id", "N/A")

    razorpay_payment_id = request.args.get("payment_id")
    razorpay_order_id = request.args.get("order_id")
    razorpay_signature = request.args.get("signature")

    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        })
    except Exception:
        flash("Payment verification failed.", "danger")
        return redirect("/buy-credits")

    # ADD PAID CREDITS
    current_user.paid_credits += credits

    # PUSH NOTIFICATION TO BUYER
    send_notification(
        user_id=current_user.id,
        user_type="hr",
        message=f"🎉 {credits} credits have been credited to your account.",
        link="/credits",
        type="credit_purchase"
    )

    # SAVE PURCHASE RECORD
    purchase = CreditPurchase(
        user_id=current_user.id,
        package_name=f"{credits} Credit Pack",
        amount_paid=amount,
        credits_bought=credits,
        credits_remaining=credits,
        price_per_credit=amount / credits
    )

    db.session.add(purchase)

    # CREDIT HISTORY
    history = CreditHistory(
        user_id=current_user.id,
        amount=credits,
        action=f"Purchased {credits} Paid Credits"
    )

    db.session.add(history)

    # -------------------------------------------------
    # HR TO HR REFERRAL REWARD
    # -------------------------------------------------

    if (
        amount >= settings.hr_minimum_purchase
        and current_user.referred_by
        and not current_user.referral_purchase_reward_given
    ):

        referrer = User.query.filter_by(
            referral_code=current_user.referred_by
        ).first()

        if referrer:

            from datetime import date

            # Reset daily count on new day
            if referrer.last_referral_reward_date != date.today():
                referrer.last_referral_reward_date = date.today()
                referrer.daily_referral_rewards = 0

            # Daily reward limit
            if referrer.daily_referral_rewards < settings.hr_daily_referral_limit:

                referrer.wallet_balance += settings.hr_to_hr_reward
                referrer.referral_earnings += settings.hr_to_hr_reward
                referrer.successful_referrals += 1
                referrer.daily_referral_rewards += 1

                current_user.referral_purchase_reward_given = True

                # PUSH NOTIFICATION TO REFERRER
                send_notification(
                    user_id=referrer.id,
                    user_type="hr",
                    message=f"🎉 Congratulations! ₹{settings.hr_to_hr_reward} has been credited to your wallet.",
                    link="/wallet",
                    type="referral_reward"
                )

    db.session.commit()

    # SEND INVOICE EMAIL
    if current_user.email:
        send_invoice_email(
            current_user,
            purchase,
            razorpay_payment_id
        )

    # PREVENT DUPLICATE REWARD
    session.pop("buy_credits", None)
    session.pop("buy_amount", None)

    return redirect("/credits")

@app.route('/wallet')
@login_required
def wallet():

    earnings = Earnings.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Earnings.created_at.desc()
    ).all()

    return render_template(
        'wallet.html',
        earnings=earnings
    )

@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():

    # Get Business Settings
    settings = get_business_settings()

    # Withdrawal History
    withdrawals = Withdrawal.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Withdrawal.created_at.desc()
    ).all()

    if request.method == "POST":

        try:
            amount = float(request.form.get("amount", 0))
        except:
            flash(
                "Invalid withdrawal amount.",
                "danger"
            )
            return redirect("/withdraw")

        # Minimum Withdrawal
        if amount < settings.minimum_withdrawal:

            flash(
                f"Minimum withdrawal is ₹{settings.minimum_withdrawal}",
                "danger"
            )

            return redirect("/withdraw")

        # Wallet Balance
        if amount > current_user.wallet_balance:

            flash(
                "Insufficient wallet balance.",
                "danger"
            )

            return redirect("/withdraw")

        # Check Payment Details

        has_upi = (
            current_user.upi_id
            and current_user.upi_id.strip()
        )

        has_bank = (
            current_user.bank_name
            and current_user.account_holder_name
            and current_user.account_number
            and current_user.ifsc_code
        )

        if not (has_upi or has_bank):

            flash(
                "Please update your payment details before requesting withdrawal.",
                "warning"
            )

            return redirect("/payment-info")

        # Create Withdrawal Request

        withdrawal = Withdrawal(

            user_id=current_user.id,

            amount=amount,

            status="Pending"

        )

        db.session.add(withdrawal)

        # Deduct Wallet
        current_user.wallet_balance -= amount

        db.session.commit()

        flash(
            "Withdrawal request submitted successfully.",
            "success"
        )

        return redirect("/withdraw")

    return render_template(

        "withdraw.html",

        withdrawals=withdrawals,

        settings=settings

    )

@app.route('/admin/withdrawals')
@login_required
def admin_withdrawals():

    if not current_user.is_admin:
        return "Access Denied"

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    query = Withdrawal.query

    if status:
        query = query.filter_by(status=status)

    withdrawals = query.order_by(
        Withdrawal.created_at.desc()
    ).all()

    withdrawal_data = []

    total_amount = 0
    pending_amount = 0

    for w in withdrawals:

        user = w.user

        if search and user:

            search_text = (
                f"{user.username} "
                f"{user.mobile or ''} "
                f"{user.email or ''} "
                f"{user.upi_id or ''} "
                f"{user.account_number or ''}"
            ).lower()

            if search.lower() not in search_text:
                continue

        total_amount += w.amount

        if w.status == "Pending":
            pending_amount += w.amount

        withdrawal_data.append({
            "withdrawal": w,
            "user": user
        })

    pending_count = Withdrawal.query.filter_by(
        status="Pending"
    ).count()

    approved_count = Withdrawal.query.filter_by(
        status="Approved"
    ).count()

    paid_count = Withdrawal.query.filter_by(
        status="Paid"
    ).count()

    rejected_count = Withdrawal.query.filter_by(
        status="Rejected"
    ).count()

    return render_template(

        "admin_withdrawals.html",

        withdrawal_data=withdrawal_data,

        total_amount=total_amount,

        pending_amount=pending_amount,

        pending_count=pending_count,

        approved_count=approved_count,

        paid_count=paid_count,

        rejected_count=rejected_count,

        search=search,

        status=status

    )

@app.route('/mark-paid/<int:id>')
@login_required
def mark_paid(id):

    if not current_user.is_admin:
        return "Access Denied"

    withdrawal = Withdrawal.query.get(id)

    withdrawal.status = "Paid"

    db.session.commit()

    flash(
        'Withdrawal marked as paid.',
        'success'
    )

    return redirect('/admin/withdrawals')

@app.route('/payment-info', methods=['GET', 'POST'])
@login_required
def payment_info():

    if request.method == 'POST':

        current_user.account_holder_name = request.form.get(
            'account_holder_name'
        )

        current_user.upi_id = request.form.get(
            'upi_id'
        )

        current_user.bank_name = request.form.get(
            'bank_name'
        )

        current_user.account_number = request.form.get(
            'account_number'
        )

        current_user.ifsc_code = request.form.get(
            'ifsc_code'
        )

        db.session.commit()

        flash(
            'Payment info updated successfully.',
            'success'
        )

        return redirect(
            url_for('payment_info')
        )

    return render_template(
        'payment_info.html'
    )

@app.route('/add-review/<int:id>', methods=['POST'])
@login_required
def add_review(id):

    candidate = Candidate.query.get(id)

    unlocked = Unlock.query.filter_by(
        user_id=current_user.id,
        candidate_id=id
    ).first()

    if not unlocked:
        return "Unlock candidate first"

    existing_review = CandidateReview.query.filter_by(
        user_id=current_user.id,
        candidate_id=id
    ).first()

    if existing_review:
        return "You already reviewed this candidate"

    review = CandidateReview(
        candidate_id=id,
        user_id=current_user.id,
        rating=int(request.form['rating']),
        review=request.form['review']
    )

    db.session.add(review)

    db.session.commit()

    return redirect(url_for('home'))

@app.route("/forgot-password-success", methods=["POST"])
def forgot_password_success():

    mobile = request.json.get("mobile")

    user = User.query.filter_by(
        mobile=mobile,
        is_deleted=False
    ).first()

    if not user:
        user = CandidateUser.query.filter_by(
            mobile=mobile,
            is_deleted=False
        ).first()

    if not user:
        return jsonify({
            "success": False
        })

    session["forgot_mobile"] = mobile

    return jsonify({
        "success": True
    })

@app.route("/check-forgot-mobile")
def check_forgot_mobile():

    mobile = request.args.get("mobile", "").strip()

    user = User.query.filter_by(
        mobile=mobile,
        is_deleted=False
    ).first()

    if not user:
        user = CandidateUser.query.filter_by(
            mobile=mobile,
            is_deleted=False
        ).first()

    return jsonify({
        "exists": user is not None
    })

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == 'POST':

        email = request.form['email']

        mobile = request.form['mobile']

        user = User.query.filter_by(
            email=email,
            mobile=mobile
        ).first()

        if not user:

            flash(
                'Email or Mobile Number Incorrect',
                'danger'
            )

            return redirect('/forgot-password')

        session['reset_user_id'] = user.id

        return redirect('/change-password')

    return render_template(
        'forgot_password.html'
    )

@app.route("/comment/<int:job_id>", methods=["POST"])
def add_comment(job_id):

    if not current_user.is_authenticated and "candidate_id" not in session:
        return jsonify({"success": False})

    text = request.form.get("comment", "").strip()

    if not text:
        return jsonify({"success": False})

    comment = Comment(
        job_id=job_id,
        comment=text
    )

    actor_name = ""
    actor_photo = ""

    if "candidate_id" in session:
        comment.candidate_id = session["candidate_id"]
        comment.hr_id = None
        candidate = CandidateUser.query.get(session["candidate_id"])
        if candidate:
            actor_name = candidate.full_name
            actor_photo = candidate.profile_photo

    elif current_user.is_authenticated:
        comment.hr_id = current_user.id
        comment.candidate_id = None
        actor_name = f"{current_user.first_name} {current_user.last_name}"
        actor_photo = current_user.profile_photo

    parent = request.form.get("parent_comment_id")

    if parent:
        comment.parent_comment_id = int(parent)

    db.session.add(comment)
    db.session.flush() # Flushes to make sure comment.job is accessible if needed

    # ==========================================
    # NOTIFY POST OWNER OF NEW COMMENT
    # ==========================================
    job = JobPost.query.get(job_id)
    if job and job.hr_id:
        # Prevent self-notification if post owner comments on their own post
        is_self_comment = (
            current_user.is_authenticated
            and job.hr_id == current_user.id
        )
        
        if not is_self_comment:
            send_notification(
                user_id=job.hr_id,
                user_type="hr",
                message=f"{actor_name} commented on your post: \"{text[:30]}...\"",
                link=f"/job-view/{job.id}",
                image=actor_photo,
                type="comment"
            )

    db.session.commit()

    return jsonify({
        "success": True,
        "comment_id": comment.id
    })

@app.route("/comment-like/<int:comment_id>", methods=["POST"])
def toggle_comment_like(comment_id):

    if current_user.is_authenticated:
        hr_id = current_user.id
        candidate_id = None

    elif "candidate_id" in session:
        hr_id = None
        candidate_id = session["candidate_id"]

    else:
        return jsonify({"success": False})

    like = CommentLike.query.filter_by(
        comment_id=comment_id,
        hr_id=hr_id,
        candidate_id=candidate_id
    ).first()

    if like:
        db.session.delete(like)
        liked = False
    else:
        db.session.add(CommentLike(
            comment_id=comment_id,
            hr_id=hr_id,
            candidate_id=candidate_id
        ))
        liked = True

    db.session.commit()

    count = CommentLike.query.filter_by(
        comment_id=comment_id
    ).count()

    return jsonify({
        "success": True,
        "liked": liked,
        "count": count
    })

@app.route("/mention-search")
def mention_search():

    q = request.args.get("q","").strip()

    results = []

    hrs = User.query.filter(
        User.company_name.ilike(f"%{q}%")
    ).limit(5).all()

    candidates = CandidateUser.query.filter(
        CandidateUser.full_name.ilike(f"%{q}%")
    ).limit(5).all()

    for u in hrs:
        results.append({
            "id": u.id,
            "type": "hr",
            "name": u.company_name
        })

    for u in candidates:
        results.append({
            "id": u.id,
            "type": "candidate",
            "name": u.full_name
        })

    return jsonify(results)

@app.route("/comments/<int:job_id>")
def get_comments(job_id):

    def serialize_comment(comment):

        hr = User.query.get(comment.hr_id) if comment.hr_id else None
        candidate = CandidateUser.query.get(comment.candidate_id) if comment.candidate_id else None

        if hr:
            name = f"{hr.first_name} {hr.last_name}"
            photo = (
                url_for("static", filename=f"uploads/{hr.profile_photo}")
                if hr and hr.profile_photo
                else ""
            )
            user_type = "hr"
        elif candidate:
            name = candidate.full_name
            photo = (
                url_for("static", filename=f"uploads/{candidate.profile_photo}")
                if candidate and candidate.profile_photo
                else ""
            )
            user_type = "candidate"
        else:
            name = "Deleted User"
            photo = ""
            user_type = ""

        liked = False
        if current_user.is_authenticated:
            liked = CommentLike.query.filter_by(
                comment_id=comment.id,
                hr_id=current_user.id
            ).first() is not None
        elif "candidate_id" in session:
            liked = CommentLike.query.filter_by(
                comment_id=comment.id,
                candidate_id=session["candidate_id"]
            ).first() is not None

        like_count = CommentLike.query.filter_by(
            comment_id=comment.id
        ).count()

        replies = Comment.query.filter_by(
            parent_comment_id=comment.id
        ).order_by(Comment.created_at.asc()).all()

        is_owner = (
            (current_user.is_authenticated and comment.hr_id == current_user.id)
            or
            ("candidate_id" in session and comment.candidate_id == session["candidate_id"])
        )

        is_post_owner = (
            current_user.is_authenticated
            and comment.job
            and comment.job.hr_id == current_user.id
        )

        return {
            "id": comment.id,
            "job_id": comment.job_id,
            "parent_comment_id": comment.parent_comment_id,
            "name": name,
            "photo": photo,
            "user_type": user_type,
            "comment": comment.comment,
            "edited": comment.edited,
            "created_at": comment.created_at.strftime("%d %b %Y %I:%M %p"),
            "likes": like_count,
            "liked": liked,
            "is_owner": is_owner,
            "is_post_owner": is_post_owner,
            "replies": [serialize_comment(reply) for reply in replies]
        }

    comments = Comment.query.filter_by(
        job_id=job_id,
        parent_comment_id=None
    ).order_by(Comment.created_at.desc()).all()

    return jsonify([serialize_comment(comment) for comment in comments])

@app.route("/edit-comment/<int:comment_id>", methods=["POST"])
def edit_post_comment(comment_id):

    comment = Comment.query.get_or_404(comment_id)

    # Check permission correctly for either HR or Candidate
    allowed = False
    if current_user.is_authenticated:
        allowed = (comment.hr_id == current_user.id)
    elif "candidate_id" in session:
        allowed = (comment.candidate_id == session["candidate_id"])

    if not allowed:
        return jsonify(success=False, message="Permission denied")

    text = request.form.get("comment", "").strip()

    if not text:
        return jsonify(success=False, message="Comment cannot be empty")

    comment.comment = text
    comment.edited = True

    db.session.commit()

    return jsonify(success=True)

@app.route("/report-comment/<int:comment_id>", methods=["POST"])
def report_post_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    reason = request.form.get("reason", "").strip()

    # Prevent duplicate reports from the same user if desired, or allow multiple
    report = CommentReport(
        comment_id=comment.id,
        reason=reason
    )

    if current_user.is_authenticated:
        report.hr_id = current_user.id
    elif "candidate_id" in session:
        report.candidate_id = session["candidate_id"]

    db.session.add(report)
    db.session.commit()

    # Check total reports for automatic deletion (threshold = 3 reports)
    total_reports = CommentReport.query.filter_by(comment_id=comment.id).count()
    if total_reports >= 3:
        # Clean up related records and delete comment automatically
        CommentLike.query.filter_by(comment_id=comment.id).delete()
        CommentReport.query.filter_by(comment_id=comment.id).delete()
        db.session.delete(comment)
        db.session.commit()
        return jsonify(success=True, auto_deleted=True, message="Comment removed due to multiple reports.")

    return jsonify(success=True, auto_deleted=False)


@app.route("/delete-comment/<int:comment_id>", methods=["POST"])
def delete_post_comment(comment_id):
    try:
        comment = Comment.query.get_or_404(comment_id)
        job = JobPost.query.get(comment.job_id)

        # Permissions: Allowed if Admin, Comment Owner, or Post Owner
        is_admin = current_user.is_authenticated and current_user.is_admin
        is_comment_owner = False
        is_post_owner = False

        if current_user.is_authenticated:
            is_comment_owner = (comment.hr_id == current_user.id)
            is_post_owner = (job and job.hr_id == current_user.id)
        elif "candidate_id" in session:
            is_comment_owner = (comment.candidate_id == session["candidate_id"])
            is_post_owner = (job and job.hr_id == session["candidate_id"]) # if candidate owns post depending on your schema

        if not (is_admin or is_comment_owner or is_post_owner):
            return jsonify(success=False, message="Permission denied")

        # Cleanup child relations
        CommentLike.query.filter_by(comment_id=comment.id).delete()
        CommentReport.query.filter_by(comment_id=comment.id).delete()
        
        db.session.delete(comment)
        db.session.commit()

        return jsonify(success=True)
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=str(e))


@app.route("/admin/reported-comments")
@login_required
def admin_reported_comments():
    if not current_user.is_admin:
        return "Access Denied", 403

    # Group reported comments for review in a separate window/template
    reported_comments = db.session.query(
        Comment,
        func.count(CommentReport.id).label("total_reports")
    ).join(
        CommentReport,
        CommentReport.comment_id == Comment.id
    ).group_by(
        Comment.id
    ).order_by(
        func.count(CommentReport.id).desc()
    ).all()

    return render_template(
        "admin_reported_comments.html",
        reported_comments=reported_comments
    )

@app.route("/shop/add-product", methods=["GET", "POST"])
@login_required
def add_product():

    # ==========================================
    # DEFAULT SHOP CATEGORIES
    # ==========================================

    create_default_shop_categories()

    categories = ProductCategory.query.filter_by(
        is_active=True
    ).all()

    # ==========================================
    # ADD PRODUCT
    # ==========================================

    if request.method == "POST":

        product = Product(

            seller_id=current_user.id,

            category_id=int(
                request.form["category_id"]
            ),

            name=request.form["name"].strip(),

            description=request.form.get(
                "description",
                ""
            ).strip(),

            hsn_code=request.form.get(
                "hsn_code"
            ),

            price=float(
                request.form.get(
                    "price",
                    0
                )
            ),

            sale_price=(
                float(request.form["sale_price"])
                if request.form.get("sale_price")
                else None
            ),

            stock=int(
                request.form.get(
                    "stock",
                    0
                )
            ),

            gst_percentage=float(
                request.form.get(
                    "gst_percent",
                    0
                )
            ),

            weight=float(
                request.form.get(
                    "weight",
                    0
                )
            ),

            length=float(
                request.form.get(
                    "length",
                    0
                )
            ),

            width=float(
                request.form.get(
                    "width",
                    0
                )
            ),

            height=float(
                request.form.get(
                    "height",
                    0
                )
            ),

            product_type=request.form.get(
                "product_type",
                "simple"
            ),

            is_active=True
        )

        db.session.add(product)

        db.session.commit()

        # ==========================================
        # PRODUCT IMAGES
        # ==========================================

        images = request.files.getlist("images")

        if len(images) > 5:

            flash(
                "Maximum 5 images allowed.",
                "danger"
            )

            db.session.delete(product)
            db.session.commit()

            return redirect(request.url)

        # Allowed image extensions
        allowed_extensions = {
            "jpg",
            "jpeg",
            "png",
            "webp"
        }

        sort_order = 1

        for image in images:

            if not image:
                continue

            if image.filename == "":
                continue

            # Check extension
            if "." not in image.filename:
                continue

            ext = image.filename.rsplit(
                ".",
                1
            )[1].lower()

            if ext not in allowed_extensions:
                continue

            # Generate unique filename
            filename = (
                f"{uuid.uuid4()}.{ext}"
            )

            # Save image
            image.save(
                os.path.join(
                    PRODUCT_UPLOAD_FOLDER,
                    filename
                )
            )

            # Save image record
            db.session.add(
                ProductImage(
                    product_id=product.id,
                    image=filename,
                    sort_order=sort_order
                )
            )

            sort_order += 1

        # ==========================================
        # PRODUCT VARIANTS
        # ==========================================

        if product.product_type == "variable":

            names = request.form.getlist(
                "variant_name[]"
            )

            values = request.form.getlist(
                "option_value[]"
            )

            prices = request.form.getlist(
                "option_price[]"
            )

            stocks = request.form.getlist(
                "option_stock[]"
            )

            for i in range(len(values)):

                # Ignore empty options
                if not values[i].strip():
                    continue

                # Variant name
                variant_name = (
                    names[i]
                    if i < len(names)
                    and names[i].strip()
                    else "Option"
                )

                # Variant price
                variant_price = (
                    float(prices[i])
                    if i < len(prices)
                    and prices[i]
                    else float(product.price)
                )

                # Variant stock
                variant_stock = (
                    int(stocks[i])
                    if i < len(stocks)
                    and stocks[i]
                    else 0
                )

                db.session.add(
                    ProductVariant(

                        product_id=product.id,

                        variant_name=variant_name,

                        option_value=values[i].strip(),

                        price=variant_price,

                        stock=variant_stock
                    )
                )

        # ==========================================
        # FINAL SAVE
        # ==========================================

        db.session.commit()

        flash(
            "Product added successfully.",
            "success"
        )

        return redirect(
            "/shop/products"
        )

    # ==========================================
    # SHOW ADD PRODUCT PAGE
    # ==========================================

    return render_template(
        "shop/add_product.html",
        categories=categories
    )

@app.route("/shop/products")
@login_required
def shop_products():

    products = Product.query.filter_by(
        seller_id=current_user.id
    ).order_by(
        Product.created_at.desc()
    ).all()

    return render_template(
        "shop_products.html",
        products=products
    )

@app.route("/shop/edit-product/<int:id>", methods=["GET", "POST"])
@login_required
def edit_product(id):

    product = Product.query.filter_by(
        id=id,
        seller_id=current_user.id
    ).first_or_404()

    categories = ProductCategory.query.filter_by(
        is_active=True
    ).all()

    if request.method == "POST":

        product.name = request.form["name"].strip()
        product.category_id = request.form["category_id"]
        product.description = request.form["description"].strip()
        product.price = float(request.form["price"])
        product.sale_price = request.form.get("sale_price") or None
        product.stock = int(request.form["stock"])

        db.session.commit()

        flash(
            "Product updated successfully.",
            "success"
        )

        return redirect("/shop/products")

    return render_template(
        "edit_product.html",
        product=product,
        categories=categories
    )

@app.route(
    "/shop/delete-product/<int:id>",
    methods=["POST"]
)
@login_required
def delete_product(id):

    product = Product.query.filter_by(
        id=id,
        seller_id=current_user.id
    ).first_or_404()

    for img in product.images:

        path = os.path.join(
            PRODUCT_UPLOAD_FOLDER,
            img.image
        )

        if os.path.exists(path):
            os.remove(path)

    db.session.delete(product)

    db.session.commit()

    flash(
        "Product deleted successfully.",
        "success"
    )

    return redirect("/shop/products")

@app.route("/shop/<int:seller_id>")
def company_shop(seller_id):

    seller = User.query.get_or_404(seller_id)

    products = Product.query.filter_by(
        seller_id=seller.id,
        status="active"
    ).order_by(
        Product.created_at.desc()
    ).all()

    return render_template(
        "company_shop.html",
        seller=seller,
        products=products
    )

@app.route("/shop")
@login_required
def shop_home():

    # ==========================================
    # CATEGORIES
    # ONLY SHOW CATEGORIES HAVING ACTIVE PRODUCTS
    # ==========================================

    categories = (
        ProductCategory.query
        .join(Product, Product.category_id == ProductCategory.id)
        .filter(
            ProductCategory.is_active == True,
            Product.status == "active"
        )
        .distinct()
        .all()
    )

    # ==========================================
    # STORES WITH ACTIVE PRODUCTS
    # ==========================================

    store_seller_ids = db.session.query(
        Product.seller_id
    ).filter(
        Product.status == "active",
        Product.seller_id.isnot(None)
    ).distinct().subquery()

    stores = User.query.filter(
        User.id.in_(store_seller_ids)
    ).all()

    # ==========================================
    # ADMIN CONTROLLED BANNERS
    # ==========================================

    banners = (
        HomepageBanner.query
        .filter_by(is_active=True)
        .order_by(HomepageBanner.display_order.asc())
        .all()
    )


    # ==========================================
    # TOP DEALS
    # ALWAYS SHOW LATEST 4
    # ==========================================

    promoted_products = (
        Product.query
        .filter_by(
            is_promoted=True,
            status="active"
        )
        .order_by(
            Product.created_at.desc()
        )
        .limit(4)
        .all()
    )


    # ==========================================
    # TRENDING NOW
    # LATEST 4 IN THIS SECTION
    # ==========================================

    trending_products = (
        Product.query
        .filter_by(
            status="active",
            show_on_home=True,
            home_section="Trending Now"
        )
        .order_by(
            Product.created_at.desc()
        )
        .limit(4)
        .all()
    )


    # ==========================================
    # GREAT DEALS
    # LATEST 4 IN THIS SECTION
    # ==========================================

    deal_products = (
        Product.query
        .filter_by(
            status="active",
            show_on_home=True,
            home_section="Great Deals"
        )
        .order_by(
            Product.created_at.desc()
        )
        .limit(4)
        .all()
    )


    # ==========================================
    # NEW ARRIVALS
    # LATEST 4
    # ==========================================

    new_arrival_products = (
        Product.query
        .filter_by(
            status="active",
            show_on_home=True,
            home_section="New Arrivals"
        )
        .order_by(
            Product.created_at.desc()
        )
        .limit(4)
        .all()
    )


    # ==========================================
    # RECOMMENDED
    # LATEST 4 IN THIS SECTION
    # ==========================================

    recommended_products = (
        Product.query
        .filter_by(
            status="active",
            show_on_home=True,
            home_section="Recommended"
        )
        .order_by(
            Product.created_at.desc()
        )
        .limit(4)
        .all()
    )


    # ==========================================
    # LATEST PRODUCTS
    # LATEST 4 ONLY
    # ==========================================

    latest_products = (
        Product.query
        .filter_by(status="active")
        .order_by(
            Product.created_at.desc()
        )
        .limit(4)
        .all()
    )


    # ==========================================
    # SHOP HOMEPAGE
    # ==========================================

    return render_template(
        "shop_home.html",

        categories=categories,

        stores=stores,

        banners=banners,

        promoted_products=promoted_products,

        trending_products=trending_products,

        deal_products=deal_products,

        new_arrival_products=new_arrival_products,

        recommended_products=recommended_products,

        latest_products=latest_products
    )

@app.route("/shop/all")
@login_required
def shop_all_products():

    promoted_products = Product.query.filter_by(
        is_promoted=True,
        status="active"
    ).order_by(
        Product.created_at.desc()
    ).all()

    products = Product.query.filter_by(
        status="active"
    ).order_by(
        Product.created_at.desc()
    ).all()

    return render_template(
        "shop_all_products.html",
        promoted_products=promoted_products,
        products=products
    )

@app.route("/share-shop/<int:seller_id>/<shop_slug>")
def company_share_shop(seller_id, shop_slug):

    seller = User.query.get_or_404(seller_id)

    products = Product.query.filter_by(
        seller_id=seller.id,
        status="active"
    ).order_by(
        Product.created_at.desc()
    ).all()

    return render_template(
        "company_share_shop.html",
        seller=seller,
        products=products
    )

@app.route("/shop/category/<int:id>")
@login_required
def shop_category(id):

    category = ProductCategory.query.get_or_404(id)

    promoted_products = Product.query.filter_by(
        category_id=id,
        status="active",
        is_promoted=True
    ).order_by(
        Product.created_at.desc()
    ).all()

    products = Product.query.filter_by(
        category_id=id,
        status="active"
    ).order_by(
        Product.created_at.desc()
    ).all()

    return render_template(
        "shop_category.html",
        category=category,
        promoted_products=promoted_products,
        products=products
    )

@app.route("/product/<int:id>")
def product_details(id):

    product = Product.query.get_or_404(id)

    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.status == "active"
    ).limit(8).all()

    product.views += 1

    db.session.commit()

    return render_template(
        "shop/product_details.html",
        product=product,
        related_products=related_products
    )

@app.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):

    product = Product.query.get_or_404(product_id)

    selected_variant = request.form.get("selected_variant")

    cart = Cart.query.filter_by(
        user_id=current_user.id
    ).first()

    if not cart:

        cart = Cart(
            user_id=current_user.id,
            seller_id=product.seller_id
        )

        db.session.add(cart)

        db.session.commit()

    elif cart.seller_id != product.seller_id:

        flash(
            "Your cart already contains products from another shop.",
            "warning"
        )

        return redirect(request.referrer)

    price = product.sale_price or product.price

    if selected_variant:

        option = ProductVariantOption.query.get(selected_variant)

        price += option.extra_price

    item = CartItem.query.filter_by(
        cart_id=cart.id,
        product_id=product.id,
        variant_option_id=selected_variant
    ).first()

    if item:

        item.quantity += 1

    else:

        item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            variant_option_id=selected_variant,
            quantity=1,
            price=price
        )

        db.session.add(item)

    db.session.commit()

    flash(
        "Product added to cart.",
        "success"
    )

    return redirect("/cart")

@app.route("/cart/increase/<int:id>")
@login_required
def increase_cart(id):

    item = CartItem.query.get_or_404(id)

    item.quantity += 1

    db.session.commit()

    return redirect("/cart")

@app.route("/cart/decrease/<int:id>")
@login_required
def decrease_cart(id):

    item = CartItem.query.get_or_404(id)

    if item.quantity > 1:

        item.quantity -= 1

        db.session.commit()

    return redirect("/cart")

@app.route("/cart/remove/<int:id>")
@login_required
def remove_cart(id):

    item = CartItem.query.get_or_404(id)

    cart = item.cart

    db.session.delete(item)

    db.session.commit()

    if len(cart.items) == 0:

        db.session.delete(cart)

        db.session.commit()

    flash(
        "Item removed.",
        "success"
    )

    return redirect("/cart")

@app.route("/cart")
@login_required
def cart():

    cart = Cart.query.filter_by(
        user_id=current_user.id
    ).first()

    subtotal = 0

    total_items = 0

    if cart:

        for item in cart.items:

            subtotal += item.price * item.quantity

            total_items += item.quantity

    return render_template(
        "cart.html",
        cart=cart,
        subtotal=subtotal,
        total=subtotal,
        total_items=total_items
    )

@app.route("/checkout")
@login_required
def checkout():

    cart = Cart.query.filter_by(
        user_id=current_user.id
    ).first_or_404()

    addresses = ShippingAddress.query.filter_by(
        user_id=current_user.id
    ).order_by(
        ShippingAddress.is_default.desc()
    ).all()

    subtotal = 0

    total_items = 0

    for item in cart.items:

        subtotal += item.price * item.quantity

        total_items += item.quantity

    shipping_charge = 0

    total = subtotal + shipping_charge

    return render_template(
        "checkout.html",
        cart=cart,
        addresses=addresses,
        subtotal=subtotal,
        shipping_charge=shipping_charge,
        total=total,
        total_items=total_items,
        razorpay_key=RAZORPAY_KEY
    )

# =========================================================
# CUSTOMER SHIPPING ADDRESS MANAGEMENT
# =========================================================

@app.route("/shop/add-address", methods=["GET", "POST"])
@app.route("/add-address", methods=["GET", "POST"])
@login_required
def add_address():

    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()
        mobile = request.form.get("mobile", "").strip()
        alternate_mobile = request.form.get("alternate_mobile", "").strip()
        address_line1 = request.form.get("address_line1", "").strip()
        address_line2 = request.form.get("address_line2", "").strip()
        landmark = request.form.get("landmark", "").strip()
        city = request.form.get("city", "").strip()
        state = request.form.get("state", "").strip()
        pincode = request.form.get("pincode", "").strip()
        country = request.form.get("country", "India").strip()
        make_default = request.form.get("is_default") == "on"

        # Required fields
        if not full_name or not mobile or not address_line1:
            flash("Please fill all required address details.", "warning")
            return redirect(request.referrer or "/checkout")

        if not city or not state or not pincode:
            flash("City, state and pincode are required.", "warning")
            return redirect(request.referrer or "/checkout")

        # If this is the first address, automatically make it default
        existing_count = ShippingAddress.query.filter_by(
            user_id=current_user.id
        ).count()

        if existing_count == 0:
            make_default = True

        # If setting this as default, remove default from other addresses
        if make_default:
            ShippingAddress.query.filter_by(
                user_id=current_user.id
            ).update(
                {"is_default": False},
                synchronize_session=False
            )

        address = ShippingAddress(
            user_id=current_user.id,
            full_name=full_name,
            mobile=mobile,
            alternate_mobile=alternate_mobile or None,
            address_line1=address_line1,
            address_line2=address_line2 or None,
            landmark=landmark or None,
            city=city,
            state=state,
            pincode=pincode,
            country=country or "India",
            is_default=make_default
        )

        db.session.add(address)
        db.session.commit()

        flash("Address added successfully.", "success")

        return redirect("/checkout")

    return render_template(
        "add_address.html"
    )


# =========================================================
# EDIT SHIPPING ADDRESS
# =========================================================

@app.route("/shop/edit-address/<int:address_id>", methods=["GET", "POST"])
@app.route("/edit-address/<int:address_id>", methods=["GET", "POST"])
@login_required
def edit_address(address_id):

    address = ShippingAddress.query.filter_by(
        id=address_id,
        user_id=current_user.id
    ).first_or_404()

    if request.method == "POST":

        address.full_name = request.form.get(
            "full_name", ""
        ).strip()

        address.mobile = request.form.get(
            "mobile", ""
        ).strip()

        address.alternate_mobile = request.form.get(
            "alternate_mobile", ""
        ).strip() or None

        address.address_line1 = request.form.get(
            "address_line1", ""
        ).strip()

        address.address_line2 = request.form.get(
            "address_line2", ""
        ).strip() or None

        address.landmark = request.form.get(
            "landmark", ""
        ).strip() or None

        address.city = request.form.get(
            "city", ""
        ).strip()

        address.state = request.form.get(
            "state", ""
        ).strip()

        address.pincode = request.form.get(
            "pincode", ""
        ).strip()

        address.country = request.form.get(
            "country", "India"
        ).strip() or "India"

        make_default = request.form.get("is_default") == "on"

        if make_default:

            ShippingAddress.query.filter(
                ShippingAddress.user_id == current_user.id,
                ShippingAddress.id != address.id
            ).update(
                {"is_default": False},
                synchronize_session=False
            )

            address.is_default = True

        db.session.commit()

        flash("Address updated successfully.", "success")

        return redirect("/checkout")

    return render_template(
        "edit_address.html",
        address=address
    )


# =========================================================
# DELETE SHIPPING ADDRESS
# =========================================================

@app.route("/shop/delete-address/<int:address_id>", methods=["POST"])
@app.route("/delete-address/<int:address_id>", methods=["POST"])
@login_required
def delete_address(address_id):

    address = ShippingAddress.query.filter_by(
        id=address_id,
        user_id=current_user.id
    ).first_or_404()

    was_default = address.is_default

    db.session.delete(address)
    db.session.commit()

    # If default address was deleted,
    # automatically make another address default
    if was_default:

        next_address = ShippingAddress.query.filter_by(
            user_id=current_user.id
        ).order_by(
            ShippingAddress.created_at.desc()
        ).first()

        if next_address:
            next_address.is_default = True
            db.session.commit()

    flash("Address deleted successfully.", "success")

    return redirect("/checkout")


# =========================================================
# SET DEFAULT SHIPPING ADDRESS
# =========================================================

@app.route(
    "/shop/set-default-address/<int:address_id>",
    methods=["POST"]
)
@app.route(
    "/set-default-address/<int:address_id>",
    methods=["POST"]
)
@login_required
def set_default_address(address_id):

    address = ShippingAddress.query.filter_by(
        id=address_id,
        user_id=current_user.id
    ).first_or_404()

    ShippingAddress.query.filter(
        ShippingAddress.user_id == current_user.id
    ).update(
        {"is_default": False},
        synchronize_session=False
    )

    address.is_default = True

    db.session.commit()

    flash("Default address updated.", "success")

    return redirect("/checkout")

@app.route("/create-marketplace-order", methods=["POST"])
@login_required
def create_marketplace_order():

    cart = Cart.query.filter_by(
        user_id=current_user.id
    ).first_or_404()

    data = request.get_json(silent=True) or {}

    address_id = data.get("address_id")

    if not address_id:
        return jsonify({
            "error": "Please select a delivery address."
        }), 400

    address = ShippingAddress.query.filter_by(
        id=int(address_id),
        user_id=current_user.id
    ).first()

    if not address:
        return jsonify({
            "error": "Invalid delivery address."
        }), 400

    subtotal = sum(
        item.price * item.quantity
        for item in cart.items
    )

    shipping = 0

    total = subtotal + shipping

    if total <= 0:
        return jsonify({
            "error": "Your cart is empty."
        }), 400

    razorpay_order = client.order.create({
        "amount": int(round(total * 100)),
        "currency": "INR",
        "payment_capture": 1
    })

    # Save checkout payment information temporarily
    session["marketplace_payment"] = {
        "razorpay_order_id": razorpay_order["id"],
        "address_id": address.id,
        "amount": total
    }

    return jsonify(razorpay_order)

@app.route("/marketplace-payment-success")
@login_required
def marketplace_payment_success():

    razorpay_payment_id = request.args.get("payment_id")
    razorpay_order_id = request.args.get("order_id")
    razorpay_signature = request.args.get("signature")

    # ---------------------------------------------------------
    # 1. VERIFY RAZORPAY PAYMENT
    # ---------------------------------------------------------

    try:

        client.utility.verify_payment_signature({

            "razorpay_order_id": razorpay_order_id,

            "razorpay_payment_id": razorpay_payment_id,

            "razorpay_signature": razorpay_signature

        })

    except Exception:

        flash(
            "Payment verification failed.",
            "danger"
        )

        return redirect("/cart")


    # ---------------------------------------------------------
    # 2. GET PAYMENT SESSION
    # ---------------------------------------------------------

    payment_data = session.get(
        "marketplace_payment"
    )

    if not payment_data:

        flash(
            "Payment session expired. Please try again.",
            "danger"
        )

        return redirect("/checkout")


    # ---------------------------------------------------------
    # 3. VERIFY RAZORPAY ORDER ID
    # ---------------------------------------------------------

    if payment_data.get(
        "razorpay_order_id"
    ) != razorpay_order_id:

        flash(
            "Invalid payment order.",
            "danger"
        )

        return redirect("/cart")


    # ---------------------------------------------------------
    # 4. GET SELECTED DELIVERY ADDRESS
    # ---------------------------------------------------------

    address_id = payment_data.get(
        "address_id"
    )

    address = ShippingAddress.query.filter_by(
        id=address_id,
        user_id=current_user.id
    ).first()

    if not address:

        flash(
            "Please select a valid delivery address.",
            "warning"
        )

        return redirect("/checkout")


    # ---------------------------------------------------------
    # 5. GET CART
    # ---------------------------------------------------------

    cart = Cart.query.filter_by(
        user_id=current_user.id
    ).first()

    if not cart or not cart.items:

        flash(
            "Your cart is empty.",
            "warning"
        )

        return redirect("/cart")


    # ---------------------------------------------------------
    # 6. CALCULATE TOTAL AGAIN FROM SERVER
    # ---------------------------------------------------------

    subtotal = 0

    for item in cart.items:

        subtotal += (
            item.price *
            item.quantity
        )

    shipping = 0

    total = subtotal + shipping


    # ---------------------------------------------------------
    # 7. VERIFY AMOUNT AGAINST PAYMENT SESSION
    # ---------------------------------------------------------

    session_amount = float(
        payment_data.get(
            "amount",
            0
        )
    )

    if round(session_amount, 2) != round(total, 2):

        flash(
            "Payment amount does not match the order amount.",
            "danger"
        )

        return redirect("/cart")


    # ---------------------------------------------------------
    # 8. CREATE ORDER NUMBER
    # ---------------------------------------------------------

    order_number = (
        "RE"
        + datetime.now().strftime("%Y%m%d")
        + str(random.randint(100000, 999999))
    )


    # ---------------------------------------------------------
    # 9. CREATE ORDER
    # ---------------------------------------------------------

    order = Order(

        order_number=order_number,

        user_id=current_user.id,

        seller_id=cart.seller_id,

        address_id=address.id,

        payment_method="Online",

        payment_status="Paid",

        order_status="Pending",

        razorpay_order_id=razorpay_order_id,

        razorpay_payment_id=razorpay_payment_id,

        subtotal=subtotal,

        shipping_charge=shipping,

        total_amount=total

    )

    db.session.add(order)

    db.session.flush()


    # ---------------------------------------------------------
    # 10. CREATE ORDER ITEMS + UPDATE STOCK
    # ---------------------------------------------------------

    for item in cart.items:

        db.session.add(

            OrderItem(

                order_id=order.id,

                product_id=item.product_id,

                variant_option_id=item.variant_option_id,

                quantity=item.quantity,

                price=item.price,

                total=item.price * item.quantity,

                product_name=item.product.name,

                product_image=(
                    item.product.images[0].image
                    if item.product.images
                    else None
                ),

                variant_name=(
                    item.variant_option.value
                    if item.variant_option
                    else None
                )

            )

        )


        # Reduce product stock

        item.product.stock -= item.quantity


        # Reduce variant stock

        if item.variant_option:

            item.variant_option.stock -= (
                item.quantity
            )


        # Increase sold count

        item.product.sold += item.quantity


    # ---------------------------------------------------------
    # 11. DELETE CART
    # ---------------------------------------------------------

    db.session.delete(cart)


    # ---------------------------------------------------------
    # 12. CALCULATE PLATFORM COMMISSION
    # ---------------------------------------------------------

    settings = get_business_settings()

    commission = (
        order.total_amount *
        settings.marketplace_commission
    ) / 100

    seller_amount = (
        order.total_amount -
        commission
    )

    order.platform_commission = commission

    order.seller_amount = seller_amount

    order.wallet_released = False


    # ---------------------------------------------------------
    # 13. SAVE EVERYTHING
    # ---------------------------------------------------------

    db.session.commit()


    # ---------------------------------------------------------
    # 14. CLEAR PAYMENT SESSION
    # ---------------------------------------------------------

    session.pop(
        "marketplace_payment",
        None
    )


    # ---------------------------------------------------------
    # 15. SUCCESS
    # ---------------------------------------------------------

    flash(
        "Order placed successfully.",
        "success"
    )

    return redirect(
        f"/order/{order.id}"
    )

@app.route("/my-orders")
@login_required
def my_orders():

    orders = Order.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Order.created_at.desc()
    ).all()

    return render_template(
        "my_orders.html",
        orders=orders
    )

@app.route("/my-orders/<int:order_id>")
@login_required
def my_order_details(order_id):

    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()

    history = OrderStatusHistory.query.filter_by(
        order_id=order.id
    ).order_by(
        OrderStatusHistory.created_at.desc()
    ).all()

    return render_template(
        "my_order_details.html",
        order=order,
        history=history
    )

@app.route("/seller/orders")
@login_required
def seller_orders():

    status = request.args.get("status")

    query = Order.query.filter_by(
        seller_id=current_user.id
    )

    if status:
        query = query.filter_by(
            order_status=status
        )

    orders = query.order_by(
        Order.created_at.desc()
    ).all()

    return render_template(
        "seller_orders.html",
        orders=orders,
        status=status
    )

@app.route("/order/<int:order_id>")
@login_required
def order_details(order_id):

    order = Order.query.get_or_404(order_id)

    if order.user_id != current_user.id and order.seller_id != current_user.id:

        abort(403)

    history = OrderStatusHistory.query.filter_by(
        order_id=order.id
    ).order_by(
        OrderStatusHistory.created_at.desc()
    ).all()

    return render_template(
        "order_details.html",
        order=order,
        history=history
    )

@app.route("/seller/order/<int:order_id>/accept")
@login_required
def accept_order(order_id):

    order = Order.query.filter_by(
        id=order_id,
        seller_id=current_user.id
    ).first_or_404()

    order.order_status = "Accepted"

    db.session.add(
        OrderStatusHistory(
            order_id=order.id,
            status="Accepted",
            remarks="Accepted by seller"
        )
    )

    db.session.commit()

    flash(
        "Order accepted.",
        "success"
    )

    return redirect(
        f"/order/{order.id}"
    )

@app.route("/seller/order/<int:order_id>/reject")
@login_required
def reject_order(order_id):

    order = Order.query.filter_by(
        id=order_id,
        seller_id=current_user.id
    ).first_or_404()

    order.order_status = "Rejected"

    db.session.add(
        OrderStatusHistory(
            order_id=order.id,
            status="Rejected",
            remarks="Rejected by seller"
        )
    )

    db.session.commit()

    flash(
        "Order rejected.",
        "success"
    )

    return redirect(
        "/seller/orders"
    )

@app.route("/cancel-order/<int:order_id>")
@login_required
def cancel_order(order_id):

    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()

    if order.order_status not in [
        "Pending",
        "Accepted"
    ]:

        flash(
            "Order cannot be cancelled.",
            "danger"
        )

        return redirect(
            f"/order/{order.id}"
        )

    order.order_status = "Cancelled"

    db.session.add(
        OrderStatusHistory(
            order_id=order.id,
            status="Cancelled",
            remarks="Cancelled by customer"
        )
    )

    db.session.commit()

    flash(
        "Order cancelled.",
        "success"
    )

    return redirect("/my-orders")

@app.route("/create-shipment/<int:order_id>")
@login_required
def create_shipment(order_id):

    order = Order.query.filter_by(

        id=order_id,

        seller_id=current_user.id

    ).first_or_404()

    pickup = SellerPickupAddress.query.filter_by(

        seller_id=current_user.id

    ).first()

    if not pickup:

        flash("Pickup address missing.","danger")

        return redirect(f"/order/{order.id}")

    if not pickup.is_verified:

        flash("Pickup address not verified.","warning")

        return redirect(f"/order/{order.id}")

    ship = get_shiprocket()

    data = ship.create_shipment(order)

    shipment = data.get("shipment_id")

    awb = data.get("awb_code")

    courier = data.get("courier_name")

    order.tracking_id = awb

    order.courier_name = courier

    order.order_status = "Packed"

    db.session.add(

        OrderStatusHistory(

            order_id=order.id,

            status="Packed",

            remarks="Shipment Created"

        )

    )

    db.session.commit()

    flash(

        "Shipment created successfully.",

        "success"

    )

    return redirect(f"/order/{order.id}")

from flask import render_template, request, redirect, flash
from flask_login import login_required, current_user

# ==========================================
# SELLER PICKUP ADDRESS
# ==========================================

@app.route("/seller/pickup")
@login_required
def seller_pickup():

    pickup = SellerPickupAddress.query.filter_by(
        seller_id=current_user.id
    ).first()

    return render_template(
        "seller_pickup.html",
        pickup=pickup
    )


# ==========================================
# SAVE PICKUP ADDRESS
# ==========================================

@app.route("/seller/pickup/save", methods=["POST"])
@login_required
def save_seller_pickup():

    pickup = SellerPickupAddress.query.filter_by(
        seller_id=current_user.id
    ).first()

    if not pickup:

        pickup = SellerPickupAddress(
            seller_id=current_user.id
        )

        db.session.add(pickup)

    pickup.pickup_name = request.form.get("pickup_name")
    pickup.contact_person = request.form.get("contact_person")
    pickup.mobile = request.form.get("mobile")
    pickup.email = request.form.get("email")

    pickup.address_line1 = request.form.get("address_line1")
    pickup.address_line2 = request.form.get("address_line2")

    pickup.city = request.form.get("city")
    pickup.state = request.form.get("state")
    pickup.pincode = request.form.get("pincode")
    pickup.country = request.form.get("country")

    pickup.gst_number = request.form.get("gst_number")

    db.session.commit()

    flash(
        "Pickup address saved successfully.",
        "success"
    )

    return redirect("/seller/pickup")


# ==========================================
# EDIT PICKUP ADDRESS
# ==========================================

@app.route("/seller/pickup/edit", methods=["GET", "POST"])
@login_required
def edit_seller_pickup():

    pickup = SellerPickupAddress.query.filter_by(
        seller_id=current_user.id
    ).first_or_404()

    if request.method == "POST":

        pickup.pickup_name = request.form.get("pickup_name")
        pickup.contact_person = request.form.get("contact_person")
        pickup.mobile = request.form.get("mobile")
        pickup.email = request.form.get("email")

        pickup.address_line1 = request.form.get("address_line1")
        pickup.address_line2 = request.form.get("address_line2")

        pickup.city = request.form.get("city")
        pickup.state = request.form.get("state")
        pickup.pincode = request.form.get("pincode")
        pickup.country = request.form.get("country")

        pickup.gst_number = request.form.get("gst_number")

        db.session.commit()

        flash(
            "Pickup address updated successfully.",
            "success"
        )

        return redirect("/seller/pickup")

    return render_template(
        "seller_pickup.html",
        pickup=pickup
    )

@app.route("/admin/pickup-addresses")
@admin_required
def admin_pickup_addresses():

    pickups = SellerPickupAddress.query.order_by(
        SellerPickupAddress.created_at.desc()
    ).all()

    return render_template(
        "admin_pickup_addresses.html",
        pickups=pickups
    )

@app.route("/admin/pickup/<int:id>/verify")
@admin_required
def verify_pickup(id):

    pickup = SellerPickupAddress.query.get_or_404(id)

    pickup.is_verified = True

    db.session.commit()

    flash(
        "Pickup Address Verified.",
        "success"
    )

    return redirect("/admin/pickup-addresses")

@app.route("/admin/pickup/<int:id>/reject")
@admin_required
def reject_pickup(id):

    pickup = SellerPickupAddress.query.get_or_404(id)

    pickup.is_verified = False

    db.session.commit()

    flash(
        "Pickup verification removed.",
        "warning"
    )

    return redirect("/admin/pickup-addresses")

@app.route("/test-shiprocket")
@admin_required
def test_shiprocket():

    try:

        ship = get_shiprocket()

        return "Shiprocket Connected Successfully"

    except Exception as e:

        return str(e)

@app.route("/check-delivery", methods=["POST"])
@login_required
def check_delivery():

    address = ShippingAddress.query.filter_by(
        id=address_id,
        user_id=current_user.id
    ).first_or_404()

    cart = Cart.query.filter_by(
        user_id=current_user.id
    ).first_or_404()

    pickup = SellerPickupAddress.query.filter_by(
        seller_id=cart.seller_id
    ).first()

    ship = get_shiprocket()

    weight = sum(
        (item.product.weight or 0) * item.quantity
        for item in cart.items
    )

    response = ship.check_serviceability(
        pickup.pincode,
        address.pincode,
        weight
    )

    return jsonify(response)

@app.route("/update-tracking/<int:order_id>")
@login_required
def update_tracking(order_id):

    order = Order.query.get_or_404(order_id)

    if not order.tracking_id:

        flash(
            "Tracking ID not available.",
            "warning"
        )

        return redirect(f"/order/{order.id}")

    ship = get_shiprocket()

    tracking = ship.track_shipment(order.tracking_id)

    shipment = tracking["tracking_data"]["shipment_track"][0]

    status = shipment["current_status"]

    order.order_status = status

    db.session.add(

        OrderStatusHistory(

            order_id=order.id,

            status=status,

            remarks="Updated from Shiprocket"

        )

    )

    if status.lower() == "delivered":

        order.delivered_at = datetime.utcnow()

    db.session.commit()

    flash(
        "Tracking updated successfully.",
        "success"
    )

    return redirect(f"/order/{order.id}")

@app.route("/seller/dashboard")
@login_required
def seller_dashboard():

    total_products = Product.query.filter_by(
        seller_id=current_user.id
    ).count()

    total_orders = Order.query.filter_by(
        seller_id=current_user.id
    ).count()

    pending_orders = Order.query.filter_by(
        seller_id=current_user.id,
        order_status="Pending"
    ).count()

    delivered_orders = Order.query.filter_by(
        seller_id=current_user.id,
        order_status="Delivered"
    ).count()

    total_sales = db.session.query(
        db.func.sum(Order.total_amount)
    ).filter(
        Order.seller_id == current_user.id,
        Order.payment_status == "Paid"
    ).scalar() or 0

    recent_orders = Order.query.filter_by(
        seller_id=current_user.id
    ).order_by(
        Order.created_at.desc()
    ).limit(10).all()

    return render_template(
        "seller_dashboard.html",
        total_products=total_products,
        total_orders=total_orders,
        pending_orders=pending_orders,
        delivered_orders=delivered_orders,
        total_sales=total_sales,
        recent_orders=recent_orders
    )

@app.route("/seller/sales-chart")
@login_required
def seller_sales_chart():

    data = []

    for i in range(30):

        day = date.today() - timedelta(days=i)

        amount = db.session.query(
            db.func.sum(Order.total_amount)
        ).filter(
            db.func.date(Order.created_at) == day,
            Order.seller_id == current_user.id
        ).scalar() or 0

        data.append({

            "date": day.strftime("%d %b"),

            "sales": amount

        })

    return jsonify(data[::-1])

@app.route("/product/<int:product_id>/review", methods=["POST"])
@login_required
def add_product_review(product_id):

    product = Product.query.get_or_404(product_id)

    order_item = db.session.query(OrderItem).join(Order).filter(
        Order.user_id == current_user.id,
        Order.order_status == "Delivered",
        OrderItem.product_id == product.id
    ).first()

    if not order_item:

        flash(
            "Only customers who purchased this product can review it.",
            "warning"
        )

        return redirect(f"/product/{product.id}")

    existing = ProductReview.query.filter_by(
        product_id=product.id,
        customer_id=current_user.id,
        order_id=order_item.order_id
    ).first()

    if existing:

        flash(
            "You have already reviewed this product.",
            "warning"
        )

        return redirect(f"/product/{product.id}")

    review = ProductReview(

        product_id=product.id,

        seller_id=product.seller_id,

        customer_id=current_user.id,

        order_id=order_item.order_id,

        rating=int(request.form["rating"]),

        title=request.form.get("title"),

        review=request.form.get("review")

    )

    db.session.add(review)

    reviews = ProductReview.query.filter_by(
        product_id=product.id
    ).all()

    product.total_reviews = len(reviews) + 1

    total = sum(r.rating for r in reviews)

    product.average_rating = (
        total + review.rating
    ) / product.total_reviews

    db.session.commit()

@app.route("/wishlist/add/<int:product_id>")
@login_required
def add_to_wishlist(product_id):

    product = Product.query.get_or_404(product_id)

    exists = Wishlist.query.filter_by(
        user_id=current_user.id,
        product_id=product.id
    ).first()

    if not exists:

        db.session.add(
            Wishlist(
                user_id=current_user.id,
                product_id=product.id
            )
        )

        db.session.commit()

    return redirect(request.referrer or f"/product/{product.id}")

@app.route("/wishlist/remove/<int:product_id>")
@login_required
def remove_from_wishlist(product_id):

    item = Wishlist.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first_or_404()

    db.session.delete(item)

    db.session.commit()

    return redirect(request.referrer or "/wishlist")

@app.route("/wishlist")
@login_required
def wishlist():

    items = Wishlist.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Wishlist.created_at.desc()
    ).all()

    return render_template(
        "wishlist.html",
        items=items
    )

@app.route("/return/<int:order_item_id>", methods=["POST"])
@login_required
def submit_return(order_item_id):

    item = OrderItem.query.get_or_404(order_item_id)

    request_return = ReturnRequest(

        order_id=item.order_id,

        order_item_id=item.id,

        product_id=item.product_id,

        customer_id=current_user.id,

        seller_id=item.product.seller_id,

        reason=request.form.get("reason"),

        description=request.form.get("description"),

        refund_amount=item.total_price

    )

    db.session.add(request_return)

    db.session.flush()

@app.route("/return/<int:order_item_id>")
@login_required
def return_product(order_item_id):

    item = OrderItem.query.get_or_404(order_item_id)

    if item.order.user_id != current_user.id:
        abort(403)

    if item.order.order_status != "Delivered":

        flash(
            "Return can only be requested after delivery.",
            "warning"
        )

        return redirect(f"/order/{item.order_id}")

    existing = ReturnRequest.query.filter_by(
        order_item_id=item.id
    ).first()

    if existing:

        flash(
            "Return request already submitted.",
            "warning"
        )

        return redirect(f"/order/{item.order_id}")

    return render_template(
        "return_product.html",
        item=item
    )

    images = request.files.getlist("images")

    for image in images:

        if image.filename:

            filename = secure_filename(image.filename)

            filename = (
                str(uuid.uuid4())
                + "_"
                + filename
            )

            image.save(
                os.path.join(
                    app.config["RETURN_UPLOAD_FOLDER"],
                    filename
                )
            )

            db.session.add(

                ReturnImage(

                    return_id=request_return.id,

                    image=filename

                )

            )

    send_notification(

        user_id=item.product.seller_id,

        user_type="hr",

        message=f"New return request for Order #{item.order.order_number}",

        link=f"/seller/returns/{request_return.id}",

        type="return"

    )

    db.session.commit()

    flash(

        "Return request submitted successfully.",

        "success"

    )

    return redirect(f"/order/{item.order_id}")

@app.route("/admin/returns")
@admin_required
def admin_returns():

    returns = ReturnRequest.query.order_by(
        ReturnRequest.created_at.desc()
    ).all()

    return render_template(
        "admin_returns.html",
        returns=returns
    )

@app.route("/admin/returns/<int:return_id>")
@admin_required
def admin_return_details(return_id):

    return_request = ReturnRequest.query.get_or_404(return_id)

    return render_template(
        "admin_return_details.html",
        return_request=return_request
    )

@app.route("/admin/returns/<int:return_id>/approve", methods=["POST"])
@admin_required
def admin_approve_return(return_id):

    return_request = ReturnRequest.query.get_or_404(return_id)

    if return_request.status == "Refunded":

        flash(
            "Refund already completed.",
            "warning"
        )

        return redirect(f"/admin/returns/{return_request.id}")

    return_request.status = "Approved"

    return_request.admin_remarks = request.form.get(
        "admin_remarks"
    )

    return_request.approved_at = india_time()

    order = Order.query.get(return_request.order_id)

    order.refund_status = "Approved"

    db.session.commit()

    send_notification(

        user_id=return_request.customer_id,

        user_type="candidate",

        message="Your refund request has been approved.",

        link=f"/return-status/{return_request.id}",

        type="refund"

    )

    flash(
        "Return approved successfully.",
        "success"
    )

    return redirect("/admin/returns")

@app.route("/admin/returns/<int:return_id>/reject", methods=["POST"])
@admin_required
def admin_reject_return(return_id):

    return_request = ReturnRequest.query.get_or_404(return_id)

    return_request.status = "Rejected"

    return_request.admin_remarks = request.form.get(
        "admin_remarks"
    )

    db.session.commit()

    send_notification(

        user_id=return_request.customer_id,

        user_type="candidate",

        message="Your refund request has been rejected.",

        link=f"/return-status/{return_request.id}",

        type="refund"

    )

    flash(
        "Return rejected.",
        "success"
    )

    return redirect("/admin/returns")

@app.route("/admin/returns/<int:return_id>/complete")
@admin_required
def complete_refund(return_id):

    return_request = ReturnRequest.query.get_or_404(return_id)

    return_request.status = "Refunded"

    return_request.completed_at = india_time()

    order = Order.query.get(return_request.order_id)

    order.refund_status = "Refunded"

    db.session.commit()

    send_notification(

        user_id=return_request.customer_id,

        user_type="candidate",

        message="Refund has been processed successfully.",

        link=f"/order/{order.id}",

        type="refund"

    )

    flash(
        "Refund completed.",
        "success"
    )

    return redirect("/admin/returns")

@app.route("/seller/returns")
@login_required
def seller_returns():

    returns = ReturnRequest.query.filter_by(
        seller_id=current_user.id
    ).order_by(
        ReturnRequest.created_at.desc()
    ).all()

    return render_template(
        "seller_returns.html",
        returns=returns
    )

@app.route("/seller/returns/<int:return_id>")
@login_required
def seller_return_details(return_id):

    return_request = ReturnRequest.query.filter_by(
        id=return_id,
        seller_id=current_user.id
    ).first_or_404()

    return render_template(
        "seller_return_details.html",
        return_request=return_request
    )

@app.route("/seller/returns/<int:return_id>/approve", methods=["POST"])
@login_required
def approve_return(return_id):

    return_request = ReturnRequest.query.filter_by(
        id=return_id,
        seller_id=current_user.id
    ).first_or_404()

    if return_request.status != "Pending":

        flash("Return request already processed.", "warning")

        return redirect(f"/seller/returns/{return_request.id}")

    return_request.status = "Seller Approved"

    return_request.seller_remarks = request.form.get(
        "seller_remarks"
    )

    return_request.approved_at = india_time()

    send_notification(

        user_id=return_request.customer_id,

        user_type="candidate",

        message="Your return request has been approved by the seller.",

        link=f"/return-status/{return_request.id}",

        type="return"

    )

    db.session.commit()

    flash("Return request approved.", "success")

    return redirect("/seller/returns")

@app.route("/seller/returns/<int:return_id>/reject", methods=["POST"])
@login_required
def reject_return(return_id):

    return_request = ReturnRequest.query.filter_by(
        id=return_id,
        seller_id=current_user.id
    ).first_or_404()

    if return_request.status != "Pending":

        flash("Return request already processed.", "warning")

        return redirect(f"/seller/returns/{return_request.id}")

    return_request.status = "Seller Rejected"

    return_request.seller_remarks = request.form.get(
        "seller_remarks"
    )

    send_notification(

        user_id=return_request.customer_id,

        user_type="candidate",

        message="Your return request has been rejected by the seller.",

        link=f"/return-status/{return_request.id}",

        type="return"

    )

    db.session.commit()

    flash("Return request rejected.", "success")

    return redirect("/seller/returns")

@app.route("/seller/returns/<int:return_id>/more-info", methods=["POST"])
@login_required
def return_more_info(return_id):

    return_request = ReturnRequest.query.filter_by(
        id=return_id,
        seller_id=current_user.id
    ).first_or_404()

    return_request.status = "More Information Required"

    return_request.seller_remarks = request.form.get(
        "seller_remarks"
    )

    send_notification(

        user_id=return_request.customer_id,

        user_type="candidate",

        message="Seller has requested more information for your return request.",

        link=f"/return-status/{return_request.id}",

        type="return"

    )

    db.session.commit()

    flash("Customer notified.", "success")

    return redirect(f"/seller/returns/{return_request.id}")

@app.route("/admin/returns/<int:return_id>/pickup")
@admin_required
def schedule_return_pickup(return_id):

    return_request = ReturnRequest.query.get_or_404(return_id)

    ship = get_shiprocket()

    response = ship.create_return_pickup(return_request)

    return_request.pickup_awb = response["awb_code"]

    return_request.pickup_status = "Scheduled"

    return_request.pickup_scheduled_at = india_time()

    db.session.commit()

    send_notification(

        user_id=return_request.customer_id,

        user_type="candidate",

        message="Return pickup has been scheduled.",

        link=f"/return-status/{return_request.id}",

        type="return"

    )

    flash("Pickup scheduled successfully.","success")

    return redirect(f"/admin/returns/{return_request.id}")

@app.route("/seller/product/<int:id>/promote")
@login_required
def promote_product(id):

    product = Product.query.filter_by(

        id=id,

        seller_id=current_user.id

    ).first_or_404()

    settings = get_business_settings()

    if current_user.credits < settings.product_promotion_price:

        flash(

            "Not enough credits.",

            "danger"

        )

        return redirect("/seller/products")

    current_user.credits -= settings.product_promotion_price

    product.is_promoted = True

    product.promotion_priority = 1

    product.promotion_amount = settings.product_promotion_price

    product.promotion_type = "Product"

    product.promotion_expires_at = (

        india_time() +

        timedelta(

            days=settings.promotion_duration_days

        )

    )

    db.session.add(

        ProductPromotion(

            product_id=product.id,

            seller_id=current_user.id,

            credits_used=settings.product_promotion_price,

            amount=settings.product_promotion_price,

            end_date=product.promotion_expires_at

        )

    )

    db.session.commit()

    send_notification(
        user_id=current_user.id,
        user_type="hr",
        message=f"{product.name} is now promoted.",
        link=f"/product/{product.id}",
        type="promotion"
    )

    return redirect("/seller/products")


@app.route("/admin/seller/<int:id>/verify")
@admin_required
def verify_seller(id):

    seller = User.query.get_or_404(id)

    seller.is_verified_seller = True

    seller.verification_status = "Verified"

    seller.verification_date = india_time()

    db.session.commit()

    send_notification(

        user_id=seller.id,

        user_type="hr",

        message="🎉 Your shop has been verified.",

        link="/profile",

        type="verification"

    )

    flash("Seller verified.","success")

    return redirect("/admin/seller-verifications")

@app.route("/shop/search")
def shop_search():

    keyword = request.args.get("q", "")
    category = request.args.get("category")
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")
    rating = request.args.get("rating")
    sort = request.args.get("sort")

    products = Product.query.filter(
        Product.is_active == True
    )

    if keyword:
        products = products.filter(
            Product.name.ilike(f"%{keyword}%")
        )

    if category:
        products = products.filter(
            Product.category_id == category
        )

    if min_price:
        products = products.filter(
            Product.price >= float(min_price)
        )

    if max_price:
        products = products.filter(
            Product.price <= float(max_price)
        )

    if rating:
        products = products.filter(
            Product.average_rating >= float(rating)
        )

    verified = request.args.get("verified")

    if verified:
        products = products.join(User).filter(
            User.is_verified_seller == True
        )

    products = products.order_by(
        Product.is_promoted.desc(),
        Product.promotion_priority.desc()
    )

    if sort == "price_low":
        products = products.order_by(
            Product.price.asc()
        )

    elif sort == "price_high":
        products = products.order_by(
            Product.price.desc()
        )

    elif sort == "rating":
        products = products.order_by(
            Product.average_rating.desc()
        )

    elif sort == "latest":
        products = products.order_by(
            Product.created_at.desc()
        )

    products = products.paginate(
        page=request.args.get("page", 1, type=int),
        per_page=20
    )

    return render_template(
        "shop_products.html",
        products=products
    )

@app.route("/seller/analytics")
@login_required
def seller_analytics():

    seller_id = current_user.id

    total_sales = db.session.query(
        db.func.sum(Order.total_amount)
    ).filter(
        Order.seller_id == seller_id,
        Order.payment_status == "Paid"
    ).scalar() or 0

    total_orders = Order.query.filter_by(
        seller_id=seller_id
    ).count()

    total_products = Product.query.filter_by(
        seller_id=seller_id
    ).count()

    total_customers = db.session.query(
        db.func.count(
            db.distinct(Order.user_id)
        )
    ).filter(
        Order.seller_id == seller_id
    ).scalar()

    return render_template(
        "seller_analytics.html",
        total_sales=total_sales,
        total_orders=total_orders,
        total_products=total_products,
        total_customers=total_customers
    )

@app.route("/seller/monthly-sales")
@login_required
def monthly_sales():

    data=[]

    for month in range(1,13):

        amount=db.session.query(

            db.func.sum(Order.total_amount)

        ).filter(

            db.extract("month",Order.created_at)==month,

            Order.seller_id==current_user.id

        ).scalar() or 0

        data.append(amount)

    return jsonify(data)

@app.route("/admin/marketplace")
@admin_required
def admin_marketplace():

    total_shops = User.query.filter_by(
        is_shop_owner=True
    ).count()

    total_products = Product.query.count()

    total_orders = Order.query.count()

    total_sales = db.session.query(
        db.func.sum(Order.total_amount)
    ).filter(
        Order.payment_status == "Paid"
    ).scalar() or 0

    total_commission = db.session.query(
        db.func.sum(Order.platform_commission)
    ).scalar() or 0

    pending_returns = ReturnRequest.query.filter(
        ReturnRequest.status.in_([
            "Pending",
            "Seller Approved",
            "Approved"
        ])
    ).count()

    pending_withdrawals = Withdrawal.query.filter_by(
        status="Pending"
    ).count()

    pending_shipments = Order.query.filter(
        Order.order_status.in_([
            "Pending",
            "Packed",
            "Shipped"
        ])
    ).count()

    latest_orders = Order.query.order_by(
        Order.created_at.desc()
    ).limit(10).all()

    return render_template(
        "admin_marketplace/dashboard.html",

        total_shops=total_shops,
        total_products=total_products,
        total_orders=total_orders,
        total_sales=total_sales,
        total_commission=total_commission,
        pending_returns=pending_returns,
        pending_withdrawals=pending_withdrawals,
        pending_shipments=pending_shipments,
        latest_orders=latest_orders
    )

@app.route("/admin/marketplace/sellers")
@admin_required
def marketplace_sellers():

    sellers = User.query.filter_by(
        is_shop_owner=True
    ).order_by(
        User.created_at.desc()
    ).all()

    return render_template(
        "admin_marketplace/sellers.html",
        sellers=sellers
    )

@app.route("/admin/marketplace/seller/<int:id>")
@admin_required
def marketplace_seller(id):

    seller = User.query.get_or_404(id)

    total_products = Product.query.filter_by(
        seller_id=id
    ).count()

    total_orders = Order.query.filter_by(
        seller_id=id
    ).count()

    total_sales = db.session.query(
        db.func.sum(Order.total_amount)
    ).filter(
        Order.seller_id == id
    ).scalar() or 0

    return render_template(

        "admin_marketplace/seller_details.html",

        seller=seller,

        total_products=total_products,

        total_orders=total_orders,

        total_sales=total_sales

    )

@app.route("/admin/marketplace/seller/<int:id>/verify")
@admin_required
def verify_marketplace_seller(id):

    seller = User.query.get_or_404(id)

    seller.is_verified_seller = True

    seller.verification_status = "Verified"

    seller.verification_date = india_time()

    db.session.commit()

    send_notification(

        user_id=seller.id,

        user_type="hr",

        message="🎉 Congratulations! Your shop has been verified.",

        link="/profile",

        type="verification"

    )

    flash(

        "Seller verified successfully.",

        "success"

    )

    return redirect(request.referrer)

@app.route("/admin/marketplace/seller/<int:id>/toggle")
@admin_required
def toggle_shop(id):

    seller = User.query.get_or_404(id)

    seller.is_shop_active = not seller.is_shop_active

    db.session.commit()

    flash(

        "Seller status updated.",

        "success"

    )

    return redirect(request.referrer)

@app.route("/admin/marketplace/seller/<int:id>/promotion")
@admin_required
def seller_promotions(id):

    promotions = ShopPromotion.query.filter_by(

        seller_id=id

    ).order_by(

        ShopPromotion.start_date.desc()

    ).all()

    return render_template(

        "admin_marketplace/seller_promotions.html",

        promotions=promotions

    )

@app.route("/admin/marketplace/seller/<int:id>/analytics")
@admin_required
def seller_admin_analytics(id):

    seller = User.query.get_or_404(id)

    products = Product.query.filter_by(

        seller_id=id

    ).all()

    return render_template(

        "admin_marketplace/seller_analytics.html",

        seller=seller,

        products=products

    )

@app.route("/admin/marketplace/products")
@admin_required
def marketplace_products():

    products = Product.query.order_by(
        Product.created_at.desc()
    ).all()

    return render_template(
        "admin_marketplace/products.html",
        products=products
    )

@app.route("/admin/marketplace/product/<int:id>")
@admin_required
def marketplace_product(id):

    product = Product.query.get_or_404(id)

    return render_template(
        "admin_marketplace/product_details.html",
        product=product
    )

@app.route("/admin/marketplace/product/<int:id>/toggle")
@admin_required
def toggle_product(id):

    product = Product.query.get_or_404(id)

    product.is_active = not product.is_active

    db.session.commit()

    flash(
        "Product status updated.",
        "success"
    )

    return redirect(request.referrer)

@app.route("/admin/marketplace/product/<int:id>/delete")
@admin_required
def delete_product_admin(id):

    product = Product.query.get_or_404(id)

    db.session.delete(product)

    db.session.commit()

    flash(
        "Product deleted successfully.",
        "success"
    )

    return redirect("/admin/marketplace/products")

@app.route("/admin/marketplace/product/<int:id>/feature")
@admin_required
def feature_product(id):

    product = Product.query.get_or_404(id)

    product.is_promoted = True

    product.promotion_priority = 999

    db.session.commit()

    flash(
        "Product marked as featured.",
        "success"
    )

    return redirect(request.referrer)

@app.route("/admin/marketplace/product-reports")
@admin_required
def product_reports():

    reports = ProductReport.query.order_by(
        ProductReport.created_at.desc()
    ).all()

    return render_template(
        "admin_marketplace/product_reports.html",
        reports=reports
    )

@app.route("/admin/marketplace/orders")
@admin_required
def marketplace_orders():

    orders = Order.query.order_by(
        Order.created_at.desc()
    ).all()

    return render_template(
        "admin_marketplace/orders.html",
        orders=orders
    )

@app.route("/admin/marketplace/order/<int:id>")
@admin_required
def marketplace_order(id):

    order = Order.query.get_or_404(id)

    return render_template(
        "admin_marketplace/order_details.html",
        order=order
    )

@app.route(
    "/admin/marketplace/order/<int:id>/status",
    methods=["POST"]
)
@admin_required
def update_order_status(id):

    order = Order.query.get_or_404(id)

    status = request.form.get("status")

    order.order_status = status

    db.session.commit()

    send_notification(

        user_id=order.user_id,

        user_type="candidate",

        message=f"Your order {order.order_number} is now {status}.",

        link=f"/order/{order.id}",

        type="order"

    )

    flash(
        "Order updated successfully.",
        "success"
    )

    return redirect(request.referrer)

@app.route("/admin/marketplace/order/<int:id>/cancel")
@admin_required
def cancel_marketplace_order(id):

    order = Order.query.get_or_404(id)

    order.order_status = "Cancelled"

    db.session.commit()

    send_notification(

        user_id=order.user_id,

        user_type="candidate",

        message="Your order has been cancelled by the admin.",

        link=f"/order/{order.id}",

        type="order"

    )

    flash(
        "Order cancelled.",
        "success"
    )

    return redirect(request.referrer)

@app.route(
    "/admin/marketplace/order/<int:id>/payment",
    methods=["POST"]
)
@admin_required
def update_payment_status(id):

    order = Order.query.get_or_404(id)

    order.payment_status = request.form.get(
        "payment_status"
    )

    db.session.commit()

    flash(
        "Payment updated.",
        "success"
    )

    return redirect(request.referrer)

@app.route("/admin/marketplace/finance")
@admin_required
def marketplace_finance():

    total_sales = db.session.query(
        db.func.sum(Order.total_amount)
    ).filter(
        Order.payment_status == "Paid"
    ).scalar() or 0

    total_commission = db.session.query(
        db.func.sum(Order.platform_commission)
    ).scalar() or 0

    seller_payout = db.session.query(
        db.func.sum(Order.seller_amount)
    ).filter(
        Order.wallet_released == True
    ).scalar() or 0

    pending_payout = db.session.query(
        db.func.sum(Order.seller_amount)
    ).filter(
        Order.wallet_released == False
    ).scalar() or 0

    total_refunds = db.session.query(
        db.func.sum(ReturnRequest.refund_amount)
    ).filter(
        ReturnRequest.status == "Refunded"
    ).scalar() or 0

    return render_template(

        "admin_marketplace/finance.html",

        total_sales=total_sales,

        total_commission=total_commission,

        seller_payout=seller_payout,

        pending_payout=pending_payout,

        total_refunds=total_refunds

    )

@app.route("/admin/marketplace/withdrawals")
@admin_required
def marketplace_withdrawals():

    withdrawals = Withdrawal.query.order_by(
        Withdrawal.created_at.desc()
    ).all()

    return render_template(

        "admin_marketplace/withdrawals.html",

        withdrawals=withdrawals

    )

@app.route("/admin/marketplace/withdrawal/<int:id>/approve")
@admin_required
def approve_marketplace_withdrawal(id):

    withdrawal = Withdrawal.query.get_or_404(id)

    withdrawal.status = "Approved"

    withdrawal.processed_at = india_time()

    db.session.commit()

    send_notification(

        user_id=withdrawal.user_id,

        user_type="hr",

        message="Your withdrawal has been approved.",

        link="/wallet",

        type="withdrawal"

    )

    flash(

        "Withdrawal approved.",

        "success"

    )

    return redirect(request.referrer)

@app.route("/admin/marketplace/withdrawal/<int:id>/reject")
@admin_required
def reject_marketplace_withdrawal(id):

    withdrawal = Withdrawal.query.get_or_404(id)

    withdrawal.status = "Rejected"

    db.session.commit()

    flash(

        "Withdrawal rejected.",

        "success"

    )

    return redirect(request.referrer)

@app.route("/admin/marketplace/commission")
@admin_required
def commission_report():

    orders = Order.query.filter(

        Order.payment_status == "Paid"

    ).all()

    return render_template(

        "admin_marketplace/commission.html",

        orders=orders

    )

@app.route("/admin/marketplace/settings",
methods=["GET","POST"])
@admin_required
def marketplace_settings():

    settings = get_business_settings()

    if request.method == "POST":

        settings.marketplace_enabled = bool(request.form.get("marketplace_enabled"))

        settings.marketplace_commission = float(request.form["marketplace_commission"])

        settings.seller_payment_hold_days = int(request.form["seller_payment_hold_days"])

        settings.free_shipping_amount = float(request.form["free_shipping_amount"])

        settings.return_window_days = int(request.form["return_window_days"])

        settings.product_promotion_price = int(request.form["product_promotion_price"])

        settings.shop_promotion_price = int(request.form["shop_promotion_price"])

        settings.marketplace_maintenance = bool(request.form.get("marketplace_maintenance"))

        db.session.commit()

        flash("Settings updated.","success")

        return redirect(request.url)

    return render_template(
        "admin_marketplace/settings.html",
        settings=settings
    )

@app.route("/admin/marketplace/banners")
@admin_required
def marketplace_banners():

    banners=HomepageBanner.query.order_by(

        HomepageBanner.display_order

    ).all()

    return render_template(

        "admin_marketplace/banners.html",

        banners=banners

    )

@app.route("/admin/marketplace/banner/add",
methods=["GET","POST"])
@admin_required
def add_banner():

    if request.method=="POST":

        image=request.files["image"]

        filename=save_image(image,"homepage_banners")

        banner=HomepageBanner(

            title=request.form["title"],

            subtitle=request.form["subtitle"],

            image=filename,

            button_text=request.form["button_text"],

            button_link=request.form["button_link"],

            display_order=int(request.form["display_order"]),

            is_active="is_active" in request.form

        )

        db.session.add(banner)

        db.session.commit()

        flash("Banner added successfully.","success")

        return redirect("/admin/marketplace/banners")

    return render_template("admin_marketplace/add_banner.html")

@app.route("/admin/marketplace/banner/<int:id>/edit",
methods=["GET","POST"])
@admin_required
def edit_banner(id):

    banner=HomepageBanner.query.get_or_404(id)

    if request.method=="POST":

        banner.title=request.form["title"]

        banner.subtitle=request.form["subtitle"]

        banner.button_text=request.form["button_text"]

        banner.button_link=request.form["button_link"]

        banner.display_order=int(request.form["display_order"])

        banner.is_active="is_active" in request.form

        if request.files.get("image"):

            banner.image=save_image(

                request.files["image"],

                "homepage_banners"

            )

        db.session.commit()

        flash("Banner updated.","success")

        return redirect("/admin/marketplace/banners")

    return render_template(

        "admin_marketplace/edit_banner.html",

        banner=banner

    )

@app.route("/admin/marketplace/banner/<int:id>/toggle")
@admin_required
def toggle_banner(id):

    banner=HomepageBanner.query.get_or_404(id)

    banner.is_active=not banner.is_active

    db.session.commit()

    return redirect(request.referrer)

@app.route("/admin/marketplace/banner/<int:id>/delete")
@admin_required
def delete_banner(id):

    banner=HomepageBanner.query.get_or_404(id)

    db.session.delete(banner)

    db.session.commit()

    flash("Banner deleted.","success")

    return redirect("/admin/marketplace/banners")

@app.route("/admin/marketplace/categories")
@admin_required
def marketplace_categories():

    categories = Category.query.order_by(
        Category.name
    ).all()

    return render_template(
        "admin_marketplace/categories.html",
        categories=categories
    )

@app.route("/admin/marketplace/category/add",
methods=["GET","POST"])
@admin_required
def add_marketplace_category():

    if request.method=="POST":

        image=None

        if request.files.get("image"):

            image=save_image(

                request.files["image"],

                "category_images"

            )

        category=Category(

            name=request.form["name"],

            description=request.form["description"],

            image=image,

            is_featured="is_featured" in request.form,

            active="active" in request.form

        )

        db.session.add(category)

        db.session.commit()

        flash("Category created.","success")

        return redirect("/admin/marketplace/categories")

    return render_template(
        "admin_marketplace/add_category.html"
    )

@app.route("/admin/marketplace/category/<int:id>/edit",
methods=["GET","POST"])
@admin_required
def edit_marketplace_category(id):

    category=Category.query.get_or_404(id)

    if request.method=="POST":

        category.name=request.form["name"]

        category.description=request.form["description"]

        category.is_featured="is_featured" in request.form

        category.active="active" in request.form

        if request.files.get("image"):

            category.image=save_image(

                request.files["image"],

                "category_images"

            )

        db.session.commit()

        flash("Category updated.","success")

        return redirect("/admin/marketplace/categories")

    return render_template(

        "admin_marketplace/edit_category.html",

        category=category

    )

@app.route("/admin/marketplace/category/<int:id>/delete")
@admin_required
def delete_marketplace_category(id):

    category=Category.query.get_or_404(id)

    db.session.delete(category)

    db.session.commit()

    flash("Category deleted.","success")

    return redirect("/admin/marketplace/categories")

@app.route("/admin/marketplace/category/<int:id>/toggle")
@admin_required
def toggle_category(id):

    category = Category.query.get_or_404(id)

    category.active = not category.active

    db.session.commit()

    flash(
        "Category status updated.",
        "success"
    )

    return redirect(request.referrer)

@app.route("/admin/marketplace/category/<int:id>")
@admin_required
def marketplace_category(id):

    category = Category.query.get_or_404(id)

    total_products = Product.query.filter_by(
        category_id=id
    ).count()

    total_sales = db.session.query(
        db.func.sum(Product.revenue)
    ).filter(
        Product.category_id == id
    ).scalar() or 0

    return render_template(

        "admin_marketplace/category_details.html",

        category=category,

        total_products=total_products,

        total_sales=total_sales

    )

@app.route("/admin/marketplace/coupons")
@admin_required
def marketplace_coupons():

    coupons = Coupon.query.order_by(
        Coupon.created_at.desc()
    ).all()

    return render_template(
        "admin_marketplace/coupons.html",
        coupons=coupons
    )

@app.route("/admin/marketplace/coupon/add",
methods=["GET","POST"])
@admin_required
def add_coupon():

    if request.method=="POST":

        coupon = Coupon(

            code=request.form["code"].upper(),

            title=request.form["title"],

            description=request.form["description"],

            discount_type=request.form["discount_type"],

            discount_value=float(request.form["discount_value"]),

            minimum_order=float(request.form["minimum_order"]),

            maximum_discount=float(request.form["maximum_discount"]),

            usage_limit=int(request.form["usage_limit"]),

            start_date=parse_datetime(
                request.form["start_date"]
            ),

            expiry_date=parse_datetime(
                request.form["expiry_date"]
            ),

            active="active" in request.form

        )

        db.session.add(coupon)

        db.session.commit()

        flash("Coupon created.","success")

        return redirect("/admin/marketplace/coupons")

    return render_template(
        "admin_marketplace/add_coupon.html"
    )

@app.route("/admin/marketplace/coupon/<int:id>/toggle")
@admin_required
def toggle_coupon(id):

    coupon = Coupon.query.get_or_404(id)

    coupon.active = not coupon.active

    db.session.commit()

    flash(
        "Coupon updated.",
        "success"
    )

    return redirect(request.referrer)

@app.route("/admin/marketplace/coupon/<int:id>/delete")
@admin_required
def delete_coupon(id):

    coupon = Coupon.query.get_or_404(id)

    db.session.delete(coupon)

    db.session.commit()

    flash(
        "Coupon deleted.",
        "success"
    )

    return redirect("/admin/marketplace/coupons")

@app.route("/admin/marketplace/coupon/<int:id>")
@admin_required
def coupon_details(id):

    coupon = Coupon.query.get_or_404(id)

    return render_template(

        "admin_marketplace/coupon_details.html",

        coupon=coupon

    )

@app.route("/admin/marketplace/coupon/<int:id>/edit",
methods=["GET","POST"])
@admin_required
def edit_coupon(id):

    coupon = Coupon.query.get_or_404(id)

    if request.method=="POST":

        coupon.code = request.form["code"].upper()

        coupon.title = request.form["title"]

        coupon.description = request.form["description"]

        coupon.discount_type = request.form["discount_type"]

        coupon.discount_value = float(request.form["discount_value"])

        coupon.minimum_order = float(request.form["minimum_order"])

        coupon.maximum_discount = float(request.form["maximum_discount"])

        coupon.usage_limit = int(request.form["usage_limit"])

        coupon.start_date = parse_datetime(
            request.form["start_date"]
        )

        coupon.expiry_date = parse_datetime(
            request.form["expiry_date"]
        )

        coupon.active = "active" in request.form

        db.session.commit()

        flash(
            "Coupon updated.",
            "success"
        )

        return redirect("/admin/marketplace/coupons")

    return render_template(

        "admin_marketplace/edit_coupon.html",

        coupon=coupon

    )

@app.route("/admin/marketplace/coupons/analytics")
@admin_required
def coupon_analytics():

    total = Coupon.query.count()

    active = Coupon.query.filter_by(
        active=True
    ).count()

    expired = Coupon.query.filter(
        Coupon.expiry_date < india_time()
    ).count()

    most_used = Coupon.query.order_by(
        Coupon.used_count.desc()
    ).first()

    return render_template(

        "admin_marketplace/coupon_analytics.html",

        total=total,

        active=active,

        expired=expired,

        most_used=most_used

    )

@app.route("/admin/marketplace/cms")
@admin_required
def cms_pages():

    pages = CMSPage.query.order_by(
        CMSPage.title
    ).all()

    return render_template(

        "admin_marketplace/cms.html",

        pages=pages

    )

@app.route("/admin/marketplace/cms/add",
methods=["GET","POST"])
@admin_required
def add_cms_page():

    if request.method=="POST":

        page = CMSPage(

            title=request.form["title"],

            slug=request.form["slug"],

            content=request.form["content"],

            meta_title=request.form["meta_title"],

            meta_description=request.form["meta_description"],

            is_published="is_published" in request.form

        )

        db.session.add(page)

        db.session.commit()

        flash(
            "Page created.",
            "success"
        )

        return redirect("/admin/marketplace/cms")

    return render_template(
        "admin_marketplace/add_cms.html"
    )

@app.route("/admin/marketplace/cms/<int:id>/edit",
methods=["GET","POST"])
@admin_required
def edit_cms_page(id):

    page = CMSPage.query.get_or_404(id)

    if request.method=="POST":

        page.title = request.form["title"]

        page.slug = request.form["slug"]

        page.content = request.form["content"]

        page.meta_title = request.form["meta_title"]

        page.meta_description = request.form["meta_description"]

        page.is_published = "is_published" in request.form

        db.session.commit()

        flash(
            "Page updated.",
            "success"
        )

        return redirect("/admin/marketplace/cms")

    return render_template(

        "admin_marketplace/edit_cms.html",

        page=page

    )

@app.route("/page/<slug>")
def cms_page(slug):

    page = CMSPage.query.filter_by(

        slug=slug,

        is_published=True

    ).first_or_404()

    return render_template(

        "cms_page.html",

        page=page

    )

@app.route("/admin/marketplace/cms/<int:id>/toggle")
@admin_required
def toggle_cms_page(id):

    page = CMSPage.query.get_or_404(id)

    page.is_published = not page.is_published

    db.session.commit()

    flash(
        "Page status updated.",
        "success"
    )

    return redirect(request.referrer)


@app.route("/admin/marketplace/cms/<int:id>/delete")
@admin_required
def delete_cms_page(id):

    page = CMSPage.query.get_or_404(id)

    db.session.delete(page)

    db.session.commit()

    flash(
        "Page deleted successfully.",
        "success"
    )

    return redirect("/admin/marketplace/cms")

@app.route("/admin/marketplace/social-links")
@admin_required
def social_links():

    links = SocialLink.query.order_by(
        SocialLink.platform
    ).all()

    return render_template(

        "admin_marketplace/social_links.html",

        links=links

    )

@app.route("/admin/marketplace/contact-settings",
methods=["GET","POST"])
@admin_required
def contact_settings():

    settings = ContactSettings.query.first()

    if not settings:

        settings = ContactSettings()

        db.session.add(settings)

        db.session.commit()

    if request.method == "POST":

        settings.company_name = request.form["company_name"]

        settings.email = request.form["email"]

        settings.support_email = request.form["support_email"]

        settings.phone = request.form["phone"]

        settings.whatsapp = request.form["whatsapp"]

        settings.address = request.form["address"]

        settings.business_hours = request.form["business_hours"]

        settings.google_map = request.form["google_map"]

        db.session.commit()

        flash(
            "Contact settings updated.",
            "success"
        )

        return redirect(request.url)

    return render_template(

        "admin_marketplace/contact_settings.html",

        settings=settings

    )

@app.route("/admin/marketplace/seo",
methods=["GET","POST"])
@admin_required
def seo_settings():

    seo = SEOSettings.query.first()

    if not seo:

        seo = SEOSettings()

        db.session.add(seo)

        db.session.commit()

    if request.method == "POST":

        seo.site_title = request.form["site_title"]

        seo.meta_description = request.form["meta_description"]

        seo.meta_keywords = request.form["meta_keywords"]

        db.session.commit()

        flash(
            "SEO settings updated.",
            "success"
        )

        return redirect(request.url)

    return render_template(

        "admin_marketplace/seo.html",

        seo=seo

    )

@app.route("/shop/manage-product/<int:id>")
@login_required
def manage_product(id):

    product = Product.query.filter_by(
        id=id,
        seller_id=current_user.id
    ).first_or_404()

    return render_template(
        "manage_product.html",
        product=product
    )

@app.route(
    "/shop/toggle-product/<int:id>",
    methods=["POST"]
)
@login_required
def owner_toggle_product(id):

    product = Product.query.filter_by(
        id=id,
        seller_id=current_user.id
    ).first_or_404()

    if product.status == "active":

        product.status = "inactive"
        product.is_active = False

        flash(
            "Product deactivated successfully.",
            "success"
        )

    else:

        product.status = "active"
        product.is_active = True

        flash(
            "Product activated successfully.",
            "success"
        )

    db.session.commit()

    return redirect(
        url_for(
            "manage_product",
            id=product.id
        )
    )

# =========================
# SINGLE DEVICE LOGIN CHECK
# =========================

@app.before_request
def verify_single_device():

    print("AUTH:", current_user.is_authenticated)
    print("USER:", current_user.get_id() if current_user.is_authenticated else None)
    print("SESSION:", dict(session))
    print("TOKEN:", session.get("session_token"))

    if not current_user.is_authenticated:
        return

    # Ignore static files
    if request.endpoint == "static":
        return

    db.session.refresh(current_user)

    # First request after Remember Me restores login
    if "session_token" not in session:
        session["session_token"] = current_user.session_token
        return

    # No session token stored in DB
    if current_user.session_token is None:
        return

    # Another device logged in
    if session.get("session_token") != current_user.session_token:
        logout_user()
        session.clear()

        flash(
            "Your account was logged in from another device.",
            "warning"
        )

        return redirect(url_for("login"))

if __name__ == "__main__":

    with app.app_context():

        db.create_all()

        create_default_shop_categories()

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
