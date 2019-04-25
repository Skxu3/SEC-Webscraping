import databaseOps, fields, utility
import numpy as np
import matplotlib.pyplot as plt
import json, copy
from bs4 import BeautifulSoup, Tag
from datetime import datetime as dt
from sklearn.feature_extraction import DictVectorizer
from pprint import pprint
from fields import numerical, categorical, typedCategorical, date, formPortion, dataType, categoricalAnalysisType, changeTypeVect, dataTypeVect

### Functions to perform basic analysis on dictionary of changes
def getCatAnalysis(changedFieldName, beforeVal, afterVal):
    catAnalysis = dict()
    catAnalysis["dataType"] = "categorical"
    catAnalysis["fieldName"] = changedFieldName
    
    if beforeVal == '':
        catAnalysis["changeType"] = "insert"
    elif afterVal == "":
        catAnalysis["changeType"] = "delete"
    else:
        catAnalysis["changeType"] = "update"
        
    if changedFieldName in typedCategorical:
        catAnalysis["updateVector"] = (beforeVal, afterVal)
    else:
        catAnalysis["editDistance"] = utility.editDistance(beforeVal, afterVal)
    
    return catAnalysis

def getNumAnalysis(changedFieldName, beforeVal, afterVal):
    numAnalysis = dict()
    numAnalysis["fieldName"] = changedFieldName
    numAnalysis["dataType"] = "numerical"
    
    if beforeVal == '':
        beforeVal = 0
        numAnalysis["changeType"] = "insert"
        afterVal = float(afterVal)
    elif afterVal == '':
        afterVal = 0
        numAnalysis["changeType"] = "delete"
        beforeVal = float(beforeVal)
        
    if beforeVal != "" and afterVal != "":
        beforeVal, afterVal = float(beforeVal), float(afterVal)
    
    change = afterVal - beforeVal
    if change != 0:
        numAnalysis["amountChanged"] = change        
        if afterVal > beforeVal:
            numAnalysis["changeDirection"] = "+" 
        else:
            numAnalysis["changeDirection"] = "-" 
        numAnalysis["percentChange"] = round(abs(change)/beforeVal*100, 3)      
        numAnalysis["changeType"] = "update"
    return numAnalysis

def getFootnoteAnalysis(analysisDic, beforeFoot, afterFoot, bFootContent, aFootContent):
    if len(beforeFoot) != 0 or len(afterFoot) != 0:
        if len(beforeFoot) > len(afterFoot):
            footChangeType = "footnote in 4"
        elif len(beforeFoot) < len(afterFoot):
            footChangeType = "footnote in 4/a"
        else:
            diffCount = sum([1 for i in range(len(beforeFoot)) if bFootContent[i] != aFootContent[i]])
            if diffCount != 0:
                footChangeType = "footnote content diff"
            else:
                if beforeFoot != afterFoot:
                    footChangeType = "footnote id diff"
                else:
                    footChangeType = ""
        if footChangeType != "":
            if "changeType" in analysisDic:
                analysisDic["changeType"] = [analysisDic["changeType"], footChangeType]
            else:
                analysisDic["changeType"] = footChangeType
    return analysisDic

def getDateAnalysis(changedFieldName, beforeVal, afterVal):
    dateAnalysis = dict()
    dateAnalysis["dataType"] = "date"
    if beforeVal == "":
        dateAnalysis["changeType"] = "insert"
    if afterVal == "":
        dateAnalysis["changeType"] = "delete"
    if beforeVal != "" and afterVal != "":
        beforeDate = dt.strptime(beforeVal, "%Y-%m-%d")
        afterDate = dt.strptime(afterVal, "%Y-%m-%d")
        dateDiff = beforeDate - afterDate
        if dateDiff != 0:
            dateAnalysis["changeType"] = "update"
            if beforeDate > afterDate:
                dateAnalysis["changeDirection"] = "+" #changed date to later
            elif beforeDate < afterDate:
                dateAnalysis["changeDirection"] = "-"
            dateAnalysis["amountChanged"] = dateDiff.total_seconds()/60/60/24 #days
    return dateAnalysis

### Run analysis on dictionary of changes
def runAnalysis(fileDic):
    files = copy.deepcopy(fileDic)
    for file in files:
        changeDic = files[file]
        for portion in formPortion:
            for rowKey in list(changeDic[portion].keys()):
                row = changeDic[portion][rowKey]
                
                for changedFieldName in list(row.keys()):
                    footnoteChangeOnly = False

                    if "value" in row[changedFieldName]['4']:
                        beforeVal = row[changedFieldName]['4']['value']
                    else:
                        beforeVal = ""
                    if "value" in row[changedFieldName]['4A']:
                        afterVal = row[changedFieldName]['4A']['value'] 
                    else: 
                        afterVal = ""

                    beforeFoot, afterFoot = None, None
                    if isinstance(beforeVal, str) and ("<value>" in beforeVal or "footnoteId" in beforeVal):
                        beforeSoup = BeautifulSoup(beforeVal)
                        beforeVal = ''.join([str(val.text) for val in beforeSoup.findAll('value')])
                        beforeFoot = [footnote.get('id') for footnote in beforeSoup.findAll('footnoteid')] #soup made it lowercased
                        if beforeVal == '':
                            footnoteChangeOnly = True

                    if isinstance(afterVal, str) and ("<value>" in afterVal or "footnoteId" in afterVal):
                        afterSoup = BeautifulSoup(afterVal)
                        afterVal = ''.join([str(val.text) for val in afterSoup.findAll('value')])
                        afterFoot = [footnote.get('id') for footnote in afterSoup.findAll('footnoteid')]

                        if footnoteChangeOnly:
                            if afterVal != '':
                                footnoteChangeOnly = False

                    bFootContent = [row[changedFieldName]['4'][fid] for fid in beforeFoot]
                    aFootContent = [row[changedFieldName]['4A'][fid] for fid in afterFoot]
                        
                    if footnoteChangeOnly:
                        tempDic = dict()
                        tempDic["dataType"] = "footnote"
                        row[changedFieldName]["analysis"] = getFootnoteAnalysis(tempDic, beforeFoot, afterFoot, bFootContent, aFootContent)
                    else: 
                        if changedFieldName in categorical:
                            analysisDic = getCatAnalysis(changedFieldName, beforeVal, afterVal)
                            row[changedFieldName]["analysis"] = getFootnoteAnalysis(analysisDic, beforeFoot, afterFoot, bFootContent, aFootContent)
                        elif changedFieldName in numerical:
                            #if "footnoteId" not in beforeVal and "footnoteId" not in afterVal:
                            analysisDic = getNumAnalysis(changedFieldName, beforeVal, afterVal)
                            row[changedFieldName]["analysis"] = getFootnoteAnalysis(analysisDic, beforeFoot, afterFoot, bFootContent, aFootContent)
                        elif changedFieldName in date:
                            analysisDic = getDateAnalysis(changedFieldName, beforeVal, afterVal)
                            row[changedFieldName]["analysis"] = getFootnoteAnalysis(analysisDic, beforeFoot, afterFoot, bFootContent, aFootContent)


#     print(json.dumps(files, indent=2))
    return files

"""
Get all analyses dictionaries
- outputs: analyses, accNums, rowIds
    analyses['portion']['data'] = raw data of analyses
    analyses['portion']['metadata'] = ex: counts for categorical analyses
    accNums['portion']: list of accNums of returned analyses
    rowIds['portion']: list of rowId of returned analyses (used to index into database)
- params: 
    dataType: "categorical" | "numerical"
    analysisType: see fields of analysisDictionary (ex:"amountChanged")
    analysisSubType: ex for analysisType=changeType, analysisSubType=1
    toVect: change output['data'] to numerical values only for dictvectorizer
"""
def getAllAnalyses(files, dataType=False, analysisType=False, analysisSubType=False, toVect=False):
    analyses = {}
    analyses["dt"], analyses["ndt"] = {}, {}
    analyses["dt"]["data"], analyses["ndt"]["data"] = [], []
    if analysisType in categoricalAnalysisType:    
        analyses["dt"]["metadata"], analyses["ndt"]["metadata"] = {}, {}
        for option in categoricalAnalysisType[analysisType]:
            analyses["dt"]["metadata"][option], analyses["ndt"]["metadata"][option] = 0, 0
    
    accNums, rowIds = {}, {}
    accNums["dt"], accNums["ndt"] = [], []
    rowIds["dt"], rowIds["ndt"] = [], []
    
    files = copy.deepcopy(files)
    for file in files:
        changeDic = files[file]
        for portion in formPortion:
            for rowKey in list(changeDic[portion].keys()):
                row = changeDic[portion][rowKey]
                for changedFieldName in list(row.keys()):
                    if "analysis" in row[changedFieldName] and (not dataType or dataType == row[changedFieldName]["analysis"]["dataType"]):
                        if analysisType and (analysisType in row[changedFieldName]["analysis"]):
                            data = row[changedFieldName]["analysis"][analysisType]
                            analyses[portion]["data"].append(data)
                            if analysisType in categoricalAnalysisType:
                                if analysisType == "changeType":
                                    for changeType in data:
                                        analyses[portion]["metadata"][changeType] += 1
                                else:
                                    analyses[portion]["metadata"][data] += 1
                            
                        elif not analysisType:
                            data = row[changedFieldName]["analysis"]
                            analyses[portion]["data"].append(data)
                        accNums[portion].append(file)
                        if "-transaction" in rowKey:
                            rowIdx = rowKey.replace("-transaction", "")
                            thisRowId = file+"-"+rowIdx
                        else:
                            rowIdx = rowKey.replace("-holding", "")
                            thisRowId = file+"-"+rowIdx+"-h"
                        rowIds[portion].append(thisRowId)
    
    if toVect:
        for portion in list(analyses.keys()):
            for dic in analyses[portion]['data']:
                if type(dic["changeType"]) == list:
                    dic["changeType"] = sum([changeTypeVect[val] for val in dic["changeType"]])
                else:
                    dic["changeType"] = changeTypeVect[dic["changeType"]]
                if dic["dataType"] == "numerical":
                    dic["fieldName"] = numerical.index(dic["fieldName"])
                elif dic["dataType"] == "categorical":
                    dic["fieldName"] = categorical.index(dic["fieldName"])
                else:
                    dic["fieldName"] = date.index(dic["fieldName"])
                dic["dataType"] = dataTypeVect[dic["dataType"]]
                if "changeDirection" in dic:
                    dic["changeDirection"] = 1 if dic["changeDirection"] == "+" else 2
    return analyses, accNums, rowIds

"""
Get labels to use for training
- input: changeDictionary
- output: numLabels, catLabels 
    numLabels/catLabels[dt/ndt][labels] = label vectors
    numLabels/catLabels[dt/ndt][featureNames] = features names
    numLabels/catLabels[dt/ndt][accNums] = accNum of each data
    numLabels/catLabels[dt/ndt][rowIds] = id of each data (for database)
"""
def getLabels(jsonChanges):
    analysis = runAnalysis(jsonChanges)

    numAnalyses, numAccNums, numRowIds = getAllAnalyses(analysis, "numerical", toVect=True)
    catAnalyses, catAccNums, catRowIds = getAllAnalyses(analysis, "categorical", toVect=True)

    numDTRecords, numNDTRecords = numAnalyses["dt"]["data"], numAnalyses["ndt"]["data"]
    catDTRecords, catNDTRecords = catAnalyses["dt"]["data"], catAnalyses["ndt"]["data"]

    vect = DictVectorizer(sparse=False)
    
    numLabels = {}
    numLabels["dt"], numLabels["ndt"] = {}, {}
    numLabels["dt"]["labels"], numLabels["dt"]["featureNames"] =  np.array([]), np.array([])
    numLabels["ndt"]["labels"], numLabels["ndt"]["featureNames"] =  np.array([]), np.array([])
    catLabels = copy.deepcopy(numLabels)
    
    numLabels["dt"]["accNums"], numLabels["ndt"]["accNums"] = numAccNums['dt'], numAccNums['ndt']
    catLabels["dt"]["accNums"], catLabels["ndt"]["accNums"] = catAccNums['dt'], catAccNums['ndt']
    
    numLabels["dt"]["rowIds"], numLabels["ndt"]["rowIds"] = numRowIds['dt'], numRowIds['ndt']
    catLabels["dt"]["rowIds"], catLabels["ndt"]["rowIds"] = catRowIds['dt'], catRowIds['ndt']
    
    if len(numDTRecords) > 0:
        numLabels["dt"]["labels"] = vect.fit_transform(numDTRecords)
        numLabels["dt"]["featureNames"] = vect.get_feature_names()
    if len(numNDTRecords) > 0:
        numLabels["ndt"]["labels"] = vect.fit_transform(numNDTRecords)
        numLabels["ndt"]["featureNames"] = vect.get_feature_names()
    if len(catDTRecords) > 0:
        catLabels["dt"]["labels"] = vect.fit_transform(catDTRecords)
        catLabels["dt"]["featureNames"] = vect.get_feature_names()
    if len(catNDTRecords) > 0:
        catLabels["dt"]["labels"] = vect.fit_transform(catNDTRecords)
        catLabels["dt"]["featureNames"] = vect.get_feature_names()

    return numLabels, catLabels