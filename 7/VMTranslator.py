from Parser import C_PUSH, C_POP, C_ARITHMETIC
from Parser import Parser
from CodeWriter import CodeWriter
import sys

input_file = sys.argv[1]
output_file = input_file.replace(".vm", ".asm")

parser = Parser(input_file)
code_writer = CodeWriter(output_file)

while parser.hasMoreLines():
    parser.advance()
    command_type = parser.commandType()
    if command_type in [C_PUSH, C_POP]:
        segment, index = parser.arg1(), parser.arg2()
        code_writer.writePushPop(command_type, segment, index)
    elif command_type == C_ARITHMETIC:
        command = parser.arg1()
        code_writer.writeArithmetic(command)

code_writer.close()
