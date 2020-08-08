#Yadon keeps track of tables, which are stored in text files... it's slow, like Yadon...
#- "Keep it simple stupid"
#- Useful as a quick and dirty way to store data on drive if efficiency is not important
#- Keys and values are all strings
#- Each row is made up of the key followed by the row values, all separated by tabs
#- Tables are edited by simply rewriting the text file
#- Keep backups of tables in case writing fails for whatever reason!
#- When manually editing the text files, make sure the last line is empty (line break) so that appending will work properly

import sys, os
from collections import OrderedDict

#Reads a table and returns either a dictionary with the table data, or None if the table doesn't exist
def ReadTable(tablename):
    try:
        file = open("{}.txt".format(tablename), encoding="utf8")
    except FileNotFoundError:
        return None
    
    table = OrderedDict()
    filecontents = file.read()
    for line in filecontents.split("\n"):
        if line == "":
            continue
        entries = line.split("\t")
        key = entries[0]
        table[key] = entries[1:]
    
    return table

#Reads a row from a table given a key and returns the list of values
#Returns None if the table doesn't exist or the key doesn't exist in the table
def ReadRowFromTable(tablename, key):
    table = ReadTable(tablename)
    
    if table is None:
        return None
    elif str(key) not in table.keys():
        return None
    else:
        return table[str(key)]

#Writes a new table, or replaces a table if it exists already (use with caution!)
#Use OrderedDict instead of a normal dict if ordering is important
def WriteTable(tablename, table):
    if not isinstance(table, dict):
        raise TypeError("yadon.WriteTable: table parameter should be a dict")
    
    #for safety measure
    old = ReadTable(tablename)
    
    #Can happen occasionally if tables are being edited very quickly
    try:
        file = open("{}.txt".format(tablename), "w", encoding="utf8")
    except OSError:
        raise
    
    #For whatever reason if writing fails, write the old table back
    try:
        for key in table.keys():
            values = [str(x) for x in table[key]]
            file.write("\t".join([str(key)] + values) + "\n")
        file.close()
    except Exception as e:
        WriteTable(tablename, old)
        raise

#Writes a row to a table only if the key doesn't exist yet (use AppendValuesToRow if this check is unwanted)
#Returns 0 if successful, -1 if not (key already exists)
#Appends to text file instead of rewriting the whole file, which should be faster
def AppendRowToTable(tablename, key, values):
    if not isinstance(values, list):
        raise TypeError("yadon.AppendRowToTable: values parameter should be a list")
    
    table = ReadTable(tablename)
    
    if table is None:
        WriteTable(tablename, {key:values})
    elif str(key) in table.keys():
        return -1
    else:
        file = open("{}.txt".format(tablename), "a", encoding="utf8")
        file.write("\t".join([str(key)] + [str(x) for x in values]) + "\n")
        file.close()
        return 0

#Writes a row to a table
#Creates a new table if it doesn't exist yet
#Replaces the row's values if the key already exists in the table
def WriteRowToTable(tablename, key, values):
    if not isinstance(values, list):
        raise TypeError("yadon.WriteRowToTable: values parameter should be a list")
    
    table = ReadTable(tablename)
    
    #if table doesn't exist yet
    if table is None:
        WriteTable(tablename, {key:values})
    #if row doesn't exist in table yet
    elif str(key) not in table.keys():
        AppendRowToTable(tablename, key, values)
    else:
        table[str(key)] = values
        WriteTable(tablename, table)

#Appends a value to a row in a table
#Creates a new table if it doesn't exist yet
#Creates a new row if the key doesn't exist in the table yet
def AppendValueToRow(tablename, key, value):
    table = ReadTable(tablename)
    
    #if table doesn't exist yet
    if table is None:
        WriteTable(tablename, {key:[value]})
    #if row doesn't exist in table yet
    elif str(key) not in table.keys():
        AppendRowToTable(tablename, key, [value])
    else:
        table[str(key)].append(value)
        WriteTable(tablename, table)

#Appends a list of values to a row in a table
#Creates a new table if it doesn't exist yet
#Creates a new row if the key doesn't exist in the table yet
def AppendValuesToRow(tablename, key, values):
    if not isinstance(values, list):
        raise TypeError("yadon.AppendValuesToRow: values parameter should be a list")
    
    table = ReadTable(tablename)
    
    #if table doesn't exist yet
    if table is None:
        WriteTable(tablename, {key:values})
    #if row doesn't exist in table yet
    elif str(key) not in table.keys():
        AppendRowToTable(tablename, key, values)
    else:
        table[str(key)] += values
        WriteTable(tablename, table)

#Removes a row from a table
#Returns 0 if successful, -1 if not (nonexistent table or key)
def RemoveRowFromTable(tablename, key):
    table = ReadTable(tablename)
    
    #if table doesn't exist
    if table is None:
        return -1
    #if row doesn't exist in table
    elif str(key) not in table.keys():
        return -1
    else:
        del table[str(key)]
        WriteTable(tablename, table)
        return 0

#Removes a value from a row in a table
#If there are identical values in the row, the first one is removed
#Returns 0 if successful, -1 if not (nonexistent table or key, or value not in row)
def RemoveValueFromRow(tablename, key, value):
    table = ReadTable(tablename)
    
    #if table doesn't exist
    if table is None:
        return -1
    #if row doesn't exist in table
    elif str(key) not in table.keys():
        return -1
    #if key doesn't exist in row
    elif str(value) not in table[str(key)]:
        return -1
    else:
        table[str(key)].remove(str(value))
        WriteTable(tablename, table)
        return 0