import sqlite3
from urllib import request, error
from sqlite3 import Error
from fields import database

"""
Database utility functions
"""

def connectToDb():
    try:
        conn = sqlite3.connect(database)
        return conn
    except Error as e:
        print(e)

def createTable(conn, tableName, tableFields):
    try:
        c = conn.cursor()
        create_sql = "CREATE TABLE IF NOT EXISTS "+tableName+" (" + tableFields +");"
        c.execute(create_sql)
    except Error as e:
        print(e)
        
def insertToTable(table, dictionary, conn):
    columns = ', '.join(dictionary.keys())
    placeholders = ', '.join('?' * len(dictionary))
    sql = 'INSERT INTO ' + table + ' ({}) VALUES ({})'.format(columns, placeholders)
    try:
        conn.execute(sql, list(dictionary.values()))
    except Exception as e:
        print(e)
        conn.close()
        return
    conn.commit()

# return all rows with accNum in table in dictionary form (keys = table field)
def getRows(cursor, accNum, table, transactionType=None):
    if transactionType is not None:
        cursor.execute("select * from "+ table +" where accNum = '" + accNum + "' and type = '" + transactionType + "';")
    else:
        cursor.execute("select * from "+ table +" where accNum = '" + accNum + "';")
    rows = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    return rows