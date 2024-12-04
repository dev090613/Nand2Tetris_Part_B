class CodeWriter:
    def __init__(self, output_file: str) -> None:

        self.file = open(output_file, "w")
            self.current_file = None
            self.label_counter = 0

        def setFileName(file_name: str) -> None:
            self.current_file = file_name
            return None

        def writeArithmetic(command) -> None:
            """
            Binary: M=M+D, M=M-D, M&D, M|D
            Unary: -M, !M
            Comparison
            """
            binary_op = { 
                    "add": "M=M+D", 
                    "sub": "M=M-D",
                    "and": "M&D", 
                    "or": "M|D"
                    }
            if command in binary_op:
                self._writeBinaryOperation(binary_op[command])

            elif command == "neg":
                self._writeUnaryOperation("M=-M")

            elif command == "not":
                self._writeUniaryOperation("M=!M")

            elif command in ["eq", "gt", "lt"]:
                self._writeComparisonOperation(command)

            return None

    def _writeBinaryOperation(operation) -> None:
        """
        Ex
            add: M=M+D
        """
        self.file.write(
                f"// Binary operation: {opertaion}\n"
                "@SP\n"
                "AM=M-1\n"
                "D=M\n"
                "A=A-1\n"
                f"{operation}\n"
                )
        return None

    def _writeUnaryOperation(operation) -> None:
        """
        operation:
            neg, not
        """
        self.file.write(
                f"// Unary operation: {}\n"
                "@SP\n"
                "A=M-1\n"
                f"{operation}\n"
                )
        return None

    def _writeComparisonOperation(operation) -> None:
        """
        operation:
            eq, gt, lt
        """
        jump_commands = {
                "eq": "JMP",
                "gt": "JGT",
                "lt": "JLT",
                }
        label = self.label_counter
        self.file.write(
                f"// Comparison operation{operation}\n"
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
                "A=M"
                "M=0"
                "@END_{label}\n"
                "0;JMP\n"

                # true case
                f"(TRUE_{label})\n"
                "@SP\n"
                "A=M"
                "M=-1"

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
        segment_table = {
                "local": "LCL",
                "argument": "ARG",
                "this": "THIS",
                "that": "THAT",
                "temp": "5", # RAM[5..12]
                "pointer": 3, # RAM[3..4]
                }
        
        if command_type == "C_PUSH":
            if segment == "constant":
                self.file.write(
                        f"// push constant {index}\n"
                        "@{index}\n"
                        "D=A\n"
                        "@SP\n"
                        "A=M\n"
                        "M=D\n"
                        "@SP\n"
                        "M=M+1"
                        )
            elif segment == "static":
                self.file.write(
                        f"// push static {index}\n"
                        "@{self.current_file}.{index}\n"
                        "D=M\n"
                        "@SP\n"
                        "A=M\n"
                        "M=D\n"
                        "@SP\n"
                        "M=M+1\n"
                        )
            elif segment in ["temp", "pointer"]:
                base = int(self.sement_table[segment])
                self.file.write(
                        f"push {segment} {index}\n"
                        "@{base + index}\n"
                        "D=M\n"
                        "@SP\n"
                        "A=M"
                        "M=D\n"
                        "SP\n"
                        "M=M+1\n"
                        )
            else:
                # local, arument, this, that segment
                self.file.write(
                        f"// push {segment} {index}\n"
                        "@{segment_table[segment]}\n"
                        "D=M\n" # D = base addr
                        
                        "@{index}\n"
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

                        "@{self.current_file}.{index}\n"
                        "M=D\n"
                        )
            elif segment in ["temp", "pointer"]:
                base = int(segment_table[segment])
                self.file.write(
                        f"// pop {segment} {index}\n"
                        "@SP\n"
                        "AM=M-1\n"
                        "D=M"
                        "@{base + index}\n"
                        "M=D\n"
                        )
            else:
                self.file.write(
                        f"// pop {segment} {index}\n"
                        "@{segment_table[segment]}\n"
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
    codewriter = CodeWriter()


if __name__ == "__main__":
    main()
