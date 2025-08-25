from countries import load_country_data_from_json
from countries import transform_country, create_table
from config import urls
import pytest
import psycopg2
import os
from dotenv import load_dotenv


def test_load_country_data_from_json():
    data = load_country_data_from_json("countries_raw.json")
    assert isinstance(data, list)
    assert "name" in data[0]
    assert "capital" in data[0]


def test_create_table():
    load_dotenv(dotenv_path="my_creds.env")
    conn = psycopg2.connect(
            dbname='countries_db',
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"), 
            host='localhost',
            port='5432'
    )
    cursor = conn.cursor()

    create_table(cursor)

    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'countries'
        );
    """)
    result = cursor.fetchone()
    assert result[0] is True

    cursor.close()
    conn.close()


def test_tranform_country():
    sample_country = {
    "name": {
        "common": "Sampleland",
        "official": "The Republic of Sampleland",
        "nativeName": {"eng": {"common": "Sampleland"}}
    },
    "currencies": {"SMP": {"name": "Sample Dollar", "symbol": "$"}},
    "idd": {"root": "+1", "suffixes": ["234"]},
    "capital": ["Sample City"],
    "region": "Test Region",
    "subregion": "Test Subregion",
    "languages": {"eng": "English"},
    "area": 12345,
    "population": 67890,
    "continents": ["Test Continent"],
    "independent": True,
    "unMember": False,
    "startOfWeek": "monday"
    }

    result = [transform_country(sample_country)]
    assert isinstance(result, list)
    assert result[0][0] == "Sampleland"
    assert result[0][3] == "SMP"
    assert result[0][7] == "Sample City"
    
    