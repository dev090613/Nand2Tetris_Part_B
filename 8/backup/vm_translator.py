from parser import Parser, CommandType
from code_writer import CodeWriter
import os, glob

class VMTranslator:
    def __init__(self, input_path: str) -> None:
        self.input_path = input_path

        if os.path.isdir(self.input_path):
            self.vm_files = glob.glob(
                    os.path.join(self.input_path, "*.vm"))
            self.output_file = os.path.join(
                    self.input_path,
                    os.path.basename(os.path.normpath(input_path)) + ".asm"
                    )
        else:
            self.vm_files = [input_path]
            self.output_file = input_path.replace(
                ".vm", ".asm"
                )
    
    def translate(self) -> None:

        with CodeWriter(self.output_file) as writer:
            if len(self.vm_files) > 1:
                writer.writeInit()

            for vm_file in self.vm_files:
                self.translate_file(vm_file, writer)
                
    def translate_file(self, vm_file, writer: CodeWriter) \
            -> None:
                """
                1. set file name
                2. parser
                3. check CommandType
                4. call writer.write*()
                """
                file_name = os.path.basename(vm_file).replace(".vm", "")
                writer.setFileName(file_name)

                parser = Parser(vm_file)

                while parser.hasMoreCommands():
                    parser.advance()
                    command_type = parser.commandType()
                    if command_type ==\
                            CommandType.C_ARITHMETIC:
                        writer.writeArithmetic(parser.arg1())
                    elif command_type in [
                            CommandType.C_PUSH,
                            CommandType.C_POP
                            ]:
                        writer.writePushPop(command_type,
                                               parser.arg1(),
                                               parser.arg2()
                                               )
                    elif command_type == CommandType.C_LABEL:
                        writer.writeLabel(parser.arg1())


                    elif command_type == CommandType.C_GOTO:
                        writer.writeGoto(parser.arg1())
                    
                    elif command_type == CommandType.C_IF:
                        writer.writeIf(parser.arg1())
                    elif command_type == CommandType.C_FUNCTION:
                        writer.writeFunction(parser.arg1(), 
                                             parser.arg2()
                                             )
                    elif command_type == CommandType.C_CALL:
                        writer.writeCall(parser.arg1(), 
                                         parser.arg2()
                                         )
                    elif command_type == CommandType.C_RETURN:
                        writer.writeReturn()
    

def main():
    import sys

    if len(sys.argv) != 2:
        print("usage: python3 vm_translator.py input_path")
        sys.exit(1)

    input_file = sys.argv[1]
    translator = VMTranslator(input_file)
    translator.translate()
    print(translator.output_file)
    print("\nprogram complete.\n")


if __name__ == "__main__":
    main()
