"""
General utility functions
"""

### Not used, see fileds.filterFields instead
# def filterFields(allFields, dropFields):
#     fields = allFields.replace("\n", "").split(",")
#     fields = [field.split(" ")[0] for field in fields]
#     fields = [field for field in fields if field not in dropFields and field != '']
#     return fields

# Shortest edit distance (Levenstein)
def editDistance(aField, bField):
    if aField == bField:
        return 0
    n, m = len(aField), len(bField)
    if aField == "None":
        return m/m
    if bField == "None":
        return n/n
    dp = [[0 for x in range(n+1)] for x in range(m+1)] 
    for i in range(m+1): 
        for j in range(n+1):
            if i == 0: 
            	dp[i][j] = j
            elif j == 0: 
                dp[i][j] = i
            elif aField[j-1] == bField[i-1]: 
                dp[i][j] = dp[i-1][j-1] 
            else: 
                dp[i][j] = 1 + min(dp[i][j-1], dp[i-1][j], dp[i-1][j-1])    
  
    return dp[m][n]/(n+m) #normalized is better

# delete from end of bField until match beginning of aField, then add rest of aField
def naiveEdit(aField, bField):
    if aField == bField:
        return 0
    n, m = len(aField), len(bField)
    if aField == "None":
        return m/m
    if bField == "None":
        return n/n
    if (len(aField) > len(bField)):
        a, b = aField, bField
    else:
        b, a = aField, bField
    numEdits = 0
    while aField.find(bField) != 0 and len(bField) > 0:
        bField = bField[:-1]
        numEdits += 1
    numEdits += len(aField) - len(bField)
    return numEdits/(n+m)