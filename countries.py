# import libraries
import requests
import json
import psycopg2
import os
from config import url1
from config import url2
from dotenv import load_dotenv

# Fetch and merge country data from REST Countries API
def fetch_country_data(url1,url2):
    """Fetches and merges country metadata from two REST Countries API endpoints.

    It takes in two arguments which are the urls of the API whose data you want to fetch
    and returns the list of the fetched API data. It also persist the data from the API locally
    in a JSON file to avoid calling the API every single time.

    Parameters
    ---------------
        url1 (str): The first API URL containing fields like name, currencies, languages, and geopolitics.
        url2 (str): The second API URL containing fields such as area, population, and continents.
    
    Requirements
    ---------------
        requests must be installed in the Python environment.

    Returns
    ---------------
        list:
            A list of merged country dictionaries. Each item in the list represents one country,
            combining data from both responses into a unified structure.
    Notes
    ---------------
        This function uses two separate API calls to overcome field length restrictions,
        and merges them by matching records index-wise using the zip() function.
        If either API call fails, it returns an empty list to prevent ETL continuation.
        It also saves the called data in a JSON file.
    """

    try:
        response1 = requests.get(url1).json()
        response2 = requests.get(url2).json()
    except Exception as e:
        print("Failed to fetch data:", e)
    # Initialize an empty list to hold the merged data
    merged_data = []

    # Merge the two responses by iterating through both lists
    for country1, country2 in zip(response1, response2): 
    # Merge dictionaries for each country
        merged_country = {**country1, **country2} 
        merged_data.append(merged_country)
    
    # Save to JSON file
    with open('countries_raw.json', 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=4)

    print("Data saved to countries_raw.json")

    return merged_data

def load_country_data_from_json(json_path='countries_raw.json'):
    """Loads country metadata from a previously saved local JSON file.

    Parameters
    ---------------
        json_path (str, optional): Path to the JSON file containing cached country data. 
        Defaults to 'countries_raw.json' if no path is provided.

    Returns
    ---------------
        list: A list of country records in dictionary format, representing the raw merged data
        originally fetched from the REST Countries API.
    
    Notes
    ---------------
        This function is intended to provide a cached data source to avoid repeated API calls.
        Useful for offline development and faster pipeline execution when the data is already available locally.
    """
    try:
        # check if json file exists in path
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        else:
            print(f"JSON file {json_path} not found")
    except Exception as e:
        print(f"Failed to load JSON: {e}")

    return None

# Transform one country record into tuple matching table schema
def transform_country(country):
    """A function that transforms a single country record from the REST Countries API into a flattened tuple
    that matches the structure of the 'countries' SQL table.

    It takes in the list of dictionaries of the API data as an argument, extracts the necessary columns,
    while also carrying out the necessary transformations like replacing missing values with defaults
    like `Unknown` and `0`.

    parameters
    ---------------
        country (dict): A dictionary representing one country's metadata from the API.
        this dictionary may contain nested keys for name, currencies, capital cities,
        calling codes(idd), and other attributes.
    
    Returns
    ---------------
    tuple
        A 17-element tuple containing formatted country information such as
        names, currencies, calling codes(idd), capital cities, region, area, and population.
        the output structure aligns with the order of columns defined in the PostgreSQL schema.
    """

    name = country.get('name', {}) 
    currencies = country.get('currencies', {})
    idd = country.get('idd', {})

    return (
        name.get('common'), 
        name.get('official'), 
        ', '.join([native.get('common', '') for native in name.get('nativeName', {}).values()]), 
        ', '.join(currencies.keys()), 
        ', '.join([value.get('name', '') for value in currencies.values()]), 
        ', '.join([value.get('symbol', '') for value in currencies.values()]), 
        ', '.join([idd.get('root', '') + suffix for suffix in idd.get('suffixes', [])]) if idd.get('suffixes') else '', 
        ', '.join(country.get('capital', [])) if country.get('capital') else "Unknown",
        country.get('region'),
        country.get('subregion'), 
        ', '.join(country.get('languages', {}).values()), 
        country.get('area', 0),
        country.get('population', 0), 
        ', '.join(country.get('continents', [])), 
        country.get('independent'), 
        country.get('unMember'), 
        country.get('startOfWeek') 
    )

def connect_db():
    """Establishes a connection to the PostgreSQL database using credentials
    stored in an environment file.

    Environment Variables
    ---------------
        USER (str): PostgreSQL username.
        PASSWORD (str): PostgreSQL password.
    
    Requirements
    ---------------
        psycopg2 must be installed in the Python environment.
        A valid '.env' file (e.g. 'my_creds.env') containing the required variables must exist.

    Returns
    ---------------
        conn(psycopg2.extensions.connection) or None
            The active database connection object if successful;
            otherwise, returns None if connection fails.)
    """

    # Load environment variables from file
    load_dotenv(dotenv_path="my_creds.env")
    try:
        conn = psycopg2.connect(
            dbname='countries_db',
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"), 
            host='localhost',
            port='5432'
        )
        print("Connected to database.")
        return conn
    except Exception as e:
        print("Database connection failed:", e) 
        return None

def create_table(cursor, sql_file = './ddl_commands/create_countries.sql'):
    """A function that executes the DDL command `create` on the database.

    It performs DDL commands like create statement on the database by parsing the argument
    `cursor` through it. It's purpose is to create the default 'countries' table in the PostgreSQL 
    database if it does not already exist, or any other create table path provided by the user
    by executing an SQL statement stored in an external file.

    parameters
    ---------------
        cursor (psycopg2.extensions.cursor): A PostgreSQL database cursor used to execute SQL commands.
        This cursor must be associated with an active database connection.

        sql_file (str, optional): Path to the SQL file containing the CREATE TABLE statement. 
        Defaults to './ddl_commands/create_countries.sql' if no path is provided.

    Returns
    ---------------
        None

    Notes
    ---------------
        This approach separates SQL logic from Python code, allowing easy reuse and scaling
        for multiple table definitions.
        Ensure the SQL file exists and contains a valid CREATE TABLE statement before execution.
    """

    with open(sql_file, 'r') as f:
        sql = f.read()
    cursor.execute(sql)
    print(f"Executed SQL from {sql_file} and the table created with uniqueness constraint.")

def insert_countries(cursor, countries, sql_file='./dml_commands/insert_countries.sql'):
    """A function that executes bulk inserts into the created table in the database.

    It executes the DML command `insert` on the created table by parsing the arguments
    `cursor` and `countries` through it. It uses the transform(param) function to transform
    each dictionary from the list of dictionaries returned from the api extraction to prepare
    it for insertion by converting to a list of tuples, and then run a bulk insert of the
    values into the created table in the database.

    Parameters
    ---------------
        cursor (psycopg2.extensions.cursor): A PostgreSQL database cursor used to execute SQL insert statements.
        Must be connected to an active database session.
        
        countries (list): A list of dictionaries containing raw country data fetched from the REST Countries API.
        Each dictionary is transformed into a tuple before insertion.

        sql_file (str, optional): Path to the SQL file containing the bulk INSERT statement. 
        Defaults to './dml_commands/insert_countries.sql' if no path is provided.

    Returns
    ---------------
        None
    """

    records = [transform_country(c) for c in countries] # transorm and convert to a list of tuples
    with open(sql_file, 'r') as f:
        sql = f.read()
    cursor.executemany(sql,records)
    print(f"Inserted {len(records)} records from {sql_file}")

# Main execution
def main():
    """Orchestrates the full ETL pipeline for retrieving, transforming, and loading 
    global country data into a PostgreSQL database.

    Steps:
        1. Extracts country metadata from the locally saved api data in json format
        and if not avalaible, fetch the data from the REST Countries API
        using load_country_data_from_json().
        2. Validates that data was successfully retrieved.
        3. Establishes a connection to a local PostgreSQL instance.
        4. Creates the target 'countries' table if it does not already exist.
        5. Transforms and inserts all country records into the database in bulk.
        6. Commits the transaction and safely closes all resources.

    Notes:
        This function acts as the entry point and is invoked only when the script is executed directly.

    Returns:
        None
    """

    # fetch API data by toggling between local or web source
    USE_CACHED = True
    countries = load_country_data_from_json() if USE_CACHED else None
    if countries is None:
        print("Fetching fresh data from API...")
        countries = fetch_country_data(url1,url2)
    if not countries:
        raise ValueError("No country data returned from API. Cannot proceed.")

    # connect to the postgresdb
    conn = connect_db()
    if not conn:
        raise ConnectionError("Failed to connect to PostgreSQL. Check your credentials or server status.")

    # initialize cursor for sql instructions
    cursor = conn.cursor()
    # create table in the database if not exists
    create_table(cursor)
    # bulk insert values into the created table
    insert_countries(cursor, countries)
    # commit insertion
    conn.commit()
    cursor.close()
    conn.close()
    print("All done!")

# Run the program only when executed on the cli
if __name__ == "__main__":
    main()















