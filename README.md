# Threat Reporting System

A comprehensive web-based platform for reporting and managing threats/harassment in workplace and educational environments. This system provides secure and anonymous reporting capabilities with multi-user dashboard access for administrators and managers.

## Overview

The Threat Reporting System is designed to help individuals (Men/Women) report problems, harassment, or threats in workplace or educational environments confidentially and securely. It features multi-level user roles, SMS notifications via Twilio, OTP verification, and detailed reporting analytics.

## Features

- **User Authentication**
  - Secure login with OTP-based verification
  - Password-based authentication
  - Session management

- **Multi-Level Dashboards**
  - User Dashboard: Submit and track personal reports
  - Manager Dashboard: Review and manage reports from team members
  - Admin Dashboard: Full system control and analytics

- **Reporting System**
  - Easy-to-use threat/harassment reporting form
  - Survey form for additional feedback collection
  - Report categorization and priority levels
  - Detailed report view with status tracking

- **SMS Notifications**
  - Twilio integration for SMS alerts
  - OTP verification via SMS
  - Report status notifications

- **Security Features**
  - User authentication and authorization
  - OTP-based email verification
  - Secure file uploads (PDFs, documents)
  - Session management with secure cookies

## Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite (with Flask SQLAlchemy ORM)
- **Frontend**: HTML5, CSS3, JavaScript
- **SMS Service**: Twilio API
- **Server**: WSGI-compatible Python application

## Project Structure

```
threat-reporting-system/
├── app.py                              # Main Flask application
├── models.py                           # Database models (User, Report, Survey, etc.)
├── sms.py                              # Twilio SMS integration
├── requirements.txt                    # Python dependencies
├── setup.bat                           # Windows setup script
├── setup.sh                            # Unix setup script
├── README.md                           # Project documentation
├── templates/                          # HTML templates
│   ├── base.html                       # Base template (navbar, layout)
│   ├── login.html                      # Login page
│   ├── verify_otp.html                 # OTP verification
│   ├── user_dashboard.html             # User report dashboard
│   ├── manager_dashboard.html          # Manager view
│   ├── admin_dashboard.html            # Admin control panel
│   ├── survey_form.html                # Survey submission
│   ├── report_details.html             # Report detail view
├── static/                             # Static assets
│   ├── css/
│   │   └── style.css                   # Main stylesheet
│   └── js/
│       └── main.js                     # JavaScript utilities
├── uploads/                            # User uploaded files
└── instance/                           # Flask instance folder (config, databases)
```

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- Twilio account with API credentials

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/SathwikGoundla/Threat-Reporting-System.git
   cd Threat-Reporting-System
   ```

2. **Create and activate virtual environment**
   
   **Windows:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
   
   **macOS/Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the root directory:
   ```
   FLASK_ENV=development
   FLASK_DEBUG=True
   SECRET_KEY=your-secret-key-here
   TWILIO_ACCOUNT_SID=your-twilio-account-sid
   TWILIO_AUTH_TOKEN=your-twilio-auth-token
   TWILIO_PHONE_NUMBER=your-twilio-phone-number
   ```

5. **Initialize the database**
   ```bash
   python app.py
   ```

   Or use the setup scripts:
   - **Windows**: `setup.bat`
   - **Unix/Linux**: `bash setup.sh`

6. **Run the application**
   ```bash
   python app.py
   ```

   The application will be available at `http://localhost:5000`

## Usage

### User Workflow

1. **Login/Signup**: Access the login page and authenticate with OTP verification
2. **Submit Report**: Navigate to the reporting form and provide details about the threat/harassment
3. **Track Status**: Monitor report status in the user dashboard
4. **Survey**: Complete feedback surveys as requested

### Manager Workflow

1. **View Reports**: Access manager dashboard to see team member reports
2. **Review Details**: Click on reports to view full details and attachments
3. **Update Status**: Change report status and add comments

### Admin Workflow

1. **System Control**: Access admin dashboard for complete system oversight
2. **User Management**: Manage user accounts and permissions
3. **Report Analytics**: View system-wide statistics and trends
4. **Configuration**: Manage system settings and features

## Database Models

- **User**: User accounts with role-based access (user, manager, admin)
- **Report**: Threat/harassment incident reports
- **Survey**: Feedback surveys
- **Attachment**: File uploads associated with reports

## API Integration

### Twilio SMS Integration
- OTP generation and delivery
- SMS notifications for report status changes
- Two-factor authentication

Required files: `sms.py` - Contains Twilio integration logic

## Security Considerations

- All user inputs are validated and sanitized
- Passwords are hashed using secure algorithms
- OTP-based multi-factor authentication
- Session tokens with expiration
- CSRF protection on forms
- Secure file upload handling

## Contributing

Contributions are welcome! Please follow these guidelines:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

For issues, questions, or suggestions, please:
- Create an issue in the GitHub repository
- Contact the development team

## Author

**Sathik Goundla**  
Email: sathwikgoundla7@gmail.com  
GitHub: [SathwikGoundla](https://github.com/SathwikGoundla)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This system is designed to help individuals report workplace and educational environment issues. All reports are treated with confidentiality and respect. Please use this platform responsibly and truthfully.

---

**Last Updated**: March 2026  
**Version**: 1.0.0
