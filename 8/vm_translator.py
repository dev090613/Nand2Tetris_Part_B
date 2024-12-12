from parser import Parser, CommandType
from code_writer import CodeWriter
import os, glob

class VMTranslator:
    def __init__(self, input_path: str):
        self.input_path = input_path

        if os.path.isdir(input_path):
            self.vm_files = glob.glob(
                    os.path.join(input_path, "*.vm"))
            self.output_file = os.path.join(
                    input_path, 
                    os.path.basename(input_path) + ".asm")
        else:
            self.vm_files = [input_path]
            self.output_file = input_path.replace(
                ".vm", ".asm"
                )
    
    def translate(self):
        """
        1. output_file
        """
        with CodeWriter(self.output_file, 'w') as writer:
            if len(writer.vm_files) > 1:
                writer.writeInit()

            for vm_file in self.vm_files:
                self.translat_file(vm_file, writer)
                
    def translate_file(self, vm_file, writer: CodeWriter) \
            -> None:
                """
                1. set file name
                2. parser
                3. check CommandType
                4. call writer.write*()
                """
                file_name = os.path.basename(vm_file).replace(
                        ".vm", "")
                self.writer.setFileName(file_name)

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
                        writer.write.C_PushPop(command_type,
                                               parser.arg1()
                                               parser.arg2()
                                               )
                    elif command_type == CommandType.C_LABEL:
                        writer.write(parser.arg1())


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
        print(usage: python3 vm_translator.py input_path)
        exit(1)

    tranlator = VMTranslator(sys.arg[1])
    tranlator.translate()
    print("\nprogram complete.\n")


if __name__ == "__main__":
    main()
