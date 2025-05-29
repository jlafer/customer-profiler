import { google } from 'googleapis';

import { delay } from './helpers.mjs';

export function getDriveApi(oAuth2Client) {
  const drive = google.drive({ version: 'v3', auth: oAuth2Client });
  return drive;
}

export function getSheetsApi(oAuth2Client) {
  const sheets = google.sheets({ version: 'v4', auth: oAuth2Client });
  return sheets;
}

export async function getOrAddSpreadsheet(drive, sheets, spreadsheetName) {
  try {
    const spreadsheetId = await getSpreadsheetIdIfExists(drive, spreadsheetName);
    console.log(`Spreadsheet ID: ${spreadsheetId}`);
    return spreadsheetId;
  } catch (error) {
    if (error.message.includes('not found')) {
      console.log(`Spreadsheet with name ${spreadsheetName} not found. Creating a new one.`);
      const spreadsheetId = await createSpreadsheet(sheets, spreadsheetName);
      console.log(`Spreadsheet created with ID: ${spreadsheetId}`);
      console.log('The spreadsheet has been created in your Google Drive root folder');
      return spreadsheetId;
    } else {
      console.error('Error getting spreadsheet ID:', error);
      throw error;
    }
  }
}

/**
 * Checks if a Google Sheets file exists by name and returns its ID
 * @param {OAuth2Client} oAuth2Client - Authenticated OAuth2 client
 * @param {string} fileName - Name of the Google Sheets file to find
 * @returns {Promise<string|null>} - Spreadsheet ID if found, null otherwise
 */
export async function getSpreadsheetIdIfExists(drive, fileName) {
  const response = await drive.files.list({
    q: `name='${fileName}' and mimeType='application/vnd.google-apps.spreadsheet'`,
    fields: 'files(id, name)',
    spaces: 'drive'
  });

  const files = response.data.files;
  if (files && files.length > 0) {
    return files[0].id;
  } else {
    // no matching file found
    throw new Error(`Spreadsheet with name ${fileName} not found`);
  }
}

export async function createSpreadsheet(sheets, spreadsheetName) {
  try {
    const spreadsheet = await sheets.spreadsheets.create({
      requestBody: {
        properties: {
          title: spreadsheetName
        }
      }
    });
    const spreadsheetId = spreadsheet.data.spreadsheetId;
    return spreadsheetId;
  } catch (err) {
    console.error('Error creating spreadsheet:', err);
    throw err;
  }
}

export async function getAllSheets(sheets, spreadsheetId) {
  return sheets.spreadsheets.get({
    spreadsheetId,
  }).then(async (response) => {
    const sheetInfo = response.data.sheets.map((sheet) => {
      return {
        id: sheet.properties.sheetId,
        title: sheet.properties.title,
        gridProperties: sheet.properties.gridProperties,
      };
    });
    return sheetInfo;
  });
}

export async function getOrAddSheet1(sheets, spreadsheetId, sheetInfo) {
  const sheet1 = sheetInfo.find((sheet) => sheet.title === 'Sheet1');
  if (sheet1) {
    return sheet1.id;
  } else {
    const newSheet = await addSheet(sheets, spreadsheetId, 'Sheet1');
    return newSheet.data.replies[0].addSheet.properties.sheetId;
  }
}

export function addSheet(sheets, spreadsheetId, title) {
  return sheets.spreadsheets.batchUpdate({
    spreadsheetId,
    resource: {
      requests: [
        {
          addSheet: {
            properties: {
              title,
            },
          },
        },
      ],
    },
  });
}

export function deleteAllSheetsBut1(sheets, spreadsheetId, sheetInfo) {
  const sheet1 = sheetInfo.find((sheet) => sheet.title === 'Sheet1');
  const sheetsToDelete = (!!sheet1)
    ? sheetInfo.filter((sheet) => sheet.id !== sheet1.id)
    : sheetInfo;
  if (sheetsToDelete.length === 0) {
    return Promise.resolve();
  }
  const sheetIdsToDelete = sheetsToDelete.map((sheet) => sheet.id);
  const requests = sheetIdsToDelete.map((sheetId) => ({
    deleteSheet: {
      sheetId,
    },
  }));
  return sheets.spreadsheets.batchUpdate({
    spreadsheetId,
    resource: {
      requests,
    },
  });
}

export async function deleteSheet(sheets, spreadsheetId, sheetId) {
  return sheets.spreadsheets.batchUpdate({
    spreadsheetId,
    resource: {
      requests: [
        {
          deleteSheet: {
            sheetId,
          },
        },
      ],
    },
  });
}

export async function setSheetProperties(sheets, spreadsheetId, sheetId, properties) {
  const requests = [
    {
      updateSheetProperties: {
        properties: {
          sheetId,
          ...properties,
        },
        fields: 'gridProperties.rowCount',
      },
    },
  ];
  const batchUpdateRequest = { requests };
  await sheets.spreadsheets.batchUpdate({
    spreadsheetId,
    resource: batchUpdateRequest,
  });
}

export function position(sheetId, rowIndex, columnIndex) {
  return { sheetId, rowIndex, columnIndex };
}

export function range(sheetId, spec) {
  const { startRow, startColumn, endRow, endColumn } = spec;
  const obj = {
    sheetId,
    startRowIndex: 0,
    startColumnIndex: 0
  }
  if (startRow) {
    obj.startRowIndex = startRow;
  }
  if (startColumn) {
    obj.startColumnIndex = startColumn;
  }
  if (endRow) {
    obj.endRowIndex = endRow;
  }
  if (endColumn) {
    obj.endColumnIndex = endColumn;
  }
  return obj;
}

export async function setRowOfStrings(sheets, spreadsheetId, start, rowValues, format) {
  const formatObj = {
    textFormat: format
  };
  const row = {
    values: rowValues.map((value) => {
      return {
        userEnteredValue: {
          stringValue: value,
        },
        userEnteredFormat: formatObj,
      };
    }),
  };
  await setCells(sheets, spreadsheetId, start, [row]);
}

export async function setRowOfValues(sheets, spreadsheetId, start, cellValues) {
  const row = {
    values: cellValues
  };
  await setCells(sheets, spreadsheetId, start, [row]);
}

export async function setColumnOfStrings(sheets, spreadsheetId, start, columnValues, format) {
  const formatObj = {
    textFormat: format
  };
  const rows = columnValues.map((value) => {
    return {
      values: [
        {
          userEnteredValue: {
            stringValue: value,
          },
          userEnteredFormat: formatObj,
        },
      ],
    };
  });
  await setCells(sheets, spreadsheetId, start, rows);
}

export async function setColumnOfValues(sheets, spreadsheetId, start, cellValues) {
  const rows = cellValues.map((cellValue) => {
    return {
      values: [cellValue],
    };
  });
  await setCells(sheets, spreadsheetId, start, rows);
}

export async function setRowsOfValues(sheets, spreadsheetId, start, cellValues) {
  const rows = cellValues.map((rowData) => {
    return {
      values: rowData
    };
  });
  await setCells(sheets, spreadsheetId, start, rows);
}

export function makeCellValue(valueDefn, data) {
  switch (valueDefn.type) {
    case 'STRING':
      return makeStringCellValue(valueDefn, data);
    case 'NUMBER':
    case 'CURRENCY':
    case 'PERCENT':
      return makeNumberCellValue(valueDefn, data);
    case 'DATE':
    case 'DATE_TIME':
    case 'TIME':
      return makeDateCellValue(valueDefn, data);
    default:
      throw new Error(`Unsupported type: ${valueDefn.type}`);
  }
}

function makeStringCellValue(valueDefn, data) {
  const userEnteredValue = { stringValue: data };
  const userEnteredFormat = { textFormat: {} };
  if (valueDefn.bold) {
    userEnteredFormat.textFormat.bold = true;
  }
  return {
    userEnteredValue,
    userEnteredFormat
  };
}

function makeNumberCellValue(valueDefn, data) {
  const userEnteredValue = { numberValue: data };
  const userEnteredFormat = { numberFormat: { type: valueDefn.type } };
  if (valueDefn.pattern) {
    userEnteredFormat.numberFormat.pattern = valueDefn.pattern;
  }
  if (valueDefn.bold) {
    userEnteredFormat.textFormat = { bold: true };
  }
  const cellValue = {
    userEnteredValue,
    userEnteredFormat
  };
  return cellValue;
}

function dateToSerial(date) {
  return (date.getTime() / 1000 / 86400) + 25569;
}

function makeDateCellValue(valueDefn, data) {
  if (!data) {
    return {
      userEnteredValue: { numberValue: null },
      userEnteredFormat: { numberFormat: { type: 'DATE' } }
    };
  }
  const validDateString = data.replace(/ /, 'T');
  const date = Date.parse(validDateString);
  const dateSerial = dateToSerial(new Date(date));
  return makeNumberCellValue(valueDefn, dateSerial);
}

async function setCells(sheets, spreadsheetId, start, rowValues) {
  // append cells to the end of the sheet
  const requests = [
    {
      updateCells: {
        rows: rowValues,
        start,
        fields: 'userEnteredValue, userEnteredFormat(numberFormat,textFormat)',
      }
    }
  ];
  await delay(1500);
  const batchUpdateRequest = { requests: requests };
  sheets.spreadsheets.batchUpdate({
    spreadsheetId: spreadsheetId,
    resource: batchUpdateRequest
  });
}

export async function wrapTextInRange(sheets, spreadsheetId, range) {
  const requests = [
    {
      repeatCell: {
        range,
        cell: {
          userEnteredFormat: {
            wrapStrategy: 'WRAP'
          }
        },
        fields: 'userEnteredFormat.wrapStrategy',
      }
    }
  ];
  await delay(1500);
  const batchUpdateRequest = { requests: requests };
  sheets.spreadsheets.batchUpdate({
    spreadsheetId: spreadsheetId,
    resource: batchUpdateRequest
  });
}

export async function setColumnFormat(sheets, spreadsheetId, sheetId, column) {
  const { width, index } = column;
  await delay(1500);
  await sheets.spreadsheets.batchUpdate({
    spreadsheetId,
    resource: {
      requests: [
        {
          updateDimensionProperties: {
            range: {
              sheetId: sheetId,
              dimension: 'COLUMNS',
              startIndex: index,
              endIndex: index + 1
            },
            properties: {
              pixelSize: width
            },
            fields: 'pixelSize'
          }
        }
      ]
    }
  });
};

export async function autoResizeColumns(sheets, spreadsheetId, sheetId, startColumn, endColumn) {
  const requests = [
    {
      autoResizeDimensions: {
        dimensions: {
          sheetId,
          dimension: 'COLUMNS',
          startIndex: 0,
          endIndex: 6
        }
      }
    }
  ];
  const batchUpdateRequest = { requests: requests };
  await delay(1500);
  await sheets.spreadsheets.batchUpdate({
    spreadsheetId: spreadsheetId,
    resource: batchUpdateRequest
  });
}