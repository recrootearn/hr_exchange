import logging
import random
import uuid
from flask import session
from flask_login import logout_user, current_user
import razorpay
from flask import send_file
import random
import smtplib
import resend
from email.mime.text import MIMEText
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, session, url_for, flash
import os
from datetime import datetime
import pandas as pd
from openpyxl import Workbook
from flask import send_file
import io
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from sqlalchemy import func
from math import ceil
import re

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

resend.api_key = "re_QT3qQPqz_Ngn6WAnA4A2ykKbH9CZEs6Fz"

RAZORPAY_KEY = "rzp_live_SukwF35NxDKD1h"
RAZORPAY_SECRET = "ctp74whaDCaF5omzFqoEg6Ya"

client = razorpay.Client(
    auth=(RAZORPAY_KEY, RAZORPAY_SECRET)
)

def generate_referral_code():
    return "RR" + str(random.randint(100000,999999))

def generate_candidate_referral_code():

    return "RC" + str(
        random.randint(100000, 999999)
    )

# =========================
# CONFIG & DB SETUP
# =========================
app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

db = SQLAlchemy(app)

# =========================
# MODELS
# =========================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    mobile = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(120), unique=True)
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
    referral_code = db.Column(db.String(20), unique=True)

    about_company = db.Column(db.Text)

    company_logo = db.Column(db.String(300))

    company_city = db.Column(db.String(100))

    company_website = db.Column(db.String(300))

    company_photos = db.Column(db.Text)

    company_city = db.Column(db.String(100))

    full_company_address = db.Column(db.Text)

    company_website = db.Column(db.String(200))

    referred_by = db.Column(db.String(20))

    total_referrals = db.Column(db.Integer, default=0)

    msme_certificate = db.Column(db.String(255))
    gumasta_certificate = db.Column(db.String(255))

    successful_referrals = db.Column(db.Integer, default=0)

    referral_earnings = db.Column(db.Float, default=0)

    referral_purchase_reward_given = db.Column(
       db.Boolean,
       default=False
)

class CandidateUser(UserMixin, db.Model):

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

    career_level = db.Column(db.String(20))

    company_name = db.Column(db.String(200))

    experience_from = db.Column(db.String(20))

    experience_to = db.Column(db.String(20))

    education = db.Column(db.Text)

    interested_fields = db.Column(db.Text)

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
        default=datetime.utcnow
    )

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

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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

    images = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
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
        default=datetime.utcnow
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
        default=datetime.utcnow
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
        default=datetime.utcnow
    )

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
        default=datetime.utcnow
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
        default=datetime.utcnow
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

    hr_minimum_purchase = db.Column(db.Integer, default=500)

    hr_daily_referral_limit = db.Column(db.Integer, default=10)
    candidate_daily_referral_limit = db.Column(db.Integer, default=10)

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

    # -------------------------
    # Audit
    # -------------------------
    updated_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_fake = db.Column(db.Boolean, default=False)
    report_count = db.Column(db.Integer, default=0)
    wrong_experience_reports = db.Column(db.Integer, default=0)

class Unlock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    candidate_id = db.Column(db.Integer)
    created_at = db.Column(
    db.DateTime,
    default=datetime.utcnow
    )

class CandidateWalletHistory(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    candidate_id = db.Column(db.Integer)

    amount = db.Column(db.Float)

    action = db.Column(db.String(200))

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

class CreditHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    amount = db.Column(db.Integer)
    action = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
        default=datetime.utcnow
    )

class LeadView(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    hr_id = db.Column(db.Integer, nullable=False)

    candidate_id = db.Column(db.Integer, nullable=False)

    viewed_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

class HRFollower(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    hr_id = db.Column(db.Integer)

    candidate_id = db.Column(db.Integer)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

class CandidateContactUnlock(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    hr_id = db.Column(db.Integer)

    candidate_user_id = db.Column(db.Integer)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

class AdminLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SupportReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    ticket_id = db.Column(db.Integer)

    sender = db.Column(db.String(50))

    message = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
        default=datetime.utcnow
    )

class SeenLead(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer)

    candidate_id = db.Column(db.Integer)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

class Withdrawal(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer
    )

    amount = db.Column(
        db.Float
    )

    status = db.Column(
        db.String(50),
        default='Pending'
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

class PasswordReset(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120))

    otp = db.Column(db.String(10))

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
    """Helper to check if current user is Harshit"""
    if not current_user.is_authenticated or current_user.username.upper() != "HARSHIT":
        return False
    return True

def get_business_settings():

    settings = BusinessSettings.query.first()

    if not settings:

        settings = BusinessSettings()

        db.session.add(settings)

        db.session.commit()

    return settings

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

def send_notification(
    user_id,
    user_type,
    message,
    link="",
    image="",
    type="general"
):

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

# =========================
# USER ROUTES
# =========================

@app.route('/')
def landing():

    return render_template(
        'splash.html'
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

    today = date.today()

    daily_login_completed = True

    today_uploads = Candidate.query.filter(
        Candidate.uploaded_by == current_user.id,
        db.func.date(Candidate.created_at) == today
    ).count()

    daily_upload_completed = today_uploads >= 10

    today_referrals = User.query.filter(
        User.referred_by == current_user.referral_code
    ).count()

    daily_referral_completed = today_referrals > 0

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

@app.route('/admin/delete-user/<int:user_id>')
@login_required
def admin_delete_user(user_id):

    user = User.query.get_or_404(user_id)

    user.is_deleted = True

    user.email = f"deleted_{user.id}@deleted.com"
    user.mobile = f"deleted_{user.id}"
    user.username = f"deleted_{user.id}"

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

            upi_id=upi

        )

        db.session.add(withdrawal)

        db.session.commit()

        flash(
            "Withdrawal request submitted.",
            "success"
        )

        return redirect("/candidate-wallet")

    return render_template(
        "candidate_withdraw.html",
        candidate=candidate,
        settings=settings
    )

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

        if not safe_wallet_debit(candidate, withdrawal.amount):

            flash(
                "Invalid withdrawal request.",
                "danger"
            )

            return redirect("/admin-candidate-withdrawals")

        db.session.add(

            CandidateWalletHistory(

        candidate_id=candidate.id,

        amount=-withdrawal.amount,

                action="Withdrawal Approved"

            )

        )

        withdrawal.status = "Approved"

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

    withdrawal.status = "Rejected"

    db.session.commit()

    flash(
        "Withdrawal Rejected.",
        "warning"
    )

    return redirect('/admin-candidate-withdrawals')

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        # CHECK USERNAME

        username = request.form['username'].strip().upper()
        mobile = request.form['mobile'].strip()

        # VALIDATE INDIAN MOBILE NUMBER

        if not re.fullmatch(r"[6-9]\d{9}", mobile):

            flash(
                "Please enter a valid 10-digit Indian mobile number.",
                "danger"
            )

            return redirect('/register')

        existing_hr = User.query.filter_by(
            username=username
        ).first()

        existing_candidate = CandidateUser.query.filter_by(
            username=username
        ).first()

        if existing_hr or existing_candidate:

            flash("Username already exists")
            return redirect('/register')

        existing_hr_mobile = User.query.filter_by(
            mobile=mobile
        ).first()

        existing_candidate_mobile = CandidateUser.query.filter_by(
            mobile=mobile
        ).first()

        if existing_hr_mobile or existing_candidate_mobile:

            flash("Mobile number already exists")
            return redirect('/register')

        # PROFILE PHOTO

        photo = request.files.get('photo')

        if photo and photo.filename:

            filename = secure_filename(
                photo.filename
            )

            photo.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )
            )

            profile_photo = filename

        else:

            profile_photo = "default.png"

        # MSME CERTIFICATE

        msme_name = ""

        msme_file = request.files.get(
            'msme_certificate'
        )

        if msme_file and msme_file.filename:

            msme_name = secure_filename(
                msme_file.filename
            )

            msme_file.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    msme_name
                )
            )

        # GUMASTA CERTIFICATE

        gumasta_name = ""

        gumasta_file = request.files.get(
            'gumasta_certificate'
        )

        if gumasta_file and gumasta_file.filename:

            gumasta_name = secure_filename(
                gumasta_file.filename
            )

            gumasta_file.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    gumasta_name
                )
            )

        # REFERRAL

        entered_referral = request.form.get(
            'referral_code'
        )

        referrer = None

        if entered_referral:

            referrer = User.query.filter_by(
                referral_code=entered_referral
            ).first()

        # CREATE USER

        user = User(

            first_name=request.form['first_name'],

            last_name=request.form['last_name'],

            mobile=mobile,

            email=request.form['email'],

            company=request.form['company'],
 
            company_city=request.form.get("company_city"),

            full_company_address=request.form.get("full_company_address"),

            company_website=request.form.get("company_website"),

            hr_type=request.form['hr_type'],

            username=username,

            password=generate_password_hash(
                request.form['password']
            ),

            profile_photo=profile_photo,

            msme_certificate=msme_name,

            gumasta_certificate=gumasta_name,

            is_approved=True,

            referral_code=generate_referral_code()

        )

        if referrer:

            user.referred_by = (
                referrer.referral_code
            )

            referrer.total_referrals += 1

        if username == "HARSHIT":

            user.is_admin = True
            user.is_approved = True

        db.session.add(user)
        db.session.commit()

        return render_template(
            'register_success.html'
        )

    return render_template(
        'register.html'
    )

@app.route('/candidate-register', methods=['GET', 'POST'])
def candidate_register():

    if request.method == 'POST':

        full_name = request.form['full_name']
        mobile = request.form['mobile'].strip()
        email = request.form['email']
        username = request.form['username'].strip().upper()
        password = request.form['password']

        # VALIDATE INDIAN MOBILE NUMBER

        if not re.fullmatch(r"[6-9]\d{9}", mobile):

            flash(
                "Please enter a valid 10-digit Indian mobile number.",
                "danger"
            )

            return redirect('/candidate-register')

        # CHECK USERNAME

        existing_hr = User.query.filter_by(
            username=username
        ).first()

        existing_candidate = CandidateUser.query.filter_by(
            username=username
        ).first()

        if existing_hr or existing_candidate:

            flash(
                'Username already exists. Please choose another username.',
                'danger'
            )

            return redirect('/candidate-register')

        # CHECK MOBILE

        existing_hr_mobile = User.query.filter_by(
            mobile=mobile
        ).first()

        existing_candidate_mobile = CandidateUser.query.filter_by(
            mobile=mobile
        ).first()

        if existing_hr_mobile or existing_candidate_mobile:

            flash(
                'Mobile number already exists.',
                'danger'
            )

            return redirect('/candidate-register')

        # RESUME UPLOAD (OPTIONAL)

        resume_name = ""

        resume_file = request.files.get(
            'resume_file'
        )

        if resume_file and resume_file.filename:

            resume_name = secure_filename(
                resume_file.filename
            )

            resume_file.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    resume_name
                )
            )

        # PROFILE PHOTO (OPTIONAL)

        profile_photo_name = ""

        profile_photo = request.files.get(
            "profile_photo"
        )

        if profile_photo and profile_photo.filename:

            profile_photo_name = secure_filename(
                profile_photo.filename
            )

            profile_photo.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    profile_photo_name
                )
            )

        # OPTIONAL REFERRAL CODE

        referral_code = request.form.get(
            "referral_code",
            ""
        ).strip().upper()

        referred_hr = None

        if referral_code:

            referred_hr = User.query.filter_by(
                referral_code=referral_code
            ).first()

        candidate_referral_code = request.form.get(
            "candidate_referral_code",
            ""
        ).strip().upper()

        referred_candidate = None

        if candidate_referral_code:

            referred_candidate = CandidateUser.query.filter_by(
        candidate_referral_code=candidate_referral_code
            ).first()

        # OTHER DETAILS

        dob = request.form.get("dob")
        city = request.form.get("city")
        qualification = request.form.get("qualification")

        # CREATE CANDIDATE

        candidate = CandidateUser(

            full_name=full_name,

            mobile=mobile,

            email=email,

            username=username,

            password=password,

            dob=dob,

            city=city,

            qualification=qualification,

            profile_photo=profile_photo_name,

            resume_file=resume_name,

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

            candidate_referral_code=generate_candidate_referral_code(),

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

        flash(
            'Registration Successful. Please Login.',
            'success'
        )

        return redirect('/candidate-login')

    return render_template(
        'candidate_register.html'
    )

@app.route('/candidate-login', methods=['GET','POST'])
def candidate_login():

    if request.method == 'POST':

        username = request.form['username'].strip()
        password = request.form['password']

        user = CandidateUser.query.filter_by(
            username=username
        ).first()

        # Candidate blocked by admin
        if user and user.is_deleted:

            flash(
                'This account has been disabled by Admin. Please create a new account.',
                'danger'
            )

            return redirect('/candidate-register')

        # Normal login
        if user and user.password == password:

            session['candidate_id'] = user.id

            flash(
                'Login Successful',
                'success'
            )

            return redirect('/candidate-dashboard')

        flash(
            'Invalid Username or Password',
            'danger'
        )

    return render_template('candidate_login.html')

@app.route('/candidate-dashboard')
def candidate_dashboard():

    if 'candidate_id' not in session:
        return redirect('/candidate-login')

    candidate = CandidateUser.query.get(
        session['candidate_id']
    )

    return render_template(
        'candidate_dashboard.html',
        candidate=candidate
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

        notification = Notification(
            user_id=candidate.id,
            user_type="candidate",
            message="Support ticket submitted successfully",
            link="/candidate-support",
            type="support",
            is_read=False
        )

        db.session.add(notification)

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

@app.route('/candidate-profile')
def candidate_profile():

    if 'candidate_id' not in session:
        return redirect('/candidate-login')

    candidate = CandidateUser.query.get(
        session['candidate_id']
    )

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

        db.session.commit()

        flash(
            "Profile Updated",
            "success"
        )

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

        candidate.password = request.form["password"]

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
        and new_status == "Interview Done"
    ):

        candidate = CandidateUser.query.get(
            application.candidate_id
        )

        if (
            candidate
            and candidate.referred_by_hr_id
            and not candidate.hr_referral_reward_given
        ):

            # Check profile completion
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

            if completion >= 100:

                referring_hr = User.query.get(
                    candidate.referred_by_hr_id
                )

                if referring_hr:

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

                        Earnings(
                            user_id=referring_hr.id,
                            amount=settings.hr_to_candidate_reward,
                            reason=f"Candidate Referral Reward - {candidate.full_name}"
                        )

                    )

                    send_notification(
                        user_id=referring_hr.id,
                        user_type="hr",
                        message=f"You earned ₹{settings.hr_to_candidate_reward} because {candidate.full_name} completed Interview.",
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

    db.session.commit()

    flash(
        "Candidate status updated successfully.",
        "success"
    )

    return redirect(request.referrer)

@app.route('/candidate/<int:id>')
@login_required
def view_candidates(id):

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
        'candidate_view.html',
        candidate=candidate,
        followers_count=followers_count,
        is_following=is_following,
    contact_unlocked=contact_unlocked,
        has_applied=has_applied
    )

@app.route('/candidate-wallet')
def candidate_wallet():

    if 'candidate_id' not in session:
        return redirect('/candidate-login')

    candidate = CandidateUser.query.get_or_404(
        session['candidate_id']
    )

    return render_template(
        'candidate_wallet.html',
        candidate=candidate
    )

@app.route('/follow-hr/<int:id>')
def follow_hr(id):

    if 'candidate_id' not in session:
        return redirect('/candidate-login')

    existing = Follow.query.filter_by(
        follower_candidate_id=session['candidate_id'],
        followed_hr_id=id
    ).first()

    candidate = CandidateUser.query.get(
        session['candidate_id']
    )

    if existing:

        db.session.delete(existing)

        notification = Notification(
            user_id=id,
            user_type="hr",
            message=f"{candidate.full_name} unfollowed you",
            link=f"/candidate/{candidate.id}",
            image=candidate.profile_photo,
            type="unfollow"
        )

        db.session.add(notification)

    else:

        db.session.add(
            Follow(
                follower_candidate_id=session['candidate_id'],
                followed_hr_id=id
            )
        )

        notification = Notification(
            user_id=id,
            user_type="hr",
            message=f"{candidate.full_name} started following you",
            link=f"/candidate/{candidate.id}",
            image=candidate.profile_photo,
            type="follow"

        )

        db.session.add(notification)

    db.session.commit()

    return redirect(f'/company/{id}')

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

        notification = Notification(
            user_id=id,
            user_type="hr",
            message=f"{current_user.first_name} {current_user.last_name} unfollowed you",
            link=f"/company/{current_user.id}",
            image=current_user.profile_photo,
            type="unfollow"
        )

        db.session.add(notification)

    else:

        db.session.add(
            Follow(
                follower_hr_id=current_user.id,
                followed_hr_id=id
            )
        )

        notification = Notification(
            user_id=id,
            user_type="hr",
            message=f"{current_user.first_name} {current_user.last_name} started following you",
            link=f"/company/{current_user.id}",
            image=current_user.profile_photo,
            type="follow"
        )

        db.session.add(notification)

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

    if current_user.credits < settings.discover_unlock_credits:

        flash(f"Need {settings.discover_unlock_credits} credits")

        return redirect(request.referrer)

    candidate = CandidateUser.query.get_or_404(id)

    # Deduct Credits
    current_user.credits -= settings.discover_unlock_credits

    db.session.add(
        CandidateContactUnlock(
            hr_id=current_user.id,
            candidate_user_id=id
        )
    )

    db.session.add(
        CreditHistory(
            user_id=current_user.id,
            amount=-settings.discover_unlock_credits,
            action="Unlocked Candidate Contact"
        )
    )

    # =====================================
    # DISCOVER REVENUE SHARING
    # =====================================

    if settings.enable_revenue_sharing:

        purchase = CreditPurchase.query.filter(
            CreditPurchase.user_id == current_user.id,
            CreditPurchase.credits_remaining > 0
        ).order_by(
            CreditPurchase.created_at.asc()
        ).first()

        if purchase:

            purchase.credits_remaining -= settings.discover_unlock_credits

            revenue = purchase.price_per_credit * settings.discover_unlock_credits

            # Candidate belongs to HR
            if (
                candidate.revenue_owner_type == "hr"
                and candidate.revenue_owner_id
            ):

                owner = User.query.get(candidate.revenue_owner_id)

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

@app.route('/post-job', methods=['GET','POST'])
@login_required
def post_job():

    if request.method == 'POST':

        files = request.files.getlist('images')

        saved_images = []

        for file in files:

            if file and file.filename:

                filename = secure_filename(
                    file.filename
                )

                file.save(
                    os.path.join(
                        app.config['UPLOAD_FOLDER'],
                        filename
                    )
                )

                saved_images.append(filename)

        job = JobPost(

            hr_id=current_user.id,

            company_name=current_user.company,

            job_title=request.form['job_title'],

            location=request.form['location'],

            salary=request.form['salary'],

            incentive=request.form.get("incentive"),

            job_timing=request.form.get("job_timing"),

            working_days = request.form.get("working_days"),

            job_type = request.form.get("job_type"),

            eligibility = request.form.get("eligibility"),

            experience_required = request.form.get("experience_required"),
         
            employment_type = request.form.get("employment_type"),

            education = request.form.get("education"),

            gender = request.form.get("gender"),

            interview_from=request.form.get("interview_from"),

            interview_to=request.form.get("interview_to"),

            interview_time=request.form.get("interview_time"),

            interview_instructions=request.form.get("interview_instructions"),

            description=request.form['description'],

            images=",".join(saved_images)

        )

        db.session.add(job)
        db.session.commit()

        # NOTIFY FOLLOWERS

        followers = Follow.query.filter_by(
            followed_hr_id=current_user.id
        ).all()

        first_image = (
            saved_images[0]
            if len(saved_images) > 0
            else ""
        )

        for f in followers:

            notification = Notification(

                user_id=f.follower_candidate_id,

                user_type="candidate",

                type="job_post",

                message=f"{current_user.company} posted a new job: {job.job_title}",

                link=f"/job/{job.id}",

                image=first_image

            )

            db.session.add(notification)

        db.session.commit()

        return redirect('/my-jobs')

    return render_template('post_job.html')

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

@app.route('/candidate-feed')
def candidate_feed():

    selected_location = request.args.get('location', '')

    jobs_query = JobPost.query

    if selected_location:
        jobs_query = jobs_query.filter(
            JobPost.location == selected_location
        )

    jobs = jobs_query.order_by(
        JobPost.created_at.desc()
    ).all()

    locations = db.session.query(
        JobPost.location
    ).distinct().order_by(
        JobPost.location
    ).all()

    locations = [
        loc[0]
        for loc in locations
        if loc[0]
    ]

    selected_id = request.args.get(
        'selected',
        type=int
    )

    applied_jobs = []

    if 'candidate_id' in session:

        applications = JobApplication.query.filter_by(
            candidate_id=session['candidate_id']
        ).all()

        applied_jobs = [
            app.job_id
            for app in applications
        ]

    return render_template(
        'candidate_feed.html',
        jobs=jobs,
        applied_jobs=applied_jobs,
        selected_id=selected_id,
        locations=locations,
        selected_location=selected_location
    )

@app.route('/discover-hr')
def discover_hr():

    city = request.args.get('city', '')

    query = User.query.filter_by(
        is_approved=True
    )

    if city:
        query = query.filter(
            User.company_city.contains(city)
        )

    hrs = query.order_by(
        User.id.desc()
    ).all()

    return render_template(
        'discover_hr.html',
        hrs=hrs,
        city=city,
        Follow=Follow
    )

@app.route('/discover-candidates')
@login_required
def discover_candidates():

    city = request.args.get('city', '')

    # CANDIDATES

    candidate_query = CandidateUser.query

    if city:
        candidate_query = candidate_query.filter(
            CandidateUser.city.contains(city)
        )

    candidates = candidate_query.order_by(
        CandidateUser.id.desc()
    ).all()

    # HRS

    hr_query = User.query.filter(
    User.is_admin == False,
    User.id != current_user.id
    )

    if city:
        hr_query = hr_query.filter(
            User.company_city.contains(city)
    )

    hrs = hr_query.order_by(
        User.id.desc()
    ).all()

    return render_template(
        'discover_candidates.html',
        candidates=candidates,
        hrs=hrs,
        city=city,
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
        candidate_id=session['candidate_id']
        ,
            status=None
    )

    db.session.add(application)

    job = JobPost.query.get(job_id)

    candidate = CandidateUser.query.get(
        session['candidate_id']
    )

    notification = Notification(
        user_id=job.hr_id,
        user_type="hr",
        message=f"{candidate.full_name} applied for {job.job_title}",
        link=f"/candidate/{candidate.id}",
        image=candidate.profile_photo,
        type="job_apply"
    )

    db.session.add(notification)

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

    notification = Notification(
        user_id=job.hr_id,
        user_type='hr',
        message=f'{current_user.first_name} applied for your job',
        link=f'/job-applicants/{id}',
        image=current_user.profile_photo,
        type='job_application'
    )

    db.session.add(notification)

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

    selected_location = request.args.get("location", "")

    query = JobPost.query.filter(
        JobPost.hr_id != current_user.id
    )

    if selected_location:
        query = query.filter_by(
            location=selected_location
        )

    jobs = query.order_by(
        JobPost.created_at.desc()
    ).all()

    # Applied jobs
    applications = JobApplication.query.filter_by(
        applicant_hr_id=current_user.id
    ).all()

    applied_jobs = [
        app.job_id
        for app in applications
    ]

    # Cities already available in database
    locations = db.session.query(
        JobPost.location
    ).distinct().order_by(
        JobPost.location
    ).all()

    locations = [
        city[0]
        for city in locations
        if city[0]
    ]

    return render_template(
        "feed.html",
        jobs=jobs,
        applied_jobs=applied_jobs,
        locations=locations,
        selected_location=selected_location
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

    db.session.delete(candidate)

    db.session.commit()

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

@app.template_filter('timeago')
def timeago(dt):

    now = datetime.utcnow()

    diff = now - dt

    seconds = diff.total_seconds()

    if seconds < 60:
        return "Just now"

    if seconds < 3600:
        return f"{int(seconds/60)}m ago"

    if seconds < 86400:
        return f"{int(seconds/3600)}h ago"

    if seconds < 604800:
        return f"{int(seconds/86400)}d ago"

    return dt.strftime("%d %b %Y")

@app.route('/feed/<int:id>')
@login_required
def feed_post(id):

    jobs = JobPost.query.filter_by(
        hr_id=current_user.id
    ).order_by(
        JobPost.created_at.desc()
    ).all()

    return render_template(
        'feed_post.html',
        jobs=jobs,
        selected_id=id
    )

@app.route('/candidate-logout')
def candidate_logout():

    session.pop('candidate_id', None)

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

        login_id = request.form['username'].strip()
        password = request.form['password'].strip()

        user = User.query.filter_by(
            mobile=login_id
        ).first()

        if not user:

            user = User.query.filter_by(
                username=login_id
            ).first()

        print("USERNAME =", request.form['username'])

        if user:
            logging.warning(f"FOUND USER = {user.username}")
            print("APPROVED =", user.is_approved)
            print("FAILED LOGINS =", user.failed_logins)
        else:
            logging.warning("USER NOT FOUND")

        if not user:
            flash("Invalid Username or Password", "danger")
            return redirect(url_for("login"))

        if user.is_deleted:
            flash("Your account has been deleted.", "danger")
            return redirect(url_for("login"))

        if user.failed_logins >= 5:
            flash("Your account has been blocked. Contact Admin.", "danger")
            return redirect(url_for("login"))

        if not user.is_approved and user.username.upper() != "HARSHIT":
            flash("Your account is pending approval.", "warning")
            return redirect(url_for("login"))

        if check_password_hash(
            user.password,
            password
        ):

            user.failed_logins = 0

            user.last_login = datetime.utcnow()

            # SINGLE DEVICE LOGIN

            token = str(uuid.uuid4())

            user.session_token = token

            db.session.commit()

            login_user(user)

            session['session_token'] = token

            return redirect(url_for('home'))

        else:

            user.failed_logins += 1

            db.session.commit()

            flash("Invalid Username or Password", "danger")
            return redirect(url_for("login"))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():

    if request.method == 'POST':

        # UPLOAD LIMIT

        if Candidate.query.filter_by(
            uploaded_by=current_user.id
        ).count() >= 100:

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

    return render_template('upload.html')

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

    is_experienced = (
        candidate.experience.strip().lower() == "experienced"
    )

    paid_cost = 2 if is_experienced else 1

    free_cost = 4 if is_experienced else 2

    # -----------------------------------------
    # Total Credit Check
    # -----------------------------------------

    total_available = (
        current_user.paid_credits +
        current_user.credits
    )

    if total_available <= 0:

        flash(
            "You don't have enough credits. Please purchase a package.",
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

    is_experienced = (
        candidate.experience.strip().lower() == "experienced"
    )

    paid_cost = 2 if is_experienced else 1

    free_cost = 4 if is_experienced else 2

    # -----------------------------------------
    # Total Credit Check
    # -----------------------------------------

    total_available = (
        current_user.paid_credits +
        current_user.credits
    )

    if total_available <= 0:

        flash(
            "You don't have enough credits. Please purchase a package.",
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
    if not admin_only(): return "Access Denied", 403
    return render_template('admin.html', total_users=User.query.count(), 
                           total_candidates=Candidate.query.count(), 
                           total_unlocks=Unlock.query.count(),
                           recent_candidates=Candidate.query.order_by(Candidate.created_at.desc()).limit(10).all())

@app.route('/admin/users')
@login_required
def admin_users():
    if not admin_only(): return "Access Denied"
    return render_template('admin_users.html', users=User.query.all())

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

        notification = Notification(
            user_id=ticket.user_id,
            user_type=ticket.user_type,
            message=f"Support replied to your ticket: {ticket.subject}",
            link=f"/support",
            type="support",
            is_read=False
        )

        db.session.add(notification)

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

        User=User

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

    query = CandidateUser.query

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
    ).all()

    total_candidates = CandidateUser.query.count()

    total_applications = JobApplication.query.count()

    return render_template(
        'admin_candidate_users.html',
        candidates=candidates,
        total_candidates=total_candidates,
        total_applications=total_applications
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
        "Mobile",
        "Email",
        "City",
        "Designation",
        "Experience",
        "Current Company",
        "Current CTC",
        "Expected CTC",
        "Skills",
        "Joined Date"
    ])

    candidates = CandidateUser.query.order_by(
        CandidateUser.id.desc()
    ).all()

    for c in candidates:

        ws.append([
            c.id,
            c.full_name,
            c.mobile,
            c.email,
            c.city,
            c.designation,
            c.experience,
            c.current_company,
            c.current_ctc,
            c.expected_ctc,
            c.skills,
            c.created_at.strftime('%d-%m-%Y')
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

    candidate.is_deleted = True

    db.session.commit()

    flash(
        "Candidate marked as deleted successfully",
        "success"
    )

    return redirect('/admin/candidate-users')

@app.route('/job/<int:job_id>')
def job_share(job_id):
    return redirect(f'/job-details/{job_id}')

@app.route('/share-job/<int:job_id>')
def share_job(job_id):

    job = JobPost.query.get_or_404(job_id)

    share_link = request.host_url.rstrip("/") + f"/job-view/{job.id}"

    return redirect(
        f"https://wa.me/?text=📢 {job.job_title}%0A{share_link}"
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

    user = User.query.filter_by(username="HARSHIT").first()

    if user:
        user.is_admin = True
        user.is_approved = True

        db.session.commit()

        return "HARSHIT is now admin"

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

    followers_count = Follow.query.filter_by(
        followed_hr_id=current_user.id
    ).count()

    following_count = 0

    return render_template(
        'profile.html',
        jobs=jobs,
        posts_count=len(jobs),
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
        'credits.html',
        history=history
    )

@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():

    if request.method == 'POST':

        # Editable Fields
        current_user.email = request.form.get('email')
        current_user.company = request.form.get('company')
        current_user.hr_type = request.form.get('hr_type')
        current_user.company_city = request.form.get('company_city')
        current_user.full_company_address = request.form.get('full_company_address')
        current_user.company_website = request.form.get('company_website')
        current_user.about_company = request.form.get('about_company')

        # Optional Bank Details
        current_user.account_holder_name = request.form.get('account_holder_name')
        current_user.bank_name = request.form.get('bank_name')
        current_user.account_number = request.form.get('account_number')
        current_user.ifsc_code = request.form.get('ifsc_code')
        current_user.upi_id = request.form.get('upi_id')

        # Profile Photo
        photo = request.files.get('photo')

        if photo and photo.filename:

            filename = secure_filename(photo.filename)

            photo.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )
            )

            current_user.profile_photo = filename

        db.session.commit()

        flash(
            'Profile Updated Successfully',
            'success'
        )

        return redirect('/profile')

    return render_template(
        'edit_profile.html'
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

        notification = Notification(
            user_id=current_user.id,
            user_type="hr",
            message="Support ticket submitted successfully",
            link=f"/ticket/{ticket.id}",
            type="support",
            is_read=False
        )

        db.session.add(notification)

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

    return render_template('buy_credits.html')


@app.route('/buy-credits/<int:amount>')
@login_required
def buy_credits(amount):

    if amount == 199:
        credits = 10

    elif amount == 399:
        credits = 25

    elif amount == 799:
        credits = 60

    elif amount == 1599:
        credits = 150

    elif amount == 3199:
        credits = 300

    elif amount == 5199:
        credits = 500

    elif amount == 9999:
        credits = 1000

    else:
        return "Invalid Package"

    order = client.order.create({
        "amount": amount * 100,
        "currency": "INR",
        "payment_capture": 1
    })

    # Save purchase info
    session['buy_credits'] = credits
    session['buy_amount'] = amount

    return render_template(
        'payment.html',
        order=order,
        amount=amount,
        razorpay_key=RAZORPAY_KEY
    )

@app.route('/payment-success')
@login_required
def payment_success():

    settings = get_business_settings()

    credits = session.get('buy_credits', 0)

    amount = session.get('buy_amount', 0)

    # ADD PAID CREDITS
    current_user.paid_credits += credits

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

    # REFERRAL REWARD
    if (
        amount >= settings.hr_minimum_purchase and
        current_user.referred_by and
        not current_user.referral_purchase_reward_given
    ):

        referrer = User.query.filter_by(
            referral_code=current_user.referred_by
        ).first()

        if (
            referrer and
            referrer.successful_referrals < 10
        ):

            referrer.wallet_balance += settings.hr_to_hr_reward
            referrer.referral_earnings += settings.hr_to_hr_reward
            referrer.successful_referrals += 1

            current_user.referral_purchase_reward_given = True

    db.session.commit()

    # PREVENT DUPLICATE REWARDS
    session.pop('buy_credits', None)
    session.pop('buy_amount', None)

    return redirect('/credits')

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

    # GET USER HISTORY
    withdrawals = Withdrawal.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Withdrawal.created_at.desc()
    ).all()

    if request.method == 'POST':

        amount = float(
            request.form['amount']
        )

        # MINIMUM LIMIT
        if amount < 500:

            flash(
                'Minimum withdrawal is ₹500',
                'danger'
            )

            return redirect('/withdraw')

        # BALANCE CHECK
        if amount > current_user.wallet_balance:

            flash(
                'Insufficient wallet balance',
                'danger'
            )

            return redirect('/withdraw')

        # CREATE REQUEST
        withdrawal = Withdrawal(

            user_id=current_user.id,

            amount=amount,

            status='Pending'
        )

        db.session.add(withdrawal)

        # DEDUCT WALLET
        current_user.wallet_balance -= amount

        db.session.commit()

        flash(
            'Withdrawal request submitted successfully.',
            'success'
        )

        return redirect('/withdraw')

    return render_template(
        'withdraw.html',
        withdrawals=withdrawals
    )

@app.route('/admin/withdrawals')
@login_required
def admin_withdrawals():

    if not current_user.is_admin:
        return "Access Denied"

    withdrawals = Withdrawal.query.order_by(
        Withdrawal.id.desc()
    ).all()

    pending_count = Withdrawal.query.filter_by(
        status="Pending"
    ).count()

    approved_count = Withdrawal.query.filter_by(
        status="Approved"
    ).count()

    return render_template(
        'admin_withdrawals.html',
        withdrawals=withdrawals,
        pending_count=pending_count,
        approved_count=approved_count
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

@app.route('/change-password', methods=['GET', 'POST'])
def change_password():

    if 'reset_user_id' not in session:

        return redirect('/forgot-password')

    user = User.query.get(
        session['reset_user_id']
    )

    if request.method == 'POST':

        password = request.form['password']

        user.password = generate_password_hash(
            password
        )

        db.session.commit()

        session.pop('reset_user_id')

        flash(
            'Password Changed Successfully',
            'success'
        )

        return render_template('register_success.html')

    return render_template(
        'change_password.html'
    )

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# =========================
# SINGLE DEVICE LOGIN CHECK
# =========================

@app.before_request
def verify_single_device():

    if current_user.is_authenticated:

        db_token = current_user.session_token

        current_session_token = session.get('session_token')

        if db_token != current_session_token:

            logout_user()

            session.clear()

            flash(
                'Your account was logged in from another device.',
                'warning'
            )

            return redirect(url_for('login'))

if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

