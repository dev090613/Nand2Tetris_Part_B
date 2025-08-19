from Parser import Parser
from CodeWriter import CodeWriter

C_PUSH, C_POP = 'C_PUSH', 'C_POP'
C_ARITHMETIC = 'C_ARITHMETIC'

class VMTranslator:
    def __init__(self, input_file):
        self.input_file = input_file
        output_file = input_file.replace(".vm", ".asm")
        # print(output_file, self.file_name)
        self.parser = Parser(input_file)
        self.code_writer = CodeWriter(output_file)

        self.file_name = input_file.split("/")[-1].replace(".vm", "")
        self.code_writer.setFileName(self.file_name)
        # print(self.code_writer.output_file)

    def translate(self):

        while self.parser.hasMoreLines():
            self.parser.advance()
            # print("It works.")
            command_type = self.parser.commandType()
            # print(command_type)
            if command_type in [C_PUSH, C_POP]:
                arg1 = self.parser.arg1()
                arg2 = self.parser.arg2()
                self.code_writer.writePushPop(command_type, arg1, arg2)

            elif command_type == C_ARITHMETIC:
                command = self.parser.arg1()
                self.code_writer.writeArithmetic(command)

        self.code_writer.close()


def main():
    import sys

    if len(sys.argv) != 2:
        msg = "Usage: python3 VMTranslator input_file.vm"
        print(msg)
        sys.exit(1)

    input_file = sys.argv[1]
    vmtranslator = VMTranslator(input_file)
    vmtranslator.translate()
    print("Program Complete.")

if __name__ == "__main__":
    main()
