import os
import time
import imaplib
import email
from email.header import decode_header
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()  # Loads configuration from .env

# Configuration – make sure these are set in your .env file
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.yandex.ru")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.yandex.ru")
USERNAME = os.getenv("YANDEX_EMAIL")
PASSWORD = os.getenv("YANDEX_PASSWORD")
MAILBOX = "INBOX"

# Local folder to store attachments
ATTACHMENTS_DIR = "emails"
if not os.path.exists(ATTACHMENTS_DIR):
    os.makedirs(ATTACHMENTS_DIR)


def fetch_unseen_emails():
    """Connects to Yandex IMAP and fetches unseen emails."""
    messages = []
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(USERNAME, PASSWORD)
        mail.select(MAILBOX)
        result, data = mail.search(None, 'UNSEEN')
        if result != 'OK':
            print("Ошибка при поиске писем.")
            return messages
        for num in data[0].split():
            result, msg_data = mail.fetch(num, '(RFC822)')
            if result != 'OK':
                print("Ошибка при получении письма.")
                continue
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            messages.append(msg)
        mail.logout()
    except Exception as e:
        print("Ошибка IMAP:", e)
    return messages


def save_attachments(msg):
    """
    Checks for any attachment in the email message.
    If found, saves each attachment to the ATTACHMENTS_DIR.
    Returns True if at least one attachment was saved.
    """
    attachment_saved = False
    for part in msg.walk():
        content_disposition = part.get("Content-Disposition", "")
        if "attachment" in content_disposition.lower():
            filename = part.get_filename()
            if filename:
                # Decode filename if needed
                decoded_filename, encoding = decode_header(filename)[0]
                if isinstance(decoded_filename, bytes):
                    decoded_filename = decoded_filename.decode(encoding or 'utf-8')
                filepath = os.path.join(ATTACHMENTS_DIR, decoded_filename)
                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))
                print("Сохранен файл:", filepath)
                attachment_saved = True
    return attachment_saved


def send_reply_email(to_address, subject, body):
    """Sends a reply email using Yandex SMTP."""
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = USERNAME
        msg["To"] = to_address
        msg.set_content(body)
        with smtplib.SMTP_SSL(SMTP_SERVER, 465) as smtp:
            smtp.login(USERNAME, PASSWORD)
            smtp.send_message(msg)
        print("Ответ отправлен:", to_address)
    except Exception as e:
        print("Ошибка при отправке ответа:", e)


def process_emails():
    """Fetch unseen emails, process attachments or reply asking for them."""
    messages = fetch_unseen_emails()
    for msg in messages:
        # Get sender email
        from_address = email.utils.parseaddr(msg.get("From"))[1]
        print("Обработка письма от:", from_address)
        # Save attachments if present
        if not save_attachments(msg):
            # No attachment found – send a reply asking for a file
            send_reply_email(
                to_address=from_address,
                subject="Запрос файла",
                body="Добрый день! Прикрепите, пожалуйста, файл с описанием заявки."
            )


def main():
    print("Запуск приёма писем...")
    while True:
        process_emails()
        # Check for new emails every minute (adjust if needed)
        time.sleep(60)


if __name__ == "__main__":
    main()
