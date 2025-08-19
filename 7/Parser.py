# add, sub, neg, eq, gt, lt, and, or, not
C_ARITHMETIC = 'C_ARITHMETIC'
# push, pop
C_PUSH, C_POP = 'C_PUSH', 'C_POP'

class Parser:
    def __init__(self, in_file):
        """
        .vm file을 받는다.
        """
        self.cur_idx = 0
        self.commands = []
        self.cur_command = ""
        with open(in_file, "r") as f:
            lines = f.readlines()

        for line in lines:
            if "//" in line:
                has_annotation = line.split("//")
                line = has_annotation[0]
            striped = line.strip()
            if striped == "":
                continue
            self.commands.append(striped)


    def hasMoreLines(self) -> bool:
        if self.cur_idx < len(self.commands):
            return True
        return False

    def advance(self):
        self.cur_command = self.commands[self.cur_idx].split(" ")
        self.cur_idx += 1

    def commandType(self):
        if self.cur_command[0] == 'push':
            return C_PUSH
        elif self.cur_command[0] == 'pop':
            return C_POP
        elif self.cur_command[0] in ['add', 'sub', 'neg', 'not',\
                         'eq', 'gt', 'lt', 'and', 'or']:
            return C_ARITHMETIC
        return "What is this command"

    def arg1(self):
        if self.commandType() == C_ARITHMETIC:
            return self.cur_command[0]
        else:
            return self.cur_command[1]
        return 

    def arg2(self):
        if self.commandType() in ['C_PUSH', 'C_POP']:
            return self.cur_command[2]
        return 

def main():
    parser = Parser("./StackArithmetic/SimpleAdd/SimpleAdd.vm")
    while parser.hasMoreLines():
        parser.advance()
        print(f"cur_command is {parser.cur_command}")
        command_type = parser.commandType()
        if command_type in [ C_PUSH, C_POP ]:
            arg1 = parser.arg1()
            arg2 = parser.arg2()
            print(command_type, arg1, arg2)
        elif command_type == C_ARITHMETIC:
            arg1 = parser.arg1()
            print(command_type, arg1)

if __name__ == "__main__":
    main()

