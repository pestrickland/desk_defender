"""`gdrive` provides functions to upload data using the Google Drive API."""

import argparse
import httplib2
import json
import os
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

# Scopes for credentials.
# If modifying these scopes, delete your previously saved credentials at
# ~/.credentials/drive-python-quickstart.json
SCOPES = "https://www.googleapis.com/auth/drive.file"
CLIENT_SECRET_FILE = "client_secret.json"
APPLICATION_NAME = "Desk Defender Image Processor"
FLAGS = argparse.ArgumentParser(parents=[tools.argparser], add_help=False)

def get_credentials():
    """Get valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid, the
    OAuth2 flow is completed to obtain the new credentials.

    Returns:
        `credentials`, the obtained credential.
    """
    home_dir = os.path.expanduser("~")
    credential_dir = os.path.join(home_dir, ".credentials")
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   "drive-python-quickstart.json")

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store)
        print("Storing credentials to " + credential_path)
    return credentials


def upload_to_drive(image, name, folder="PiCam"):
    """Upload image to Google Drive.

    Creates a Google Drive API service object and uploads the supplied image to
    the specified folder. If it doesn't exist, the folder will be created.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build("drive", "v3", http=http)

    query = ("mimeType = 'application/vnd.google-apps.folder' and "
             "name contains '{}'".format(folder))

    response = service.files.list(q=query, fields="files(id, name)").execute()

    if response.get("files", [])[0].get("name") == folder:
        # Get id of existing folder named `folder`.
        folder_id = response.get("files", [])[0].get("id")
    else:
        # Otherwise create a new folder and get its id.
        folder_metadata = {"name": "{}".format(folder),
                           "mimeType": "application/vnd.google-apps.folder"}
        folder_id = service.files().create(body=folder_metadata,
                                           fields="id").execute().get("id")

    upload = service.files().create(body={"name": name,
                                          "parents": [folder_id]},
                                    media_body=image,
                                    fields="id, name").execute()
    print(json.dumps(upload, sort_keys=True, indent=4))

    service.files().create(media_body=image).execute()
