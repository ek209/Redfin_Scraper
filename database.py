import sqlite3

con = sqlite3.connect("rf_data.db")

#TODO Decorate functions to use less functions for create_tables and try_statement

#create tables if they don't exist
def create_tables(cur, sql_statements):
    for statement in sql_statements:
        try:
            cur.execute(statement)
        except sqlite3.OperationalError:
            pass

#creates cursor to create tables
def db_connect_and_create():
    cur = con.cursor()
    create_tables(cur,
                  ["CREATE TABLE bad_zips(zip_code int PRIMARY KEY)",
                   "CREATE TABLE region(region_id int PRIMARY KEY, market varchar(255) NOT NULL, region_type_id int NOT NULL, region_id_search_value varchar(255) UNIQUE NOT NULL)"])
    cur.close()

#loads good and bad zip lists from db
def db_load_zip_lists(): 
    cur = con.cursor()
    bad_zip_list = [zip[0] for zip in cur.execute('SELECT zip_code FROM bad_zips').fetchall()]
    good_zip_list = [int(zip[3]) for zip in cur.execute('SELECT * FROM region').fetchall()]
    cur.close()
    return bad_zip_list, good_zip_list

def db_add_bad_zip(zip_code):
    cur = con.cursor()
    try:
        cur.execute('INSERT INTO bad_zips VALUES (?)', (zip_code,))
        con.commit()
    except sqlite3.OperationalError:
        pass
    cur.close()

#adds region data to db
def db_add_region_data(params):
    cur = con.cursor()
    try:
        cur.execute('INSERT INTO region VALUES (?, ?, ?, ?)', params)
        con.commit()
    except sqlite3.OperationalError:
        pass
    cur.close()




