from parser import Parser
from codewriter import CodeWriter
class VMTranslator:
    def __init__(self, input_file):
        self.input_file = input_file
        output_file = input_file.replace(".vm", ".asm")

        self.parser = Parser(input_file)
        self.code_writer = CodeWriter(output_file)

        file_name = input_file.split("/")[-1].replace(".vm", "")
        self.code_writer.setFileName(file_name)

    def translate(self):

        while self.parser.hasMoreCommands():
            self.parser.advance()
            command_type = self.parser.commandType()

            if command_type == "C_ARITHMETIC":
                self.code_writer.writeArithmetic(
                        self.parser.arg1()
                        )
            elif command_type in ["C_PUSH", "C_POP"]:
                self.code_writer.writePushPop(
                        command_type,
                        self.parser.arg1(),
                        int(self.parser.arg2())
                        )
        self.code_writer.file.close()

def main():
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python3 VMTranslator.py input_file.vm\n")
        sys.exit(1)

    input_file = sys.argv[1]
    vm_translator = VMTranslator(input_file)
    vm_translator.translate()
    print("\nprogram complete.\n")




if __name__ == "__main__":
    main()
