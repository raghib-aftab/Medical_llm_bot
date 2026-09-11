import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime, timedelta
import zoneinfo
from config import settings


class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = settings.gmail_user
        self.sender_password = settings.gmail_pass
        
        # In-memory OTP storage (use Redis in production)
        self.otp_storage = {}
        
    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email using SMTP"""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = to_email
            
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, to_email, message.as_string())
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def generate_otp(self, length: int = 6) -> str:
        """Generate a random numeric OTP"""
        return ''.join(random.choices(string.digits, k=length))
    
    def generate_password(self, length: int = 12) -> str:
        """Generate a random password"""
        chars = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(random.choices(chars, k=length))
    
    def store_otp(self, email: str, otp: str, user_data: dict = None):
        """Store OTP with expiry time (5 minutes)"""
        self.otp_storage[email] = {
            "otp": otp,
            "expires_at": datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata")) + timedelta(minutes=5),
            "user_data": user_data
        }
    
    def verify_otp(self, email: str, otp: str) -> tuple[bool, Optional[dict]]:
        """Verify OTP and return user data if valid"""
        if email not in self.otp_storage:
            return False, None
        
        stored = self.otp_storage[email]
        
        if datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata")) > stored["expires_at"]:
            del self.otp_storage[email]
            return False, None
        
        if stored["otp"] != otp:
            return False, None
        
        user_data = stored.get("user_data")
        del self.otp_storage[email]
        return True, user_data
    
    async def send_signup_otp(self, email: str, name: str, otp: str) -> bool:
        """Send OTP for signup verification"""
        subject = "Verify Your Email - Medical AI"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .otp-box {{ background: #667eea; color: white; font-size: 32px; font-weight: bold; text-align: center; padding: 20px; border-radius: 10px; letter-spacing: 8px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 Medical AI</h1>
                    <p>Email Verification</p>
                </div>
                <div class="content">
                    <h2>Hello {name}!</h2>
                    <p>Thank you for signing up with Medical AI. To complete your registration, please use the following OTP:</p>
                    <div class="otp-box">{otp}</div>
                    <p><strong>This OTP is valid for 5 minutes.</strong></p>
                    <p>If you didn't request this verification, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>© 2024 Medical AI. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return self._send_email(email, subject, html_content)
    
    async def send_password_reset(self, email: str, name: str, new_password: str) -> bool:
        """Send new password for forgot password"""
        subject = "Password Reset - Medical AI"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .password-box {{ background: #28a745; color: white; font-size: 24px; font-weight: bold; text-align: center; padding: 20px; border-radius: 10px; margin: 20px 0; word-break: break-all; }}
                .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 Medical AI</h1>
                    <p>Password Reset</p>
                </div>
                <div class="content">
                    <h2>Hello {name}!</h2>
                    <p>Your password has been reset. Here is your new temporary password:</p>
                    <div class="password-box">{new_password}</div>
                    <div class="warning">
                        <strong>⚠️ Important:</strong> Please change this password after logging in for security reasons.
                    </div>
                    <p>If you didn't request this password reset, please contact our support immediately.</p>
                </div>
                <div class="footer">
                    <p>© 2024 Medical AI. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return self._send_email(email, subject, html_content)
    
    async def send_appointment_confirmation(
        self, 
        email: str, 
        name: str, 
        doctor_name: str,
        specialization: str,
        appointment_date: str,
        appointment_time: str,
        hospital_name: str,
        reason: str = ""
    ) -> bool:
        """Send appointment booking confirmation email"""
        subject = "Appointment Confirmed - Medical AI"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .appointment-card {{ background: white; border: 2px solid #28a745; border-radius: 10px; padding: 20px; margin: 20px 0; }}
                .appointment-card h3 {{ color: #28a745; margin-top: 0; }}
                .detail-row {{ display: flex; padding: 10px 0; border-bottom: 1px solid #eee; }}
                .detail-label {{ font-weight: bold; width: 150px; color: #666; }}
                .detail-value {{ flex: 1; }}
                .success-badge {{ background: #28a745; color: white; padding: 5px 15px; border-radius: 20px; display: inline-block; margin-bottom: 20px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 Medical AI</h1>
                    <p>Appointment Confirmation</p>
                </div>
                <div class="content">
                    <span class="success-badge">✓ Confirmed</span>
                    <h2>Hello {name}!</h2>
                    <p>Your appointment has been successfully booked. Here are the details:</p>
                    
                    <div class="appointment-card">
                        <h3>📋 Appointment Details</h3>
                        <div class="detail-row">
                            <span class="detail-label">👨‍⚕️ Doctor:</span>
                            <span class="detail-value">{doctor_name}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">🏥 Specialization:</span>
                            <span class="detail-value">{specialization}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">📍 Hospital:</span>
                            <span class="detail-value">{hospital_name}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">📅 Date:</span>
                            <span class="detail-value">{appointment_date}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">⏰ Time:</span>
                            <span class="detail-value">{appointment_time}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">📝 Reason:</span>
                            <span class="detail-value">{reason or 'Not specified'}</span>
                        </div>
                    </div>
                    
                    <p><strong>Please arrive 15 minutes before your scheduled time.</strong></p>
                    <p>If you need to reschedule or cancel, please do so at least 24 hours in advance.</p>
                </div>
                <div class="footer">
                    <p>© 2024 Medical AI. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return self._send_email(email, subject, html_content)
    
    async def send_appointment_cancellation(
        self, 
        email: str, 
        name: str, 
        doctor_name: str,
        specialization: str,
        appointment_date: str,
        appointment_time: str,
        hospital_name: str
    ) -> bool:
        """Send appointment cancellation email"""
        subject = "Appointment Cancelled - Medical AI"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .appointment-card {{ background: white; border: 2px solid #dc3545; border-radius: 10px; padding: 20px; margin: 20px 0; }}
                .appointment-card h3 {{ color: #dc3545; margin-top: 0; }}
                .detail-row {{ display: flex; padding: 10px 0; border-bottom: 1px solid #eee; }}
                .detail-label {{ font-weight: bold; width: 150px; color: #666; }}
                .detail-value {{ flex: 1; text-decoration: line-through; color: #999; }}
                .cancelled-badge {{ background: #dc3545; color: white; padding: 5px 15px; border-radius: 20px; display: inline-block; margin-bottom: 20px; }}
                .rebook {{ background: #007bff; color: white; padding: 15px 30px; border-radius: 5px; text-decoration: none; display: inline-block; margin-top: 20px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 Medical AI</h1>
                    <p>Appointment Cancellation</p>
                </div>
                <div class="content">
                    <span class="cancelled-badge">✗ Cancelled</span>
                    <h2>Hello {name}!</h2>
                    <p>Your appointment has been cancelled. Here were the details:</p>
                    
                    <div class="appointment-card">
                        <h3>📋 Cancelled Appointment</h3>
                        <div class="detail-row">
                            <span class="detail-label">👨‍⚕️ Doctor:</span>
                            <span class="detail-value">{doctor_name}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">🏥 Specialization:</span>
                            <span class="detail-value">{specialization}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">📍 Hospital:</span>
                            <span class="detail-value">{hospital_name}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">📅 Date:</span>
                            <span class="detail-value">{appointment_date}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">⏰ Time:</span>
                            <span class="detail-value">{appointment_time}</span>
                        </div>
                    </div>
                    
                    <p>If you need to book a new appointment, please visit our platform.</p>
                </div>
                <div class="footer">
                    <p>© 2024 Medical AI. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return self._send_email(email, subject, html_content)


# Create singleton instance
email_service = EmailService()
