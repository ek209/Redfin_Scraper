import sqlite3
import pandas as pd
import os
import datetime as dt

DB_PATH = os.environ.get('RF_DB_URI')
con = sqlite3.connect(DB_PATH)


def create_tables(cur, sql_statements):
    """Executes the sql statements unless there is an operational error. 
    If operational error, does nothing.

    Args:
        cur (Cursor): Cursor object to execute statement
        sql_statements (List): Statements to execute
    """
    for statement in sql_statements:
        try:
            cur.execute(statement)
        except sqlite3.OperationalError:
            pass

def db_connect_and_create():
    """Creates cursor connection to connect to database and execute table creation statements

    """
    cur = con.cursor()
    create_tables(cur,
                  ['''CREATE TABLE sold_properties(sale_type VARCHAR, sold_date VARCHAR,
                    property_type VARCHAR, address VARCHAR, city VARCHAR, state_prov VARCHAR, postal_code INT, price INT, 
                   beds FLOAT, baths FLOAT, location VARCHAR, sqft INT, lot_size INT, year_built INT, days_on_market INT, 
                   price_per_sqft INT, hoa_monthly INT, status VARCHAR, next_open_house_start VARCHAR, next_open_house_end VARCHAR, url VARCHAR,
                   source VARCHAR, mls INT, lat FLOAT, lng FLOAT, region_id INT, region_id_for_excel_dl INT,
                   sold_year INT, sold_month INT, sold_day INT, PRIMARY KEY(mls, lat, lng, sold_date))''',
                    '''CREATE TABLE region_ids(region_id INT, region_type_id INT, region_type_search_id INT,
                    name VARCHAR(255) NOT NULL, leanedName VARCHAR(255) NOT NULL, market VARCHAR(255), 
                    market_id INT, market_display_name VARCHAR(255), url VARCHAR(255) UNIQUE, 
                   polygon VARCHAR, isBoundingBox BOOLEAN, isRedfinServiced BOOLEAN NOT NULL, PRIMARY KEY(region_id, region_type_id))''',
                   '''CREATE TABLE invalid_ids(region_type_search_id INT, region_type_id INT,
                   PRIMARY KEY (region_type_search_id, region_type_id))'''])
                  #["CREATE TABLE bad_zips(zip_code int PRIMARY KEY)",
                   #"CREATE TABLE region(region_id int PRIMARY KEY, market varchar(255) NOT NULL, region_type_id int NOT NULL, region_id_search_value varchar(255) UNIQUE NOT NULL)"])
    cur.close()

def db_load_valid(region_type_id):
    cur = con.cursor()
    valid = [id for id in cur.execute('SELECT region_id, region_type_id FROM region_ids WHERE region_type_id=(?)', (region_type_id,)).fetchall()]
    cur.close()
    return valid

def db_new_sold_dates():
    con = sqlite3.connect('rf_data.db')
    cur = con.cursor()
    data = pd.read_sql(('SELECT *  FROM sold_properties WHERE sold_date IS NOT NULL and sold_year IS NULL'), con)
    count = data.shape[0]
    for row in data.values:
        count = count -1 
        print(count)
        sold_date = row[1]
        try:
            new_sold_date = dt.datetime.strptime(row[1], "%B-%d-%Y")
            year = new_sold_date.year
            day = new_sold_date.day
            month = new_sold_date.month
            new_sold_date = new_sold_date.isoformat()
        except TypeError:
            continue
        mls = row[22] 
        lat = row[23] 
        lng = row[24]
        cur.execute('''UPDATE sold_properties
                    SET sold_year = (?), sold_day = (?), sold_month = (?)
                    WHERE mls = (?) AND lat = (?) AND lng = (?) AND sold_date = (?)''', (year, day, month, mls, lat, lng, sold_date))
        con.commit()
    cur.close()

    con.close()

def db_load_tested(region_type_id):
    """Loads already searched zip codes from the bad_zips table as bad_zip_list
    and good zip codes from region table

    Returns:
        List: Two lists, list of bad zip codes, list of good zip codes.
    """
    cur = con.cursor()
    invalid = [id[0] for id in cur.execute('SELECT region_type_search_id FROM invalid_ids WHERE region_type_id=(?)',(region_type_id,)).fetchall()]
    valid = [id[0] for id in cur.execute ('SELECT region_type_search_id FROM region_ids WHERE region_type_id=(?)', (region_type_id,)).fetchall()]
    tested = set(invalid).union(set(valid))
    cur.close()
    return tested


def db_add_tested_ids(params):
    """Adds invalid_id to invalid_ids table, does nothing if operational error

    Args:
        params (Tuple): Params to add to table 
    """
    con = sqlite3.connect("rf_data.db")
    cur = con.cursor()
    try:
        cur.execute('INSERT INTO invalid_ids VALUES (?,?)', params)
        con.commit()
    except sqlite3.OperationalError:
        pass
    cur.close()
    con.close()

def db_add_sold_data(params):
    """Adds params list to region table and commits change to db.
    If exception caught it does nothing.

    Args:
        params (Tuple): List of values to add to the region db.
    """
    con = sqlite3.connect("rf_data.db")
    cur = con.cursor()
    try:
        cur.execute('INSERT INTO sold_properties VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', params)
        con.commit()
    except (sqlite3.OperationalError, sqlite3.IntegrityError):
        pass
    cur.close()
    con.close()

def db_sold_searched():
    #ids that need to be searched again my prop type [1902]
    cur = con.cursor()
    searched = [id for id in cur.execute('SELECT DISTINCT region_id, region_id_for_excel_dl FROM sold_properties').fetchall()]
    cur.close()
    return searched

def db_add_new_region_data(params):
    """Adds params list to region table and commits change to db.
    If exception caught it does nothing.

    Args:
        params (Tuple): List of values to add to the region db.
    """
    con = sqlite3.connect("rf_data.db")
    cur = con.cursor()
    try:
        cur.execute('INSERT INTO region_ids VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', params)
        con.commit()
    except (sqlite3.OperationalError, sqlite3.IntegrityError):
        pass
    cur.close()
    con.close


