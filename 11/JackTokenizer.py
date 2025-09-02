import os, glob, sys, re

KEYWORD, SYMBOL, IDENTIFIER, INT_CONST, STRING_CONST = (
    "KEYWORD",
    "SYMBOL",
    "IDENTIFIER",
    "INT_CONST",
    "STRING_CONST",
)
(
    CLASS,
    METHOD,
    FUNCTION,
    CONSTRUCTOR,
    INT,
    BOOLEAN,
    CHAR,
    VOID,
    VAR,
    STATIC,
    FIELD,
    LET,
    DO,
    IF,
    ELSE,
    WHILE,
    RETURN,
    TRUE,
    FALSE,
    NULL,
    THIS,
) = (
    "CLASS",
    "METHOD",
    "FUNCTION",
    "CONSTRUCTOR",
    "INT",
    "BOOLEAN",
    "CHAR",
    "VOID",
    "VAR",
    "STATIC",
    "FIELD",
    "LET",
    "DO",
    "IF",
    "ELSE",
    "WHILE",
    "RETURN",
    "TRUE",
    "FALSE",
    "NULL",
    "THIS",
)


class JackTokenizer:
    def __init__(self, input_file):
        """
        raw_code -> cleaned code: str
        공백과 white space를 건너뛴다.
        """
        with open(input_file, "r") as f:
            raw_code = f.read()

        self.current_token = ""
        self.current_token_type = None
        self.current_idx = 0
        self.code = self._clean_code(raw_code)

        self.digit_set = "0123456789"
        self.kw_table = {
            "class": CLASS,
            "method": METHOD,
            "function": FUNCTION,
            "constructor": CONSTRUCTOR,
            "int": INT,
            "boolean": BOOLEAN,
            "char": CHAR,
            "void": VOID,
            "var": VAR,
            "static": STATIC,
            "field": FIELD,
            "let": LET,
            "do": DO,
            "if": IF,
            "else": ELSE,
            "while": WHILE,
            "return": RETURN,
            "true": TRUE,
            "false": FALSE,
            "null": NULL,
            "this": THIS,
        }

        self.symbol_table = {
            "{": "{",
            "}": "}",
            "(": "(",
            ")": ")",
            "[": "[",
            "]": "]",
            ".": ".",
            ",": ",",
            ";": ";",
            "+": "+",
            "-": "-",
            "*": "*",
            "/": "/",
            "&": "&amp",
            "|": "|",
            "<": "&lt;",
            ">": "&gt;",
            "=": "=",
            "~": "~",
            "\\": "&quot;",
        }

    def _clean_code(self, code: str) -> str:
        code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
        code = re.sub(r"//.*", "", code)
        code = re.sub(r"\s+", " ", code)
        return code.strip()

    def hasMoreTokens(self) -> bool:
        return self.current_idx < len(self.code)

    def advance(self) -> None:
        """
        Set self.current_token, self.current_idx
        """
        if not self.hasMoreTokens():
            return

        while self.code[self.current_idx] == " ":
            self.current_idx += 1

        first_char = self.code[self.current_idx]
        if first_char in self.symbol_table:
            # symbol
            self.current_token = first_char
            self.current_idx += 1
            self.current_token_type = SYMBOL
        elif first_char in "0123456789":
            # intConstant
            left = self.current_idx
            while (
                self.current_idx < len(self.code)
                and self.code[self.current_idx] in "0123456789"
            ):
                self.current_idx += 1
            self.current_token = self.code[left : self.current_idx]
            self.current_token_type = INT_CONST
        elif first_char == '"':
            # stringConstant
            self.current_idx += 1
            left = self.current_idx
            while (
                self.current_idx < len(self.code) and self.code[self.current_idx] != '"'
            ):
                self.current_idx += 1
            self.current_token = self.code[left : self.current_idx]
            self.current_idx += 1
            self.current_token_type = STRING_CONST
        else:
            # keyword or identifier
            left = self.current_idx
            while (
                self.current_idx < len(self.code)
                and self.code[self.current_idx].isalnum()
                or self.code[self.current_idx] == "_"
            ):
                self.current_idx += 1
            self.current_token = self.code[left : self.current_idx]
            if self.current_token in self.kw_table:
                self.current_token_type = KEYWORD
            else:
                self.current_token_type = IDENTIFIER

        return

    def tokenType(self):
        return self.current_token_type

    def keyWord(self):
        return self.kw_table[self.current_token]

    def symbol(self) -> str:
        return self.symbol_table[self.current_token]

    def identifier(self) -> str:
        return self.current_token

    def intVal(self) -> int:
        return int(self.current_token)

    def stringVal(self) -> str:
        return self.current_token
