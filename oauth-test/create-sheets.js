const fs = require('fs');
const path = require('path');
const readline = require('readline');
const { google } = require('googleapis');
const open = require('open');

// OAuth 2.0 scopes needed for Google Drive and Sheets
const SCOPES = [
  'https://www.googleapis.com/auth/drive.file',
  'https://www.googleapis.com/auth/spreadsheets'
];

// Path to store token
const TOKEN_PATH = path.join(__dirname, 'token.json');
// Path to store credentials
const CREDENTIALS_PATH = path.join(__dirname, 'credentials.json');

// Create readline interface for user input
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

/**
 * Create a new spreadsheet in Google Drive root folder
 */
async function main() {
  try {
    console.log('Starting Google Sheets creation utility...');
    
    // Load client credentials
    let credentials;
    try {
      credentials = JSON.parse(fs.readFileSync(CREDENTIALS_PATH, 'utf8'));
    } catch (err) {
      console.error('Error loading client credentials file:');
      console.error('1. Go to https://console.cloud.google.com/');
      console.error('2. Create a project and enable the Google Drive and Google Sheets APIs');
      console.error('3. Create OAuth 2.0 credentials and download as credentials.json');
      console.error('4. Place credentials.json in the same directory as this script');
      process.exit(1);
    }

    // Create OAuth2 client
    const { client_secret, client_id, redirect_uris } = credentials.installed || credentials.web;
    const oAuth2Client = new google.auth.OAuth2(client_id, client_secret, redirect_uris[0]);

    // Check if we have stored token
    let token;
    try {
      token = JSON.parse(fs.readFileSync(TOKEN_PATH, 'utf8'));
      oAuth2Client.setCredentials(token);
      await createSpreadsheet(oAuth2Client);
    } catch (err) {
      // No stored token, get a new one
      await getNewToken(oAuth2Client);
    }
  } catch (error) {
    console.error('Error occurred:', error);
  } finally {
    rl.close();
  }
}

/**
 * Get and store new token after prompting for user authorization
 * @param {OAuth2Client} oAuth2Client The OAuth2 client to get token for
 */
async function getNewToken(oAuth2Client) {
  const authUrl = oAuth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
  });
  
  console.log('Authorize this app by visiting this URL:');
  console.log(authUrl);
  
  // Open the authorization URL in the default browser
  await open(authUrl);
  
  // Get the authorization code from the user
  const code = await new Promise((resolve) => {
    rl.question('Enter the code from that page here: ', (code) => {
      resolve(code);
    });
  });

  // Exchange the authorization code for tokens
  try {
    const { tokens } = await oAuth2Client.getToken(code);
    oAuth2Client.setCredentials(tokens);
    
    // Store the token for future use
    fs.writeFileSync(TOKEN_PATH, JSON.stringify(tokens));
    console.log('Token stored to', TOKEN_PATH);
    
    // Create a spreadsheet with the authenticated client
    await createSpreadsheet(oAuth2Client);
  } catch (err) {
    console.error('Error retrieving access token:', err);
    process.exit(1);
  }
}

/**
 * Create a new Google Sheets spreadsheet
 * @param {OAuth2Client} auth An authorized OAuth2 client
 */
async function createSpreadsheet(auth) {
  // Get the spreadsheet name from user
  const sheetName = await new Promise((resolve) => {
    rl.question('Enter the name for the new spreadsheet: ', (name) => {
      resolve(name || 'Untitled Spreadsheet');
    });
  });

  // Create Sheets instance
  const sheets = google.sheets({ version: 'v4', auth });
  
  try {
    // Create a new spreadsheet
    const spreadsheet = await sheets.spreadsheets.create({
      requestBody: {
        properties: {
          title: sheetName
        }
      }
    });
    
    const spreadsheetId = spreadsheet.data.spreadsheetId;
    const spreadsheetUrl = spreadsheet.data.spreadsheetUrl;
    
    console.log(`Success! Spreadsheet created with ID: ${spreadsheetId}`);
    console.log(`URL: ${spreadsheetUrl}`);
    
    // The created spreadsheet is automatically in the user's root Drive folder
    console.log('The spreadsheet has been created in your Google Drive root folder');
    
    return spreadsheetId;
  } catch (err) {
    console.error('Error creating spreadsheet:', err);
    throw err;
  }
}

// Run the program
main();