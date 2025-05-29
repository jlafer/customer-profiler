from dotmap import DotMap
from datetime import datetime, timedelta

"""
This function prints selected properties of data structures such as arrays,
objects, DotMaps, and dictionaries. The caller can specify the properties
to print and the indentation level.
The function handles nested structures and prints the properties in a
human-readable format.
"""

def print_selected_properties(schema, label, obj, indent=2):
  """
  Prints selected properties of a data structure as documented in the schema.
  The function handles nested structures and prints the properties in a
  human-readable format.
  """
  if schema["type"] == "object":
    print(f"{' ' * indent}{label}{{")
    for prop, propSchema in schema["properties"].items():
      if prop in obj and propSchema["print"]:
        print_selected_properties(propSchema, f"{prop}: ", obj[prop], indent + 2)
    print(f"{' ' * indent}}}")
  elif schema["type"] == "array":
    print(f"{' ' * indent}{label}[")
    for item in obj:
      print_selected_properties(schema["items"], '', item, indent + 2)
    print(f"{' ' * indent}]")
  elif schema["type"] == "string":
    print(f"{' ' * indent}{label}'{obj}'")
  else:
    print(f"{' ' * indent}{label}{obj}")
  return

def transformRowsAndColsToObjects(records):
  """
  Transforms an object containing a list of columns and a list of rows into a list of objects.
  For example, if the input records are:
  {
    "columns": ["col1", "col2"],
    "rows": [
      [1, 2],
      [3, 4]
    ]
  }
  The output will be:
  [
    {"col1": 1, "col2": 2},
    {"col1": 3, "col2": 4}
  ]
  """
  objects = []
  for row in records["rows"]:
    obj = DotMap()
    for i, col in enumerate(records["cols"]):
      obj[col] = row[i]
    objects.append(obj)
  return objects

def makeDatesFromToday(long, short, lag):
  """
  Returns a dictionary with the start date of the previous month,
  plus the end dates for a long period and a short period,
  plus the dates that lag the end dates by two days.
  Return all dates as string properties of a DotMap object.
  """
  dates = DotMap()
  today = datetime.today()
  currMoStart = today.replace(day=1)
  prevMoEnd = currMoStart - timedelta(days=1)
  prevMoStart = prevMoEnd.replace(day=1)
  if (long == 'month'):
    endLong = currMoStart
  else:
    endLong = prevMoStart + timedelta(days=long)
  endLongLag = endLong + timedelta(days=lag)
  if (short == 'week'):
    endShort = prevMoStart + timedelta(days=7)
  else:
    endShort = prevMoStart + timedelta(days=short)
  endShortLag = endShort + timedelta(days=lag)
  dates.start_date = prevMoStart.strftime("%Y-%m-%d")
  dates.end_date_short = endShort.strftime("%Y-%m-%d")
  dates.end_date_short_lag = endShortLag.strftime("%Y-%m-%d")
  dates.end_date_long = endLong.strftime("%Y-%m-%d")
  dates.end_date_long_lag = endLongLag.strftime("%Y-%m-%d")
  return dates
