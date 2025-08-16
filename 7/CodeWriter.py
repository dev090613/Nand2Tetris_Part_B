C_ARITHMETIC = 'C_ARITHMETIC'
C_PUSH = 'C_PUSH'
C_POP = 'C_POP'
SEGMENT_POINTERS = {
    'local': 'LCL',
    'argument': 'ARG',
    'this': 'THIS',
    'that': 'THAT',
}

class CodeWriter:
    def __init__(self, out_file_path):
        self.output_file = open(out_file_path, "w")
        self.label_counter = 0

    def _write(self, command) -> None:
        self.output_file.write(command + "\n")

    def _writePush(self):
        """push D
        @SP
        A=M
        M=D
        @SP
        M=M+1
        """
        self._write("@SP")
        self._write("A=M")
        self._write("M=D")
        self._write("@SP")
        self._write("M=M+1")

    def _writePushConstant(self, idx) -> None:
        self._write(f"@{idx}")
        self._write("D=A")
        self._writePush()

    def _writePushSegment(self, segment, idx) -> None:
        self._write(f"@{idx}")
        self._write("D=A")
        self._write(f"@{SEGMENT_POINTERS[segment]}")
        self._write("A=M+D")
        self._write("D=M")
        self._writePush()

    def _writePop(self):
        """D = pop
        @SP
        AM=M-1
        D=M
        """
        self._write("@SP")
        self._write("AM=M-1")
        self._write("D=M")

    def _writePopSegment(self, segment, idx) -> None:
        """pop local 2
        """
        # D = RAM[SEGMENT_POINTERS[segment] + idx]
        self._write(f"@{idx}")
        self._write("D=A")
        self._write(f"@{SEGMENT_POINTERS[segment]}")
        self._write("D=M+D")
        # RAM[R13] = D
        self._write("@R13")
        self._write("M=D")
        # D = pop
        self._writePop()
        # *R13 = D
        self._write("@R13")
        self._write("A=M")
        self._write("M=D")

    def _writeBinary(self, command):
        """
        parser.arg1의 반환값이 add, sub와 같은 이항 연산자라면
        """
        self._writePop()
        self._write("A=M-1")
        if command == "add":
            self._write("M=M+D")
        elif command == "sub":
            self._write("M=M-D")
        elif command == "and":
            self._write("M=M&D")
        elif command == "or":
            self._write("M=M|D")
        return

    def _writeCompare(self, command):
        """
        D = pop
        A = M - 1
        D = M - D
        @{}
        """
        true_label = f"TRUE_{self.label_counter}"
        end_label = f"END_{self.label_counter}"
        self.label_counter += 1

        self._writePop()
        self._write("A=M-1")
        self._write("D=M-D")

        self._write(f"@{true_label}")
        if command == "gt":
            self._write("D;JGT")
        elif command == "lt":
            self._write("D;JLT")
        elif command == "eq":
            self._write("D;JEQ")

        self._write("D=0")
        self._write(f"@{end_label}")
        self._write("0;JMP")

        self._write(f"({true_label})")
        self._write("D=-1")

        self._write(f"({end_label})")
        self._writePush()
        
    def _writeUnary(self, command):
        """neg, not
        @SP
        AM=M-1
        M=M-1
        """
        self._write("@SP")
        self._write("A=M-1")
        if command == "neg":
            self._write("M=-M")
        elif command == "not":
            self._write("M=!M")

    def writeArithmetic(self, command):
        if command in ["add", "sub", "and", "or"]:
            self._writeBinary(command)
        elif command in ["gt", "lt", "eq"]:
            self._writeCompare(command)
        elif command in ["not", "neg"]:
            self._writeUnary(command)

    def writePushPop(self, command_type, segment, idx):
        if command_type == C_PUSH and segment == "constant":
            self._writePushConstant(idx)

        elif command_type == C_PUSH\
            and segment in ["local", "argument", "this", "that"]:
            self._writePushSegment(segment, idx)
        elif command_type == C_POP:
            self._writePopSegment(segment, idx)

    def close(self):
        self.output_file.close()
