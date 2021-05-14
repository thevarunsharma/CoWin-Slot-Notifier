#!/usr/bin/env python3

import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class CowinMailer:
    
    PORT_NUMBER = 587                   # port for outlook
    SMTP_SERVER = "smtp.office365.com"  # server for outlook
    
    @staticmethod
    def name_email_parser(line: str):
        email_regex = r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}'
        pattern = re.compile(
            r'(^\s*(.+)\s+<\s*(' + email_regex + ')\s*>\s*$)|(^\s*(' + email_regex + ')\s*$)',
            re.IGNORECASE)
        matched = pattern.match(line)
        if matched:
            if matched[1]:
                return {
                    "to_name" : f"{matched[2]} <{matched[3]}>",
                    "email" : matched[3]
                    }
            else:
                return {
                    "to_name" : matched[5],
                    "email" : matched[5]
                    }
        
        raise ValueError(f"Error while parsing recipient info '{line}'")
    
    @staticmethod
    def format_as_HTML(found_info: list):
        html = "" 
        for info in found_info:
            area_info = ", ".join(f"{key}: <i>{str(val).title()}</i>" for key, val in info["area"].items())
            header_html = f"<h3>Slots Available in {area_info} on {info['date']}</h3>"
            info_html = "<ol>"
            for center_id, center in info.get("centers").items():
                item_html = f"""<li>
                <h3>{center['name']}</h3>
                <h4>{center['address']}</h4>
                <h4>Mode: {center['fee_mode']}</h4>
                <strong>Available: {center['available_capacity']}</strong><br/>
                Age Limit: {center['age_limit']} &nbsp&nbsp&nbsp&nbsp Vaccine: <i>{center['vaccine']}</i>
                </li>
                """
                info_html += item_html
            info_html += "</ol>"
            html += f"""
                {header_html}
                {info_html}
            """
        final_html = f"""
        <html>
            <body>
                {html}
            </body>
        </html>
        """
        return final_html
    
    @staticmethod
    def auth_credentials(email: str,
                         password: str):
        mailserver = smtplib.SMTP(__class__.SMTP_SERVER, __class__.PORT_NUMBER)
        mailserver.starttls()
        # raises error if authentication fails
        mailserver.login(email, password)
        mailserver.quit()
    
    def __init__(self,
                 sender_email: str,
                 sender_name: str,
                 password: str):
        
        self.sender_email = sender_email
        self.sender_name = sender_name
        self.password = password
        self.recipients = []
        with open("credentials", "r") as fh:
            for line in fh.readlines():
                line = line.strip()
                if line:
                    self.recipients.append(__class__.name_email_parser(line))
    
    def compose_mail(self,
                     html: str,
                     to_name: str) -> str:
        
        message = MIMEMultipart()
        message['From'] = f"{self.sender_name} <{self.sender_email}>"
        message['To'] = to_name
        message['Subject'] = "CoWin Slot Notification"
        
        message.attach(MIMEText(html, 'html'))
        message.add_header('reply-to', 'cowin-notifier@protonmail.com')
        return message.as_string()


    def send_email_notif(self, 
                         found_info: list):
        
        mailserver = smtplib.SMTP(__class__.SMTP_SERVER, __class__.PORT_NUMBER)
        mailserver.starttls()
        mailserver.login(self.sender_email, self.password)
    
        html = __class__.format_as_HTML(found_info)
        
        for recipient in self.recipients:
            to_name = recipient['to_name']
            to_email = recipient['email']
            message = self.compose_mail(html, to_name)        
            mailserver.sendmail(self.sender_email, to_email, message)
        
        mailserver.quit()
