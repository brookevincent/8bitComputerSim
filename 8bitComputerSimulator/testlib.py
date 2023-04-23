import developerToolkit as dtk

def exec_lib(line, lineNumber):
    if len(line) == 1:
        dtk.SendError(f"NO FUNCTION ON LINE {lineNumber}")
    else:
        match line[1]:
            case "helloworld":
                print("Hello World")