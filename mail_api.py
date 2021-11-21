import string
import os
import re
import random
import requests
import pyperclip

url = 'https://www.1secmail.com/api/v1/'
domain = random.choice(['1secmail.com', '1secmail.net', '1secmail.org'])


def create_name():
    # creates a random 10 char string
    s = string.ascii_lowercase + string.digits
    name = ''.join(random.choice(s) for i in range(10))
    return name


def get_api_inbox(email):
    # calls api for new emails
    mail_split = email.split('@')
    reqLink = f'{url}?action=getMessages&login={mail_split[0]}&domain={mail_split[1]}'
    msgs_res = requests.get(reqLink).json()
    if not msgs_res:
        return []

    # if mailbox has mail get it's content from api
    for msg in msgs_res:
        id = msg['id']
        msgRead = f'{url}?action=readMessage&login={mail_split[0]}&domain={mail_split[1]}&id={id}'
        msg['content'] = requests.get(msgRead).json()['textBody']

    # save to local directory
    save_to_inbox(msgs_res)

    # return the email list for display by UI
    return msgs_res


def save_to_inbox(msgs):
    # takes the list of emails msgs and saves to local directory

    # handle directory path
    current_dir = os.getcwd()
    final_dir = os.path.join(current_dir, r'Inbox')
    if not os.path.exists(final_dir):
        os.makedirs(final_dir)

    # write msgs to dir
    for msg in msgs:
        mail_local_path = os.path.join(final_dir, f'{msg["id"]}.txt')
        with open(mail_local_path, 'w') as file:
            txt = f"From: {msg['from']}\nSubject: {msg['subject']}\nDate: {msg['date']}\nContent:\n{msg['content']}"
            file.write(txt)


def start_mail(is_random, custom_domain_input):
    # call api to init our new mail
    try:
        req_url = f'{url}?login={create_name() if is_random else custom_domain_input}&domain={domain}'
        requests.get(req_url)
        userName = re.search(r'login=(.*)&', req_url).group(1)
        _domain = re.search(r'domain=(.*)', req_url).group(1)

        email = f'{userName}@{_domain}'
        pyperclip.copy(email)
        return email

    # dispose in case call was interrupted
    except KeyboardInterrupt:
        mail_split = email.split('@')
        data = {
            'action': 'deleteMailbox',
            'login': f'{mail_split[0]}',
            'domain': f'{mail_split[1]}'
        }
        
        requests.post('https://www.1secmail.com/mailbox', data=data)
        return ''
