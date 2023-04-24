#main
import interpreter as inter

def main():
    inter.RunInterpreter("""
    * a 0000
    strin a
    l b
    + a 00
    ? Z
        strout [endl]Program End
    :
        cout a
        *+ a 0001
        g b
    _
    """)
    
main()