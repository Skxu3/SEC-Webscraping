# SEC-Webscraping
- Research project for Haas

Pipeline
0. (fetch idx files)
1. Script.py: Fetch html files, parse information, and populate database
2. Matching.py: Go through database and find potential form 4 & form 4/a matches, return matches in form of changeJson
3. Analyze.py: Analyze the changes between matches of form 4 and 4/a, vectorize metadata of changes as labels
4. Predict.ipynb: Takes in data and labels as created by analyze.py, preprocess data, then feed data into classifiers

File structure
- analyze.py: includes functions to perform basic analysis on dictionary of changes
    - runAnalysis: run analysis on dictionary of changes
    - getAllAnalyses: return all analyses dictionaries
    - getLabels: convert the metadata created from analysis to labels

- databaseOps.py: includes functions to interact with database
    - connectToDb
    - createTable
    - insertToTable
    - getRows
    
- matching.py: functions to match form 4 and form 4/a
    - get4ATo4Matches: Given list fourA, return possible form 4 form each form fourA (optionally return top 4 best form 4s)
    - get4ATo4Changes: Given list of fourAs, find most likely form 4 for each fourA, then describe changes between 4 and 4/A

- fields.py: includes fields for database tables, parser, and analysis

- parsing.py: parser class. parses xml file and store fields into tables form4Head, form4ndt, form4dt, and form4footNote

- script.py: reads in .idx file, iterates through list of accession numbers and fetches xml file for each form, then uses parser to parse each form and store fields into database

- utility.py: general utility functions
    - editDistance: calculate shortest Levenstein edit distance
    - naiveEdit: naive edit distance; delete from end of bField until match beginning of aField, then add rest of aField
    
