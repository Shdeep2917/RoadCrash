'''
import requests
import pandas as pd

url = "https://data.opencity.in/api/3/action/package_show"
params = {
    "id": "delhi-road-crashes-data"
}


response = requests.get(url, params=params)

data = response.json()

resources = data["result"]["resources"]
df = pd.DataFrame(resources)

print(df)

print("\nTOTAL RESOURCES:", len(resources))

for i, resource in enumerate(resources, start=1):

    print("\n------------------------------")
    print("TABLE:", i)
    print("NAME:", resource.get("name"))
    print("ID:", resource.get("id"))
    print("FORMAT:", resource.get("format"))
    print("------------------------------")


# -----------------------------------------
# 3. Access every table
# -----------------------------------------

tables = {}

for i, resource in enumerate(resources, start=1):

    resource_id = resource["id"]
    resource_name = resource.get("name", f"Table_{i}")

    print(f"\nLoading: {resource_name}")

    api_url = "https://data.opencity.in/api/3/action/datastore_search"

    params = {
        "resource_id": resource_id,
        "limit": 5000
    }

    response = requests.get(api_url, params=params)

    if response.status_code != 200:
        print("Could not access:", resource_name)
        continue

    result = response.json()

    if not result["success"]:
        print("Datastore unavailable:", resource_name)
        continue

    records = result["result"]["records"]

    # Convert API data into Pandas DataFrame
    df = pd.DataFrame(records)

    # Store DataFrame
    tables[resource_name] = df

    print("Rows:", len(df))
    print("Columns:", list(df.columns))


# -----------------------------------------
# 4. Show all loaded tables
# -----------------------------------------

print("\n\n==============================")
print("ALL LOADED TABLES")
print("==============================")

for name, df in tables.items():

    print("\nTABLE:", name)

    print(df)

    print("\nShape:", df.shape)
'''


import requests
import pandas as pd


# ==========================================================
# 1. Get dataset information
# ==========================================================

url = "https://data.opencity.in/api/3/action/package_show"

params = {
    "id": "delhi-road-crashes-data"
}

response = requests.get(url, params=params)

if response.status_code != 200:
    print("Could not access dataset")
    exit()

data = response.json()

if not data["success"]:
    print("Dataset unavailable")
    exit()


# ==========================================================
# 2. Get all resources / tables
# ==========================================================

resources = data["result"]["resources"]

print("\nTOTAL RESOURCES:", len(resources))

for i, resource in enumerate(resources, start=1):

    print("\n------------------------------")
    print("TABLE:", i)
    print("NAME:", resource.get("name"))
    print("ID:", resource.get("id"))
    print("FORMAT:", resource.get("format"))
    print("------------------------------")


# ==========================================================
# 3. Download every table completely
# ==========================================================

tables = {}

for i, resource in enumerate(resources, start=1):

    resource_id = resource.get("id")
    resource_name = resource.get("name") or f"Table_{i}"

    print("\n======================================")
    print("Loading:", resource_name)
    print("======================================")

    api_url = "https://data.opencity.in/api/3/action/datastore_search"

    all_records = []

    limit = 5000
    offset = 0

    while True:

        params = {
            "resource_id": resource_id,
            "limit": limit,
            "offset": offset
        }

        response = requests.get(api_url, params=params)

        if response.status_code != 200:
            print("Could not access:", resource_name)
            break

        result = response.json()

        if not result.get("success"):
            print("Datastore unavailable:", resource_name)
            break

        records = result["result"]["records"]

        # No more records
        if not records:
            break

        # Add records to this table
        all_records.extend(records)

        print("Loaded:", len(all_records), "rows")

        # If less than 5000 were returned,
        # this is the last batch
        if len(records) < limit:
            break

        offset += limit

    # ======================================================
    # Convert THIS table into its own DataFrame
    # ======================================================

    df = pd.DataFrame(all_records)

    # Store separately
    tables[resource_name] = df

    print("\nDataFrame created")
    print("Table:", resource_name)
    print("Rows:", len(df))
    print("Columns:", list(df.columns))


# ==========================================================
# 4. Show all DataFrames
# ==========================================================

print("\n\n")
print("======================================================")
print("              ALL LOADED DATAFRAMES")
print("======================================================")


for name, df in tables.items():

    print("\n\n---------------------------------------------")
    print("DATAFRAME:", name)
    print("---------------------------------------------")

    print(df)

    print("\nShape:", df.shape)

'''
# ==========================================================
# 5. SAVE ALL DATAFRAMES INTO MYSQL
# ==========================================================

import mysql.connector
import re

# ----------------------------------------------------------
# Connect to MySQL
# ----------------------------------------------------------

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""
)

cursor = connection.cursor()

# ----------------------------------------------------------
# Create database
# ----------------------------------------------------------

cursor.execute("CREATE DATABASE IF NOT EXISTS road_crashes")

# Select database
cursor.execute("USE road_crashes")

print("\n======================================================")
print("CONNECTED TO MYSQL")
print("Database: road_crashes")
print("======================================================")


# ----------------------------------------------------------
# Function to clean table name
# ----------------------------------------------------------

def clean_table_name(name):

    # Replace spaces and special characters with _
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)

    # Make lowercase
    name = name.lower()

    return name


# ----------------------------------------------------------
# Save every DataFrame
# ----------------------------------------------------------

for name, df in tables.items():

    table_name = clean_table_name(name)

    print("\nSaving table:", table_name)
        # Check whether DataFrame has columns
    if df.empty and len(df.columns) == 0:
        print("Skipping:", table_name)
        print("Reason: DataFrame has no columns.")
        continue

    if len(df.columns) == 0:
        print("Skipping:", table_name)
        print("Reason: No columns available.")
        continue

    # ---------------------------------------------
    # Create columns
    # ---------------------------------------------

    columns = []

    for column in df.columns:

        column_name = clean_table_name(str(column))

        # Store everything as TEXT initially
        columns.append(f"`{column_name}` TEXT")

    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{table_name}` (
        {", ".join(columns)}
    )
    """

    cursor.execute(create_table_query)

    # ---------------------------------------------
    # Insert data
    # ---------------------------------------------

    column_names = [
        clean_table_name(str(column))
        for column in df.columns
    ]

    column_string = ", ".join(
        f"`{column}`"
        for column in column_names
    )

    placeholders = ", ".join(
        ["%s"] * len(column_names)
    )

    insert_query = f"""
    INSERT INTO `{table_name}`
    ({column_string})
    VALUES ({placeholders})
    """

    # Convert DataFrame rows into tuples
    for row in df.itertuples(index=False, name=None):

        # Convert NaN to None
        row = tuple(
            None if pd.isna(value) else str(value)
            for value in row
        )

        cursor.execute(insert_query, row)

    connection.commit()

    print(
        "Successfully saved:",
        len(df),
        "rows"
    )


'''

# ==========================================================
# 6. SAVE ALL DATAFRAMES INTO EXCEL
# ==========================================================

import re

excel_file = "Road_Crashes_Data.xlsx"

with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:

    for name, df in tables.items():

        # Excel sheet names cannot contain these characters
        sheet_name = re.sub(r'[\\/*?:\[\]]', '_', str(name))
        sheet_name = sheet_name.strip("'")[:31] or "Sheet"

        # Ensure sheet names are unique
        original_name = sheet_name
        count = 1

        while sheet_name in writer.sheets:
            suffix = f"_{count}"
            sheet_name = original_name[:31 - len(suffix)] + suffix
            count += 1

        # Save each DataFrame in its own worksheet
        df.to_excel(
            writer,
            sheet_name=sheet_name,
            index=False
        )

        print(f"Saved worksheet: {sheet_name}")

print("\nExcel file created successfully!")
print("File name:", excel_file)
print("Location: Current working directory")

print("\n======================================================")
print("ALL DATA SAVED SUCCESSFULLY!")
print("======================================================")
