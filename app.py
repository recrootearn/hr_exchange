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

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)

resend.api_key = "re_QT3qQPqz_Ngn6WAnA4A2ykKbH9CZEs6Fz"

RAZORPAY_KEY = "rzp_live_SukwF35NxDKD1h"
RAZORPAY_SECRET = "ctp74whaDCaF5omzFqoEg6Ya"

client = razorpay.Client(
    auth=(RAZORPAY_KEY, RAZORPAY_SECRET)
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

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20), unique=True)
    experience = db.Column(db.String(50))
    designation = db.Column(db.String(200))
    city = db.Column(db.String(100))
    category = db.Column(db.String(100))
    uploaded_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_fake = db.Column(db.Boolean, default=False)
    report_count = db.Column(db.Integer, default=0)
    wrong_experience_reports = db.Column(db.Integer, default=0)

class Unlock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    candidate_id = db.Column(db.Integer)

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
    subject = db.Column(db.String(300))
    message = db.Column(db.Text)
    status = db.Column(db.String(50), default='Open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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

# =========================
# USER ROUTES
# =========================

@app.route('/')
@login_required
def home():

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

    # HIDE OWN CANDIDATES

    query = Candidate.query.filter(
        Candidate.is_fake == False,
        Candidate.uploaded_by != current_user.id
    )

    # FILTERS

    if industry:

        query = query.filter_by(
            category=industry
        )

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

    return render_template(
        'dashboard.html',
        candidates=candidates,
        unlocked_ids=unlocked_ids,
        my_uploads_count=Candidate.query.filter_by(
            uploaded_by=current_user.id
        ).count(),
        my_unlocks_count=len(unlocked_ids),
        CandidateReview=CandidateReview,
        User=User
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

    sort = request.args.get('sort')

    lead_filter = request.args.get('lead_filter')

    page = request.args.get('page', 1, type=int)

    unlocked_ids = [

        u.candidate_id

        for u in Unlock.query.filter_by(
            user_id=current_user.id
        ).all()
    ]

    # REMOVE OWN UPLOADS

    query = Candidate.query.filter(

        ~Candidate.id.in_(unlocked_ids),

        Candidate.uploaded_by != current_user.id
    )

    # SEARCH FILTERS

    if designation:

        query = query.filter(
            Candidate.designation.contains(designation)
        )

    if city:

        query = query.filter(
            Candidate.city.contains(city)
        )

    if industry:

        query = query.filter_by(
            category=industry
        )

    # EXPERIENCE FILTER

    if experience:

        query = query.filter_by(
            experience=experience
        )

    # READ / UNREAD

    seen_ids = [

        s.candidate_id

        for s in SeenLead.query.filter_by(
            user_id=current_user.id
        ).all()
    ]

    if lead_filter == 'read':

        query = query.filter(
            Candidate.id.in_(seen_ids)
        )

    elif lead_filter == 'unread':

        query = query.filter(
            ~Candidate.id.in_(seen_ids)
        )

    # SORTING

    if sort == 'old':

        query = query.order_by(
            Candidate.created_at.asc()
        )

    else:

        query = query.order_by(
            Candidate.created_at.desc()
        )

    # PAGINATION

    candidates = query.paginate(
    page=page,
    per_page=10,
    error_out=False
)

    # AUTO MARK AS READ

    for c in candidates.items:

        existing_seen = SeenLead.query.filter_by(
            user_id=current_user.id,
            candidate_id=c.id
        ).first()

        if not existing_seen:

            db.session.add(

                SeenLead(
                    user_id=current_user.id,
                    candidate_id=c.id
                )
            )

    db.session.commit()

    return render_template(

        'locked.html',

        candidates=candidates,

        unlocked_ids=unlocked_ids,

        CandidateReview=CandidateReview,

        User=User
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
        u.candidate_id for u in unlocked
    ]

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
            Candidate.designation.contains(designation)
        )

    if city:

        query = query.filter(
            Candidate.city.contains(city)
        )

    if industry:

        query = query.filter_by(
            category=industry
        )

    if experience:

        query = query.filter_by(
            experience=experience
        )

    # =========================
    # SORTING
    # =========================

    if sort == 'old':

        query = query.order_by(
            Candidate.id.asc()
        )

    else:

        query = query.order_by(
            Candidate.id.desc()
        )

    # =========================
    # PAGINATION
    # =========================

    candidates = query.paginate(
        page=page,
        per_page=10,
        error_out=False
    )

    # =========================
    # RENDER
    # =========================

    return render_template(
        'leads.html',
        candidates=candidates,
        unlocked_ids=unlocked_ids,
        CandidateReview=CandidateReview,
        User=User,
        tab=tab
    )

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        # CHECK USERNAME

        if User.query.filter_by(
            username=request.form['username']
        ).first():

            return "Username already exists"

        # PHOTO UPLOAD (OPTIONAL)

        photo = request.files.get('photo')

        if photo and photo.filename != "":

            filename = secure_filename(photo.filename)

            photo.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )
            )

            profile_photo = filename

        else:

            profile_photo = "default.png"

        # CREATE USER

        user = User(

            first_name=request.form['first_name'],

            last_name=request.form['last_name'],

            mobile=request.form['mobile'],

            email=request.form['email'],

            company=request.form['company'],

            hr_type=request.form['hr_type'],

            username=request.form['username'],

            password=generate_password_hash(
                request.form['password']
            ),

            profile_photo=profile_photo,

            is_approved=True
        )

        # MAKE HARSHIT ADMIN

        if request.form['username'].upper() == "HARSHIT":

            user.is_admin = True

            user.is_approved = True

        db.session.add(user)

        db.session.commit()

        return render_template(
            'register_success.html'
        )

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        user = User.query.filter_by(
            username=request.form['username']
        ).first()

        if not user:
            return "Invalid Login"

        if user.failed_logins >= 5:
            return "Blocked"

        if not user.is_approved and user.username.upper() != "HARSHIT":
            return "Pending Approval"

        if check_password_hash(
            user.password,
            request.form['password']
        ):

            user.failed_logins = 0

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

            return "Invalid Login"

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
        ).count() >= 500:

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

            uploaded_by=current_user.id
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

                uploaded_by=current_user.id
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

    # prevent unlocking own candidate
    if candidate.uploaded_by == current_user.id:

        flash(
            "You cannot unlock your own candidate.",
            "danger"
        )

        return redirect(request.referrer)

    # CHECK TOTAL CREDITS
    total_credits = current_user.credits + current_user.paid_credits

    if total_credits <= 0:

        flash(
            "You don't have enough credits.",
            "danger"
        )

        return redirect(request.referrer)

    # already unlocked
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

    # CREATE UNLOCK ENTRY
    unlock = Unlock(
        user_id=current_user.id,
        candidate_id=id
    )

    db.session.add(unlock)

    # GET UPLOADER
    uploader = User.query.get(candidate.uploaded_by)

    # =========================================
    # USE PAID CREDIT FIRST
    # =========================================

    if current_user.paid_credits > 0:

        current_user.paid_credits -= 1

        # uploader earns only on paid credits
        if uploader:

            earning = 6

            uploader.wallet_balance += earning

            earn = Earnings(

                user_id=uploader.id,

                amount=earning,

                reason=f"Candidate unlocked: {candidate.name}"
            )

            db.session.add(earn)

    else:

        # USE FREE CREDIT
        current_user.credits -= 1

    # CREDIT HISTORY
    history = CreditHistory(

        user_id=current_user.id,

        amount=-1,

        action=f"Unlocked: {candidate.name}"
    )

    db.session.add(history)

    # SAVE DATABASE
    db.session.commit()

    # SUCCESS POPUP
    flash(
        "Lead transferred to Unlocked Candidates successfully.",
        "success"
    )

    # STAY ON SAME PAGE
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

    tickets = SupportTicket.query.all()

    return render_template(
        'admin_support.html',
        tickets=tickets,
        User=User,
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

    db.session.commit()

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

    return render_template(
        'profile.html'
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

        current_user.first_name = request.form['first_name']

        current_user.last_name = request.form['last_name']

        current_user.mobile = request.form['mobile']

        current_user.email = request.form['email']

        current_user.company = request.form['company']

        current_user.hr_type = request.form['hr_type']

        # PHOTO UPDATE

        photo = request.files.get('photo')

        if photo and photo.filename != "":

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
            subject=request.form['subject'],
            message=request.form['message']
        )

        db.session.add(ticket)

        db.session.commit()

    page = request.args.get('page', 1, type=int)

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

    if amount == 149:
        credits = 10

    elif amount == 299:
        credits = 25

    elif amount == 599:
        credits = 50

    elif amount == 999:
        credits = 100

    elif amount == 1999:
        credits = 250

    elif amount == 3499:
        credits = 500

    elif amount == 5999:
        credits = 1000

    else:
        return "Invalid Package"

    order = client.order.create({
        "amount": amount * 100,
        "currency": "INR",
        "payment_capture": 1
    })

    session['buy_credits'] = credits

    return render_template(
        'payment.html',
        order=order,
        amount=amount,
        razorpay_key=RAZORPAY_KEY
    )

@app.route('/payment-success')
@login_required
def payment_success():

    credits = session.get('buy_credits', 0)

    current_user.credits += credits

    history = CreditHistory(
        user_id=current_user.id,
        amount=credits,
        action=f"Purchased {credits} Credits"
    )

    db.session.add(history)

    db.session.commit()

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
        Withdrawal.created_at.desc()
    ).all()

    return render_template(
        'admin_withdrawals.html',
        withdrawals=withdrawals,
        User=User
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

