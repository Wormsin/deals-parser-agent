import imaplib
import email
from email.header import decode_header
import uuid
import json
from dotenv import load_dotenv
import os
import shutil

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()  # Loads configuration from .env

# Configuration – make sure these are set in your .env file
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.yandex.ru")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.yandex.ru")
USERNAME = os.getenv("YANDEX_EMAIL")
PASSWORD = os.getenv("YANDEX_PASSWORD")
MAILBOX = "INBOX"

ATTACHMENTS_DIR = "mail_agent/attachments"

def connect_to_imap():
    """Connects to Yandex IMAP server."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(USERNAME, PASSWORD)
        return mail
    except Exception as e:
        print("Ошибка IMAP:", e)

def fetch_unseen_emails(mail):
    messages = []
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
    return messages

# Функция для загрузки и сохранения базы данных компаний
def load_company_database(file_name="mail_agent/database/contacts_db.json"):
    try:
        with open(file_name, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_company_database(data, file_name="mail_agent/database/contacts_db.json"):
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)


# Функция для обработки письма
def new_company_check(msg):
    company_db = load_company_database()
    # Разбор письма
    sender_email = msg['From']
    
    # Проверка, есть ли такая компания в базе
    company_id = None
    for company in company_db:
        if company['email'] == sender_email:
            company_id = company['id_company']
            break
    
    # Если компании с таким email нет, добавляем новую
    if company_id is None:
        company_id = str(uuid.uuid4())  # Генерация уникального ID для компании
        new_company = [{"id_company": company_id, "email": sender_email}]
        company_db.extend(new_company)
        save_company_database(company_db)
        print(f"Добавлена новая компания: {sender_email}")
            
def read_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode()  # Получаем тело письма
    else:
        body = msg.get_payload(decode=True).decode()
    return body

def save_attachments(msg):
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
    if attachment_saved:
        shutil.copy(filepath, "classification_rag/emails/"+decoded_filename)
    return attachment_saved
    

