random var: have prob of being a certain value (->prob dist)
- each 4/a's match = random var: have prob of being a certain form 4
	- sum of prob = 1

"""
for each 4/a, try to find original 4:
	run loose filter to get list of possible 4
	for each possible match 4, score it: ex 4/10
		score = # matches in header/dt/ndt


		for the ones that dont match (unit length normalization???)
		score =  levenshtein/edit distance: http://www.kodyaz.com/articles/fuzzy-string-matching-using-levenshtein-distance-sql-server.aspx
			- func: smaller the score the closer the match 
			-  run on every pair of field values
		score = ????
			more matches the better
			lower avg edit dist?? or sum of edit dist

	create prob dist of match [form 4 accNum: prob]
	- prob sum to 1

- compare(aRows, bRows)
	match w row number
"""
fourA = [list of accNum]

aHead = cur.execute("select * from form4Head where accNum = '" + fourA[i]+ "';").fetchall()
aDT = cur.execute("select * from form4dT where accNum = '" + fourA[i]+ "';").fetchall()
aNDT = cur.execute("select * from form4ndT where accNum = '" + fourA[i]+ "';").fetchall()

query = ""

matches = cur.execute(query).fetchall() #grouped by [(aAcc, bAcc)]
probDist = []
headScores, dtScores, ndtScores = [], [], []
for match in matches:	
	bAcc = match[1]
	
	bHead = cur.execute("select * from form4Head where accNum = '" + bAcc + "';").fetchall()

	bDT = cur.execute("select * from form4dT where accNum = '" + bAcc + "';").fetchall()
	bNDT = cur.execute("select * from form4ndT where accNum = '" + bAcc + "';").fetchall()

	headScore, dtScore, ndtScore = compare(aHead, bHead), compare(aDT, bDT), compare(aNDT, bNDT)
	headScores.append(headScore)
	dtScores.append(dtScore)
	ndtScores.append(ndtScore)

probDist[match] = prob


def score(aRows, bRows):
	numMatches, editDist, naiveDist = compare(aRows, bRows)
	score = numMatches - editDist - naiveDist
	return score/len(aRows)

# rows need to be ordered by row num
def compare(aRows, bRows):
	numMatches = 0
	editDists, naiveDists = [], []
	for j in range(len(aRows)):
		aFields, bFields = aRows[j], bRows[j]
		numMatches += sum([1 for i in range(len(aFields)) if aFields[i] == bFields[i]])
		editDists.append([editDistance(aFields[i], bFields[i]) for i in range(len(aFields))])
		naiveDists.append([naiveEdit(aFields[i], bFields[i]) for i in range(len(aFields))])
	return numMatches, editDists, naiveDists

# Shortest edit distance (Levenstein)
def editDistance(aField, bField):
	n, m = len(aField), len(bField)
	dp = [[0 for x in range(n+1)] for x in range(m+1)] 

    for i in range(m+1): 
        for j in range(n+1):
            if i == 0: 
            	dp[i][j] = j
            elif j == 0: 
                dp[i][j] = i
            elif str1[i-1] == str2[j-1]: 
                dp[i][j] = dp[i-1][j-1] 
            else: 
                dp[i][j] = 1 + min(dp[i][j-1], dp[i-1][j], dp[i-1][j-1])    
  
    return dp[m][n] 

# delete from end of bField until match beginning of aField, then add rest of aField
def naiveEdit(aField, bField):
    if (len(aField) > len(bField)):
        a, b = aField, bField
    else:
        b, a = aField, bField
    numEdits = 0
    while aField.find(bField) != 0 and len(bField) > 0:
        bField = bField[:-1]
        numEdits += 1
    numEdits += len(aField) - len(bField)
    return numEdits
