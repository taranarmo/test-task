# Steps to enable gmail API

1. Open Google cloud console and enable API (and create project if none exists) at https://console.cloud.google.com/flows/enableapi?apiid=gmail.googleapis.com
1. (Optional) Add consent screen to your app
1. Authorize credentials for desktop app at https://console.cloud.google.com/apis/credentials (described in details at https://developers.google.com/gmail/api/quickstart/python)
1. Put credentials.json file in the directory with `gmail_api.py`

After that API is enabled and you need to add users to list of test users to get access to it (if app is not published).
