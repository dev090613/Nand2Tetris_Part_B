C_ARITHMETIC = 'C_ARITHMETIC'
C_PUSH = 'C_PUSH'
C_POP = 'C_POP'

class CodeWriter:
    def __init__(self, out_file_path):
        self.output_file = open(out_file_path, "w")
        self.file_name = None
        self.label_counter = 0
        self.segment_table = {
            'local': 'LCL',
            'argument': 'ARG',
            'this': 'THIS',
            'that': 'THAT',
            'temp': 5, # 5..12
            'pointer': 3, # 3..4
        } 
    
    def setFileName(self, file_name) -> None:
        self.file_name = file_name

    def _write(self, command) -> None:
        self.output_file.write(command + "\n")

    def _writePush(self, segment, idx) -> None:

        if segment in ["local", "argument", "this", "that"]:
            self._write(f"@{idx}")
            self._write("D=A")
            self._write(f"@{self.segment_table[segment]}")
            self._write("A=D+M")
            self._write("D=M")

            self._write("@SP")
            self._write("A=M")
            self._write("M=D")
            self._write("@SP")
            self._write("M=M+1")

        elif segment in ['temp', 'pointer']:
            base = self.segment_table[segment] + int(idx)
            self._write(f"@{base}")
            self._write("D=M")

            self._write("@SP")
            self._write("A=M")
            self._write("M=D")

            self._write("@SP")
            self._write("M=M+1")

        elif segment == 'static':
            self._write(f"@{self.file_name}.{idx}")
            self._write("D=M")

            self._write("@SP")
            self._write("A=M")
            self._write("M=D")

            self._write("@SP")
            self._write("M=M+1")

        elif segment == 'constant':
            self._write(f"@{idx}")
            self._write("D=A")

            self._write("@SP")
            self._write("A=M")
            self._write("M=D")

            self._write("@SP")
            self._write("M=M+1")

        return

    def _writePop(self, segment, idx) -> None:
        if segment in ['local', 'argument', 'this', 'that']:
            # ex. pop local 2
            # D = *LCL + idx
            self._write(f"@{idx}")
            self._write("D=A")
            self._write(f"@{self.segment_table[segment]}")
            self._write("D=D+M")
            # RAM[13] = D = *LCL + idx
            self._write("@R13")
            self._write("M=D")
            # D = pop
            self._write("@SP")
            self._write("AM=M-1")
            self._write("D=M")
            # *RAM[13] = D
            self._write("@R13")
            self._write("A=M")
            self._write("M=D")
        
        elif segment in ['temp', 'pointer']:
            # ex. pop pointer 0
            # base = self.segment_table[segment] + idx
            base = self.segment_table[segment] + int(idx)
            # D = pop
            self._write("@SP")
            self._write("AM=M-1")
            self._write("D=M")
            #
            self._write(f"@{base}")
            self._write("M=D")

        elif segment == 'static':
            # pop static 0
            self._write("@SP")
            self._write("AM=M-1")
            self._write("D=M")
            # @fileName.num
            self._write(f"@{self.file_name}.{idx}")
            self._write("M=D")
            
        return

    def _writeBinary(self, command):
        binary_ops = {
                "add": "M=D+M",
                "sub": "M=M-D",
                "and": "M=D&M",
                "or": "M=D|M",
        }

        self._write("@SP")
        self._write("AM=M-1")
        self._write("D=M")
        self._write("A=A-1")
        self._write(f"{binary_ops[command]}")

        return

    def _writeCompare(self, command):
        comparison_ops = {
                "gt": "D;JGT",
                "eq": "D;JEQ",
                "lt": "D;JLT",
        }

        TRUE_LABEL = f"TRUE_{self.label_counter}"
        END_LABEL = f"END_{self.label_counter}"
        self.label_counter += 1

        self._write("@SP")
        self._write("AM=M-1")
        self._write("D=M")

        self._write("@SP")
        self._write("AM=M-1")
        self._write("D=M-D")

        self._write(f"@{TRUE_LABEL}")
        self._write(f"{comparison_ops[command]}")

        # false case *SP = 0
        self._write("@SP")
        self._write(f"A=M")
        self._write("M=0")
        self._write(f"@{END_LABEL}")
        self._write("0;JMP")

        # true case *SP = -1
        self._write(f"({TRUE_LABEL})")
        self._write("@SP")
        self._write("A=M")
        self._write("M=-1")

        # END label
        self._write(f"({END_LABEL})")
        self._write("@SP")
        self._write("M=M+1")
        
    def _writeUnary(self, command):
        unary_ops = {
                "neg": "M=-M",
                "not": "M=!M",
        }

        self._write("@SP")
        self._write("A=M-1")
        self._write(f"{unary_ops[command]}")

    def writeArithmetic(self, command):
        if command in ["add", "sub", "and", "or"]:
            # print("writeArithmetic - add, sub, and, or")
            self._writeBinary(command)

        elif command in ["gt", "lt", "eq"]:
            # print("writeArithmetic - gt, lt, eq")
            self._writeCompare(command)

        elif command in ["not", "neg"]:
            # print("writeArithmetic - not, neg")
            self._writeUnary(command)

    def writePushPop(self, command_type, segment, idx):

        if command_type == C_PUSH:
            self._writePush(segment, idx)

        elif command_type == C_POP:
            self._writePop(segment, idx)

    def close(self):
        self.output_file.close()
