from Parser import Parser
from CodeWriter import CodeWriter
import os, glob

C_PUSH, C_POP = 'C_PUSH', 'C_POP'
C_ARITHMETIC = 'C_ARITHMETIC'
C_LABEL, C_IF, C_GOTO = 'C_LABEL', 'C_IF', 'C_GOTO'
C_FUNC, C_CALL, C_RET = 'C_FUNC', 'C_CALL', 'C_RET'

class VMTranslator:
    def __init__(self, input_path):
        self.file_name = ""

        if os.path.isdir(input_path):
            normalized = os.path.normpath(input_path)
            pattern = os.path.join(normalized, "*.vm")
            self.vm_files = glob.glob(pattern)

            dir_name = os.path.basename(normalized)
            self.output_file = os.path.join(input_path, dir_name + ".asm")

        else:

            self.vmfiles = [input_path]
            self.output_file = input_path.replace(".vm", ".asm")

    def translate(self):

        code_writer = CodeWriter(self.output_file)
        code_writer.writeInit()

        for vm_file in self.vm_files:
            file_name = os.path.basename(vm_file).replace(".vm", "")
            code_writer.setFileName(file_name)

            parser = Parser(vm_file)

            while parser.hasMoreLines():
                parser.advance()

                command_type = parser.commandType()
                if command_type in [C_PUSH, C_POP]:
                    arg1 = parser.arg1()
                    arg2 = parser.arg2()
                    code_writer.writePushPop(command_type, arg1, arg2)
                elif command_type == C_ARITHMETIC:
                    command = parser.arg1()
                    code_writer.writeArithmetic(command)

                elif command_type == C_LABEL:
                    label = parser.arg1()
                    code_writer.writeLabel(label)

                elif command_type == C_IF:
                    label = parser.arg1()
                    code_writer.writeIf(label)

                elif command_type == C_GOTO:
                    label = parser.arg1()
                    code_writer.writeGoto(label)

                elif command_type == C_FUNC:
                    functionName = parser.arg1()
                    nVars = parser.arg2()
                    code_writer.writeFunction(functionName, nVars)

                elif command_type == C_CALL:
                    functionName = parser.arg1()
                    nArgs = parser.arg2()
                    code_writer.writeCall(functionName, nArgs)

                elif command_type == C_RET:
                    code_writer.writeReturn()

        code_writer.close()


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
