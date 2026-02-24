import os
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from dotenv import load_dotenv

load_dotenv()

# Check for required email settings
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

conf = None
if MAIL_USERNAME and MAIL_PASSWORD and MAIL_PASSWORD != "your_app_password":
    conf = ConnectionConfig(
        MAIL_USERNAME=MAIL_USERNAME,
        MAIL_PASSWORD=MAIL_PASSWORD,
        MAIL_FROM=os.getenv("MAIL_FROM", MAIL_USERNAME),
        MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
        MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
        MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME", "TaskManager"),
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True
    )
else:
    print("⚠️ Email settings not configured in .env. Email features will be disabled.")

async def send_credentials_email(email: EmailStr, fullname: str, password: str):
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; rounded: 8px;">
            <h2 style="color: #137fec;">Welcome to TaskManager!</h2>
            <p>Hello <strong>{fullname}</strong>,</p>
            <p>Your account has been created by the administrator. Here are your login credentials:</p>
            <div style="background-color: #f6f7f8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Login URL:</strong> <a href="http://localhost:8000">TaskManager</a></p>
                <p style="margin: 5px 0;"><strong>Email:</strong> {email}</p>
                <p style="margin: 5px 0;"><strong>Temporary Password:</strong> {password}</p>
            </div>
            <p style="color: #ff4444; font-size: 0.9em;">Please change your password after your first login for security.</p>
            <p>Best regards,<br>The TaskManager Team</p>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="Your TaskManager Account Credentials",
        recipients=[email],
        body=html,
        subtype=MessageType.html
    )

    if conf:
        try:
            fm = FastMail(conf)
            await fm.send_message(message)
            print(f"✅ Email sent successfully to {email}")
        except Exception as e:
            print(f"⚠️ Failed to send email to {email}: {e}")
            print(f"📧 User {fullname} was created with password: {password}")
    else:
        print(f"📧 Simulated Email to {email}: User {fullname} created with password {password}")
