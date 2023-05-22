import string 

abort_program = False
result = 0
flags = [False, False, False, False, False] #order = carry, parity, negative, zero, overflow
reserved_tokens = ("ADD", "SUB", "AND", "OR", "XOR", "NOT", "TCOMP", "RSH", 
                  "LSH", "IF", "ELSE", "FUNC", "EXEC", "LABEL", "GOTO", "END", 
                  "SET", "ALLOC", "PTRA", "PTRD", "DEL","RESULT", "CARRY", "PARITY", "NEGATIVE", 
                  "ZERO", "OVERFLOW",
                  "COUT", "UNOUT", "SNOUT", "STROUT", "CIN", "NIN", "STRIN", "LOAD", "//", "ENDPROGRAM") #contains list of every reserved token
label_list = {} #contains all labels and their line number
function_list = {} #contains all labels and their line number
line_back_up_list = [] #contains list of lines to return to after function finishes executing
allocated_memory_list = {} #contains list of all allocated memory locations
variable_list = {} #contains list of every vairable and their memory location

#sends an error message and ends the program
def send_error(message):
    global abort_program
    abort_program = True
    print(message)

#checks if string s only contains hex digits
def contains_HEX_digits(s):
    return all(ch in string.hexdigits for ch in s)

#interprates values
def get_value(numberAsString, lineNumber):
    global result, variable_list, allocated_memory_list
    if contains_HEX_digits(numberAsString) and len(numberAsString) == 2:
        return(int(numberAsString, 16))
    elif numberAsString == "RESULT":
        return result
    elif numberAsString in variable_list.keys():
        return allocated_memory_list[variable_list[numberAsString]]
    else:
        send_error(f"INVALID ARGUMENT ON LINE {lineNumber}, ARGUMENT MUST BE MEMORY LOCATION OR 2 DIGIT HEX STRING")
        return 0

#sets flags after an operation
def set_flags():
    global flags
    flags = [False, False, False, False, False] #reset
    #set parity flag
    flags[1] = (result%2 == 1)
    #set negative flag
    flags[2] = (result&0x80 == 0x80)

    #set zero flag
    flags[3] = (result&0xff == 0)