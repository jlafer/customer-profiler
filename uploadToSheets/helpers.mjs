import * as R from 'ramda';

export function getPathToData(data, source) {
  const dataPath = source.split('.');
  return R.path(dataPath, data);
}

export function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
