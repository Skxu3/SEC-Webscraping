conn = connectToDb(database)
createTable(conn, 'form4Head', headTblFields)
createTable(conn, 'form4dT', dTTblSql)
createTable(conn, 'form4nDT', nDTTblSql)
createTable(conn, 'form4footNote', footNoteTblFields)

#fname = "2007_4A_accNum"
fname = "2017Form4.csv"
#fname = "flowers_com_inc2014.txt"
#fname = "2017Form4a"

with open(fname) as f:
    urls = f.read().splitlines()

failed = []
thisTime = urls[4001:5002]
#thisTime = urls[1:501] #500 forms 4s
for link in thisTime:
    #link = "0001084869-07-000035"
    links = link.split(",")
    url = "https://www.sec.gov/Archives/" + links[len(links)-1]
    #url = "https://www.sec.gov/Archives/" + link + ".txt"
    #url = "https://www.sec.gov/Archives/edgar/data/1214101/0001104659-07-084171.txt"
    
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
    parseHead(soup, accNum)
    parseTransacs(soup, accNum)