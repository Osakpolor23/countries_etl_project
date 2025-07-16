# import libraries
import requests
import json
import psycopg2

# Main execution
def main():
    # fecth the API data
    countries = fetch_country_data()
    # print(json.dumps(countries, indent=2))  # indent=2 for pretty printing
    # if no data is returned(or an empty list is returned)
    if not countries:
        # raise ValueError with an error message
        raise ValueError("No country data returned from API. Cannot proceed.")

    # connect to the postgresdb
    conn = connect_db()
    # if connection failed(or None is returned)
    if not conn:
        # raise ConnectionError with an error message
        raise ConnectionError("Failed to connect to PostgreSQL. Check your credentials or server status.")

    # initialize cursor for sql instructions
    cursor = conn.cursor()
    # create table in the database if not exists
    create_table(cursor)
    # bulk insert values into the created table
    insert_countries(cursor, countries)
    # commit insertion
    conn.commit()
    # close cursor
    cursor.close()
    # close connection to the gostgresdb
    conn.close()
    # print successful message if everything completed
    print("All done!")

# Extract the world country data from this API https://restcountries.com/v3.1/all
"""I observed that the API requires the field names to be specified before it can be called,so I indicated 
all the columns I needed while calling the API. I also ran into an issue of getting the error message:
{"message": "'fields' query not specified", "status": 400}
which could be as a result of the API having trouble parsing overly long fields parameters
or hitting an internal limit (possibly on the query string length or field processing).
So, I decided to breakdown my requests into two chunks as a walkaround
"""

# Fetch and merge country data from REST Countries API
def fetch_country_data():
    url1 = "https://restcountries.com/v3.1/all?fields=name,independent,unMember,startOfWeek,currencies,idd,capital,region,subregion,languages"
    url2 = "https://restcountries.com/v3.1/all?fields=area,population,continents"
    
    try:
        response1 = requests.get(url1).json()
        response2 = requests.get(url2).json()
    except Exception as e:
        print("Failed to fetch data:", e)
        return []
    
    # Initialize an empty list to hold the merged data
    merged_data = []

    # Merge the two responses by iterating through both lists
    for country1, country2 in zip(response1, response2): # zip combines two lists into pairs by index(position)
    # Merge dictionaries for each country
        merged_country = {**country1, **country2} # Merging two dictionaries using unpacking operator(**)
        merged_data.append(merged_country) # Append the merged country data to the list.

    return merged_data

# Transform one country record into tuple matching table schema
def transform_country(country):
    # get the dictionaries within the country dictionary
    name = country.get('name', {})
    currencies = country.get('currencies', {})
    idd = country.get('idd', {})

    # extract and return the needed columns in the preferred format
    return (
        name.get('common'), # extracting common name
        name.get('official'), # extracting official name
        ', '.join([native.get('common', '') for native in name.get('nativeName', {}).values()]), # all common native name - comma separated
        ', '.join(currencies.keys()), # all possible currency codes - comma separated
        ', '.join([value.get('name', '') for value in currencies.values()]), # all possible currency names comma separated
        ', '.join([value.get('symbol', '') for value in currencies.values()]), # all possible currency symbols - comma separated
        ', '.join([idd.get('root', '') + suffix for suffix in idd.get('suffixes', [])]) if idd.get('suffixes') else '', # all possible calling codes/idd  - comma separated
        ', '.join(country.get('capital', [])) if country.get('capital') else "Unknown", # all possible capital cities - comma separated
        country.get('region'), # region
        country.get('subregion'), # subregion
        ', '.join(country.get('languages', {}).values()), # all possible official languages - comma separated
        country.get('area', 0), # area with default 0 when missing
        country.get('population', 0), # population with default zero when missing
        ', '.join(country.get('continents', [])), # all possible continents - comma separated
        country.get('independent'), # independence
        country.get('unMember'), # UN membership
        country.get('startOfWeek') # start of week day
    )


# Connect to PostgreSQL
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname='countries_db',
            user='postgres',
            password='my_pgadmin_password',
            host='localhost',
            port='5432'
        )
        print("Connected to database.")
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        return None

# Create table if not exists
def create_table(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS public.countries (
        id SERIAL PRIMARY KEY,
        country_name TEXT,
        official_name TEXT,
        native_names TEXT,
        currency_codes TEXT,
        currency_names TEXT,
        currency_symbols TEXT,
        idd_codes TEXT,
        capitals TEXT,
        region TEXT,
        subregion TEXT,
        languages TEXT,
        area REAL,
        population BIGINT,
        continents TEXT,
        independent BOOLEAN,
        un_member BOOLEAN,
        start_of_week TEXT,
        CONSTRAINT unique_country_profile UNIQUE (
        country_name,
        official_name,
        region,
        area,
        continents
            )
    )
    """)
    print("Table 'countries' created in the postgresdb with uniqueness constraint.")

# Bulk insert records
def insert_countries(cursor, countries):
    records = [transform_country(c) for c in countries]
    cursor.executemany("""
        INSERT INTO public.countries (
            country_name, official_name, native_names,
            currency_codes, currency_names, currency_symbols,
            idd_codes, capitals, region, subregion, languages,
            area, population, continents,
            independent, un_member, start_of_week
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT ON CONSTRAINT unique_country_profile DO NOTHING;""", records)
    print(f"Inserted {len(records)} countries")


# Run the program only when executed on the cli
if __name__ == "__main__":
    main()















