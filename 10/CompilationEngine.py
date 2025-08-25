from JackTokenizer import IDENTIFIER, KEYWORD, INT_CONST, STRING_CONST, SYMBOL

class CompilationEngine:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.xml_output = []
        self.tokenizer.advance()
        self.compileClass()

    def _eat_keyword(self, expected_token):
        """
        현재 토큰이 예상된 토큰이 맞다면, 작성
        아니라면, 에러 발생
        """
        token_type = self.tokenizer.tokenType()
        current_token = self.tokenizer.current_token

        if token_type == KEYWORD and current_token == expected_token:
            self.xml_output.append(f"<keyword>{current_token}</keyword>")
            self.tokenizer.advance()
        else:
            raise ValueError(f"Expected: {expected_token},\
                    found: {current_token}")

    def _eat_symbol(self, expected_token):
        token_type = self.tokenizer.tokenType() # SYMBOL
        current_token = self.tokenizer.current_token # {
        if token_type == SYMBOL and current_token == expected_token:
            self.xml_output.append(f"<symbol>{self.tokenizer.symbol()}</symbol>")
            self.tokenizer.advance()
        else:
            raise ValueError(f"Expected: {expected_token},\
                    found: {current_token}")

    def _eat_identifier(self):
        """
        인자를 받지 않음 주의
        """
        token_type = self.tokenizer.tokenType()
        current_token = self.tokenizer.current_token
        if token_type == IDENTIFIER:
            self.xml_output.append(f"<identifier>{current_token}</identifier>")
            self.tokenizer.advance()
        else:
            raise ValueError(f"expected token type is identifier, but: {token_type}")

    def compileClass(self):
        self.xml_output.append("<class>")

        self._eat_keyword("class")
        self._eat_identifier()
        self._eat_symbol("{")

        class_var_dec = ["static", "field"]
        subroutines = ["constructor", "method", "function"]
        while self.tokenizer.current_token in class_var_dec + subroutines:
            cur_token = self.tokenizer.current_token
            if cur_token in class_var_dec:
                self.compileClassVarDec()
            else:
                self.compileSubroutine()
        self._eat_symbol("}")

        self.xml_output.append("</class>")

    def compileClassVarDec(self):
        """
        static | field type varName (, varName)*
        """
        self.xml_output.append('<classVarDec>')
        # keyword: 'static' | field
        cur_token = self.tokenizer.current_token
        if cur_token in ['static', 'field']:
            self._eat_keyword(cur_token)
        else:
            raise ValueError(f"expected: 'static', 'field'")
        # keyword or identifier
        self._compileType()
        # varName
        self._eat_identifier()
        # (, varName)*
        while self.tokenizer.current_token == ",":
            self._eat_symbol(",")
            self._eat_identifier()
        # ;
        self._eat_symbol(';')

        self.xml_output.append('</classVarDec>')
    
    def _compileType(self):
        # Keyword or identifier
        # Keyword: 'void' | 'type'
        token_type = self.tokenizer.tokenType()
        if token_type == KEYWORD:
            cur_token = self.tokenizer.current_token
            if cur_token in ['int', 'char', 'boolean', 'void']:
                self._eat_keyword(cur_token)
            else:
                raise ValueError(f"expected: 'int', 'char', 'boolean', 'void'")
        elif token_type == IDENTIFIER:
            self._eat_identifier()
        else:
            raise ValueError("expected: 'void' | 'type'")

    def compileSubroutine(self):
        self.xml_output.append("<subroutineDec>")

        # Keyword: 'constructor' | 'function' | 'method'
        cur_token = self.tokenizer.current_token
        if cur_token in ['constructor', 'function', 'method']:
            self._eat_keyword(cur_token)
        else:
            raise ValueError("expected: 'constructor' | 'function' | 'method'")
        # type
        self._compileType()
        # Identifier: subroutineName
        self._eat_identifier()
        # Symbol: '(' 
        self._eat_symbol('(')
        # call compileParameterList
        self.compileParameterList()
        # Symbol: ')'
        self._eat_symbol(')')
        # call compileSubroutineBody
        self.compileSubroutineBody()
        # close tag </SubroutineDec>
        self.xml_output.append("</subroutineDec>")

    def compileParameterList(self):
        self.xml_output.append("<parameterList>")

        token_value = self.tokenizer.current_token
        token_type = self.tokenizer.tokenType()
        if token_value != ')':
            self._compileType()
            self._eat_identifier()
            # (, argName)*
            while self.tokenizer.current_token == ",":
                self._eat_symbol(',')
                self._compileType()
                self._eat_identifier()

        self.xml_output.append("</parameterList>")

    def compileVarDec(self):
        # var type varName
        self.xml_output.append("<varDec>")

        self._eat_keyword('var')
        self._compileType()
        self._eat_identifier()
        while self.tokenizer.current_token == ',':
            self._eat_symbol(',')
            self._eat_identifier()
        self._eat_symbol(';')

        self.xml_output.append("</varDec>")

    def compileStatements(self):
        self.xml_output.append("<statements>")

        statements_keywords = ["let", "if", "while", "do", "return"]
        while self.tokenizer.current_token in statements_keywords:
            cur_token = self.tokenizer.current_token
            if cur_token == "let":
                self.compileLet()
            elif cur_token == "if":
                self.compileIf()
            elif cur_token == "while":
                self.compileWhile()
            elif cur_token == "do":
                self.compileDo()
            elif cur_token == "return":
                self.compileReturn()

        self.xml_output.append("</statements>")

    def compileSubroutineBody(self):
        # { varDec* statements }
        self.xml_output.append("<subroutineBody>")

        self._eat_symbol("{")
        # varDec*
        while self.tokenizer.current_token == 'var':
            self.compileVarDec()
        # statements
        self.compileStatements()

        self._eat_symbol("}")

        self.xml_output.append("</subroutineBody>")

    def compileExpression(self):
        # term (op term)*
        self.xml_output.append("<expression>")

        self.compileTerm()
        op_list = ["+", "-", "/", "*", "/", "&", "|", "<", ">", "="]
        while self.tokenizer.current_token in op_list:
            self._eat_symbol(self.tokenizer.current_token)
            self.compileTerm()

        self.xml_output.append("</expression>")

    def compileTerm(self):
        self.xml_output.append("<term>")

        token_type = self.tokenizer.tokenType()
        token_value = self.tokenizer.current_token
        
        if token_type == INT_CONST:
            self.xml_output.append(f"<integerConstant>{self.tokenizer.intVal()}</integerConstant>")
            self.tokenizer.advance()

        elif token_type == STRING_CONST:
            self.xml_output.append(f"<stringConstant>{self.tokenizer.stringVal()}</stringConstant>")
            self.tokenizer.advance()

        elif token_type == KEYWORD:
            # true, false, null, this
            if token_value in ['true', 'false', 'null', 'this']:
                self._eat_keyword(token_value)
            else:
                raise ValueError(f"expected: 'true', 'false', 'null', 'this', found: {token_value}")

        elif token_type == IDENTIFIER:
            # varName, array, call subroutine
            self._eat_identifier()
            cur_token = self.tokenizer.current_token
            if cur_token == '[':
                self._eat_symbol('[')
                self.compileExpression()
                self._eat_symbol(']')
            elif cur_token == '.':
                self._eat_symbol('.')
                self._eat_identifier()
                self._eat_symbol('(')
                self.compileExpressionList()
                self._eat_symbol(')')
            elif cur_token == '(': # draw()
                self._eat_symbol('(')
                self.compileExpressionList()
                self._eat_symbol(')')

        elif token_value == '(':
            # ( expression )
            self._eat_symbol('(')
            self.compileExpression()
            self._eat_symbol(')')
        elif token_value in ['-', '~']:
            # unaryOp term
            self._eat_symbol(token_value)
            self.compileTerm()

        self.xml_output.append("</term>")

    def compileLet(self):
        # let varName ('[', expression, ']')? = expression ;
        self.xml_output.append("<letStatement>")

        self._eat_keyword('let')
        self._eat_identifier()
        # if Array -> [ expression ]
        if self.tokenizer.current_token == '[':
            self._eat_symbol('[')
            self.compileExpression()
            self._eat_symbol(']')
        self._eat_symbol('=')
        self.compileExpression()
        self._eat_symbol(';')

        self.xml_output.append("</letStatement>")

    def compileIf(self):
        self.xml_output.append('<ifStatement>')

        self._eat_keyword('if')
        self._eat_symbol('(')
        self.compileExpression()
        self._eat_symbol(')')

        self._eat_symbol('{')
        self.compileStatements()
        self._eat_symbol('}')

        if self.tokenizer.current_token == "else":
            self._eat_keyword('else')
            self._eat_symbol('{')
            self.compileStatements()
            self._eat_symbol('}')

        self.xml_output.append('</ifStatement>')

    def compileWhile(self):
        self.xml_output.append('<whileStatement>')
        self._eat_keyword('while')

        self._eat_symbol('(')
        self.compileExpression()
        self._eat_symbol(')')

        self._eat_symbol('{')
        self.compileStatements()
        self._eat_symbol('}')
        
        self.xml_output.append('</whileStatement>')

    def _compileSubroutineCall(self):
        # ex. draw()
        # ex. Output.printInt(num)
        self._eat_identifier()

        cur_token = self.tokenizer.current_token
        if cur_token == '.':
            self._eat_symbol('.')
            self._eat_identifier()

        self._eat_symbol('(')
        self.compileExpressionList()
        self._eat_symbol(')')

    def compileExpressionList(self):
        # expression (, expression)*
        self.xml_output.append('<expressionList>')
        if self.tokenizer.current_token != ")":
            self.compileExpression()
            while self.tokenizer.current_token == ',':
                self._eat_symbol(',')
                self.compileExpression()
        self.xml_output.append('</expressionList>')

    def compileDo(self):
        self.xml_output.append("<doStatement>")
        # do subroutineCall ;
        self._eat_keyword('do')
        self._compileSubroutineCall()
        self._eat_symbol(';')
        self.xml_output.append("</doStatement>")

    def compileReturn(self):
        # return; 
        # return expression;
        self.xml_output.append("<returnStatement>")

        self._eat_keyword('return')
        if self.tokenizer.current_token != ';':
            self.compileExpression()
        self._eat_symbol(';')

        self.xml_output.append("</returnStatement>")
