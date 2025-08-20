from enum import Enum

class CommandType(Enum):
    C_ARITHMETIC = "arithmetic"
    C_POP = "pop"
    C_PUSH = "push"
    C_LABEL = "label"
    C_GOTO = "goto"
    C_IF = "if-goto"
    C_FUNCTION = "function"
    C_RETURN = "return"
    C_CALL = "call"

class Parser:
    def __init__(self, input_file):

        with open(input_file, 'r') as f:
            self.commands = []

            for line in f:
                comment_start = line.find("//")
                if comment_start != -1:
                    line = line[:comment_start]

                line = line.strip()
                if line:
                    self.commands.append(line)

        self.current_command = None
        self.command_index = -1

    def hasMoreCommands(self) -> bool:
        return self.command_index < len(self.commands) - 1

    def advance(self) -> None:
        
        self.command_index += 1
        self.current_command = self.commands[
                self.command_index]
        self.parts = self.current_command.split()

    def commandType(self) -> CommandType:

        first_word = self.parts[0]

        if first_word in [ "sub", "add", "neg", "not",
                          "and", "or", "eq", "gt", "lt" ]:
            return CommandType.C_ARITHMETIC

        elif first_word in [ "push", "pop" ]:
            if first_word == "push":
                return CommandType.C_PUSH
            elif first_word == "pop":
                return CommandType.C_POP

        elif first_word in [ "label", "goto", "if-goto" ]:
            if first_word == "label":
                return CommandType.C_LABEL
            elif first_word == "if-goto":
                return CommandType.C_IF
            elif first_word == "goto":
                return CommandType.C_GOTO

        elif first_word in [ "function",\
                "call", "return" ]:
            if first_word == "function":
                return CommandType.C_FUNCTION

            elif first_word == "call":
                return CommandType.C_CALL

            elif first_word == "return":
                return CommandType.C_RETURN
        else:
            raise ValueError("")

    def arg1(self) -> CommandType:
        """
        CommandType.C_ARITHMETIC: 
            ex. add
            => Return add
        
        else
            ex. label symbol
            => Return label
        """
        command_type = self.commandType()
        if command_type == CommandType.C_ARITHMETIC:
            return self.parts[0]
        else:
            return self.parts[1]

    def arg2(self) -> int:
        """
        ex. vm: function mult 2
            => Return 2
        """
        return int(self.parts[2])

def main():

    # parser = Parser("ProgramFlow/BasicLoop/BasicLoop.vm")
    parser = Parser("ProgramFlow/FibonacciSeries/FibonacciSeries.vm")

    while parser.hasMoreCommands():
        parser.advance()

        command = parser.commands[parser.command_index]
        command_type = parser.commandType()

        print(f"VM command: {command}")
        if command_type == CommandType.C_ARITHMETIC:
            print(f"Arg1: {parser.arg1()}")
            print(f"Command Type: {command_type}\n")
        else:
            print(f"Command Type: {command_type}\n")
            

if __name__ == "__main__":
    main()
