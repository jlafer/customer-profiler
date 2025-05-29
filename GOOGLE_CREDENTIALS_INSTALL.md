# Google Credentials Install Instructions
For Twilio SEs to use the `uploadToSheets` program, Google Cloud's authentication system requires that it have access to the "client credentials" for a Google Cloud Project. Those can be created in the Google Cloud console. There are two choices for creation and ownership of the project, consent screen and credentials: either each SE can create their own for use within their own Google account or an IT administrator for Twilio's Google Cloud Organization (twilio.com) can create them and share the credentials with any SE who wants to use the program.

This document provides instructions for SEs who want to create their own Project, Consent Screen and Client Credentials. It also covers the installation of the credentials file in the project folder structure.

## Background on Google OAuth
The `uploadToSheets` program uses two Google Workspace APIs -- Drive and Sheets -- to manipulate the user's worksheet output file. On execution, the program must authenticate the user and gain authorization from the user to access their Google Drive. For this, the program relies on Google's OAuth 2.0 facilities. Google requires that the program be associated with a Google Cloud Project and asociated Consent Screen. Further, the program must present its own OAuth 2.0 client credentials to the Google Authentication server before Google OAuth will allow the user to be authenticated. All of these OAuth artifacts are created in the Google Cloud console. Here are the steps.

## Create and Install OAuth Credentials
1. Create a Google Cloud Project (or use an existing one)
- Go to the [Google Cloud Console](https://console.cloud.google.com/):
  - Create a new Project.
  - Under "APIs & Services" > "Enabled APIs & services", enable the Google Sheets API and the Google Drive API.

2. Configure an OAuth Consent Screen
- Go to "APIs & Services" > "OAuth consent screen".
- Fill in the required fields (App name, User support email, Developer contact information, etc.).
- Choose "Internal" for the audience user type.
- Add the necessary scopes:
  - auth/spreadsheets
  - auth/drive.file
- For production use, publish the app (this requires review by Google since it is using a sensitive scope, auth/spreadsheets). For personal use, there should be no need to publish the application.

3. Create OAuth 2.0 Client Credentials
- Go to APIs & Services > Credentials.
- Click Create Credentials > OAuth client ID.
- Choose "Desktop App" for the Application type.
- Give the client a name.
- Click on the "Create" button.
- Back on the Credentials list page, click on the download icon for the new client to download the `client_secret_<your_id>.json` file.
  - This file contains the program's Client ID and Client Secret.
## Install the Credentials
- Rename the file to `client_secret.json` and move it to the `uploadToSheets` subfolder of this project repository.