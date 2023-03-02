import base64
import os
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly', # for searching
    'https://www.googleapis.com/auth/gmail.send', # message composing
    ]


def initialize_credentials():
    """
    Check creds token and create one if not exists
    copied from google sample
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


class GmailApi:
    def __init__(
            self,
            creds=None,
            ):
        if not creds:
            self.creds = initialize_credentials()
        self.service = build('gmail', 'v1', credentials=self.creds)

    def send_message(
            self,
            message_from,
            message_to,
            subject,
            content,
            ):
        """
        Create and send simplest message according to RFC2822.
        Returns None if failed to send the message.
        """
        try:
            message = EmailMessage()
            message.set_content(content)
            message['To'] = message_to
            message['From'] = message_from
            message['Subject'] = subject

            # encoded message
            # requiered by python wrapping of gmail api
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
                .decode()

            create_message = {
                'raw': encoded_message
            }
            # pylint: disable=E1101
            send_message = (self.service.users().messages().send
                            (userId="me", body=create_message).execute())
            print(f'Message Id: {send_message["id"]}')
        except HttpError as error:
            print(f'An error occurred: {error}')
            send_message = None
            return send_message

    def searh_messages(
            self,
            keywords=None,
            subject_keywords=None,
            max_pages=3,
            ):
        """
        Search for messages containing keywords
        Returns a dictionary of messages from first pages (controlled by max_pages) and token to query next page of messages
        """
        if (keywords or subject_keywords):
            q = ''
            if keywords:
                q += (' OR '.join(keywords))
            if subject_keywords:
                q += (' OR')
                q += (' OR '.join([f'subject:{keyword}' for keyword in subject_keywords]))
            messages = []
            for i in range(max_pages):
                query = self.service.users().messages().list(
                    userId='me', q=q)
                response = query.execute()
                messages.extend(response['messages'])
            return {'messages': messages, 'nextPageToken': response['nextPageToken']}
        else:
            raise ValueError('Keywords were not provided')
