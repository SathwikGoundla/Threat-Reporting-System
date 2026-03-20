"""
Email Notification Service for Threat Reporting System
Sends automated emails when cases are resolved using Flask-Mail with Gmail SMTP
"""

import os
from flask_mail import Mail, Message
from datetime import datetime

mail = Mail()

def init_mail(app):
    """Initialize Flask-Mail with app configuration"""
    app.config['MAIL_SERVER']   = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT']     = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS']  = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 
                                                        os.environ.get('MAIL_USERNAME'))
    mail.init_app(app)
    return mail

def send_case_resolved_email(user_email, report_id, solution_text, problem_type, report_description):
    """
    Send beautiful HTML email when case is resolved
    
    Args:
        user_email: User's email address
        report_id: Report ID number
        solution_text: Admin's solution
        problem_type: Type of problem reported
        report_description: Brief description of the issue
    
    Returns:
        dict: {'success': bool, 'email': str or None, 'error': str or None}
    """
    if not user_email:
        return {'success': False, 'email': None, 'error': 'No email address provided'}
    
    try:
        subject = f"✅ Case #{report_id} Resolved - Threat Reporting System"
        
        # Beautiful HTML email template
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .header h2 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    background: #f8f9fa;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .info-box {{
                    background: white;
                    padding: 15px;
                    margin: 15px 0;
                    border-left: 4px solid #667eea;
                    border-radius: 5px;
                }}
                .info-label {{
                    font-weight: bold;
                    color: #667eea;
                    font-size: 12px;
                    text-transform: uppercase;
                    margin-bottom: 5px;
                }}
                .info-value {{
                    font-size: 14px;
                    color: #333;
                }}
                .solution-box {{
                    background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
                    padding: 20px;
                    border-radius: 5px;
                    margin: 20px 0;
                    border-left: 4px solid #28a745;
                }}
                .solution-title {{
                    color: #28a745;
                    font-weight: bold;
                    margin-bottom: 10px;
                    font-size: 16px;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #999;
                    font-size: 12px;
                    border-top: 1px solid #ddd;
                    margin-top: 20px;
                }}
                .badge {{
                    display: inline-block;
                    background: #28a745;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>✅ Your Case Has Been Resolved!</h2>
                </div>
                
                <div class="content">
                    <p>Hello,</p>
                    
                    <p>We're pleased to inform you that your reported case has been reviewed and resolved by our administration team.</p>
                    
                    <div class="info-box">
                        <div class="info-label">📋 Case ID</div>
                        <div class="info-value">#{report_id}</div>
                    </div>
                    
                    <div class="info-box">
                        <div class="info-label">📌 Problem Type</div>
                        <div class="info-value">{problem_type}</div>
                    </div>
                    
                    <div class="info-box">
                        <div class="info-label">📝 Your Report</div>
                        <div class="info-value">{report_description}</div>
                    </div>
                    
                    <div class="solution-box">
                        <div class="solution-title">✨ Resolution & Recommendations:</div>
                        <p>{solution_text}</p>
                    </div>
                    
                    <p style="color: #28a745; font-weight: bold;">
                        <span class="badge">RESOLVED</span>
                    </p>
                    
                    <p>If you have any follow-up questions or concerns, please don't hesitate to contact us through the reporting system.</p>
                    
                    <p>Thank you for helping us maintain a safe and secure environment!</p>
                    
                    <div class="footer">
                        <p>
                            Threat Reporting System<br>
                            This email was sent to you as a notification of case resolution.<br>
                            <strong>⚠️ Disclaimer:</strong> This document contains confidential information. 
                            Please handle with care and do not share with unauthorized persons.<br>
                            Generated on {datetime.now().strftime('%d %B %Y at %I:%M %p')}
                        </p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text fallback
        text_body = f"""
        Case Resolution Notification
        ============================
        
        Hello,
        
        Your case #{report_id} has been resolved.
        
        Problem Type: {problem_type}
        
        Your Report: {report_description}
        
        Resolution:
        {solution_text}
        
        Status: RESOLVED
        
        Thank you for using the Threat Reporting System.
        """
        
        # Create message
        msg = Message(
            subject=subject,
            recipients=[user_email],
            html=html_body,
            body=text_body
        )
        
        # Send email
        mail.send(msg)
        
        return {
            'success': True,
            'email': user_email,
            'error': None
        }
        
    except Exception as e:
        print(f"❌ Email sending failed: {str(e)}")
        return {
            'success': False,
            'email': user_email,
            'error': str(e)
        }

def send_status_update_email(user_email, report_id, old_status, new_status, comments=None):
    """
    Send email when report status is updated
    
    Args:
        user_email: User's email address
        report_id: Report ID
        old_status: Previous status
        new_status: New status
        comments: Optional manager comments
    
    Returns:
        dict: {'success': bool, 'error': str or None}
    """
    if not user_email:
        return {'success': False, 'error': 'No email address provided'}
    
    try:
        subject = f"📢 Status Update: Case #{report_id}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #667eea; color: white; padding: 20px; text-align: center; border-radius: 5px; }}
                .content {{ background: #f8f9fa; padding: 20px; margin-top: 20px; border-radius: 5px; }}
                .status-badge {{ display: inline-block; padding: 8px 15px; border-radius: 20px; font-weight: bold; }}
                .status-updated {{ background: #ffc107; color: white; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Case Status Updated</h2>
                </div>
                <div class="content">
                    <p>Hello,</p>
                    <p>The status of your case #<strong>{report_id}</strong> has been updated.</p>
                    <p>
                        <strong>Previous Status:</strong> {old_status.replace('_', ' ').title()}<br>
                        <strong>New Status:</strong> <span class="status-badge status-updated">{new_status.replace('_', ' ').title()}</span>
                    </p>
                    {f'<p><strong>Comments:</strong> {comments}</p>' if comments else ''}
                    <p>Thank you for using the Threat Reporting System.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            recipients=[user_email],
            html=html_body
        )
        
        mail.send(msg)
        return {'success': True, 'error': None}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}
