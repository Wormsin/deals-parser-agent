from email_reader import connect_to_imap, fetch_unseen_emails, new_company_check, save_attachments
import time


def main():
    print("Запуск приёма писем...")
    mail = connect_to_imap()
    try:
        while True:
            messages = fetch_unseen_emails(mail)
            for msg in messages:
                new_company_check(msg)
                #body = read_email_body(msg)
                save_attachments(msg)
                #print("Тело письма:", body)
            
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nПрерывание работы, закрываем соединение с сервером...")
        mail.logout()


if __name__ == "__main__":
    main()
