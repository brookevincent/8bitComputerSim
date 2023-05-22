import developerToolkit as dtk
ltm = 0

def exec_lib(line, lineNumber):
    global ltm
    if len(line) == 1:
        dtk.SendError(f"NO FUNCTION ON LINE {lineNumber}")
    else:
        match line[1]:
            case "helloworld":
                print("Hello World")
            case "rev":
                print(line)
                if len(line) == 3:
                    ltm = dtk.GetValue(line[2], lineNumber)
            case "rout":
                print(ltm)
