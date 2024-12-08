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
        self.command_type = None

    def hasMoreCommands(self) -> bool:
        return self.command_index < len(self.commands) - 1

    def advance(self) -> None:
        
        self.command_index += 1
        self.current_command = self.commands[
                self.command_index]
        self.parts = self.current_command.split()

    def commandType(self, command) -> CommandType:

        first_word = self.parts[0]

        if first_word in ["sub", "add", "neg", "not",
                          "and", "or", "eq", "gt", "lt"]:
            return CommandType.C_ARITHMETIC

        elif  

