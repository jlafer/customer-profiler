# customer-profiler
This utility consists of two programs: `customer-profiler.py` for downloading selected Twilio account data from the Presto DB platform and `uploadToSheets.mjs` for uploading the data into a Google Sheets worksheet. This data is useful for quickly understanding key aspects of how the customer uses Twilio services.

## customer-profiler.py
The data downloading program uses a Python-based SQL interface to Twilio's Presto DB platform. This interface uses the Odin data gateway to access tables in the "Hive" data catalog. It downloads data and writes it to an `account.json` file in a folder of your choice.

### Authentication
The Odin gateway allows access using your Twilio Single Signon (SSO) username and password, which must be configured into the `.env` file in the parent project folder.

You must be connected to the Twilio network via the GlobalProtect VPN to execute the program.

### Authorization
Running the program also requires read-only permissions on a set of tables. The list of tables includes:
- billable_item_metadata_alex
- counters_by_billable_item_complete
- counters_by_subaccount
- currency_exchange_rates
- messaging_services
- providers
- rawpii_accounts
- rawpii_calls
- rawpii_phone_numbers
- redacted_voice_insights_call_summary_lite
- short_codes
- stored_value_transactions

You must request access to these tables via the Twilio Service Portal, opening a ticket in the `Information Technology` catalog, the `Applications & Access` category, and the `Request Access to Data Analytics Apps` item.

Select `Presto` as the "application you need help with." Choose `Production` as the "Presto Environment for your request." Select the Option `Permission and Access Management`.

If you know of another user that has the required permissions for the `customer-profiler` program, you can clone their permissions by selecting `Clone an Existing Users Access` as the Request Type.

If not, you will need to submit a separate request for each table by selecting `Request Access to Table` for the Request Type each time. You will then select the `public` schema and then press the "Search Tables" button to refresh the list of tables in the pick-list. Once refreshed, use the "Select Table" control to select a table name from the list above. Once selected, press the "Search Permissions" button to refresh the list of permissions for the table and then select the desired one, which usually says something about "read only" or "SOX" permissions. 

For the "Business Justification" you can say something like, "I am a Twilio SE and I am analyzing customer usage of our products."

### Deployment
To provide a controlled Python execution environment, some mechanism is needed. There are various approaches and it differs by O/S. For Macintosh, you can use tools like `venv` and `pipenv`. If you know Python well, you probably have it handled. If not, on a Macintosh you can do the following:

- Install `pipenv`
```
pip3 install pipenv --user
```

- Add the pipenv folder to your PATH variable.

- Upgrade pipenv
```
pip install --user --upgrade pipenv
```

- Enter the pipenv virtual environment (in the project directory)
```
pipenv shell
```

### Configuration
Copy `.env.example` to `.env` and edit the variables to give them your actual values.

### Execution
In the parent project folder, after setting up your Python (v3) execution environment, as described above, execute the following command line to run the data download for an account. The folder path is where the output files will be written and should already exist. For an ISV, supply the parent account SID. 

`python <acctSid> <folderPath>`

## uploadToSheets.mjs
The data-uploading program uses the Google Sheets API to write the data to a set of tabs in a Google worksheet.

### Client Credentials
The program requires Google OAuth 2.0 client credentials to access your Google Drive to create a Sheets worksheet file. If the SE leadership has arranged for Twilio IT to set up these credentials, you can request a copy from them or another SE who has them. If not, or you want to create your own, you can do so by following the instructions in the `GOOGLE_CREDENTIALS_INSTALL` markdown file. In either case, you will need to have the `client_secret.json` file installed in the `uploadToSheets` folder before you run the program.

### Execution
In the `uploadToSheets` subfolder, execute the following command line to run the upload.
`node uploadToSheets.mjs <worksheet-name> <folderPath>`

The worksheet name is the name that will be used to create the Sheets file in the root of your Google Drive.
The folder path points to the folder that contains the downloaded files written by `customer-profiler.py`.

### Authentication and Authorization with Google
If you have not previously authenticated with Google and authorized the program to access the Drive and Sheets APIs, the program will open your default browser and navigate to Google to complete those steps.

When you authorize the program for the `drive.file` and `spreadsheets` resource scopes, the browser tab will be redirected to your `localhost` and nothing will be shown. However, the URL will contain a `code` query parameter, which you must copy for use back in the program command line prompt. Here's what the URL will look like:

http://localhost/?code=<auth-code>&scope=https://www.googleapis.com/auth/drive.file%20https://www.googleapis.com/auth/spreadsheets

Copy just the `<auth-code>` value and paste it into the prompt back in the terminal window.

The result of successful authentication and authorization is a `token.json` file that the program saves in the `uploadToSheets` subfolder. It will be used for authorization going forward (until the token expires, in which case you should delete the file and re-run the program).

Next, the program will look for the named spreadsheet file in the root folder of your Twilio Google Drive. It will overwrite its contents if found. If not found, it will create a new one. The program writes progress messages to the terminal as it reads the input files and writes them into the spreadsheet. When the program finishes execution, the spreadsheet will be ready to review.