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

fname = "2016Q4_2017Q4form4a_3MCO.idx"

with open(fname) as f:
    urls = f.read().splitlines()

thisTime = urls
for link in thisTime:
    links = link[link.find("edgar"):link.find("txt")+3]
    url = "https://www.sec.gov/Archives/" + links

    try:
        response = request.urlopen(url)
    except error.HTTPError as err:
        failed.append(url)
        continue
    
    the_page = response.read()
    content = the_page.decode(encoding='latin-1')
    # file = open("test", "w") #"test" = url to where you want to save file
    # file.write(content) 

    parts = links.split("/")
    if len(parts) == 5: 
        accNum = parts[len(parts)-3] + '/' +parts[len(parts)-2] + '/' + parts[len(parts)-1].split('.')[0]
    if len(parts) == 4: 
        accNum = parts[len(parts)-2] + '/' + parts[len(parts)-1].split('.')[0]
   
    if "4/A" in link: 
        documentType = "4/A"
    else:
        documentType = "4"

    # start parsing
    begin = content.find("<SEC-DOCUMENT>")
    end = content.find("-----END")
    xmlFile = content[begin:end]
    soup = BeautifulSoup(xmlFile, 'xml')
    parser = Parser(soup, accNum, documentType, conn)
    parser.parseHead()
    parser.parseTransacs()