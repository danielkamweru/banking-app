import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from typing import List

# Gmail Configuration
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", "muiathomas.mt@gmail.com"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "utmj nweh rcbb cswr"),
    MAIL_FROM=os.getenv("MAIL_FROM", "muiathomas.mt@gmail.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "True").lower() == "true",
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "False").lower() == "true",
    USE_CREDENTIALS=os.getenv("USE_CREDENTIALS", "True").lower() == "true",
    VALIDATE_CERTS=os.getenv("VALIDATE_CERTS", "True").lower() == "true"
)

# MY GROUP MAILS
GROUP8_TEAM = [
    "Ashley.mararo@student.moringaschool.com",
    "david.kuron@student.moringaschool.com",
    "yvonne.kadenyi@student.moringaschool.com",
    "daniel.kamweru@student.moringaschool.com",
    "thomas.mbula@student.moringaschool.com"
]

async def send_transaction_email(
    email: EmailStr, 
    name: str, 
    amount: float, 
    balance: float, 
    type: str,
    cc_emails: List[EmailStr] = None
):
    if cc_emails is None:
        cc_emails = GROUP8_TEAM

    subject = f"{type} Confirmation - Group8 Bank"
    
    html = f"""
    <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 20px auto; border: 1px solid #dcdcdc; border-radius: 10px; overflow: hidden;">
                <div style="background-color: #2c3e50; color: #ffffff; padding: 20px; text-align: center;">
                    <h1 style="margin: 0;">{type} Confirmation</h1>
                </div>
                <div style="padding: 30px;">
                    <p>Dear <strong>{name}</strong>,</p>
                    <p>Your recent {type.lower()} of <strong>KSh {amount:,.2f}</strong> was successful.</p>
                    
                    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #eee;"><strong>Amount:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #eee; color: #27ae60; font-weight: bold;">
                                KSh {amount:,.2f}
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #eee;"><strong>New Balance:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">
                                KSh {balance:,.2f}
                            </td>
                        </tr>
                    </table>
                    
                    <p>Thank you for banking with Group8.</p>
                </div>
                <div style="background-color: #f4f4f4; padding: 15px; text-align: center; font-size: 11px; color: #777;">
                    Notice: This is an audit-tracked transaction. Team members are CC'd automatically.
                </div>
            </div>
        </body>
    </html>
    """

 
    all_recipients = [email] + cc_emails

    message = MessageSchema(
        subject=subject,
        recipients=all_recipients, 
        cc=cc_emails, 
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    
    try:
        await fm.send_message(message)
        print(f" SUCCESS: Email delivered to {email} and all {len(cc_emails)} team members.")
    except Exception as e:
        print(f" SMTP ERROR: {e}")