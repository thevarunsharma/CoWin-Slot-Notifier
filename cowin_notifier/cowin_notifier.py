#!/usr/bin/env python3

import click
import json
import smtplib
import sys
from .cowin_center_fetcher import fetch_centers_by_district_state, fetch_centers_by_pincode
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

with open("credentials", "r") as fh:
    PORT_NUMBER = int(fh.readline())
    SMTP_SERVER = fh.readline().strip()
    FROM_EMAIL = fh.readline().strip()
    FROM_NAME = fh.readline().strip() 
    TO_EMAIL = fh.readline().strip()
    TO_NAME = fh.readline().strip()
    PASSWORD = fh.readline().strip()


def get_available_slots(date: str, 
                        pincode: str = None, 
                        state: str = None, 
                        district: str = None,
                        age_group: int = 45) -> dict:
    if pincode:
        centers = fetch_centers_by_pincode(pincode, date)
        available = {"Area" : {
            "Pincode": pincode
            }}
    elif state and district:
        centers = fetch_centers_by_district_state(district, state, date)
        available = {"Area" : {
            "District": district,
            "State": state
            }}
    else:
        raise ValueError("Either 'pincode' or both 'state' and 'district' need to be passed")
    
    info = available["centers"] = {}
    for center in centers:
        center_id = center['center_id']
        center_name = center['name']
        center_address = center['address']
        for session in center.get('sessions'):
            if session['available_capacity'] > 0 and session['min_age_limit'] <= age_group:
                if center_id not in info:
                    info[center_id] = {
                            "Name": center_name,
                            "Address": center_address,
                            "Sessions": []
                            }
                info[center_id]['Sessions'].append({
                    "Date": session['date'],
                    "Available Capacity": session['available_capacity'],
                    "Age Limit": session['min_age_limit'],
                    "Vaccine": session['vaccine'],
                    "Slots": session['slots']
                    })
    return available

def format_as_HTML(info):
    area_info = ", ".join(f"{key}: <i>{str(val).title()}</i>" for key, val in info["Area"].items())
    header_html = f"<h3>Slots Available in {area_info}</h3>"
    info_html = "<ol>"
    for center_id, center in info.get("centers").items():
        item_html = f"""<li>
        <h3>{center['Name']}</h3>
        <h4>{center['Address']}</h4>
        <ul>
        """
        for sess in center['Sessions']:
            item_html += f"""
            <li>
                <strong>{sess['Date']} &nbsp&nbsp&nbsp&nbsp Available: {sess['Available Capacity']}</strong><br/>
                Age Limit: {sess['Age Limit']} &nbsp&nbsp&nbsp&nbsp Vaccine: <i>{sess['Vaccine']}</i>
            </li>
            """
        item_html += "</ul></li>"
        info_html += item_html
    info_html += "</ol>"
    html = f"""
    <html>
        <body>
            {header_html}
            {info_html}
        </body>
    </html>
    """
    return html

def compose_mail(info):
    message = MIMEMultipart()
    message['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
    message['To'] = f"{TO_NAME} <{TO_EMAIL}>"
    message['Subject'] = "CoWin Slot Notification"
    
    html = format_as_HTML(info)
    message.attach(MIMEText(html, 'html'))
    message.add_header('reply-to', 'cowin-notifier@protonmail.com')
    return message.as_string()


def send_email_notif(info):
    message = compose_mail(info)
    mailserver = smtplib.SMTP(SMTP_SERVER, PORT_NUMBER)
    mailserver.starttls()
    mailserver.login(FROM_EMAIL, PASSWORD)
    mailserver.sendmail(FROM_EMAIL, TO_EMAIL, message)
    mailserver.quit()


@click.command()
@click.argument('date')
@click.option('--verbose', '-v', is_flag=True, help='Display verbose information')
@click.option('--pincode', '-p', default=None, help='Pincode to search by')
@click.option('--district', '-d', default=None, help='District to search by')
@click.option('--state', '-s', default=None, help='State for district to search by')
@click.option('--age-group', '-a', default=45, help='Age Group to filter by')
def main(date,
         pincode,
         district,
         state,
         age_group,
         verbose):
    """
    Sends E-Mail Notification for available CoWin Slots on DATE
    """
    # fetch available slots
    available = get_available_slots(date, 
                                    pincode=pincode, 
                                    state=state, 
                                    district=district, 
                                    age_group=age_group)
    if verbose:
        click.echo(json.dumps(available, indent=2))
    
    if available['centers']:
        send_email_notif(available)
        click.echo("EMAIL NOTIFICATION SENT SUCCESSFULLY")
    else:
        click.echo("NO AVAILABLE SLOTS FOUND")
    

if __name__ == '__main__':
    main()
