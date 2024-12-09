from parser import Parser, CommandType

class CodeWriter:
    def __init__(self, output_file: str):
        
        self.file = open(output_file, 'w')
        self.current_file = None
        self.current_function = "Global"
        self.label_counter = 0

        self.binary_op = {
                "add": "M=M+D",
                "sub": "M=M-D",
                "and": "M=M&D",
                "or": "M=M|D",
                }
        self.segment_table = {
                "local": "LCL",
                "argument": "ARG",
                "this": "THIS",
                "that": "THAT",
                "temp": "5",
                "pointer": "3"
                }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file: 
            self.file.close()
        return 
    def setFileName(self, file_name) -> None:
        self.current_file = file_name

    def writeArithmetic(self, command) -> None:
        """
        ex. if command_type == \
                CommandType.C_ARITHMETIC
                self.code_writer.\
                        writeArithmetic(command)
        binary, unary, comparison
             "sub", "add", "neg", "not",
              "and", "or", "eq", "gt", "lt" 
        """
        # binary
        if command in self.binary_op:
            self._writeBinaryOperation(self.binary_op[command])
        # unary
        elif command == "neg":
            self._writeUnaryOperation("M=-M")

        elif command == "not":
            self._writeUnaryOperation("M=!M")
        # comparison
        elif command in ["eq", "gt", "lt"]:
            self._writeComparisonOperation(command)
        
        return

    def _writeBinaryOperation(self, operation):
        """
        "add": "M=M+D",
        "sub": "M=M-D",
        "and": "M=M&D",
        "or": "M=M|D",
        """
        self.file.write(
                "@SP\n"
                "AM=M-1\n"
                "D=M\n"

                "A=A-1\n"
                f"{operation}\n"
                )
        return

    def _writeUnaryOperation(self, operation) -> None:
        """
        "neg": "M=-M"
        "not": "M=!M"
        """
        self.file.write(
                "@SP\n"
                "A=M-1\n"
                f"{operation}\n"
                )
        return

    def _writeComparisonOperation(self, operation) -> None:
        """
        eq, gt, lt
        """
        jump_commands = {
                "eq": "JEQ",
                "gt": "JGT",
                "lt": "JLT",
                }
        label = self.label_counter
        self.file.write(
                "@SP\n"
                "AM=M-1\n"
                "D=M\n"

                "@SP\n"
                "AM=M-1\n"
                "D=M-D\n"

                f"@TRUE_{label}\n"
                f"D;{jump_commands[operation]}\n"

                # false
                "@SP\n"
                "A=M\n"
                "M=0\n" # stack top = 0
                f"@END_{label}\n"
                "0;JMP\n"

                # true
                f"(TRUE_{label})\n"
                "@SP\n"
                "A=M\n"
                "M=-1\n"

                # end
                f"(END_{label})\n"
                "@SP\n"
                "M=M+1\n"
                )
        self.label_counter += 1
        return

    def writePushPop(self, command_type, segment, index) -> None:
        """
        C_PUSH, C_POP
        """
        if command_type == CommandType.C_PUSH:
            if segment == "constant":
                self.file.write(
                        f"@{index}\n"
                        "D=A\n"
                        # stack top = value
                        "@SP\n"
                        "A=M\n"
                        "M=D\n"
                        # SP++
                        "@SP\n"
                        "M=M+1\n"
                        )
            elif segment == "static":
                self.file.write(
                        f"@{self.current_file}.{index}"
                        "D=M\n"
                        # stack top = fileName.index
                        "@SP\n"
                        "A=M\n"
                        "M=D\n"
                        # SP++
                        "@SP\n"
                        "M=M+1\n"
                        )
            elif segment in [ "temp", "pointer"]:
                base = int(self.segment_table[segment])
                self.file.write(
                        f"@{base + index}\n"
                        "D=M\n"
                        # stack top = base + index
                        "@SP\n"
                        "A=M\n"
                        "M=D\n"
                        # SP++
                        "@SP\n"
                        "M=M+1\n"
                        )
            else:
                # local, argument, this, that
                self.file.write(
                        # access base addr
                        f"@{self.segment_table[segment]}\n"
                        "D=M\n"
                        # increase index
                        f"@{index}\n"
                        # move to base + idx
                        "A=D+A\n"
                        "D=M\n" # D = RAM[base + idx]
                        # stack top = D
                        "@SP\n"
                        "A=M\n"
                        "M=D\n"
                        # SP++
                        "@SP\n"
                        "M=M+1\n"
                        )

        elif command_type == CommandType.C_POP:
            if segment == "static":
                self.file.write(
                        # move to stack top
                        "@SP\n"
                        "AM=M-1\n"
                        "D=M\n"

                        "@{self.current_file}.{index}\n"
                        "M=D\n"
                        )
            elif segment in [ "temp", "pointer" ]:
                base = int(self.segment_table[segment])
                self.file.write(
                        # move to stack top 
                        "@SP\n"
                        "AM=M-1\n"
                        "D=M\n"
                        # move to base + i
                        f"@{base + index}\n"
                        "M=D\n"
                        )
            else:
                self.file.write(
                        f"@{self.segment_table[segment]}\n"
                        "D=M\n"
                        # add index
                        f"@{index}\n"
                        "D=D+A\n"
                        # add to R13
                        "@R13\n"
                        "M=D\n"
                        # move to stack top
                        "@SP\n"
                        "AM=M-1\n"
                        "D=M\n"
                        
                        "@R13\n"
                        "A=M\n"
                        "M=D\n"
                        )
        return

    def writeLabel(self, label) -> None:
        """
        VM: label LOOP
            => CommandType.C_LABEL
        asm: (cur_func$LOOP)
        ex. Sys.init$LOOP
        """
        self.file.write(
                f"({self.current_function}${label})\n"
                )
        return

    def writeGoto(self, label: str) -> None:
        """
        VM: goto LOOP
        asm:
            @cur_func$LOOP
            0;JMP
        """
        self.file.write(
                f"@{self.current_function}${label}\n"
                "0;JMP\n"
                )
        return

    def writeIf(self, label) -> None:
        """
        vm: if-goto label
        asm:
            ...
        """
        self.file.write(
                "@SP\n"
                "AM=M-1\n"
                "D=M\n"
                f"@{self.current_function}${label}\n"
                "D;JNE\n"
                )
        return


def main():
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 CodeWrite.py")
        exit(1)

    input_file = sys.argv[1]
    output_file = input_file.replace(".vm", ".asm")

    parser = Parser(input_file)

    with CodeWriter(output_file) as writer:
        file_name = input_file.split("/")[-1].\
                replace(".vm", "")
        writer.setFileName(file_name)

        while parser.hasMoreCommands():
            parser.advance()
            command_type = parser.commandType()
            # print(command_type)
            if command_type == CommandType.C_ARITHMETIC:
                writer.writeArithmetic(parser.arg1())
            elif command_type in [
                    CommandType.C_POP,
                    CommandType.C_PUSH,
                    ]:

                writer.writePushPop(
                        command_type,
                        parser.arg1(),
                        parser.arg2()
                        )

            elif command_type == CommandType.C_LABEL:
                writer.writeLabel(parser.arg1())

            elif command_type == CommandType.C_GOTO:
                writer.writeGoto(parser.arg1())
            
            elif command_type == CommandType.C_IF:
                writer.writeIf(parser.arg1())

    print("\nprogram complete.\n")


if __name__ == "__main__":
    main()
