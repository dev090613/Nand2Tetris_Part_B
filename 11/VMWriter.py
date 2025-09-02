class VMWriter:
    """
    vm code를 생성하여,
    .vm 출력 파일을 작성함
    """
    def __init__(self, outputFile):
        self.output_file = open(outputFile, "w")

    def writePush(self, segment, index: int):
        """
        push constant 5,
        push local 0, 와 같은 코드를 작성함
        """
        self.output_file.write(f"push {segment} {index}\n")

    def writePop(self, segment, index: int):
        self.output_file.write(f"pop {segment} {index}\n")

    def writeArithmetic(self, op):
        """산술-논리 연산: add, sub, neg, gt, lt, eq, not
        CompilationEngine이 sub, neg 등을 알려줄 것
        """
        self.output_file.write(f"{op}\n")

    def writeLabel(self, label):
        """
        label L1
        """
        self.output_file.write(f"label {label}\n")

    def writeGoto(self, label):
        """
        goto label
        """
        self.output_file.write(f"goto {label}\n")

    def writeIf(self, label):
        """
        if-goto label
        """
        self.output_file.write(f"if-goto {label}\n")

    def writeCall(self, name, nArgs):
        """
        call Math.multiply 2
        """
        self.output_file.write(f"call {name} {nArgs}\n")

    def writeFunction(self, name, nLocals):
        """
        function Main.main 2
        """
        self.output_file.write(f"function {name} {nLocals}\n")

    def writeReturn(self):
        self.output_file.write(f"return\n")

    def close(self):
        self.output_file.close()
