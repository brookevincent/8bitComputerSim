#main
import interpreter as inter

def main():
    inter.RunInterpreter("""
    import testlib
    testlib helloworld
    """)
    
main()