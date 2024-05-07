import smtplib
import imaplib
import email
from email.mime.text import MIMEText
import google.generativeai as genai
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MAIL = os.environ.get("MAIL")
PASS = os.environ.get("PASS")
API_KEY = os.environ.get("API_KEY")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')


def fetch_emails():
    # Connect to IMAP server
    mail = imaplib.IMAP4_SSL('imap.gmx.com')
    mail.login(MAIL, PASS)

    # Select inbox folder
    mail.select('inbox')

    # Search for unread emails
    result, data = mail.search(None, 'UNSEEN')

    for num in data[0].split():
        # Fetch email data
        result, data = mail.fetch(num, '(RFC822)')
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Extract sender, subject, and body
        sender = msg['From']
        subject = msg['Subject']
        body = msg.get_payload()

        # Call AI to generate response
        response = generate_response(body)
        print(response)

        # Send response
        send_email(subject, response, sender)

def generate_response(input_text):
    # Call the OpenAI API to generate response
    response = model.generate_content('You are helping me answer my emails automatically as Joshua Meyer. Only write the response to the following mail in the inbox:' + input_text)
    return response.text + "\n\n" + "This response was generated by an AI model."

def send_email(subject, message, to):
    from_email = MAIL
    from_password = PASS
    to_email = to

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    gmail = smtplib.SMTP('smtp.gmx.com', 587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(from_email, from_password)
    gmail.send_message(msg)

def main():
    fetch_emails()

if __name__ == "__main__":
    main()
