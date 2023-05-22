#main
import interpreter as inter

def main():
    inter.RunInterpreter("""
    //basic calulator

    ALLOC a 0000
    ALLOC b 0001
    
    STROUT Input first number: 
    NIN a

    STROUT Input second number: 
    NIN b

    ALLOC operation 0002
    STROUT Input operation from the folowing: [endl]1 - Addition [endl]2 - Subtraction [endl]3 - and [endl]4 - or [endl]5 - xor [endl]
    NIN operation

    //check for addition
    SUB operation 01
    IF ZERO
        ADD a b
        GOTO end
    END
    //check for subtraction
    SUB operation 02
    IF ZERO
        SUB a b
        GOTO end
    END
    //check for and
    SUB operation 03
    IF ZERO
        AND a b
        GOTO end
    END
    //check for or
    SUB operation 04
    IF ZERO
        OR a b
        GOTO end
    END
    //check for xor
    SUB operation 04
    IF ZERO
        XOR a b
        GOTO end
    END
    LABEL end
    SNOUT RESULT
    """)
    
main()