/*
  This program reads an account.json file from a specified folder and uploads
  its contents to the specified Google Sheets document in the user's G-Drive
  root folder.

  The Google Sheets file name is passed as the first command line argument.
  The path name of the folder is passed as the second command line argument.
  The Google account credentials are stored in the credentials.json file.
*/

import dotenv from 'dotenv';
import path from 'path';

import { readFiles, readJsonFile } from './files.mjs';
import { getPathToData } from './helpers.mjs';
import {
  getDriveApi, getSheetsApi, getOrAddSpreadsheet,
  getAllSheets, getOrAddSheet1, addSheet, deleteAllSheetsBut1, deleteSheet, setSheetProperties,
  setColumnFormat, wrapTextInRange, position, range, makeCellValue,
  setColumnOfStrings, setColumnOfValues, setRowOfStrings, setRowsOfValues
} from './sheets.mjs';
import { getAuthorizedClient } from './auth.mjs';
dotenv.config();

const [, , spreadsheetName, folderName] = process.argv;

const credentialsPath = path.join('.', 'client_secret.json');

if (!spreadsheetName || !folderName) {
  console.error('Usage: node uploadToSheets.mjs <spreadsheetName> <folderName>');
  process.exit(1);
}

async function uploadToSheets(api, spreadsheetId, schema, data) {
  for (const tab of schema.tabs) {
    console.log(`Uploading data for tab: ${tab.name}`);
    const tabData = getPathToData(data, tab.source);
    if (!tabData) {
      continue;
    }
    if (tab.type === 'static') {
      const sheetName = tab.name;
      tab.bounds = { maxRow: 0, maxCol: 0 };
      await uploadDataToSheet(api, spreadsheetId, sheetName, tab, tabData);
    }
    else {
      for (const sheetData of tabData) {
        const sheetName = sheetData[tab.name];
        tab.bounds = { maxRow: 0, maxCol: 0 };
        console.log(`Uploading data for sheet: ${sheetName}`);
        await uploadDataToSheet(api, spreadsheetId, sheetName, tab, sheetData);
      }
    }
  }
}

async function uploadDataToSheet(api, spreadsheetId, sheetName, tab, data) {
  const sheet = await addSheet(api, spreadsheetId, sheetName);
  const sheetId = sheet.data.replies[0].addSheet.properties.sheetId;

  for (const column of tab.columns) {
    await setColumnFormat(api, spreadsheetId, sheetId, column);
  }

  for (const section of tab.sections) {
    const sectionData = (section.source)
      ? data[section.source]
      : data;
    await uploadSection(api, spreadsheetId, sheetId, tab.bounds, section, sectionData);
  }
}

async function uploadSection(api, spreadsheetId, sheetId, bounds, section, sectionData) {
  if (section.style === 'list') {
    await uploadList(api, spreadsheetId, sheetId, bounds, section, sectionData);
  }
  else {
    await uploadTable(api, spreadsheetId, sheetId, bounds, section, sectionData);
  }
}

async function uploadList(api, spreadsheetId, sheetId, bounds, section, sectionData) {
  const labels = section.values.map((value) => value.label);
  await setColumnOfStrings(api, spreadsheetId, position(sheetId, bounds.maxRow, 0), labels, { bold: true });
  const cellValues = section.values.map((value) => makeCellValue(value, sectionData[value.field]));
  await setColumnOfValues(api, spreadsheetId, position(sheetId, bounds.maxRow, 1), cellValues);
  await wrapTextInRange(
    api,
    spreadsheetId,
    range(sheetId, { startRow: bounds.maxRow, startColumn: 0, endRow: bounds.maxRow + labels.length, endColumn: 2 })
  );
  bounds.maxRow += labels.length + 1;
  bounds.maxCol += 3;
}

async function uploadTable(api, spreadsheetId, sheetId, bounds, section, sectionData) {
  const allFields = section.keys.concat(section.values);
  const labels = allFields.map((fld) => fld.label);
  const endRow = bounds.maxRow + sectionData.length + 1;
  if (endRow > 1000) {
    setSheetProperties(api, spreadsheetId, sheetId, { gridProperties: { rowCount: endRow } });
  }
  const endColumn = bounds.maxCol + labels.length;
  await wrapTextInRange(
    api,
    spreadsheetId,
    range(sheetId, { startRow: bounds.maxRow, startColumn: bounds.maxCol, endRow, endColumn })
  );
  await setRowOfStrings(api, spreadsheetId, position(sheetId, bounds.maxRow++, 0), labels, { bold: true });
  bounds.maxCol += allFields.length + 1;
  let firstRow = 0;
  const numRowsInSection = sectionData.length;
  while (firstRow < numRowsInSection) {
    // get a batch of 50 rows
    const batchOfRows = sectionData.slice(firstRow, firstRow + 50);
    await setBatchOfRows(api, spreadsheetId, sheetId, allFields, bounds, batchOfRows);
    firstRow += 50;
  }
  bounds.maxRow += 1;
}

async function setBatchOfRows(api, spreadsheetId, sheetId, allFields, bounds, rows) {
  const cellValues = rows
    .map(dataRow => makeRowOfCellValues(allFields, dataRow));
  await setRowsOfValues(api, spreadsheetId, position(sheetId, bounds.maxRow, 0), cellValues);
  bounds.maxRow += rows.length;
}

function makeRowOfCellValues(fields, dataRow) {
  const cellValues = fields.map((field) => {
    const value = dataRow[field.field];
    const cellValue = makeCellValue(field, value);
    return cellValue;
  });
  return cellValues;
}

async function main() {
  try {
    const schema = await readJsonFile('report-schema.json');
    const data = await readFiles(folderName);
    const oAuth2Client = await getAuthorizedClient(credentialsPath);
    const drive = getDriveApi(oAuth2Client);
    const sheets = getSheetsApi(oAuth2Client);
    const spreadsheetId = await getOrAddSpreadsheet(drive, sheets, spreadsheetName);
    const sheetInfo = await getAllSheets(sheets, spreadsheetId);
    const sheet1id = await getOrAddSheet1(sheets, spreadsheetId, sheetInfo);
    await deleteAllSheetsBut1(sheets, spreadsheetId, sheetInfo);
    await uploadToSheets(sheets, spreadsheetId, schema, data);
    await deleteSheet(sheets, spreadsheetId, sheet1id);
    console.log('Data uploaded successfully.');
  } catch (error) {
    console.error('Error:', error);
  }
}

main();