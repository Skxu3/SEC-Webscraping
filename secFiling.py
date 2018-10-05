#python3
import urllib.request
import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_project(conn, project):
    sql = ''' INSERT INTO projects(name,begin_date,end_date)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, project)
    return cur.lastrowid


def main():
    database = "/Users/Star/desktop/academics/haas web dev/ACCT/database.db"
    create_header_table = """ CREATE TABLE IF NOT EXISTS header (
         accession_number integer PRIMARY KEY,
         documentType text,
         public_doc_count integer,
         periodOfReport text,
         filed_date text,
         changed_date text,
         issuer_company_name text,
         issuer_central_index_key integer,
         issuer_industrial_classification text,
         issuer_irs_number integer,
         issuer_incorporation_state text,
         issuer_fiscal_year_end text,
         issuer_business_street1 text,
         issuer_business_city text,
         issuer_business_state text,
         issuer_business_zip text,
         issuer_business_phone text,
         issuer_mail_street1 text,
         issuer_mail_street2 text,
         issuer_mail_city text,
         issuer_mail_state text,
         issuer_mail_zip text,
         reporting_owner_company_name text,
         reporting_owner_central_index_key integer,
         reporting_owner_form_type text,
         reporting_owner_sec_act text,
         reporting_owner_sec_file_number text,
         reporting_owner_film_number text,
         reporting_owner_business_phone text,
         reporting_owner_mail_street1 text,
         reporting_owner_mail_city text,
         reporting_owner_mail_state text,
         reporting_owner_mail_zip text
        ); """

    create_derivative_table = """ CREATE TABLE IF NOT EXISTS deriativeTransactions (
        accession_number integer PRIMARY KEY,
        row_number integer,
        security_title text,
        conversion_or_exercise_price integer,
        footnote_id text,
        transaction_date text,
        transaction_form_type text,
        transaction_code text,
        equity_swap_involved integer,
        transaction_shares integer,
        transaction_price_per_share integer,
        transaction_acquired_disposed_code text,
        exercise_date text,
        expiration_date text,
        underlying_security_title text,
        underlying_security_shares text,
        shared_owned_following_transaction text,
        direct_or_indirect_ownership text
        ); """

    create_nonderivative_table = """ CREATE TABLE IF NOT EXISTS nonDeriativeTransactions (
         accession_number integer PRIMARY KEY,
         row_number integer,
         security_title text,
         transaction_date text,
         transaction_form_type text,
         transaction_code text,
         equity_swap_involved integer,
         transaction_shares integer,
         transaction_price_per_share integer,
         transaction_acquired_disposed_code text,
         shared_owned_following_transaction text,
         direct_or_indirect_ownership text
        ); """

    conn = create_connection(database)
    if conn is not None:
        create_table(conn, create_header_table)
        create_table(conn, create_derivative_table)
        create_table(conn, create_nonderivative_table)
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()

"""
for url in urls:
    response = urllib.request.urlopen(url)
    the_page = response.read()
    content = the_page.decode(encoding='latin-1')
    file_handle.write(content)
"""