#interpreter
import developerToolkit as dtk
import importlib
import os

codeToRun = []
importedLibariesList = []



#turns text of code into lines with tokens
def SplitCodeIntoLinesAndTokens(code):
    global codeToRun
    codeToRun = code.split("\n")
    for lineNum in range(len(codeToRun)):
        codeToRun[lineNum] = codeToRun[lineNum].split()

#returns the two's compliment of a number
def GetTwosCompliment(num):
    output = (~num) & 0xFF
    return output + 1

#performs ALU operations
def PerformALUOperation(line, lineNumber):
    match line[0]:
        case "+": #ADD
            if len(line) == 1 or len(line) == 2:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, ADDITION REQUIRES 2 ARGUMENTS, TOO FEW GIVEN")
            elif len(line) > 3:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, ADDITION REQUIRES 2 ARGUMENTS, TOO MANY GIVEN")
            else:
                dtk.result = dtk.GetValue(line[1], lineNumber) + dtk.GetValue(line[2], lineNumber)
                dtk.SetFlags()
                #set overflow
                if dtk.result >= 0x100:
                    dtk.result = dtk.result - 0x100
                    dtk.flags[4] = True  
        case "-": #SUBTRACT
            if len(line) == 1 or len(line) == 2:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, SUBTRACTION REQUIRES 2 ARGUMENTS, TOO FEW GIVEN")
            elif len(line) > 3:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, SUBTRACTION REQUIRES 2 ARGUMENTS, TOO MANY GIVEN")
            else:
                dtk.result = dtk.GetValue(line[1], lineNumber) + GetTwosCompliment(dtk.GetValue(line[2], lineNumber))
                dtk.SetFlags()
                #set carry
                if dtk.result >= 0x100:
                    dtk.result = dtk.result - 0x100
                    dtk.flags[0] = True
        case "&": #AND
            if len(line) == 1 or len(line) == 2:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, AND REQUIRES 2 ARGUMENTS, TOO FEW GIVEN")
            elif len(line) > 3:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, AND REQUIRES 2 ARGUMENTS, TOO MANY GIVEN")
            else:
                dtk.result = dtk.GetValue(line[1], lineNumber) & dtk.GetValue(line[2], lineNumber)
                dtk.result = dtk.result & 0xff
                dtk.SetFlags()
        case "|": #OR
            if len(line) == 1 or len(line) == 2:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, OR REQUIRES 2 ARGUMENTS, TOO FEW GIVEN")
            elif len(line) > 3:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, OR REQUIRES 2 ARGUMENTS, TOO MANY GIVEN")
            else:
                dtk.result = dtk.GetValue(line[1], lineNumber) | dtk.GetValue(line[2], lineNumber)
                dtk.result = dtk.result & 0xff
                dtk.SetFlags()
        case "^": #XOR
            if len(line) == 1 or len(line) == 2:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, XOR REQUIRES 2 ARGUMENTS, TOO FEW GIVEN")
            elif len(line) > 3:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, XOR REQUIRES 2 ARGUMENTS, TOO MANY GIVEN")
            else:
                dtk.result = dtk.GetValue(line[1], lineNumber) ^ dtk.GetValue(line[2], lineNumber)
                dtk.result = dtk.result & 0xff
                dtk.SetFlags()
        case "~": #TWO'S COMPLIMENT
            print("here")
            if len(line) == 1:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, TWO'S COMPLIMENT REQUIRES 1 ARGUMENT, NONE GIVEN")
            elif len(line) > 2:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, TWO'S COMPLIMENT REQUIRES 1 ARGUMENT, TOO MANY GIVEN")
            else:
                dtk.result = GetTwosCompliment(dtk.GetValue(line[1], lineNumber))
                dtk.SetFlags()
        case "!": #NOT
            if len(line) == 1:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, NOT REQUIRES 1 ARGUMENT, NONE GIVEN")
            elif len(line) > 2:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, NOT REQUIRES 1 ARGUMENT, TOO MANY GIVEN")
            else:
                dtk.result = ~dtk.GetValue(line[1], lineNumber)
                dtk.result = dtk.result & 0xff
                dtk.SetFlags()
        case ">": #RIGHT SHIFT
            if len(line) == 1:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, RIGHT SHIFT REQUIRES 1 ARGUMENT, NONE GIVEN")
            elif len(line) > 2:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, RIGHT SHIFT REQUIRES 1 ARGUMENT, TOO MANY GIVEN")
            else:
                val = dtk.GetValue(line[1], lineNumber)
                result = val >> 1
                result = result & 0xff
                dtk.SetFlags()
                #set carry
                if val%2 == 1:
                    dtk.flags[0] = True
        case "<": #LEFT SHIFT
            if len(line) == 1:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, RIGHT SHIFT REQUIRES 1 ARGUMENT, NONE GIVEN")
            elif len(line) > 2:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, RIGHT SHIFT REQUIRES 1 ARGUMENT, TOO MANY GIVEN")
            else:
                dtk.result = dtk.GetValue(line[1], lineNumber) << 1
                dtk.SetFlags()
                #set overflow
                if dtk.result >= 0x100:
                    dtk.result = dtk.result & 0xff
                    dtk.flags[4] = True
        case _:
            dtk.SendError(f"INVALID FUNCTION ON LINE {lineNumber}")

#Goes to the next instance after the starting line of a set of characters in the code
def GoToNextCharacter(startingLine, searchedCharacters):
    scopeState = 1 #counts number of openings/ closings of scopes
    currentLine = 0
    while currentLine < len(codeToRun):
        if currentLine < startingLine + 1:
            currentLine = startingLine + 1
        
        if len(codeToRun[currentLine]) >= 1:
            
            if codeToRun[currentLine][0] in searchedCharacters:
                scopeState -= 1
                if scopeState == 0:
                    return currentLine
            elif codeToRun[currentLine][0] == "?":
                scopeState+=1
        
        currentLine+=1
            
    dtk.SendError(f"UNBOUNDED SCOPE ERROR STARTING AT {startingLine}, SCOPE MUST TERMINATE WITH {searchedCharacters}")
    if scopeState > 1:
        dtk.SendError(f"UNDEFINED SCOPE ERROR STARTING AT {startingLine}, {scopeState} UNBOUNDED SCOPES")
    return 0

#Goes to the next instance after the starting line of a set of characters in the code
def GoToLabel(startingLine, labelName):
    global codeToRun
    if labelName in dtk.labelList.keys():
        return dtk.labelList[labelName]
    else:
        currentLine = 0
        while currentLine < len(codeToRun):
            if len(codeToRun[currentLine]) == 2:
                if codeToRun[currentLine][0] == "l" and codeToRun[currentLine][1] == labelName:
                    dtk.labelList.update({labelName : currentLine})
                    return currentLine
                elif codeToRun[currentLine][0] == "l":
                    dtk.labelList.update({codeToRun[currentLine][1] : currentLine})
            currentLine+=1

        dtk.SendError(f"INVALID NAME ERROR STARTING AT {startingLine}, NO SUCH LABEL \"{labelName}\"")
        return startingLine

#performs CPU operations
def PerformCPUOperation(line, lineNumber):
    match line[0]:
        case "?": #if
            if len(line) == 1:
                dtk.SendError(f"INVALID CONDITIONAL ON LINE {lineNumber}, FLAG MUST BE PRESENT")
            elif len(line) > 2 or not line[1] in ["C", "P", "N", "Z", "O"]:
                dtk.SendError(f"INVALID CONDITIONAL ON LINE {lineNumber}, INVALID FLAG CONFIGURATION, FLAG MUST BE ONE OF C, P, N, Z, O")
            else:
                carryState = (line[1] == "C") and dtk.flags[0]
                parityState = (line[1] == "P") and dtk.flags[1]
                negativeState = (line[1] == "N") and dtk.flags[2]
                zeroState = (line[1] == "Z") and dtk.flags[3]
                overflowState = (line[1] == "O") and dtk.flags[4]
                dtk.lineBackUpList.append(GoToNextCharacter(lineNumber, ["_"]))
                if not (carryState or parityState or negativeState or zeroState or overflowState):
                    return GoToNextCharacter(lineNumber, [":", "_"])
                else:
                    return lineNumber
        case ":": #else bracket
            return GoToNextCharacter(lineNumber, ["_"])
        case "l": #label
            if len(line) == 1:
                dtk.SendError(f"INVALID NAME ERROR ON LINE {lineNumber}, LABEL MUST HAVE A NAME")
            elif len(line) > 2:
                dtk.SendError(f"INVALID NAME ERROR ON LINE {lineNumber}, LABEL NAME MUST BE A CONTINUOUS STRING")
            else:
                if line[1] in dtk.labelList.keys():
                    if not dtk.labelList[line[1]] == lineNumber:
                        dtk.SendError(f"INVALID NAME ERROR ON LINE {lineNumber}, NAME MUST BE UNIQUE, NAME \"{line[1]}\" ALREADY EXISTS")
                else:
                    dtk.labelList.update({line[1] : lineNumber})
            return lineNumber
        case "g": # go to
            if len(line) == 1:
                dtk.SendError(f"INVALID NAME ERROR ON LINE {lineNumber}, GOTO MUST HAVE A NAME")
            elif len(line) > 2:
                dtk.SendError(f"INVALID NAME ERROR ON LINE {lineNumber}, NAME MUST BE CONTINUOUS STRING")
            else:
                return GoToLabel(lineNumber, line[1])
        case "f": #function
            if len(line) == 1:
                dtk.SendError(f"INVALID NAME ERROR ON LINE {lineNumber}, FUNCTION MUST HAVE A NAME")
            elif len(line) > 2:
                dtk.SendError(f"INVALID NAME ERROR ON LINE {lineNumber}, FUNCTION NAME MUST BE A CONTINUOUS STRING")
            else:
                if line[1] in dtk.functionList.keys():
                    if not dtk.functionList[line[1]] == lineNumber:
                        dtk.SendError(f"INVALID NAME ERROR ON LINE {lineNumber}, NAME MUST BE UNIQUE, NAME \"{line[1]}\" ALREADY EXISTS")
                else:
                    dtk.functionList.update({line[1] : lineNumber})
                    return GoToNextCharacter(lineNumber, ["_"])
        case "x": #execute function
            if len(line) == 1:
                dtk.SendError(f"INVALID NAME ERROR ON LINE {lineNumber}, EXECUTE MUST HAVE A NAME")
            elif len(line) > 2:
                dtk.SendError(f"INVALID NAME ERROR ON LINE {lineNumber}, FUNCTION NAME MUST BE CONTINUOUS STRING")
            else:
                if line[1] in dtk.functionList.keys():
                    dtk.lineBackUpList.append(lineNumber)
                    return dtk.functionList[line[1]]
                else:
                    dtk.SendError(f"INVALID NAME ERROR ON LINE {lineNumber}, FUNCTION NAME DOES NOT EXIST")
                    return lineNumber
        case "_": #end scope
            if len(line) >= 2:
                dtk.SendError(f"INVALID SCOPE ERROR ON LINE {lineNumber}, \"_\" CANNOT CONTAIN ANY OTHER CHARACTERS")
            elif len(dtk.lineBackUpList) > 0:
                return dtk.lineBackUpList.pop()
            else:
                return lineNumber       
        case _:
            return lineNumber

#checks if a given memory location is valid
def CheckMemoryLoc(memoryString, lineNumber):
    if len(memoryString) > 4 or len(memoryString) < 4:
        dtk.SendError(f"INVALID MEMORY LOCATION ON LINE {lineNumber}, MEMORY LOCATION MUST BE INDEXED WITH 4 HEX DIGITS")
        return False
    else:
        if dtk.ContainsHEXDigits(memoryString):
            return True
        else:
            dtk.SendError(f"INVALID MEMORY LOCATION ON LINE {lineNumber}, MEMORY LOCATION MUST BE INDEXED WITH 4 HEX DIGITS")
            return False

#allocates, modifies, and removes memory     
def PerformMemoryOperation(line, lineNumber):
    match line[0]:
        case "*": #allocate memory
            if len(line) < 3:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, VARIBALE DECLARATION REQUIRES 2 ARGUMENTS, TOO FEW GIVEN")
            elif len(line) > 3:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, VARIBALE DECLARATION REQUIRES 2 ARGUMENTS, TOO MANY GIVEN")
            else:
                if CheckMemoryLoc(line[2], lineNumber):
                    memLoc = int(line[2], 16)
                    if not line[1] in dtk.reservedTokens:
                        if not memLoc in dtk.allocatedMemoryList.keys():
                            dtk.allocatedMemoryList.update({memLoc: 0})
                        dtk.variableList.update({line[1] : memLoc})
                    else:
                        dtk.SendError(f"INVALID NAME ERROR ON LINE {lineNumber}, VARIBALE NAME CANNOT BE \"{line[1]}\", TOKEN ALREADY RESERVED")
        case "=": #set to
            if len(line) < 3:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, SET REQUIRES 2 ARGUMENTS, TOO FEW GIVEN")
            elif len(line) > 3:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, SET REQUIRES 2 ARGUMENTS, TOO MANY GIVEN")
            else:
                if line[1] in dtk.variableList.keys():
                    dtk.allocatedMemoryList.update({dtk.variableList[line[1]]: dtk.GetValue(line[2], lineNumber)})
                else:
                    dtk.SendError(f"INVALID VARIABLE NAME ON LINE {lineNumber}, VARIABLE NAME DOES NOT EXIST")
        case "*+": #increase memory loc
            if len(line) < 3:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, ADVANCE MEM REQUIRES 2 ARGUMENTS, TOO FEW GIVEN")
            elif len(line) > 3:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, DEADVANCE MEM REQUIRES 2 ARGUMENTS, TOO MANY GIVEN")
            else:
                if line[1] in dtk.variableList.keys():
                    if CheckMemoryLoc(line[2], lineNumber):
                        newLoc = int(dtk.variableList[line[1]]) + int(line[2], 16)
                        if newLoc <= 0xffff and newLoc >= 0:
                            if not newLoc in dtk.allocatedMemoryList.keys():
                                dtk.allocatedMemoryList.update({newLoc: 0})
                            dtk.variableList.update({line[1] : newLoc})
                        else: dtk.SendError(f"INVALID VARIABLE REALLOCATION ON LINE {lineNumber}, NEW LOCATION OUTSIDE OF MEMORY BOUNDS")
                else:
                    dtk.SendError(f"INVALID VARIABLE NAME ON LINE {lineNumber}, VARIABLE NAME DOES NOT EXIST")
        case "*-": #decrease memory loc
            if len(line) < 3:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, ADVANCE MEM REQUIRES 2 ARGUMENTS, TOO FEW GIVEN")
            elif len(line) > 3:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, DEADVANCE MEM REQUIRES 2 ARGUMENTS, TOO MANY GIVEN")
            else:
                if line[1] in dtk.variableList.keys():
                    if CheckMemoryLoc(line[2], lineNumber):
                        newLoc = int(dtk.variableList[line[1]]) - int(line[2], 16)
                        if newLoc <= 0xffff and newLoc >= 0:
                            if not newLoc in dtk.allocatedMemoryList.keys():
                                dtk.allocatedMemoryList.update({newLoc: 0})
                            dtk.variableList.update({line[1] : newLoc})
                        else: dtk.SendError(f"INVALID VARIABLE REALLOCATION ON LINE {lineNumber}, NEW LOCATION OUTSIDE OF MEMORY BOUNDS")
                else:
                    dtk.SendError(f"INVALID VARIABLE NAME ON LINE {lineNumber}, VARIABLE NAME DOES NOT EXIST")
        case "d": #delete variable
            if len(line) < 2:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, ADVANCE MEM REQUIRES 2 ARGUMENTS, TOO FEW GIVEN")
            elif len(line) > 2:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, DEADVANCE MEM REQUIRES 2 ARGUMENTS, TOO MANY GIVEN")
            else:
                if line[1] in dtk.variableList.keys():
                    dtk.variableList.pop(line[1])
                else:
                    dtk.SendError(f"INVALID VARIABLE NAME ON LINE {lineNumber}, VARIABLE NAME DOES NOT EXIST")

#reads input and gives output to user
def PerformIOOperation(line, lineNumber):
    match line[0]:
        case "unout": #unsigned out
            if len(line) == 1:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, UNOUT REQUIRES 1 ARGUMENT, NONE GIVEN")
            elif len(line) > 2:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, UNOUT REQUIRES 1 ARGUMENT, TOO MANY GIVEN")
            else:
                print(dtk.GetValue(line[1], lineNumber), end="\0")
        case "snout": #signed out
            if len(line) == 1:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, SNOUT REQUIRES 1 ARGUMENT, NONE GIVEN")
            elif len(line) > 2:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, SNOUT REQUIRES 1 ARGUMENT, TOO MANY GIVEN")
            else:
                val = dtk.GetValue(line[1], lineNumber)
                if val > 128:
                    print(-1*GetTwosCompliment(val), end="\0")
                elif val == 128:
                    print(128, end="\0")
                else:
                    print(val, end="\0")
        case "cout": #character out
            if len(line) == 1:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, COUT REQUIRES 1 ARGUMENT, NONE GIVEN")
            elif len(line) > 2:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, COUT REQUIRES 1 ARGUMENT, TOO MANY GIVEN")
            else:
                val = dtk.GetValue(line[1], lineNumber)
                print(chr(val), end="\0")
        case "strout":
            if len(line) == 1:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, STROUT REQUIRES 1 ARGUMENT, NONE GIVEN")
            else:
                outputString = ""
                for stringIndex in range(len(line)):
                    if stringIndex != 0 and stringIndex != len(line)-1: 
                        outputString+=line[stringIndex]+" "
                    elif stringIndex == len(line)-1:
                        outputString+=line[stringIndex]
                print(outputString.replace("[endl]", "\n"), end="\0")
        case "nin": #numeric in
            if len(line) == 1:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, NIN REQUIRES 1 ARGUMENT, NONE GIVEN")
            elif len(line) > 2:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, NIN REQUIRES 1 ARGUMENT, TOO MANY GIVEN")
            else:
                enteredValue = input()
                if enteredValue.isdecimal():
                    enteredValue = int(enteredValue) & 0xff
                else:
                    enteredValue = 0
                
                if line[1] in dtk.variableList.keys():
                    dtk.allocatedMemoryList.update({dtk.variableList[line[1]]: enteredValue})
                else:
                    dtk.SendError(f"INVALID VARIABLE NAME ON LINE {lineNumber}, VARIABLE NAME DOES NOT EXIST")
        case "cin": #character in
            if len(line) == 1:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, NIN REQUIRES 1 ARGUMENT, NONE GIVEN")
            elif len(line) > 2:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, NIN REQUIRES 1 ARGUMENT, TOO MANY GIVEN")
            else:
                enteredValue = input()
                if len(enteredValue) > 1:
                    enteredValue = enteredValue[0]
                
                if line[1] in dtk.variableList.keys():
                    dtk.allocatedMemoryList.update({dtk.variableList[line[1]]: ord(enteredValue) & 0xff})
                else:
                    dtk.SendError(f"INVALID VARIABLE NAME ON LINE {lineNumber}, VARIABLE NAME DOES NOT EXIST")
        case "strin": #string in
            if len(line) == 1:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, STRIN REQUIRES 1 ARGUMENT, NONE GIVEN")
            elif len(line) > 2:
                dtk.SendError(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, STRIN REQUIRES 1 ARGUMENT, TOO MANY GIVEN")
            else:
                enteredValue = input()
                startingMemoryLoc = "" #memory location where input is placed

                if line[1] in dtk.variableList.keys():
                    startingMemoryLoc = dtk.variableList[line[1]]
                elif dtk.ContainsHEXDigits(line[1]) and len(line) == 4:
                    startingMemoryLoc = int(line[1], 16)
                else:
                    dtk.SendError(f"INVALID VARIABLE NAME ON LINE {lineNumber}, VARIABLE NAME DOES NOT EXIST")
                
                if startingMemoryLoc != "":
                    startingMemoryLoc -= 1
                    for char in enteredValue:
                        startingMemoryLoc+=1
                        if startingMemoryLoc > 0xffff:
                            dtk.SendError(f"INVALID MEMORY LOCATION ON LINE {lineNumber}, MEMORY OVERFLOW")
                            break
                        dtk.allocatedMemoryList.update({startingMemoryLoc : ord(char) & 0xff})


#adds a library to list
def AddLibrary(line, lineNumber):
    global importedLibariesList
    if len(line) == 1:
        dtk.SendError(f"LIBRARY INCLUDE ERROR ON LINE {lineNumber}, NO LIBRARY NAME GIVEN")
    elif len(line) > 2:
        dtk.SendError(f"LIBRARY INCLUDE ERROR ON LINE {lineNumber}, ONLY ONE LIBRARY NAME ALLOWED")
    else:
        if os.path.isfile(line[1]+".py"):
            lib = importlib.import_module(line[1])
            if "exec_lib" in dir(lib):
                importedLibariesList.append(line[1])
        else:
           dtk.SendError(f"LIBRARY INCLUDE ERROR ON LINE {lineNumber}, NO SUCH LIBRARY EXISTS") 
            
#runs and executes the interpretor
def RunInterpreter(code):
    global codeToRun, importedLibariesList

    SplitCodeIntoLinesAndTokens(code)
    
    print(codeToRun)
    lineNumber = 0

    while lineNumber < len(codeToRun):
        line = codeToRun[lineNumber]
        if len(line) != 0:
            if line[0] in ["+", "-", "&", "|", "^", "!", "~", ">", "<"]: #ALU OPERATIONS
                PerformALUOperation(line, lineNumber)
            elif line[0] in ["?", ":", "f", "x", "l", "g", "_"]: #CPU OPERATIONS
                newLine = PerformCPUOperation(line, lineNumber)
                lineNumber = newLine
            elif line[0] in ["=", "*", "*+", "*-"]: #MEMORY OPERATIONS
                PerformMemoryOperation(line, lineNumber)
            elif line[0] in ["cout", "unout", "snout", "strout", "cin", "nin", "strin"]: #INPUT AND OUTPUT
                PerformIOOperation(line, lineNumber)
            elif line[0] == "#": #COMMENT
                continue
            elif line[0] == "import": #IMPORT LIBRARY
                AddLibrary(line, lineNumber)
            elif line[0] in importedLibariesList: #EXECUTE FUNCTION IN LIBRARY
                try:
                    importlib.import_module(line[0]).exec_lib(line, lineNumber)
                except:
                    dtk.SendError(f"LIBRARY ERROR ON LINE {lineNumber}, INVALID 'exec_lib' FUNCTION IN LIBRARY {line[0]}")

        if dtk.abortProgram:
            break
        else:
            lineNumber+=1