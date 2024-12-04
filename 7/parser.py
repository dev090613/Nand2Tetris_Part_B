class Parser:
    def __init__(self, input_file):
        
        with open(input_file, "r") as f:
            self.commands = []

            for line in f:
                comment_start = line.find("//")
                if comment_start != -1:
                    line = line[:comment_start]

                line = line.strip()
                if line:
                    self.commands.append(line)

        self.current_command = -1
        self.command_type = None

    def hasMoreCommands(self) -> bool:
        return self.current_command < len(self.commands) - 1

    def _getCommandType(self, command: str) -> str:
        """
        Returns:
            str: C_ARITHMETIC, C_POP/PUSH
        """
        first_word = command.split()[0]
        if first_word in ['add', 'sub', 'neg',
                          'eq', 'gt', 'lt',
                          'and', 'or', 'not']:
            return 'C_ARITHMETIC'
        if first_word == "push":
            return "C_PUSH"
        if first_word == "pop":
            return "C_POP"

        return None
    
    def advance(self) -> None:
        if self.hasMoreCommands():
            self.current_command += 1
            command = self.commands[self.current_command]
            self.command_type = self._getCommandType(command)

    def commandType(self) -> str:
        """
        Returns:
            str: C_ARITHMETIC or C_POP/PUSH
        """
        return self.command_type

    def arg1(self) -> str:
        """
        Returns:
            str: arg1 or command
        """
        command = self.commands[self.current_command]
        command_type = self.commandType()
        if command_type == "C_ARITHMETIC":
            return command
        elif command_type in ["C_PUSH", "C_POP"]:
            # ex. push constant 7
            return command.split()[1]
        return None

    def arg2(self) -> int:
        """
        Returns:
            int: second arg of current command
        """
        return int(self.commands[self.current_command].split()[2])


def main():
    parser = Parser("../nand2tetris/projects/7/StackArithmetic/SimpleAdd/SimpleAdd.vm")

    while parser.hasMoreCommands():
        parser.advance()
        command_type = parser.commandType()

        if command_type == "C_ARITHMETIC":
            print(f"command type: {command_type}")
            print(f"command arg1: {parser.arg1()}")
        else:
            print(f"command type: {command_type}")
            print(f"command arg1: {parser.arg1()}")
            print(f"command arg2: {parser.arg2()}")
        print()

if __name__ == "__main__":
    main()
