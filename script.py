import sqlite3
from urllib import request, error
from sqlite3 import Error
from bs4 import BeautifulSoup

from databaseOps import connectToDb, createTable
from parsing import Parser
from fields import *

"""
Create tables
"""

conn = connectToDb()
createTable(conn, 'form4Head', headTblFields)
createTable(conn, 'form4dT', dTTblSql)
createTable(conn, 'form4nDT', nDTTblSql)
createTable(conn, 'form4footNote', footNoteTblFields)

#fname = "2007_4A_accNum" 
#fname = "flowers_com_inc2014.txt"

fname = "2017Form4.csv" #form 4
#fname = "2017Form4a" #400 4/a

with open(fname) as f:
    urls = f.read().splitlines()

thisTime = urls[1:2] #500 forms 4s
for link in thisTime:
    links = link.split(",")
    url = "https://www.sec.gov/Archives/" + links[len(links)-1] #for 4s
    #url = "https://www.sec.gov/Archives/" + link + ".txt" #for 2014form4a 
    try:
        response = request.urlopen(url)
    except error.HTTPError as err:
        failed.append(url)
        continue
    
    the_page = response.read()
    content = the_page.decode(encoding='latin-1')
    file = open("test", "w")
    file.write(content) 

    #parts = link.split("/")
    parts = links[len(links)-1].split('/')
    if len(parts) == 5: #.../data/1084869/000108486914000025/0001084869-14-000025.txt
        accNum = parts[len(parts)-3] + '/' +parts[len(parts)-2] + '/' + parts[len(parts)-1].split('.')[0]
    if len(parts) == 4: #.../data/1214101/0001104659-07-084171.txt
        accNum = parts[len(parts)-2] + '/' + parts[len(parts)-1].split('.')[0]
        
    # start parsing
    begin = content.find("<SEC-DOCUMENT>")
    end = content.find("-----END")
    xmlFile = content[begin:end]
    soup = BeautifulSoup(xmlFile, 'xml')
    parser = Parser(soup, accNum, conn)
    parser.parseHead()
    parser.parseTransacs()