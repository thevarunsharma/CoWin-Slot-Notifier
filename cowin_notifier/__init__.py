#!/usr/bin/env python3

import click
import gc
import json
import time
from .cowin_data_utils import get_ist_date, get_available_slots, get_diff_value
from .cowin_mail_utils import CowinMailer
from diskcache import Cache

RECUR_PERIOD = 60 * 5          # 5 minutes

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Display verbose information')
@click.option('--pincode', '-p', default=None, help='Pincode to search by')
@click.option('--district', '-d', default=None, help='District to search by')
@click.option('--state', '-s', default=None, help='State for district to search by')
@click.option('--age-group', '-a', default=45, help='Age Group to filter by')
def main(pincode,
         district,
         state,
         age_group,
         verbose):
    """
    Sends E-Mail Notification for available CoWin Slots
    """
    cache = Cache(".previous")
    # sender's name for email
    sender_name = click.prompt("Sender's Name", default="CoWin Notifier")
    # sender's email address
    sender_email = click.prompt("Sender's Email")
    # sender's login password
    password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
    
    click.echo("CoWin Notifier running...")
    # mailer for sending emails
    mailer = CowinMailer(sender_email, 
                         sender_name, 
                         password)
    
    try:
        while True:
            cache.expire()
            date = get_ist_date()
            # fetch available slots
            available = get_available_slots(date, 
                                            pincode=pincode, 
                                            state=state, 
                                            district=district, 
                                            age_group=age_group)
            
            # get difference from cached value and update it
            centers = get_diff_value(available,
                                     cache,
                                     date,
                                     pincode=pincode,
                                     state=state,
                                     district=district,
                                     age_group=age_group)
            
            if centers is not None:
                # if cached value doesn't match current value
                click.echo("{0:-^100}".format("NEW CoWIN SLOTS FOUND"))
                available['centers'] = centers

                if verbose:
                    click.echo(json.dumps(available, indent=2))
    
                if available['centers']:
                    mailer.send_email_notif(available)
                    click.echo("EMAIL NOTIFICATION SENT SUCCESSFULLY!")
            
            gc.collect()
            time.sleep(RECUR_PERIOD)
    
    except KeyboardInterrupt:
        cache.close()
        click.echo("Aborted.")

if __name__ == '__main__':
    main()
