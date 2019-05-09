import utility, databaseOps, fields
import numpy as np
import json, pulp
from bs4 import BeautifulSoup, Tag
from fields import getHeadFields, getDTFields, getNDTFields, getFootFields, filterFields
from utility import *

"""
Functions used to match Form 4 and Form 4/A.
"""

conn = databaseOps.connectToDb()
cur = conn.cursor()

"""
Compare 2 rows of data
- aRow & bRow are dictionaries 
"""
def compareByCols(aRow, bRow):
    numMatches = 0
    editDists, naiveDists = [], []
    cols = list(aRow.keys())
    numCols = len(cols)
    for j in range(numCols):
        numMatches += sum([1 for i in range(numCols) if aRow[cols[i]] == bRow[cols[i]]])
        editDists.append(sum([editDistance(str(aRow[cols[i]]), str(bRow[cols[i]])) for i in range(numCols)]))
        naiveDists.append(sum([naiveEdit(str(aRow[cols[i]]), str(bRow[cols[i]])) for i in range(numCols)]))
#     print((numMatches - sum(editDists) - sum(naiveDists))/numCols)
    return (numMatches - sum(editDists) - sum(naiveDists))/numCols #more negative = more unlike
#     return numMatches - sum(editDists) - sum(naiveDists) #more negative = more unlike

# given aRows, return prob dist of bRows being match for each aRow
# dict[aRow][probs] = prob
def getMatchProbDist(aRows, bRows, identifier): #4/a, 4
    probDist = dict()
    for aRow in aRows:
        probDist[aRow[identifier]] = dict()

    # if only 1 transaction in each
    if len(aRows) == 1 and len(bRows) == 1:
        probDist[aRows[0][identifier]][bRows[0][identifier]] = 1
        return probDist
    
    # score matching each 4a with each 4
    for aRow in aRows:
        transacMatchScores = dict()
        for bRow in bRows:
            transacMatchScores[bRow[identifier]] = compareByCols(aRow, bRow)
            
        #normalize scores 
        total = 0
        scores = transacMatchScores.values()
        minScore = min(scores)
        for key in transacMatchScores.keys():
            if minScore < 0:
                transacMatchScores[key] += abs(minScore) + 0.0000000001 #prevent from nan
            total += transacMatchScores[key]
        for key in transacMatchScores.keys():
            probDist[aRow[identifier]][key] = transacMatchScores[key]/total
        
    #print('probDist', json.dumps(probDist, indent=2))
    return probDist

# Use LP to get optimal matches; Formulate matching as max weighted matching
def getOptMatches(probDist):
    fourAIDs = list(probDist.keys())
    fourIDs = list(probDist[fourAIDs[0]].keys())
    n, m = len(fourAIDs), len(fourIDs)
    allVars, variables = [], []
    for i in range(n):
        x = [str(i) + '|' + str(j) for j in range(m)]
        variables.append(x)

    lp = pulp.LpProblem("max weighted matching", pulp.LpMaximize)
    lstVars = []
    for j in range(len(variables)):
        a = [pulp.LpVariable(variables[j][i], lowBound = 0, upBound = 1, cat='Integer') for i in range(len(variables[j]))]
        lstVars.append(a)
        allVars += a
        
    objFunc, varWeightMap = [], {}
    for var in allVars:
        varName = var.name.split('|')
        fourAID, fourID = fourAIDs[int(varName[0])], fourIDs[int(varName[1])]
        objFunc += [(var, probDist[fourAID][fourID])] 
        varWeightMap[var.name] = probDist[fourAID][fourID]
    objFunc = pulp.LpAffineExpression(objFunc)
    lp += objFunc

    for j in range(len(lstVars)):
        cons = [(var, 1) for var in lstVars[j]]
        lp += pulp.LpAffineExpression(cons) <= 1 #constraints
    lp.solve()
    # for variable in lp.variables(): # if want to see weights
    #     print("{} = {}".format(variable.name, variable.varValue))
    
    chosenVars = [(var.name, varWeightMap[var.name]) for var in lp.variables() if var.varValue == 1]
    chosenVars = sorted(chosenVars, key=lambda tup: tup[1], reverse=True) #sort by prob of matching
    
    allMatches, unmatched = [], []
    for i in range(n): #only top m matches
        chosenName = chosenVars[i][0].split('|')
        if i < m:
            allMatches.append((fourAIDs[int(chosenName[0])], fourIDs[int(chosenName[1])]))
        else:
            unmatched.append(fourAIDs[int(chosenName[0])])
    return allMatches, unmatched
    
# Used to create changeDictionary: get the fields that was changed 
def getChangedFields(aRow, bRow, tblFields, fourAID="", fourID=""):
    changedFields = dict()
    for field in tblFields:
        after, before = dict(), dict()
        if bRow is None or bRow == [] or bRow[field] == 'null' or bRow[field] is None:
            if aRow[field] == "null" or aRow[field] is None:
                continue
            else:
                after['value'] = aRow[field]
                attachFootNote(after, field, aRow, fourAID)
        elif (aRow[field] == "null" or aRow[field] is None) and (bRow[field] != 'null' or bRow[field] is not None):
            before['value'] = bRow[field]
            attachFootNote(before, field, bRow, fourID)
        elif aRow[field] != bRow[field]:
            after['value'] = aRow[field]
            attachFootNote(after, field, aRow, fourAID)
            before['value'] = bRow[field]
            attachFootNote(before, field, bRow, fourID)
        if len(after) > 0 or len(before) > 0:
            changedFields[field] = dict()
        if len(after) > 0 or len(before) > 0:
            changedFields[field]['4A'] = after
            changedFields[field]['4'] = before
    return changedFields

# Used to create changeDictionary: get the footnotes that was changed 
def attachFootNote(dic, field, row, accNum):
    if isinstance(row[field], str) and "footnoteId" in row[field]: 
    	#<footnoteId id=\"F1\"/><footnoteId id=\"F2\"/>"
        soup = BeautifulSoup(row[field])
        footnotes = soup.findAll('footnoteid')
        
        for footnote in footnotes:
            fId = footnote.get('id')
            query = "select footNote from form4footNote where accNum='"+ accNum + "' and fId = '"+ fId +"' and footNoteField = '" + field + "';" 

            matches = cur.execute(query).fetchall() #grouped by [(aAcc, bAcc)]
            dic[fId] = matches[0][0]

# Given list fourA, print possible form 4 form each form fourA along with probability distribution
# See comment if only want to return top match
### compare just head; using rownumber and dictionary fields
def get4ATo4Matches(fourA):
    aTo4 = dict()
    for idx in range(len(fourA)):
        aHead = databaseOps.getRows(cur, fourA[idx], "form4Head")
        query = "select B.accNum as bAcc from(select * from form4head group by accNum) A, (select * from form4head group by accNum) B where A.accNum='"+ fourA[idx] + "' and B.documentType = '4' and A.dateOfOriginalSubmission = B.filedDate;" 

        matches = cur.execute(query).fetchall()

        if len(matches) < 1:
            print("No clear match for ", fourA[idx])
            continue

        probDist = dict()
        headScores, totalScores = dict(), dict()
        for match in matches:
            bAcc = match[0]
            bHead = databaseOps.getRows(cur, bAcc, "form4Head")

            mHeadScores = np.zeros(len(bHead))

            for aRow in aHead:
                for bIdx in range(len(bHead)):
                    bRow = bHead[bIdx]
                    if aRow['rowNumber'] == bRow['rowNumber']:
                        mHeadScores[bIdx] = compareByCols(aRow, bRow)    

            totalScore = sum(mHeadScores)
            headScores[bAcc], totalScores[bAcc] = mHeadScores, totalScore

        scores = totalScores.values()
        minScore = min(scores)
        total = 0
        for key in totalScores.keys():
            if minScore < 0:
                totalScores[key] += abs(minScore) + 0.0000000000001 #prevent from nan
            total += totalScores[key]
        for key in totalScores.keys():
            probDist[key] = totalScores[key]/total 

        # TODO: Only keep top possible match
        aTo4[fourA[idx]] = max(probDist, key=probDist.get)

        # TODO: Uncomment if want to see probability distribution of possible matches (based on head fields only)
#         values = sorted(probDist.values(), reverse=True)
#         aTo4[fourA[idx]] = dict()
#         for key in probDist.keys():
#             if probDist[key] in values[:4]: #only show top 4
#                 aTo4[fourA[idx]][key] = probDist[key]

    #print(json.dumps(aTo4, indent=2))
    return aTo4

# Given list of fourAs, find most likely form 4 for each fourA, then describe changes between 4 and 4/A
def get4ATo4Changes(fourAs):
    diff = dict()
    for idxx in range(len(fourAs)):
        fourA = fourAs[idxx]

        aHead = databaseOps.getRows(cur, fourA, "form4Head")

        aDTT = databaseOps.getRows(cur, fourA, "form4dT", "transaction")
        aDTH = databaseOps.getRows(cur, fourA, "form4dT", "holding")
        aNDTT = databaseOps.getRows(cur, fourA, "form4ndT", "transaction")    
        aNDTH = databaseOps.getRows(cur, fourA, "form4ndT", "holding")

        aTransacs = [aDTT, aDTH, aNDTT, aNDTH]
        labels = ["dt", "dt", "ndt", "ndt"]
        tblFields = [dtFields, dtFields, ndtFields, ndtFields]
        identifiers = ["dTId", "dTId", "nDTId", "nDTId"]

        aFoot = databaseOps.getRows(cur, fourA, "form4footnote")    

        query = "select B.accNum as bAcc from form4head A, form4head B where A.accNum='"+ fourA + "' and B.documentType = '4' and A.dateOfOriginalSubmission = B.filedDate and A.rptOwnerName = B.rptOwnerName;" 

        matches = cur.execute(query).fetchall() #grouped by [(aAcc, bAcc)]

        if len(matches) < 1:
            print("No clear match for ", fourAs[idxx])
            continue

        matchDiff, lenChanges = dict(), 0
        for match in matches:
            four = match[0]

            bHead = databaseOps.getRows(cur, four, "form4Head")

            bDTT = databaseOps.getRows(cur, four, "form4dT", "transaction")
            bDTH = databaseOps.getRows(cur, four, "form4dT", "holding")
            bNDTT = databaseOps.getRows(cur, four, "form4ndT", "transaction")    
            bNDTH = databaseOps.getRows(cur, four, "form4ndT", "holding")        

            bFoot = databaseOps.getRows(cur, four, "form4footnote")
            bTransacs = [bDTT, bDTH, bNDTT, bNDTH]

            thisMatchDiff = dict() 
            #what field changed in head, dt, ndt, footnote??
            thisMatchDiff["head"], thisMatchDiff["dt"], thisMatchDiff["ndt"] = dict(), dict(), dict()
            for aRow in aHead:
                for bRow in bHead:
                    if aRow['rowNumber'] == bRow['rowNumber']:
                        changedFields = getChangedFields(aRow, bRow, headFields)
                        if len(changedFields) != 0:
                            thisMatchDiff["head"][aRow['rowNumber']] = changedFields
                        break

            for idx in range(len(aTransacs)):
                aTransac, bTransac = aTransacs[idx], bTransacs[idx]
                label, fields, identifier = labels[idx], tblFields[idx], identifiers[idx]
                if len(aTransac) != 0:
                    if len(aTransac) == len(bTransac):            
                        for aRow in aTransac:
                            for bRow in bTransac:
                                if aRow['rowNumber'] == bRow['rowNumber']:
                                    changedFields = getChangedFields(aRow, bRow, fields, aRow['accNum'], bRow['accNum'])
                                    if len(changedFields) != 0:
                                        thisMatchDiff[label][str(aRow['rowNumber']) + '-' + aRow['type']] = changedFields
                                    break
                    elif len(bTransac) == 0:
                        for aRow in aTransac:
                            thisMatchDiff[label][str(aRow['rowNumber']) + '-' + aRow['type']] = getChangedFields(aRow, None, fields, aRow['accNum'])
                    else:
                        probDist = getMatchProbDist(aTransac, bTransac, identifier) #4/a, 4
                        optMatches, unmatched = getOptMatches(probDist) #get matches

                        if len(optMatches) < 1:
                            print("No clear match for ", fourAs[idxx])
                            continue

                        matchA = [match[0] for match in optMatches]
                        matchB = [match[1] for match in optMatches]

                        unMatchedRows = [aRow for aRow in aTransac if aRow[identifier] in unmatched]

                        for matchIdx in range(len(optMatches)):
                            #find full row corresponding to aRows[matchIdx]
                            aRow, bRow = None, None

                            for aT in aTransac:
                                if aT[identifier] == matchA[matchIdx]:
                                    aRow = aT
                                    break
                            for bT in bTransac:
                                if bT[identifier] == matchB[matchIdx]:
                                    bRow = bT
                                    break

                            changedFields = getChangedFields(aRow, bRow, fields, aRow['accNum'], bRow['accNum'])
                            if len(changedFields) != 0:
                                thisMatchDiff[label][str(aRow['rowNumber']) + '-' + aRow['type']] = changedFields
                        for aRow in unMatchedRows:
                            thisMatchDiff[label][str(aRow['rowNumber']) + '-' + aRow['type']] = getChangedFields(aRow, None, fields, aRow['accNum'])
            #matchDiff[four] = thisMatchDiff #display changes with all possible 4's

            #only display best matched form 4
            thisLenChanges = len(thisMatchDiff["head"]) + len(thisMatchDiff["dt"]) + len(thisMatchDiff["ndt"])
            if matchDiff == {} or (matchDiff != {} and thisLenChanges < lenChanges):
                thisMatchDiff["accNum"] = four
                matchDiff = thisMatchDiff
                lenChanges = thisLenChanges  

        diff[fourA] = matchDiff
    #print(json.dumps(diff, indent=2))
    return diff

headFields = getHeadFields()
headDropField = ['filedDate', 'dateOfOriginalSubmission', 'accNum', 'headId', 'documentType', 'rptOwnerFormType', 'changedDate', 'rptOwnerFilmNum']
headFields = filterFields(headFields, headDropField)

ndtFields = getNDTFields()
ndtDropField = ['accNum', 'nDTId', 'footNoteId', 'rowNumber', 'type', 'documentType']
ndtFields = filterFields(ndtFields, ndtDropField)
dtFields = getDTFields()

dtDropField = ['accNum', 'dTId', 'footNoteId', 'rowNumber', 'type', 'documentType']
dtFields = filterFields(dtFields, dtDropField)

footFields = getFootFields()
footDropField = ['accNum', 'fId', 'footNoteId', 'rowNumber', 'type', 'documentType']
footFields = filterFields(footFields, footDropField)

