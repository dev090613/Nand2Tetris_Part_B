class CodeWriter:
    def __init__(self, output_file: str) -> None:

        self.file = open(output_file, "w")
        self.current_file = None
        self.label_counter = 0

        self.binary_op = { 
                "add": "M=M+D", 
                "sub": "M=M-D",
                "and": "M=M&D", 
                "or": "M=M|D"
                }
        self.segment_table = {
                "local": "LCL",
                "argument": "ARG",
                "this": "THIS",
                "that": "THAT",
                "temp": "5", # RAM[5..12]
                "pointer": "3", # RAM[3..4]
                }

    def __enter__(self):
        '''
        with -> enter to context
        '''
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        out of with bolck -> resource retrieve
        """
        if self.file:
            self.file.close()

    def setFileName(self, file_name: str) -> None:
        self.current_file = file_name
        return

    def writeArithmetic(self, command) -> None:
        """
        Binary: M=M+D, M=M-D, M&D, M|D
        Unary: -M, !M
        Comparison
        """
        if command in self.binary_op:
            self._writeBinaryOperation(self.binary_op[command])

        elif command == "neg":
            self._writeUnaryOperation("M=-M")

        elif command == "not":
            self._writeUnaryOperation("M=!M")

        elif command in ["eq", "gt", "lt"]:
            self._writeComparisonOperation(command)

        return

    def _writeBinaryOperation(self, operation) -> None:
        """
        Ex
            add: M=M+D
        """
        self.file.write(
                f"// Binary operation: {operation}\n"
                "@SP\n"
                "AM=M-1\n"
                "D=M\n"
                "A=A-1\n"
                f"{operation}\n"
                )
        return

    def _writeUnaryOperation(self, operation) -> None:
        """
        operation:
            neg, not
        """
        self.file.write(
                f"// Unary operation: {operation}\n"
                "@SP\n"
                "A=M-1\n"
                f"{operation}\n"
                )
        return

    def _writeComparisonOperation(self, operation) -> None:
        """
        operation:
            eq, gt, lt
        """
        jump_commands = {
                "eq": "JEQ",
                "gt": "JGT",
                "lt": "JLT",
                }
        label = self.label_counter
        self.file.write(
                f"// Comparison operation {operation}\n"
                "@SP\n"
                "AM=M-1\n"
                "D=M\n" # move to second val(y)

                "@SP\n"
                "AM=M-1\n"
                "D=M-D\n" # x > y, x < y, ...

                f"@TRUE_{label}\n"
                f"D;{jump_commands[operation]}\n"

                # false case
                "@SP\n"
                "A=M\n"
                "M=0\n"
                f"@END_{label}\n"
                "0;JMP\n"

                # true case
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
        return None

    def writePushPop(self, command_type: str, segment: str, index: int) -> None:
        """
        command_type:
            C_PUSH, C_POP
        segment:
            local, argument, this, that, constant, static,
            temp, pointer
        """
                
        if command_type == "C_PUSH":
            if segment == "constant":
                self.file.write(
                        f"// push constant {index}\n"
                        f"@{index}\n"
                        "D=A\n"
                        "@SP\n"
                        "A=M\n"
                        "M=D\n"
                        "@SP\n"
                        "M=M+1\n"
                        )
            elif segment == "static":
                self.file.write(
                        f"// push static {index}\n"
                        f"@{self.current_file}.{index}\n"
                        "D=M\n"
                        "@SP\n"
                        "A=M\n"
                        "M=D\n"
                        "@SP\n"
                        "M=M+1\n"
                        )
            elif segment in ["temp", "pointer"]:
                base = int(self.segment_table[segment])
                self.file.write(
                        f"// push {segment} {index}\n"
                        f"@{base + index}\n"
                        "D=M\n"
                        "@SP\n"
                        "A=M\n"
                        "M=D\n"
                        "@SP\n"
                        "M=M+1\n"
                        )
            else: # local, argument, this, that segment
                
                self.file.write(
                        f"// push {segment} {index}\n"
                        f"@{self.segment_table[segment]}\n"
                        "D=M\n" # D = base addr
                        
                        f"@{index}\n"
                        "A=D+A\n"
                        "D=M\n" # D = RAM[base + idx]

                        "@SP\n"
                        "A=M\n"
                        "M=D\n"

                        "@SP\n"
                        "M=M+1\n"
                        )

        elif command_type == "C_POP":
            if segment == "static":
                self.file.write(
                        f"// pop static {index}\n"
                        "@SP\n"
                        "AM=M-1\n"
                        "D=M\n"

                        f"@{self.current_file}.{index}\n"
                        "M=D\n"
                        )
            elif segment in ["temp", "pointer"]:
                base = int(self.segment_table[segment])
                self.file.write(
                        f"// pop {segment} {index}\n"
                        "@SP\n"
                        "AM=M-1\n"
                        "D=M\n"
                        f"@{base + index}\n"
                        "M=D\n"
                        )
            else: # local, argument, this, that
                self.file.write(
                        f"// pop {segment} {index}\n"
                        f"@{self.segment_table[segment]}\n"
                        "D=M\n"
                        f"@{index}\n"
                        "D=D+A\n"

                        "@R13\n"
                        "M=D\n"

                        "@SP\n"
                        "AM=M-1\n"
                        "D=M\n"
                        
                        "@R13\n"
                        "A=M\n"
                        "M=D\n"
                        )



def main():
    import sys
    import os
    from parser import Parser

    if len(sys.argv) != 2:
        print("Usage: python3 codewrite.py input_file")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = input_file.replace(".vm", ".asm")

    parser = Parser(input_file)

    with CodeWriter(output_file) as writer:
        file_name = input_file.split("/")[-1].replace(".vm", "")
        writer.setFileName(file_name)

        while parser.hasMoreCommands():
            parser.advance()
            command_type = parser.commandType()

            if command_type == "C_ARITHMETIC":
                writer.writeArithmetic(parser.arg1())
            elif command_type in ["C_POP", "C_PUSH"]:
                writer.writePushPop(
                        command_type,
                        parser.arg1(),
                        int(parser.arg2())
                        )
    print("\n\tprogram complete.\n\t")

if __name__ == "__main__":
    main()
