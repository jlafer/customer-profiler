import { google } from 'googleapis';
import path from 'path';
import fs from 'fs';

import { rl } from './files.mjs';
import open from 'open';

// OAuth 2.0 scopes needed for Google Drive and Sheets
const scopes = [
  'https://www.googleapis.com/auth/drive.file',
  'https://www.googleapis.com/auth/spreadsheets'
];

const tokenPath = path.join('.', 'token.json');

export async function getAuthorizedClient(credentialsPath) {
  let oAuth2Client;
  try {
    // load Google API credentials from a local file
    const content = await fs.promises.readFile(credentialsPath);
    const credentials = JSON.parse(content);

    // create an OAuth2 client with the given credentials
    const { client_secret, client_id, redirect_uris } = credentials.installed;
    oAuth2Client = new google.auth.OAuth2(client_id, client_secret, redirect_uris[0]);
  } catch (err) {
    console.log('Error authorizing the application with the client_secret.json file:', err);
    console.error('Error while loading and using the client credentials file:');
    console.error('1. Go to https://console.cloud.google.com/');
    console.error('2. Create a project and enable the Google Drive and Google Sheets APIs');
    console.error('3. Create an OAuth 2.0 consent screen of type Desktop app');
    console.error('4. Create OAuth 2.0 client credentials and download as client_secret.json');
    console.error('5. Place client_secret.json in the same directory as this script');
    process.exit(1);
  }

  let authorized = false;
  while (!authorized) {
    try {
      const content = await fs.promises.readFile(tokenPath, 'utf8');
      const token = JSON.parse(content);
      oAuth2Client.setCredentials(token);
      authorized = true;
    } catch (err) {
      await getNewToken(oAuth2Client);
    }
  }
  rl.close();
  return oAuth2Client;
}

async function getNewToken(oAuth2Client) {
  const authUrl = oAuth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: scopes,
  });
  
  console.log('Authorize this app by visiting this URL:');
  console.log(authUrl);
  
  // open the authorization URL in the user's default browser
  open(authUrl);
  
  // get the authorization code from the user, who must copy it from
  // the URL query parameter and paste it into the command line
  const code = await new Promise((resolve) => {
    rl.question('Enter the code from that page here: ', (code) => {
      resolve(code);
    });
  });

  try {
    // exchange the authorization code for a token
    const { tokens } = await oAuth2Client.getToken(code);
    
    // store the token for subsequent reading by the app
    const tokenPath = path.join('.', 'token.json');
    fs.writeFileSync(tokenPath, JSON.stringify(tokens));
    console.log('Token stored to', tokenPath);
  } catch (err) {
    console.error('Error retrieving access token:', err);
    process.exit(1);
  }
}
