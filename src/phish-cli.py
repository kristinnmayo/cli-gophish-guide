#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import csv
import configparser
import requests.packages.urllib3
import time
from datetime import datetime, timedelta
from gophish import Gophish
from gophish.models import (Campaign, Group, Page, SMTP, Template, User)

# =============================================================================
# initialize and define variables to hold gophish objects
# pass command line arguments to corresponding methods
# print basic stats for newly created campaign
# =============================================================================
def launch(args):
    CAMPAIGN_NAME, SENDER_NAME, SENDER_EMAIL, TARGET_LIST, EMAIL_HTML, EMAIL_SUBJECT, LANDING_URL, LANDING_HTML, LAUNCH_DATETIME = args
    
    group = newgroup(CAMPAIGN_NAME, TARGET_LIST)
    sender = newsender(CAMPAIGN_NAME, SENDER_NAME, SENDER_EMAIL)
    page = newpage(CAMPAIGN_NAME, LANDING_HTML)
    template = newtemplate(CAMPAIGN_NAME, EMAIL_HTML, EMAIL_SUBJECT)
    campaign = newcampaign(CAMPAIGN_NAME, LANDING_URL, group, sender, template, page, LAUNCH_DATETIME)
    exit('Success: {} campaign created (status={})'.format(campaign.name, campaign.status))

# =============================================================================
# give examples, prompt for each attribute, display chosen parameters
# prompt for confirmation, assemble attributes in list to pass to launch
# options to start over from entry to guide() or exit program
# =============================================================================
def guide():
    print('\nFormat: ./phish.py <title> <sendername> <senderemail> <targetlist.csv> <email.html> <emailsubject> <pageurl> <page.html> <launchtime>')
    
    print('\n\teg: <title>')
    print('\t    "New Phishing Campaign"')
    CAMPAIGN_NAME = input('\n\t    Name of campaign: ')
 
    print('\n\teg: <sendername> <senderemail>')
    print('\t    "Jane Smith" jrsmith@email.com')
    SENDER_NAME = input('\n\t    Sender full name: ')
    SENDER_EMAIL = input('\t    Sender email address: ')

    print('\n\teg: <targetlist.csv>')
    print('\t    users.csv')    
    TARGET_LIST = input('\n\t    File name/path to list of targets: ')
    
    print('\n\teg: <email.html> <emailsubject>')
    print('\t    schedule.html "Conference Schedule Update"')    
    EMAIL_HTML = input('\n\t    File name/path to email contents: ')
    EMAIL_SUBJECT = input('\t    Subject line of email: ') 
    
    print('\n\teg: <pageurl> <page.html>')
    print('\t    http://fakeurl.com pages/landing.html')    
    LANDING_URL = input('\n\t    URL of landing page: ')
    LANDING_HTML = input('\t    File name/path to page contents: ')
    
    print('\n\teg: <launchtime>')
    print('\t    1999/12/31@23:59')
    LAUNCH_DATETIME = input('\n\t    Date/time of launch: ')

    if '@' in LAUNCH_DATETIME:
        d, t = LAUNCH_DATETIME.split('@')
    else:
        exit('\n\nImproper datetime format')

    print('\n\n>>> Creating campaign\n')
    print('             Name: {}'.format(CAMPAIGN_NAME))
    print('           Sender: {}'.format(SENDER_NAME))
    print('     From Address: {}'.format(SENDER_EMAIL))
    print('          Targets: {}'.format(TARGET_LIST))
    print('       Email Code: {}'.format(EMAIL_HTML))
    print('    Email Subject: {}'.format(EMAIL_SUBJECT))
    print('         Page URL: {}'.format(LANDING_URL))
    print('        Page Code: {}'.format(LANDING_HTML))
    print('           Launch: {} @ {}'.format(d, t))

    print('\n\n>>> Ready to Launch?\n')
    print('          1) Yes')
    print('          2) No, start over')
    print('          3) No, exit')
    confirm = input('\nSelection: ')

    if confirm == '1':
        args = [CAMPAIGN_NAME, SENDER_NAME, SENDER_EMAIL, TARGET_LIST, EMAIL_HTML, EMAIL_SUBJECT, LANDING_URL, LANDING_HTML, LAUNCH_DATETIME]
        launch(args)
    elif confirm == '2':
        guide()
    else:
        exit('\n\nCanceled campaign creation. You entered: {}'.format(confirm))

# =============================================================================
# accept group attributes as arguments
# pass each csv row to newuser(), append each user to targetlist
# initializ new gophish group object, targets must be list form
# returns reference to group object, or AttributeError if post fails
# =============================================================================
def newgroup(name, path):
    targetlist = []
    fieldnames = ['First Name', 'Last Name', 'Email', 'Position']
    try:
        with open(path) as file:
            reader = csv.DictReader(file, fieldnames)
            for row in reader:
                if row:
                    targetlist.append(newuser(row))
                    
        group = Group(name=name, targets=targetlist)

    except(FileNotFoundError):
        exit('\tError: no such file {}'.format(path))

    try:
        group = api.groups.post(group)
        print('\nSuccess: {} target group created'.format(group.name))
        return group

    except(AttributeError):
        exit('\n\tError:  failed to create target group (possible duplicate)\n')

# =============================================================================
# accept single row of csv, cast to gophish type
# initialize and return reference to new gophish template object
# =============================================================================
def newuser(row):
    return (User(first_name=row['First Name'], last_name=row['Last Name'],
                 email=row['Email'], position=row['Position']))

# =============================================================================
# accept sender attributes as arguments
# initialize new gophish sender object
# email address format "First Last <flast@mail.com>"
# returns reference to sender object, or AttributeError if post fails
# =============================================================================
def newsender(name, sender, email):
    address = sender + ' <' + email + '>'
    smtp = SMTP(name=name, from_address=address,
                host=sender_host, ignore_cert_errors=True)
        
    try:
        smtp = api.smtp.post(smtp)
        print('Success: {} sender profile created'.format(smtp.name))
        return smtp

    except(AttributeError):
        exit(
                '\n\n\tError: failed to create sender profile (possible duplicate name or invalid email)\n'
                )

# =============================================================================
# accept page attributes as arguments
# initialize new gophish page object
# returns reference to page object, or AttributeError if post fails
# =============================================================================
def newpage(name, path):
    try:
        with open(path) as file:
            html = file.read()
            page = Page(name=name, html=html)
    
    except(FileNotFoundError):
        exit('\n\tError: no such file {}\n'.format(path))

    try:
        page = api.pages.post(page)
        print('Success: {} landing page created'.format(page.name))
        return page

    except(AttributeError):
        exit('\n\tError: failed to create landing page (possible duplicate)\n')

# =============================================================================
# accept template attributes as arguments
# initialize new gophish template object
# source attempts to parse null attachment, raises error - ignore
# returns reference to template object, or AttributeError if post fails
# =============================================================================
def newtemplate(name, path, subject):
    try:
        with open(path) as file:
            html = file.read()
    
        template = Template(name=name, subject=subject, html=html)

    except(FileNotFoundError):
        exit('\n\tError: no such file {}\n'.format(path))

    try:
        template = api.templates.post(template)

    except(TypeError):
        # possible source code bug, attempts to parse null attachment
        print('\n\t### ignore bug (attempt to parse empty attachment list)\n')

    try:
        print('Success: {} email template created'.format(template.name))
        return template
    
    except(AttributeError):
        exit('\n\tError: failed to create email template (possible duplicate)\n')

# =============================================================================
# accept campaign attributes as arguments
# initialize new gophish campaign object, group attribute must be in list form
# returns reference to campaign object, or AttributeError if post fails
# =============================================================================
def newcampaign(name, url, group, smtp, template, page, timestamp):
    launching = phishingtime(timestamp)
    campaign = Campaign(name=name, groups=[group], page=page,
                        template=template, smtp=smtp, url=url, launch_date=launching)
    
    try:
        campaign = api.campaigns.post(campaign)
        return campaign

    except(AttributeError):
        exit('\n\tError: failed to create campaign (possible invalid url or datetime)\n')

# =============================================================================
# accept user defined timestamp, convert to datetime
# find local timezone, convert timestamp to utc
# return iso formatted string
# =============================================================================
def phishingtime(stamp):
    launching = datetime.strptime(stamp, '%Y/%m/%d@%H:%M')
    offset = timedelta(hours=(time.timezone/3600))
    launching += offset
    launching = launching.isoformat()
    return (launching + 'Z')

# =============================================================================
# check number of command line arguments
# if given, pass to launch, else print format on exit
# =============================================================================
def main():
    global api, sender_host, verify

    if sys.version_info < (3, 0, 0):
        exit('\nNot compatible with python 2\n')

    config = configparser.ConfigParser()
    config.read('phish.cfg')

    api_key = config.get('DEFAULT','api_key')
    host_url = config.get('DEFAULT','host_url')
    sender_host = config.get('DEFAULT','sender_host')
    verify = config.get('DEFAULT','verify')

    test = ["True", "False"]
    if verify in test:
        if not eval(verify):
            requests.packages.urllib3.disable_warnings()
    else:
        exit('Error: configuration variable (verify) is undefined')

    api = Gophish(api_key, host_url, verify=False)

    if len(sys.argv) == 10:
        args = sys.argv[1:]
        launch(args)
        
    elif len(sys.argv) == 2:
        flag = sys.argv[1]
        if flag == '-g':
            guide()

    exit('\nWrong number of command line arguments'
         '\n\nFormat: ./phish.py <title> <sendername> <senderemail> <targetlist.csv> <email.html> <emailsubject> <pageurl> <page.html> <launchtime>'
                
         '\n\n    eg: ./phish.py "Campaign Name" "John Doe" jdoe@mail.com targets.csv email.html "Email Subject Line" http://phishing.com page.html 2018/06/29@14:30'
         '\n        ./phish.py "Phish Test Title" "JK Rowling" jkr@mail.com /path/targets.csv email.html "New Book" https://login.phishing.com page.html 1999/12/31@23:59\n'
                
         '\n\n         title.............name for new campaign objects'
         '\n         sendername........first and last name as should appear in email header'
         '\n         senderemail.......address as should appear in email header'
         '\n         targetlist........csv file (fieldnames=First Name,Last Name,Email,Position)'
         '\n         email.html........contents of email in html format'
         '\n         emailsubject......subject line as will appear in email'
         '\n         pageurl...........phony link address to be used in email'
         '\n         page.html.........contents of landing page in html format'
         '\n         launchtime........date and time (24hr) to send email'
         
         '\n\n Alternative:'
         
         '\n         -g................campaign creation guide '

         '\n\n !format for launchtime MUST use format YYYY/MM/DD@HH:MM [eg: 2018/06/14@4:22]\n'
                )
  
main()
