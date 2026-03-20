from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    phone      = db.Column(db.String(20), unique=True, nullable=False)
    email      = db.Column(db.String(120), nullable=True)
    role       = db.Column(db.String(20), default='user')   # user / manager / admin
    is_active  = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    reports         = db.relationship('Report', backref='user',    lazy=True, foreign_keys='Report.user_id')
    managed_reports = db.relationship('Report', backref='manager', lazy=True, foreign_keys='Report.manager_id')
    admin_reports   = db.relationship('Report', backref='admin',   lazy=True, foreign_keys='Report.admin_id')
    solutions       = db.relationship('Solution', backref='admin', lazy=True)

class OTP(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    otp        = db.Column(db.String(10), nullable=False)
    is_used    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts   = db.Column(db.Integer, default=0)
    user       = db.relationship('User', backref='otps')

class Report(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    manager_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    admin_id       = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    category       = db.Column(db.String(50),  nullable=False)
    problem_type   = db.Column(db.String(100), nullable=False)
    custom_problem = db.Column(db.Text, nullable=True)
    description    = db.Column(db.Text, nullable=False)
    voice_message  = db.Column(db.String(200), nullable=True)
    status         = db.Column(db.String(50), default='pending')
    manager_comments = db.Column(db.Text, nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at     = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    attachments    = db.relationship('Attachment', backref='report', lazy=True, cascade='all, delete-orphan')
    keywords       = db.relationship('Keyword',    backref='report', lazy=True, cascade='all, delete-orphan')
    solutions      = db.relationship('Solution',   backref='report', lazy=True, cascade='all, delete-orphan')
    case_matches   = db.relationship('CaseMatch',  backref='report', lazy=True, cascade='all, delete-orphan')

class Attachment(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    report_id   = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    filename    = db.Column(db.String(200), nullable=False)
    filepath    = db.Column(db.String(500), nullable=False)
    file_type   = db.Column(db.String(100), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Keyword(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    report_id  = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    keyword    = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Solution(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    report_id     = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    admin_id      = db.Column(db.Integer, db.ForeignKey('user.id'),   nullable=False)
    solution_text = db.Column(db.Text, nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

# ═════════════════════════════════════════════════════════════════════════════
# NEW MODELS FOR ENHANCED FEATURES
# ═════════════════════════════════════════════════════════════════════════════

class PastCase(db.Model):
    """Store government/police solved cases for AI matching"""
    id             = db.Column(db.Integer, primary_key=True)
    case_title     = db.Column(db.String(300), nullable=False)
    category       = db.Column(db.String(50),  nullable=False)  # workplace/educational
    problem_type   = db.Column(db.String(100), nullable=False)
    description    = db.Column(db.Text, nullable=False)
    solution       = db.Column(db.Text, nullable=False)  # How police/govt solved it
    authority      = db.Column(db.String(200), nullable=False)  # Police dept, court, etc.
    case_date      = db.Column(db.DateTime, nullable=True)
    source_url     = db.Column(db.String(500), nullable=True)
    keywords       = db.Column(db.Text, nullable=True)  # Comma-separated keywords
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

class CaseMatch(db.Model):
    """Links reports to similar past cases"""
    id             = db.Column(db.Integer, primary_key=True)
    report_id      = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    past_case_id   = db.Column(db.Integer, db.ForeignKey('past_case.id'), nullable=False)
    similarity     = db.Column(db.Float, nullable=False)  # 0.0 to 1.0
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    past_case      = db.relationship('PastCase', backref='matches')

class EmailLog(db.Model):
    """Track all sent emails"""
    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    report_id      = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=True)
    email_type     = db.Column(db.String(50), nullable=False)  # case_resolved, status_update, etc.
    recipient      = db.Column(db.String(120), nullable=False)
    subject        = db.Column(db.String(200), nullable=False)
    sent_at        = db.Column(db.DateTime, default=datetime.utcnow)
    status         = db.Column(db.String(20), default='sent')  # sent, failed, bounced
    user           = db.relationship('User', backref='emails')
    report         = db.relationship('Report', backref='email_logs')
