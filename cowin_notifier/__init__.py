#!/usr/bin/env python3

import click
import gc
import json
import time
from .cowin_data_utils import get_available_slots, get_diff_value, next_x_days
from .cowin_mail_utils import CowinMailer
from diskcache import Cache

RECUR_PERIOD = 60 * 5          # 5 minutes

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Display verbose information')
@click.option('--pincode', '-p', default=None, help='Pincode to search by')
@click.option('--district', '-d', default=None, help='District to search by')
@click.option('--state', '-s', default=None, help='State for district to search by')
@click.option('--age-group', '-a', default=45, help='Age Group to filter by')
@click.option('--check-period', '-c', default=5, help='Number of days in future to be checked')
@click.option('--recur-period', '-r', type=int, default=None, help='Frequency of recurring updation in seconds')
@click.option('--vaccine', default=None, help='Specific vaccine')
@click.option('--dose', type=int, default=None, help='Dose 1 or 2')
def main(pincode,
         district,
         state,
         age_group,
         verbose,
         check_period,
         recur_period,
         vaccine,
         dose):
    """
    Sends E-Mail Notification for available CoWin Slots
    """
    cache = Cache(".previous")
    # sender's name for email
    sender_name = click.prompt("Sender's Name", default="CoWin Notifier").strip()
    # sender's email address
    sender_email = click.prompt("Sender's Email").strip()
    # sender's login password
    password = click.prompt("Password", hide_input=True, confirmation_prompt=True).strip()
    
    click.echo("CoWin Notifier running...")
    # mailer for sending emails
    mailer = CowinMailer(sender_email, 
                         sender_name, 
                         password)
    
    if recur_period:
        global RECUR_PERIOD
        RECUR_PERIOD = recur_period
        
    try:
        while True:
            cache.expire()
            dates = next_x_days(check_period)
            
            found = []          # list of found available slots
            for date in dates:
                # fetch available slots
                available = get_available_slots(date, 
                                                pincode=pincode, 
                                                state=state, 
                                                district=district, 
                                                age_group=age_group,
                                                vaccine=vaccine,
                                                dose=dose)
                
                # get difference from cached value and update it
                centers = get_diff_value(available,
                                        cache,
                                        date,
                                        pincode=pincode,
                                        state=state,
                                        district=district,
                                        age_group=age_group,
                                        vaccine=vaccine,
                                        dose=dose)
                
                if centers is not None:
                    # if cached value doesn't match current value
                    found.append(available)
            
            if found:
                click.echo("{0:-^100}".format("NEW CoWIN SLOTS FOUND"))
                if verbose:
                    click.echo(json.dumps(found, indent=2))
                
                mailer.send_email_notif(found)
                click.echo("EMAIL NOTIFICATION SENT SUCCESSFULLY!")
        
            gc.collect()
            time.sleep(RECUR_PERIOD)

    except KeyboardInterrupt:
        cache.close()
        click.echo("Aborted.")

if __name__ == '__main__':
    main()
