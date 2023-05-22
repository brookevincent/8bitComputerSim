#interpreter
import developerToolkit as dtk
import importlib
import os

codeToRun = []
importedLibariesList = []



#turns text of code into lines with tokens
def split_code_into_lines_and_tokens(code):
    global codeToRun
    codeToRun = code.split("\n")
    for lineNum in range(len(codeToRun)):
        if "//" in codeToRun[lineNum]:
            codeToRun[lineNum] = codeToRun[lineNum].split('//', 1)[0].split()
        else:
            codeToRun[lineNum] = codeToRun[lineNum].split()



#returns the two's compliment of a number
def get_twos_compliment(num):
    output = (~num) & 0xFF
    return output + 1

#performs ALU operations
def perform_ALU_operation(line, lineNumber):
    match line[0]:
        case "ADD": #ADD
            if len(line) == 1 or len(line) == 2:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, ADDITION REQUIRES 2 ARGUMENTS, TOO FEW GIVEN")
            elif len(line) > 3:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, ADDITION REQUIRES 2 ARGUMENTS, TOO MANY GIVEN")
            else:
                dtk.result = dtk.get_value(line[1], lineNumber) + dtk.get_value(line[2], lineNumber)
                dtk.set_flags()
                #set overflow
                if dtk.result >= 0x100:
                    dtk.result = dtk.result - 0x100
                    dtk.flags[4] = True  
        case "SUB": #SUBTRACT
            if len(line) == 1 or len(line) == 2:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, SUBTRACTION REQUIRES 2 ARGUMENTS, TOO FEW GIVEN")
            elif len(line) > 3:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, SUBTRACTION REQUIRES 2 ARGUMENTS, TOO MANY GIVEN")
            else:
                dtk.result = dtk.get_value(line[1], lineNumber) + get_twos_compliment(dtk.get_value(line[2], lineNumber))
                dtk.set_flags()
                #set carry
                if dtk.result >= 0x100:
                    dtk.result = dtk.result - 0x100
                    dtk.flags[0] = True
        case "AND": #AND
            if len(line) == 1 or len(line) == 2:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, AND REQUIRES 2 ARGUMENTS, TOO FEW GIVEN")
            elif len(line) > 3:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, AND REQUIRES 2 ARGUMENTS, TOO MANY GIVEN")
            else:
                dtk.result = dtk.get_value(line[1], lineNumber) & dtk.get_value(line[2], lineNumber)
                dtk.result = dtk.result & 0xff
                dtk.set_flags()
        case "OR": #OR
            if len(line) == 1 or len(line) == 2:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, OR REQUIRES 2 ARGUMENTS, TOO FEW GIVEN")
            elif len(line) > 3:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, OR REQUIRES 2 ARGUMENTS, TOO MANY GIVEN")
            else:
                dtk.result = dtk.get_value(line[1], lineNumber) | dtk.get_value(line[2], lineNumber)
                dtk.result = dtk.result & 0xff
                dtk.set_flags()
        case "XOR": #XOR
            if len(line) == 1 or len(line) == 2:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, XOR REQUIRES 2 ARGUMENTS, TOO FEW GIVEN")
            elif len(line) > 3:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, XOR REQUIRES 2 ARGUMENTS, TOO MANY GIVEN")
            else:
                dtk.result = dtk.get_value(line[1], lineNumber) ^ dtk.get_value(line[2], lineNumber)
                dtk.result = dtk.result & 0xff
                dtk.set_flags()
        case "TCOMP": #TWO'S COMPLIMENT
            print("here")
            if len(line) == 1:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, TWO'S COMPLIMENT REQUIRES 1 ARGUMENT, NONE GIVEN")
            elif len(line) > 2:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, TWO'S COMPLIMENT REQUIRES 1 ARGUMENT, TOO MANY GIVEN")
            else:
                dtk.result = get_twos_compliment(dtk.get_value(line[1], lineNumber))
                dtk.set_flags()
        case "NOT": #NOT
            if len(line) == 1:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, NOT REQUIRES 1 ARGUMENT, NONE GIVEN")
            elif len(line) > 2:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, NOT REQUIRES 1 ARGUMENT, TOO MANY GIVEN")
            else:
                dtk.result = ~dtk.get_value(line[1], lineNumber)
                dtk.result = dtk.result & 0xff
                dtk.set_flags()
        case "RSH": #RIGHT SHIFT
            if len(line) == 1:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, RIGHT SHIFT REQUIRES 1 ARGUMENT, NONE GIVEN")
            elif len(line) > 2:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, RIGHT SHIFT REQUIRES 1 ARGUMENT, TOO MANY GIVEN")
            else:
                val = dtk.get_value(line[1], lineNumber)
                result = val >> 1
                result = result & 0xff
                dtk.set_flags()
                #set carry
                if val%2 == 1:
                    dtk.flags[0] = True
        case "LSH": #LEFT SHIFT
            if len(line) == 1:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, RIGHT SHIFT REQUIRES 1 ARGUMENT, NONE GIVEN")
            elif len(line) > 2:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, RIGHT SHIFT REQUIRES 1 ARGUMENT, TOO MANY GIVEN")
            else:
                dtk.result = dtk.get_value(line[1], lineNumber) << 1
                dtk.set_flags()
                #set overflow
                if dtk.result >= 0x100:
                    dtk.result = dtk.result & 0xff
                    dtk.flags[4] = True
        case _:
            dtk.send_error(f"INVALID FUNCTION ON LINE {lineNumber}")

#Goes to the next instance after the starting line of a set of characters in the code
def go_to_next_character(startingLine, searchedCharacters):
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
            elif codeToRun[currentLine][0] == "IF":
                scopeState+=1
        
        currentLine+=1
            
    dtk.send_error(f"UNBOUNDED SCOPE ERROR STARTING AT {startingLine}, SCOPE MUST TERMINATE WITH {searchedCharacters}")
    if scopeState > 1:
        dtk.send_error(f"UNDEFINED SCOPE ERROR STARTING AT {startingLine}, {scopeState} UNBOUNDED SCOPES")
    return 0

#Goes to the next instance after the starting line of a set of characters in the code
def go_to_label(startingLine, labelName):
    global codeToRun
    if labelName in dtk.label_list.keys():
        return dtk.label_list[labelName]
    else:
        currentLine = 0
        while currentLine < len(codeToRun):
            if len(codeToRun[currentLine]) == 2:
                if codeToRun[currentLine][0] == "LABEL" and codeToRun[currentLine][1] == labelName:
                    dtk.label_list.update({labelName : currentLine})
                    return currentLine
                elif codeToRun[currentLine][0] == "LABEL":
                    dtk.label_list.update({codeToRun[currentLine][1] : currentLine})
            currentLine+=1

        dtk.send_error(f"INVALID NAME ERROR STARTING AT {startingLine}, NO SUCH LABEL \"{labelName}\"")
        return startingLine

#performs CPU operations
def perform_CPU_operation(line, lineNumber):
    match line[0]:
        case "IF": #if
            if len(line) == 1:
                dtk.send_error(f"INVALID CONDITIONAL ON LINE {lineNumber}, FLAG MUST BE PRESENT")
            elif len(line) > 2 or not line[1] in ["CARRY", "PARITY", "NEGATIVE", "ZERO", "OVERFLOW"]:
                dtk.send_error(f"INVALID CONDITIONAL ON LINE {lineNumber}, INVALID FLAG CONFIGURATION, FLAG MUST BE ONE OF CARRY, PARITY, NEGATIVE, ZERO, OVERFLOW")
            else:
                carryState = (line[1] == "CARRY") and dtk.flags[0]
                parityState = (line[1] == "PARITY") and dtk.flags[1]
                negativeState = (line[1] == "NEGATIVE") and dtk.flags[2]
                zeroState = (line[1] == "ZERO") and dtk.flags[3]
                overflowState = (line[1] == "OVERFLOW") and dtk.flags[4]
                dtk.line_back_up_list.append(go_to_next_character(lineNumber, ["END"]))
                if not (carryState or parityState or negativeState or zeroState or overflowState):
                    return go_to_next_character(lineNumber, ["ELSE", "END"])
                else:
                    return lineNumber
        case "ELSE": #else bracket
            return go_to_next_character(lineNumber, ["END"])
        case "LABEL": #label
            if len(line) == 1:
                dtk.send_error(f"INVALID NAME ERROR ON LINE {lineNumber}, LABEL MUST HAVE A NAME")
            elif len(line) > 2:
                dtk.send_error(f"INVALID NAME ERROR ON LINE {lineNumber}, LABEL NAME MUST BE A CONTINUOUS STRING")
            else:
                if line[1] in dtk.label_list.keys():
                    if not dtk.label_list[line[1]] == lineNumber:
                        dtk.send_error(f"INVALID NAME ERROR ON LINE {lineNumber}, NAME MUST BE UNIQUE, NAME \"{line[1]}\" ALREADY EXISTS")
                else:
                    dtk.label_list.update({line[1] : lineNumber})
            return lineNumber
        case "GOTO": # go to
            if len(line) == 1:
                dtk.send_error(f"INVALID NAME ERROR ON LINE {lineNumber}, GOTO MUST HAVE A NAME")
            elif len(line) > 2:
                dtk.send_error(f"INVALID NAME ERROR ON LINE {lineNumber}, NAME MUST BE CONTINUOUS STRING")
            else:
                return go_to_label(lineNumber, line[1])
        case "FUNC": #function
            if len(line) == 1:
                dtk.send_error(f"INVALID NAME ERROR ON LINE {lineNumber}, FUNCTION MUST HAVE A NAME")
            elif len(line) > 2:
                dtk.send_error(f"INVALID NAME ERROR ON LINE {lineNumber}, FUNCTION NAME MUST BE A CONTINUOUS STRING")
            else:
                if line[1] in dtk.function_list.keys():
                    if not dtk.function_list[line[1]] == lineNumber:
                        dtk.send_error(f"INVALID NAME ERROR ON LINE {lineNumber}, NAME MUST BE UNIQUE, NAME \"{line[1]}\" ALREADY EXISTS")
                else:
                    dtk.function_list.update({line[1] : lineNumber})
                    return go_to_next_character(lineNumber, ["_"])
        case "EXEC": #execute function
            if len(line) == 1:
                dtk.send_error(f"INVALID NAME ERROR ON LINE {lineNumber}, EXECUTE MUST HAVE A NAME")
            elif len(line) > 2:
                dtk.send_error(f"INVALID NAME ERROR ON LINE {lineNumber}, FUNCTION NAME MUST BE CONTINUOUS STRING")
            else:
                if line[1] in dtk.function_list.keys():
                    dtk.line_back_up_list.append(lineNumber)
                    return dtk.function_list[line[1]]
                else:
                    dtk.send_error(f"INVALID NAME ERROR ON LINE {lineNumber}, FUNCTION NAME DOES NOT EXIST")
                    return lineNumber
        case "END": #end scope
            if len(line) >= 2:
                dtk.send_error(f"INVALID SCOPE ERROR ON LINE {lineNumber}, \"_\" CANNOT CONTAIN ANY OTHER CHARACTERS")
            elif len(dtk.line_back_up_list) > 0:
                return dtk.line_back_up_list.pop()
            else:
                return lineNumber       
        case _:
            return lineNumber

#checks if a given memory location is valid
def check_memory_loc(memoryString, lineNumber):
    if len(memoryString) > 4 or len(memoryString) < 4:
        dtk.send_error(f"INVALID MEMORY LOCATION ON LINE {lineNumber}, MEMORY LOCATION MUST BE INDEXED WITH 4 HEX DIGITS")
        return False
    else:
        if dtk.contains_HEX_digits(memoryString):
            return True
        else:
            dtk.send_error(f"INVALID MEMORY LOCATION ON LINE {lineNumber}, MEMORY LOCATION MUST BE INDEXED WITH 4 HEX DIGITS")
            return False

#allocates, modifies, and removes memory     
def perform_memory_operation(line, lineNumber):
    match line[0]:
        case "ALLOC": #allocate memory
            if len(line) < 3:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, VARIBALE DECLARATION REQUIRES 2 ARGUMENTS, TOO FEW GIVEN")
            elif len(line) > 3:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, VARIBALE DECLARATION REQUIRES 2 ARGUMENTS, TOO MANY GIVEN")
            else:
                if check_memory_loc(line[2], lineNumber):
                    memLoc = int(line[2], 16)
                    if not line[1] in dtk.reserved_tokens:
                        if not memLoc in dtk.allocated_memory_list.keys():
                            dtk.allocated_memory_list.update({memLoc: 0})
                        dtk.variable_list.update({line[1] : memLoc})
                    else:
                        dtk.send_error(f"INVALID NAME ERROR ON LINE {lineNumber}, VARIBALE NAME CANNOT BE \"{line[1]}\", TOKEN ALREADY RESERVED")
        case "SET": #set to
            if len(line) < 3:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, SET REQUIRES 2 ARGUMENTS, TOO FEW GIVEN")
            elif len(line) > 3:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, SET REQUIRES 2 ARGUMENTS, TOO MANY GIVEN")
            else:
                if line[1] in dtk.variable_list.keys():
                    dtk.allocated_memory_list.update({dtk.variable_list[line[1]]: dtk.get_value(line[2], lineNumber)})
                else:
                    dtk.send_error(f"INVALID VARIABLE NAME ON LINE {lineNumber}, VARIABLE NAME DOES NOT EXIST")
        case "PTRA": #increase memory loc
            if len(line) < 3:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, ADVANCE MEM REQUIRES 2 ARGUMENTS, TOO FEW GIVEN")
            elif len(line) > 3:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, DEADVANCE MEM REQUIRES 2 ARGUMENTS, TOO MANY GIVEN")
            else:
                if line[1] in dtk.variable_list.keys():
                    if check_memory_loc(line[2], lineNumber):
                        newLoc = int(dtk.variable_list[line[1]]) + int(line[2], 16)
                        if newLoc <= 0xffff and newLoc >= 0:
                            if not newLoc in dtk.allocated_memory_list.keys():
                                dtk.allocated_memory_list.update({newLoc: 0})
                            dtk.variable_list.update({line[1] : newLoc})
                        else: dtk.send_error(f"INVALID VARIABLE REALLOCATION ON LINE {lineNumber}, NEW LOCATION OUTSIDE OF MEMORY BOUNDS")
                else:
                    dtk.send_error(f"INVALID VARIABLE NAME ON LINE {lineNumber}, VARIABLE NAME DOES NOT EXIST")
        case "PTRD": #decrease memory loc
            if len(line) < 3:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, ADVANCE MEM REQUIRES 2 ARGUMENTS, TOO FEW GIVEN")
            elif len(line) > 3:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, DEADVANCE MEM REQUIRES 2 ARGUMENTS, TOO MANY GIVEN")
            else:
                if line[1] in dtk.variable_list.keys():
                    if check_memory_loc(line[2], lineNumber):
                        newLoc = int(dtk.variable_list[line[1]]) - int(line[2], 16)
                        if newLoc <= 0xffff and newLoc >= 0:
                            if not newLoc in dtk.allocated_memory_list.keys():
                                dtk.allocated_memory_list.update({newLoc: 0})
                            dtk.variable_list.update({line[1] : newLoc})
                        else: dtk.send_error(f"INVALID VARIABLE REALLOCATION ON LINE {lineNumber}, NEW LOCATION OUTSIDE OF MEMORY BOUNDS")
                else:
                    dtk.send_error(f"INVALID VARIABLE NAME ON LINE {lineNumber}, VARIABLE NAME DOES NOT EXIST")
        case "DEL": #delete variable
            if len(line) < 2:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, ADVANCE MEM REQUIRES 2 ARGUMENTS, TOO FEW GIVEN")
            elif len(line) > 2:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, DEADVANCE MEM REQUIRES 2 ARGUMENTS, TOO MANY GIVEN")
            else:
                if line[1] in dtk.variable_list.keys():
                    dtk.variable_list.pop(line[1])
                else:
                    dtk.send_error(f"INVALID VARIABLE NAME ON LINE {lineNumber}, VARIABLE NAME DOES NOT EXIST")

#reads input and gives output to user
def perform_IO_operation(line, lineNumber):
    match line[0]:
        case "UNOUT": #unsigned out
            if len(line) == 1:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, UNOUT REQUIRES 1 ARGUMENT, NONE GIVEN")
            elif len(line) > 2:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, UNOUT REQUIRES 1 ARGUMENT, TOO MANY GIVEN")
            else:
                print(dtk.get_value(line[1], lineNumber), end="\0")
        case "SNOUT": #signed out
            if len(line) == 1:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, SNOUT REQUIRES 1 ARGUMENT, NONE GIVEN")
            elif len(line) > 2:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, SNOUT REQUIRES 1 ARGUMENT, TOO MANY GIVEN")
            else:
                val = dtk.get_value(line[1], lineNumber)
                if val > 128:
                    print(-1*get_twos_compliment(val), end="\0")
                elif val == 128:
                    print(128, end="\0")
                else:
                    print(val, end="\0")
        case "COUT": #character out
            if len(line) == 1:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, COUT REQUIRES 1 ARGUMENT, NONE GIVEN")
            elif len(line) > 2:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, COUT REQUIRES 1 ARGUMENT, TOO MANY GIVEN")
            else:
                val = dtk.get_value(line[1], lineNumber)
                print(chr(val), end="\0")
        case "STROUT":
            if len(line) == 1:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, STROUT REQUIRES 1 ARGUMENT, NONE GIVEN")
            else:
                outputString = ""
                for stringIndex in range(len(line)):
                    if stringIndex != 0 and stringIndex != len(line)-1: 
                        outputString+=line[stringIndex]+" "
                    elif stringIndex == len(line)-1:
                        outputString+=line[stringIndex]
                print(outputString.replace("[endl]", "\n"), end="\0")
        case "NIN": #numeric in
            if len(line) == 1:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, NIN REQUIRES 1 ARGUMENT, NONE GIVEN")
            elif len(line) > 2:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, NIN REQUIRES 1 ARGUMENT, TOO MANY GIVEN")
            else:
                enteredValue = input()
                if enteredValue.isdecimal():
                    enteredValue = int(enteredValue) & 0xff
                else:
                    enteredValue = 0
                
                if line[1] in dtk.variable_list.keys():
                    dtk.allocated_memory_list.update({dtk.variable_list[line[1]]: enteredValue})
                else:
                    dtk.send_error(f"INVALID VARIABLE NAME ON LINE {lineNumber}, VARIABLE NAME DOES NOT EXIST")
        case "CIN": #character in
            if len(line) == 1:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, NIN REQUIRES 1 ARGUMENT, NONE GIVEN")
            elif len(line) > 2:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, NIN REQUIRES 1 ARGUMENT, TOO MANY GIVEN")
            else:
                enteredValue = input()
                if len(enteredValue) > 1:
                    enteredValue = enteredValue[0]
                
                if line[1] in dtk.variable_list.keys():
                    dtk.allocated_memory_list.update({dtk.variable_list[line[1]]: ord(enteredValue) & 0xff})
                else:
                    dtk.send_error(f"INVALID VARIABLE NAME ON LINE {lineNumber}, VARIABLE NAME DOES NOT EXIST")
        case "STRIN": #string in
            if len(line) == 1:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, STRIN REQUIRES 1 ARGUMENT, NONE GIVEN")
            elif len(line) > 2:
                dtk.send_error(f"INVALID NUMBER OF ARGUMENTS ON LINE {lineNumber}, STRIN REQUIRES 1 ARGUMENT, TOO MANY GIVEN")
            else:
                enteredValue = input()
                startingMemoryLoc = "" #memory location where input is placed

                if line[1] in dtk.variable_list.keys():
                    startingMemoryLoc = dtk.variable_list[line[1]]
                elif dtk.contains_HEX_digits(line[1]) and len(line) == 4:
                    startingMemoryLoc = int(line[1], 16)
                else:
                    dtk.send_error(f"INVALID VARIABLE NAME ON LINE {lineNumber}, VARIABLE NAME DOES NOT EXIST")
                
                if startingMemoryLoc != "":
                    startingMemoryLoc -= 1
                    for char in enteredValue:
                        startingMemoryLoc+=1
                        if startingMemoryLoc > 0xffff:
                            dtk.send_error(f"INVALID MEMORY LOCATION ON LINE {lineNumber}, MEMORY OVERFLOW")
                            break
                        dtk.allocated_memory_list.update({startingMemoryLoc : ord(char) & 0xff})


#adds a library to list
def add_library(line, lineNumber):
    global importedLibariesList
    if len(line) == 1:
        dtk.send_error(f"LIBRARY INCLUDE ERROR ON LINE {lineNumber}, NO LIBRARY NAME GIVEN")
    elif len(line) > 2:
        dtk.send_error(f"LIBRARY INCLUDE ERROR ON LINE {lineNumber}, ONLY ONE LIBRARY NAME ALLOWED")
    else:
        if os.path.isfile(line[1]+".py"):
            lib = importlib.import_module(line[1])
            if "exec_lib" in dir(lib):
                importedLibariesList.append(line[1])
        else:
           dtk.send_error(f"LIBRARY INCLUDE ERROR ON LINE {lineNumber}, NO SUCH LIBRARY EXISTS") 
            
#runs and executes the interpretor
def RunInterpreter(code):
    global codeToRun, importedLibariesList

    split_code_into_lines_and_tokens(code)
    
    print(codeToRun)
    lineNumber = 0

    while lineNumber < len(codeToRun):
        line = codeToRun[lineNumber]
        if len(line) != 0:
            if line[0] in ["ADD", "SUB", "AND", "OR", "XOR", "NOT", "TCOMP", "RSH", "LSH"]: #ALU OPERATIONS
                perform_ALU_operation(line, lineNumber)
            elif line[0] in ["IF", "ELSE", "FUNC", "EXEC", "LABEL", "GOTO", "END"]: #CPU OPERATIONS
                newLine = perform_CPU_operation(line, lineNumber)
                lineNumber = newLine
            elif line[0] in ["SET", "ALLOC", "PTRA", "PTRD", "DEL"]: #MEMORY OPERATIONS
                perform_memory_operation(line, lineNumber)
            elif line[0] in ["COUT", "UNOUT", "SNOUT", "STROUT", "CIN", "NIN", "STRIN"]: #INPUT AND OUTPUT
                perform_IO_operation(line, lineNumber)
            elif line[0] == "#": #COMMENT
                continue
            elif line[0] == "LOAD": #IMPORT LIBRARY
                add_library(line, lineNumber)
            elif line[0] in importedLibariesList: #EXECUTE FUNCTION IN LIBRARY
                try:
                    importlib.import_module(line[0]).exec_lib(line, lineNumber)
                except:
                    dtk.send_error(f"LIBRARY ERROR ON LINE {lineNumber}, INVALID 'exec_lib' FUNCTION IN LIBRARY {line[0]}")

        if dtk.abort_program:
            break
        else:
            lineNumber+=1