import string 

abortProgram = False
result = 0
flags = [False, False, False, False, False] #order = carry, parity, negative, zero, overflow
reservedTokens = ("+", "-", "&", "|", "^", "!", "~", ">", 
                  "<", "?", ":", "f", "x", "l", "g", "_", 
                  "=", "*", "*+", "*-", "R", "C", "P", "N", 
                  "Z", "O") #contains list of every reserved token
labelList = {} #contains all labels and their line number
functionList = {} #contains all labels and their line number
lineBackUpList = [] #contains list of lines to return to after function finishes executing
allocatedMemoryList = {} #contains list of all allocated memory locations
variableList = {} #contains list of every vairable and their memory location

#sends an error message and ends the program
def SendError(message):
    global abortProgram
    abortProgram = True
    print(message)

#checks if string s only contains hex digits
def ContainsHEXDigits(s):
    return all(ch in string.hexdigits for ch in s)

#interprates values
def GetValue(numberAsString, lineNumber):
    global result, variableList, allocatedMemoryList
    if ContainsHEXDigits(numberAsString) and len(numberAsString) == 2:
        return(int(numberAsString, 16))
    elif numberAsString == "R":
        return result
    elif numberAsString in variableList.keys():
        return allocatedMemoryList[variableList[numberAsString]]
    else:
        SendError(f"INVALID ARGUMENT ON LINE {lineNumber}, ARGUMENT MUST BE MEMORY LOCATION OR 2 DIGIT HEX STRING")
        return 0

#sets flags after an operation
def SetFlags():
    global flags
    flags = [False, False, False, False, False] #reset
    #set parity flag
    flags[1] = (result%2 == 1)
    #set negative flag
    flags[2] = (result&0x80 == 0x80)

    #set zero flag
    flags[3] = (result&0xff == 0)