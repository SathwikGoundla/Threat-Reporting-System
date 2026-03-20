"""
Threat Reporting System — Main Application
OTP is sent via Twilio SMS to the user's real phone number.
"""

import os
import secrets
from datetime import datetime, timedelta
from functools import wraps

from dotenv import load_dotenv
load_dotenv()  # Load .env FIRST before anything else

from flask import (Flask, render_template, request, redirect,
                   url_for, flash, session, send_from_directory)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (LoginManager, login_user, login_required,
                         logout_user, current_user)
from werkzeug.utils import secure_filename
import phonenumbers
import pyotp
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from sms import send_otp_sms   # ← Twilio SMS function

# ── Download NLTK data quietly ────────────────────────────────────────────────
for pkg in ('punkt', 'stopwords', 'punkt_tab'):
    try:
        if pkg == 'stopwords':
            nltk.data.find('corpora/stopwords')
        else:
            nltk.data.find(f'tokenizers/{pkg}')
    except (LookupError, OSError):
        nltk.download(pkg, quiet=True)

# ── Flask app setup ───────────────────────────────────────────────────────────
app = Flask(__name__)
app.config['SECRET_KEY']                  = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI']     = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER']               = 'uploads'
app.config['MAX_CONTENT_LENGTH']          = 50 * 1024 * 1024   # 50 MB
app.config['PERMANENT_SESSION_LIFETIME']  = timedelta(days=1)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ── Extensions ────────────────────────────────────────────────────────────────
from models import db, User, OTP, Report, Attachment, Keyword, Solution
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ── Admin / Manager phone numbers (from .env) ─────────────────────────────────
ADMIN_PHONE    = os.environ.get('ADMIN_PHONE', '+919949258081')
MANAGER_PHONES = [p.strip() for p in
                  os.environ.get('MANAGER_PHONES', '+919949258081,+919398018154').split(',')]

# ── Helpers ───────────────────────────────────────────────────────────────────
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in first.', 'error')
                return redirect(url_for('login'))
            if current_user.role not in roles:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator

def generate_otp() -> str:
    """Generate a secure 6-digit numeric OTP."""
    return pyotp.TOTP(pyotp.random_base32()).now()

def extract_keywords(text: str) -> list:
    if not text:
        return []
    threat_keywords = {
        'abuse','harass','assault','rape','molest','touch','hit','beat',
        'fight','violence','attack','push','slap','tease','bully','taunt',
        'threat','blackmail','cyber','online','stress','anxiety','depression',
        'fear','trauma','discrimination','unsafe','security','stalk','shame'
    }
    try:
        tokens = word_tokenize(text.lower())
    except Exception:
        tokens = text.lower().split()
    found = []
    for t in tokens:
        if t in threat_keywords and t not in found:
            found.append(t)
    return found[:10]

# ═════════════════════════════════════════════════════════════════════════════
#  ROUTES
# ═════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return redirect(url_for('dashboard') if current_user.is_authenticated else url_for('login'))


# ── LOGIN ─────────────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        phone_raw = request.form.get('phone', '').strip()
        try:
            # Validate & format phone number
            parsed = phonenumbers.parse(phone_raw, None)
            if not phonenumbers.is_valid_number(parsed):
                flash('❌ Invalid phone number. Use format: +919949258081', 'error')
                return render_template('login.html')

            phone = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

            # Create user if first time
            user = User.query.filter_by(phone=phone).first()
            if not user:
                role = ('admin'   if phone == ADMIN_PHONE else
                        'manager' if phone in MANAGER_PHONES else
                        'user')
                user = User(phone=phone, role=role)
                db.session.add(user)
                db.session.commit()

            # Generate 6-digit OTP
            otp_value = generate_otp()

            # Save OTP to DB
            db.session.add(OTP(
                user_id=user.id,
                otp=otp_value,
                expires_at=datetime.utcnow() + timedelta(minutes=5)
            ))
            db.session.commit()

            # ── SEND OTP VIA TWILIO SMS ────────────────────────────────────
            result = send_otp_sms(phone, otp_value)
            # ──────────────────────────────────────────────────────────────

            if result['success']:
                print(f"[SMS SENT] OTP {otp_value} → {phone} | SID: {result['sid']}")
                session['pending_phone'] = phone
                flash(f'✅ OTP sent to {phone} via SMS. Check your messages!', 'success')
                return redirect(url_for('verify_otp'))
            else:
                # SMS failed — still print to console as fallback so dev can test
                print(f"\n{'='*50}")
                print(f"  ⚠️  SMS FAILED: {result['error']}")
                print(f"  FALLBACK OTP for {phone}: {otp_value}")
                print(f"{'='*50}\n")
                session['pending_phone'] = phone
                flash(
                    f'⚠️ SMS could not be delivered ({result["error"]}). '
                    f'Check the terminal for your OTP.',
                    'warning'
                )
                return redirect(url_for('verify_otp'))

        except phonenumbers.phonenumberutil.NumberParseException:
            flash('❌ Cannot parse phone number. Include country code e.g. +919949258081', 'error')
        except Exception as e:
            flash(f'❌ Error: {str(e)}', 'error')

    return render_template('login.html')


# ── VERIFY OTP ────────────────────────────────────────────────────────────────
@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'pending_phone' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        entered = request.form.get('otp', '').strip()
        phone   = session['pending_phone']

        user = User.query.filter_by(phone=phone).first()
        if not user:
            flash('User not found. Please login again.', 'error')
            return redirect(url_for('login'))

        # Get latest unused, non-expired OTP
        otp_record = (OTP.query
                      .filter_by(user_id=user.id, is_used=False)
                      .filter(OTP.expires_at > datetime.utcnow())
                      .order_by(OTP.created_at.desc())
                      .first())

        if otp_record and otp_record.otp == entered:
            otp_record.is_used = True
            user.last_login    = datetime.utcnow()
            db.session.commit()

            login_user(user, remember=True)
            session.pop('pending_phone', None)
            flash(f'✅ Login successful! Welcome {user.role.title()}.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('❌ Invalid or expired OTP. Please try again or request a new one.', 'error')

    # Mask phone for display: +91XXXXX58081
    phone = session.get('pending_phone', '')
    masked = phone[:3] + 'X'*5 + phone[-5:] if len(phone) > 8 else phone
    return render_template('verify_otp.html', masked_phone=masked)


# ── RESEND OTP ────────────────────────────────────────────────────────────────
@app.route('/resend-otp')
def resend_otp():
    if 'pending_phone' not in session:
        return redirect(url_for('login'))

    phone = session['pending_phone']
    user  = User.query.filter_by(phone=phone).first()

    if user:
        otp_value = generate_otp()
        db.session.add(OTP(
            user_id=user.id,
            otp=otp_value,
            expires_at=datetime.utcnow() + timedelta(minutes=5)
        ))
        db.session.commit()

        result = send_otp_sms(phone, otp_value)
        if result['success']:
            print(f"[SMS RESENT] OTP {otp_value} → {phone}")
            flash('✅ New OTP sent to your phone via SMS!', 'success')
        else:
            print(f"\n[RESEND FALLBACK] OTP for {phone}: {otp_value}\n")
            flash(f'⚠️ SMS failed. Check terminal for OTP. ({result["error"]})', 'warning')

    return redirect(url_for('verify_otp'))


# ── LOGOUT ────────────────────────────────────────────────────────────────────
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ── DASHBOARD ROUTER ──────────────────────────────────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif current_user.role == 'manager':
        return redirect(url_for('manager_dashboard'))
    return redirect(url_for('user_dashboard'))


# ── USER ──────────────────────────────────────────────────────────────────────
@app.route('/user/dashboard')
@login_required
@role_required('user')
def user_dashboard():
    reports = (Report.query
               .filter_by(user_id=current_user.id)
               .order_by(Report.created_at.desc()).all())
    return render_template('user_dashboard.html', reports=reports)


@app.route('/user/survey', methods=['GET', 'POST'])
@login_required
@role_required('user')
def survey_form():
    if request.method == 'POST':
        report = Report(
            user_id=current_user.id,
            category=request.form.get('category'),
            problem_type=request.form.get('problem_type'),
            custom_problem=request.form.get('custom_problem'),
            description=request.form.get('description')
        )
        db.session.add(report)
        db.session.flush()

        for kw in extract_keywords(report.description):
            db.session.add(Keyword(report_id=report.id, keyword=kw))

        if 'files' in request.files:
            for f in request.files.getlist('files'):
                if f and f.filename:
                    fname = secure_filename(f.filename)
                    fpath = os.path.join(app.config['UPLOAD_FOLDER'], f"{report.id}_{fname}")
                    f.save(fpath)
                    db.session.add(Attachment(
                        report_id=report.id, filename=fname,
                        filepath=fpath, file_type=f.content_type
                    ))

        db.session.commit()
        flash('✅ Report submitted successfully!', 'success')
        return redirect(url_for('user_dashboard'))

    return render_template('survey_form.html')


# ── MANAGER ───────────────────────────────────────────────────────────────────
@app.route('/manager/dashboard')
@login_required
@role_required('manager', 'admin')
def manager_dashboard():
    pending  = Report.query.filter_by(status='pending').order_by(Report.created_at.asc()).all()
    verified = (Report.query.filter_by(status='verified_by_manager')
                .order_by(Report.created_at.desc()).limit(10).all())
    return render_template('manager_dashboard.html',
                           pending_reports=pending, verified_reports=verified)


@app.route('/report/<int:report_id>/verify', methods=['POST'])
@login_required
@role_required('manager', 'admin')
def verify_report(report_id):
    report   = Report.query.get_or_404(report_id)
    action   = request.form.get('action')
    comments = request.form.get('comments')
    if action == 'approve':
        report.status, report.manager_id, report.manager_comments = (
            'verified_by_manager', current_user.id, comments)
        flash('✅ Report verified and forwarded to admin.', 'success')
    elif action == 'reject':
        report.status, report.manager_id, report.manager_comments = (
            'rejected', current_user.id, comments)
        flash('Report rejected.', 'info')
    db.session.commit()
    return redirect(url_for('manager_dashboard'))


# ── ADMIN ─────────────────────────────────────────────────────────────────────
@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    verified = Report.query.filter_by(status='verified_by_manager').order_by(Report.created_at.asc()).all()
    resolved = (Report.query.filter_by(status='resolved')
                .order_by(Report.created_at.desc()).limit(20).all())
    return render_template('admin_dashboard.html',
                           verified_reports=verified, resolved_reports=resolved)


@app.route('/report/<int:report_id>/solve', methods=['POST'])
@login_required
@role_required('admin')
def solve_report(report_id):
    report = Report.query.get_or_404(report_id)
    db.session.add(Solution(
        report_id=report.id,
        admin_id=current_user.id,
        solution_text=request.form.get('solution')
    ))
    report.status   = 'resolved'
    report.admin_id = current_user.id
    db.session.commit()
    flash('✅ Solution provided. Report marked as resolved.', 'success')
    return redirect(url_for('admin_dashboard'))


# ── REPORT DETAILS ────────────────────────────────────────────────────────────
@app.route('/report/<int:report_id>')
@login_required
def view_report(report_id):
    report = Report.query.get_or_404(report_id)
    if current_user.role == 'user' and report.user_id != current_user.id:
        flash('You do not have permission to view this report.', 'error')
        return redirect(url_for('dashboard'))
    return render_template('report_details.html', report=report)


# ── FILE SERVING ──────────────────────────────────────────────────────────────
@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ── STARTUP ───────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("\n" + "="*55)
        print("  ✅ Threat Reporting System started!")
        print("  🌐 Open: http://localhost:5000")
        print("  📱 OTP will be sent via Twilio SMS")
        print("  ⚠️  Make sure TWILIO_PHONE_NUMBER is set in .env")
        print("="*55 + "\n")
    app.run(debug=True, port=5000)
