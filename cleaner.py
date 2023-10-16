import os
from dotenv import load_dotenv
from exchangelib import DELEGATE, Account, Credentials, HTMLBody
from tqdm import tqdm
import logging

load_dotenv()

# Function to mark emails as read
def mark_emails_as_read(emails, account):
    update_emails = []
    for email in emails:
        email.is_read = True
        update_emails.append((email, ["is_read"]))
    try:
        account.bulk_update(update_emails)
    except Exception as e:
        print(f"An error occurred while marking emails as read: {e}")

# Function to connect to the email account
def connect_to_account():
    email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    credentials = Credentials(email, password)
    account = Account(email, credentials=credentials, autodiscover=True)
    return account

def main():
    try:
        account = connect_to_account()
    except:
        print("Failed to connect to the email account.")
        sys.exit()

    while True:
        search_text = input("Enter text to search in email addresses: ")

        # Filtering unread emails from the server that match the search string
        unread_emails = account.inbox.filter(is_read=False).filter(sender__contains=search_text).order_by('-datetime_received').only('id', 'subject', 'datetime_received')

        # Fetching ids as we'll need them for multiprocessing
        total_unread_emails = unread_emails.count()
        email_data = [(email.id, email.subject) for email in tqdm(unread_emails, desc='Fetching emails', unit='email', total=total_unread_emails)]

        # Display the subjects of the 50 newest emails
        for _, subject in email_data[:50]:
            print(f"- {subject}")
        print(f"Subjects of the 50 newest emails out of {total_unread_emails}:")

        # Ask for user confirmation
        user_input = input("Do you want to mark these emails as read? (yes/no): ").strip().lower()
        if user_input != 'yes':
            continue

        mark_emails_as_read(unread_emails, account)
        
        print(f"Marked {total_unread_emails} emails as read.")

if __name__ == "__main__":
    main()
