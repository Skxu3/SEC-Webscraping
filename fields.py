"""
Fields used by database tables and parser
"""

### Database table fields ###
database = "./ACCT/database2.db"

headTblFields = """accNum text NOT NULL,
headId text PRIMARY KEY NOT NULL,
rowNumber integer DEFAULT 1,
documentType text NOT NULL,
publicDocCount integer DEFAULT 0,
periodOfReport text,
filedDate text,
changedDate text,
schemaVersion text,
dateOfOriginalSubmission text,
notSubjectToSection16 integer DEFAULT 0,
issuerName text,
issuerCik text,
issuerIndustrialClassification text,
issuerIrs text,
issuerIncorpState text,
issuerFiscalYrEnd text,
issuerBusinessStreet1 text,
issuerBusinessCity text,
issuerBusinessState text,
issuerBusinessZip text,
issuerBusinessPhone text,
issuerMailStreet1 text,
issuerMailStreet2 text,
issuerMailCity text,
issuerMailState text,
issuerMailZip text,
issuerTradingSymbol text,
rptOwnerName text,
rptOwnerCik text DEFAULT 0,
rptOwnerFormType text,
rptOwnerSecAct text,
rptOwnerSecFileNum text,
rptOwnerFilmNum text,
rptOwnerBusinessPhone text,
rptOwnerStreet1 text,
rptOwnerStreet2 text,
rptOwnerCity text,
rptOwnerState text,
rptOwnerZipCode text,
rptOwnerStateDescription text,
rptOwnerMailStreet1 text,
rptOwnerMailStreet2 text,
rptOwnerMailCity text,
rptOwnerMailState text,
rptOwnerMailZip text,
rptOwnerisDirector integer DEFAULT 0,
rptOwnerisOfficer integer DEFAULT 0,
rptOwnerisTenPercentOwner integer DEFAULT 0,
rptOwnerisOther integer DEFAULT 0"""

dTTblFields = """accNum text NOT NULL,
dTId text PRIMARY KEY NOT NULL,
rowNumber integer DEFAULT 1,
securityTitle text,
conversionOrExercisePrice text,
transactionDate text,
transactionFormType text,
transactionCode text,
equitySwapInvolved text,
transactionShares text,
transactionPricePerShare text,
transactionAcquiredDisposedCode text,
exerciseDate text,
expirationDate text,
underlyingSecurityTitle text,
underlyingSecurityShares text,
sharesOwnedFollowingTransaction text,
directOrIndirectOwnership text,
footNoteId text,"""

nDTTblFields = """accNum text NOT NULL,
nDTId text PRIMARY KEY NOT NULL,
rowNumber integer DEFAULT 1,
securityTitle text,
transactionDate text,
transactionFormType text,
transactionCode text,
equitySwapInvolved text,
transactionTimelines text,
transactionShares text,
transactionPricePerShare text,
transactionAcquiredDisposedCode text,
sharesOwnedFollowingTransaction text,
directOrIndirectOwnership text,
natureOfOwnership text,
footNoteId text,"""

footNoteTblFields = """accNum text NOT NULL,
rowNumber integer DEFAULT 1,
footNoteId text PRIMARY KEY NOT NULL,
fId text,
originalTableType text,
footNoteField text,
footNote text"""

dTTblSql = dTTblFields + "FOREIGN KEY(footNoteId) REFERENCES form4footNote(footNoteId)"
nDTTblSql = nDTTblFields + "FOREIGN KEY(footNoteId) REFERENCES form4footNote(footNoteId)"

### Parser fields ###
textHeadMap = {"ACCESSION NUMBER": "accNum",
              "CONFORMED SUBMISSION TYPE": "documentType",
              "PUBLIC DOCUMENT COUNT": "publicDocCount",
              "CONFORMED PERIOD OF REPORT": "periodOfReport",
              "FILED AS OF DATE": "filedDate",
              "DATE AS OF CHANGE": "changedDate"}
issuerMap = {"COMPANY CONFORMED NAME": "issuerName",
              "CENTRAL INDEX KEY": "issuerCik",
              "STANDARD INDUSTRIAL CLASSIFICATION": "issuerIndustrialClassification",
              "IRS NUMBER": "issuerIrs",
              "STATE OF INCORPORATION": "issuerIncorpState",
              "FISCAL YEAR END": "issuerFiscalYrEnd"}
issuerBizMap = {"STREET 1": "issuerBusinessStreet1",
              "CITY": "issuerBusinessCity",
              "STATE": "issuerBusinessState",
              "ZIP": "issuerBusinessZip",
              "BUSINESS PHONE": "issuerBusinessPhone"}
issuerMailMap = {"STREET 1": "issuerMailStreet1",
              "STREET 2": "issuerMailStreet2",
              "CITY": "issuerMailCity",
              "STATE": "issuerMailState",
              "ZIP": "issuerMailZip"}
ownerMap = {"COMPANY CONFORMED NAME": "rptOwnerName",
          "CENTRAL INDEX KEY": "rptOwnerCik",
          "FORM TYPE": "rptOwnerFormType",
          "SEC ACT": "rptOwnerSecAct",
          "SEC FILE NUMBER": "rptOwnerSecFileNum",
          "FILM NUMBER": "rptOwnerFilmNum",
          "STREET 1": "rptOwnerMailStreet1",
          "STREET 2": "rptOwnerMailStreet2",
          "CITY": "rptOwnerMailCity",
          "STATE": "rptOwnerMailState",
          "ZIP": "rptOwnerMailZip",
          "BUSINESS PHONE": "rptOwnerBusinessPhone"}
xml2SqlOwnFields = {"isDirector" : "rptOwnerisDirector",
                 "isOfficer": "rptOwnerisOfficer", 
                 "isTenPercentOwner": "rptOwnerisTenPercentOwner", 
                 "isOther": "rptOwnerisOther"}
xmlEtcHeaders = ["schemaVersion", "documentType", "periodOfReport", "dateOfOriginalSubmission", "notSubjectToSection16"]
xmlIssHeaders = ["issuerCik", "issuerName", "issuerTradingSymbol"]
xmlOwnHeaders = ["rptOwnerCik", "rptOwnerName", "rptOwnerStreet1", "rptOwnerStreet2", "rptOwnerCity", "rptOwnerState","rptOwnerZipCode", "rptOwnerStateDescription", "isDirector", "isOfficer", "isTenPercentOwner", "isOther"]

def getFields(allFields):
    fields = allFields.replace("\n", "").split(",")
    fields = [field.split(" ")[0] for field in fields]
    return fields
def getHeadFields():
    return getFields(headTblFields)
def getDTFields():
    return getFields(dTTblFields)
def getNDTFields():
    return getFields(nDTTblFields)
def getFootFields():
    return getFields(footNoteTblFields)