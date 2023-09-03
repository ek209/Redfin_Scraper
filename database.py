import sqlite3

con = sqlite3.connect("rf_data.db")

#TODO Decorate functions to use less functions for create_tables and try_statement

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
                  ["CREATE TABLE bad_zips(zip_code int PRIMARY KEY)",
                   "CREATE TABLE region(region_id int PRIMARY KEY, market varchar(255) NOT NULL, region_type_id int NOT NULL, region_id_search_value varchar(255) UNIQUE NOT NULL)"])
    cur.close()

def db_load_zip_lists():
    """Loads already searched zip codes from the bad_zips table as bad_zip_list
    and good zip codes from region table

    Returns:
        List: Two lists, list of bad zip codes, list of good zip codes.
    """
    cur = con.cursor()
    bad_zip_list = [zip[0] for zip in cur.execute('SELECT zip_code FROM bad_zips').fetchall()]
    good_zip_list = [int(zip[3]) for zip in cur.execute('SELECT * FROM region').fetchall()]
    cur.close()
    return bad_zip_list, good_zip_list

def db_add_bad_zip(zip_code):
    """Adds bad zip code to bad_zips table, does nothing if operational error

    Args:
        zip_code (Int): Zip code to add to table
    """
    cur = con.cursor()
    try:
        cur.execute('INSERT INTO bad_zips VALUES (?)', (zip_code,))
        con.commit()
    except sqlite3.OperationalError:
        pass
    cur.close()

def db_add_region_data(params):
    """Adds params list to region table and commits change to db.
    If exception caught it does nothing.

    Args:
        params (Tuple): List of values to add to the region db.
    """
    cur = con.cursor()
    try:
        cur.execute('INSERT INTO region VALUES (?, ?, ?, ?)', params)
        con.commit()
    except sqlite3.OperationalError:
        pass
    cur.close()




