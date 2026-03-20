# 🛡️ Threat Reporting System
### Confidential Safety Platform — OTP via Twilio SMS

---

## ⚡ SETUP (One Time)

### Windows
Double-click `setup.bat`

### Mac / Linux
```
chmod +x setup.sh && ./setup.sh
```

---

## 📱 CONFIGURE TWILIO PHONE NUMBER

1. Go to https://console.twilio.com
2. Click **Phone Numbers → Manage → Active Numbers**
3. Copy your Twilio number (format: +1XXXXXXXXXX)
4. Open the `.env` file and set:
   ```
   TWILIO_PHONE_NUMBER=+1XXXXXXXXXX
   ```

> ⚠️ **Trial Account Restriction:** Twilio trial accounts can only
> send SMS to **verified numbers**. Go to:
> console.twilio.com → Verified Caller IDs → Add Number
> and verify each phone number that should receive OTPs.

---

## 🚀 RUN

```
python app.py         (Windows)
python3 app.py        (Mac/Linux)
```

Open: **http://localhost:5000**

---

## 📲 HOW OTP WORKS

1. User enters phone number on login page
2. Server generates a 6-digit OTP
3. **Twilio sends OTP via SMS** to the phone
4. User enters OTP — auto-submits at 6 digits
5. OTP expires in 5 minutes

---

## 👥 ROLES

| Role    | Phone (default)   | Access |
|---------|------------------|--------|
| Admin   | +919949258081    | Full access |
| Manager | +919876543211    | Review & forward |
| User    | Any other number | Submit reports |

Change in `.env`:
```
ADMIN_PHONE=+91XXXXXXXXXX
MANAGER_PHONES=+91XXXXXXXXXX,+91YYYYYYYYYY
```

---

## 🔄 REPORT WORKFLOW

User → [PENDING] → Manager reviews → [VERIFIED] → Admin resolves → [RESOLVED]

---

## ❓ TROUBLESHOOTING

**OTP not received?**
- Check console.twilio.com → Verified Caller IDs
- Add the target phone number there (trial accounts only)
- Check Messaging Geographic Permissions for India

**"21608" error?**
- Number not verified in Twilio. Add it to Verified Caller IDs.

**pip errors?**
- Run: `pip install -r requirements.txt --break-system-packages`
