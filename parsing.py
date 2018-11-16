from bs4 import BeautifulSoup, Tag
from databaseOps import insertToTable
from fields import *
"""
Parser class
"""
class Parser:
    def __init__(self, soup, accNum, conn):
        self.soup = soup
        self.accNum = accNum
        self.conn = conn

    def parseSecHeader(self, lines, sqlMap, sqlDic):
        lines = lines.replace(":", "").split('\n')
        for line in lines:
            if "\t" in line:
                parts = line.split('\t')
                parts = [x for x in parts if x != '']
                if parts and parts[0] in sqlMap:
                    sqlDic[sqlMap[parts[0]]] = parts[1]
        return sqlDic

    def addXmlHeader(self, sqlDic, xmlFields, xml2SqlMap):
        for field in xmlFields:
            val = self.soup.find(field)
            if val:
                val = val.getText()
            key = field
            if xml2SqlMap and field in xml2SqlMap:
                key = xml2SqlMap[field]
            if key == 'dateOfOriginalSubmission' and val:
                val = val.replace("-", "")
            sqlDic[key] = val

    def addXmlHeaderMultiple(self, sqlDics, xmlFields, xml2SqlMap, index):
        for field in xmlFields:
            key = field
            if xml2SqlMap and field in xml2SqlMap:
                key = xml2SqlMap[field]

            vals = self.soup.find_all(field)
            if vals:
                sqlDics[key] = vals[index].getText()

    def parseXml(self, xmlFieldList, transactionsList, transactionType):
        xmlLis = xmlFieldList.split('\n')
        xmlFields = []
        for field in xmlLis:
            fieldParts = field.split(' ')
            xmlFields.append(fieldParts[0])

        sqlDic = {}
        if transactionType == 'derivativeTransaction':
            footNoteTag = 'dt'
        else:
            footNoteTag = 'ndt'
        for row in range(len(transactionsList)):
            sqlDic[row+1] = {}
            sqlDic[row+1]['footnotes'] = []
            for field in xmlFields:
                if field == 'accNum':
                    val = self.accNum
                elif field == 'rowNumber':
                    val = row+1
                elif field == 'dTId' or field == 'nDTId':
                    val = self.accNum+'-'+str(row+1)
                elif field == 'footNoteId':
                    continue
                elif field == 'transactionTimelines':
                    field = 'transactionTimeliness'
                else:
                    results = transactionsList[row].find(field)
                    if results:
                        val = ''.join([str(x) for x in results.contents if x != '\n'])
                        for x in results.contents:
                            if x and isinstance(x, Tag):
                                fId = x.get('id')
                                if fId is not None:
                                    foot = {'accNum': self.accNum,
                                           'rowNumber': row+1,
                                           'footNoteId': self.accNum+'-'+ str(row+1)+'-'
                                            +footNoteTag + '-' + fId + '-' + field,
                                           'fId': fId,
                                           'originalTableType': transactionType,
                                           'footNoteField': field
                                           }
                                    sqlDic[row+1]['footnotes'].append(foot)
                    else:
                        val = None
                if field == 'transactionTimeliness':
                    field = 'transactionTimelines'
                sqlDic[row+1][field] = val
        return sqlDic

    def fillFootNoteText(self, footnotes):
        for note in footnotes:
            fId = note['fId']
            footnote = self.soup.find('footnote', {'id': fId})
            if footnote:
                note['footNote'] = footnote.contents[0].replace('\n', '')

    def insertToTransacTables(self, sql, tableName):
        for rowNum in sql.keys():
            row = sql[rowNum]
            footnotes = row.pop('footnotes')
            self.fillFootNoteText(footnotes)

            insertToTable(tableName, row, self.conn)

            for note in footnotes:
                insertToTable('form4footNote', note, self.conn)

    def parseHead(self):
        sqlDic = {} 

        # SEC-HEADER
        sec_header = self.soup.find("ACCEPTANCE-DATETIME").getText()
        issuerBegin = sec_header.find("ISSUER")
        ownerBegin = sec_header.find("REPORTING-OWNER")

        # Process top of SEC-HEADER
        etcHeader = sec_header[:issuerBegin]
        sqlDic = self.parseSecHeader(etcHeader, textHeadMap, sqlDic)
        self.addXmlHeader(sqlDic, xmlEtcHeaders, None)

        # SEC-HEADER Issuer section
        issuerHead = sec_header[issuerBegin:ownerBegin]

        # Issuer company data
        sqlDic = self.parseSecHeader(issuerHead, issuerMap, sqlDic)
        self.addXmlHeader(sqlDic, xmlIssHeaders, None)

        bizBegin = issuerHead.find("BUSINESS ADDRESS")
        mailBegin = issuerHead.find("MAIL ADDRESS")

        # SEC-HEADER Issuer business address
        issuerHeadBiz = issuerHead[bizBegin:mailBegin]
        sqlDic = self.parseSecHeader(issuerHeadBiz, issuerBizMap, sqlDic)

        # SEC-HEADER Issuer mail address
        issuerHeadMail = issuerHead[mailBegin:]
        sqlDic = self.parseSecHeader(issuerHeadMail, issuerMailMap, sqlDic)

        # SEC-HEADER Reporting owners section & insert into table
        rOwners = sec_header.split("REPORTING-OWNER:")[1:]
        for index in range(len(rOwners)):
            sqlDic = self.parseSecHeader(rOwners[index], ownerMap, sqlDic)
            self.addXmlHeaderMultiple(sqlDic, xmlOwnHeaders, xml2SqlOwnFields, index)
            sqlDic['rowNumber'] = index+1 
            sqlDic['accNum'] = self.accNum
            sqlDic['headId'] = self.accNum + "-" + str(index+1)
            #print(sqlDic['headId'])
            insertToTable('form4head', sqlDic, self.conn)

    def parseTransacs(self):
        # Process derivative transactions
        derivativeTransactions = self.soup.find_all("derivativeTransaction")
        sql = self.parseXml(dTTblFields, derivativeTransactions, 'derivativeTransaction')
        self.insertToTransacTables(sql, 'form4dT')

        # Process non-derivative transactions
        nonDerivativeTransactions = self.soup.find_all("nonDerivativeTransaction")
        sqlNT = self.parseXml(nDTTblFields, nonDerivativeTransactions, 'nonDerivativeTransaction')
        self.insertToTransacTables(sqlNT, 'form4nDT')