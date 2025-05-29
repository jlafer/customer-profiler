import { readFile } from 'fs/promises';
import readline from 'readline';

export async function readFiles(folderName) {
  const data = {};
  let fileName = folderName + '/account.json';
  data.acct = await readJsonFile(fileName);
  return data;
}

export async function readJsonFile(filePath) {
  const fileContent = await readFile(filePath, { encoding: 'utf-8' });
  return JSON.parse(fileContent);
}

// create a readline interface for capturing user input
export const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

export function getUserInput(prompt) {
  return new Promise((resolve) => {
    rl.question(prompt, (answer) => {
      resolve(answer);
    });
  });
}