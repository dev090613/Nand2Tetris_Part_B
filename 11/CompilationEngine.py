from JackTokenizer import IDENTIFIER, KEYWORD, INT_CONST, STRING_CONST, SYMBOL
from SymbolTable import SymbolTable
from VMWriter import VMWriter

class CompilationEngine:
    def __init__(self, tokenizer, output_file):
        self.tokenizer = tokenizer
        self.symbol_table = SymbolTable()
        self.vm_writer = VMWriter(output_file)

        self.className = ""
        self.label_index = 0

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
            self.tokenizer.advance()
        else:
            raise ValueError(f"Expected: {expected_token},\
                    found: {current_token}")

    def _eat_symbol(self, expected_token):
        token_type = self.tokenizer.tokenType() # SYMBOL
        current_token = self.tokenizer.current_token # {
        if token_type == SYMBOL and current_token == expected_token:
            self.tokenizer.advance()
        else:
            raise ValueError(f"Expected: {expected_token},\
                    found: {current_token}")

    def _eat_identifier(self) -> str:
        """
        인자를 받지 않음 주의
        """
        token_type = self.tokenizer.tokenType()
        current_token = self.tokenizer.current_token
        n = current_token
        if token_type == IDENTIFIER:
            self.tokenizer.advance()
        else:
            raise ValueError(f"expected token type is identifier, but: {token_type}")

        return n

    def compileClass(self):

        self._eat_keyword("class")
        self.className = self._eat_identifier()
        self._eat_symbol("{")

        class_var_dec = ["static", "field"]
        subroutines = ["constructor", "method", "function"]
        while self.tokenizer.current_token in class_var_dec + subroutines:
            cur_token = self.tokenizer.current_token
            if cur_token in class_var_dec:
                self.compileClassVarDec()
            else:
                self.compileSubroutine(self.className)
        self._eat_symbol("}")

    def compileClassVarDec(self):
        """
        static | field type varName (, varName)*
        """
        # keyword: 'static' | field
        cur_token = self.tokenizer.current_token
        if cur_token in ['static', 'field']:
            k = cur_token
            self._eat_keyword(cur_token)
        else:
            raise ValueError(f"expected: 'static', 'field'")
        # keyword or identifier
        t = self._compileType()
        # varName
        n = self._eat_identifier()
        self.symbol_table.define(n, t, k)
        # (, varName)*
        while self.tokenizer.current_token == ",":
            self._eat_symbol(",")
            n = self._eat_identifier()
            self.symbol_table.define(n, t, k)
        # ;
        self._eat_symbol(';')

    def _compileType(self) -> str:
        # Keyword or identifier
        # Keyword: 'void' | 'type'
        token_type = self.tokenizer.tokenType()
        if token_type == KEYWORD:
            cur_token = self.tokenizer.current_token
            if cur_token in ['int', 'char', 'boolean', 'void']:
                t = cur_token
                self._eat_keyword(cur_token)
            else:
                raise ValueError(f"expected: 'int', 'char', 'boolean', 'void'")
        elif token_type == IDENTIFIER:
            t = self.tokenizer.current_token
            self._eat_identifier()
        else:
            raise ValueError("expected: 'void' | 'type'")

        return t

    def compileSubroutine(self, className):
        """
        constructor | function | method 
            type subroutineName(parameterList)
        """
        self.symbol_table.startSubroutine()

        # Keyword: 'constructor' | 'function' | 'method' 
        subroutine_kind = self.tokenizer.current_token
        if subroutine_kind in ['constructor', 'function', 'method']:
            self._eat_keyword(subroutine_kind)
        else:
            raise ValueError("expected: 'constructor' | 'function' | 'method'")

        # type
        self._compileType()

        # Identifier: subroutineName
        subroutineName = self._eat_identifier()

        if subroutine_kind == 'method':
            self.symbol_table.define('this', className, 'argument')

        # Symbol: '(' 
        self._eat_symbol('(')
        # call compileParameterList
        self.compileParameterList()
        # Symbol: ')'
        self._eat_symbol(')')
        # call compileSubroutineBody
        self.compileSubroutineBody(className, subroutineName, subroutine_kind)

    def compileParameterList(self):

        token_value = self.tokenizer.current_token
        token_type = self.tokenizer.tokenType()
        if token_value != ')':
            t = self._compileType()
            n = self._eat_identifier()
            self.symbol_table.define(n, t, 'argument')
            # (, argName)*
            while self.tokenizer.current_token == ",":
                self._eat_symbol(',')
                t = self._compileType()
                n = self._eat_identifier()
                self.symbol_table.define(n, t, 'argument')

    def compileVarDec(self):
        """var type varName
        var int my_number
        """
        self._eat_keyword('var')
        t = self._compileType()
        n = self._eat_identifier()
        self.symbol_table.define(n, t, 'local')

        while self.tokenizer.current_token == ',':
            self._eat_symbol(',')
            n = self._eat_identifier()
            self.symbol_table.define(n, t, 'local')
        self._eat_symbol(';')

    def compileStatements(self):
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

    def compileSubroutineBody(self, className, subroutineName, subroutineKind):
        """{ varDec* statements }
        {
            var int temp; // coompileVarDec()
            let temp = 0; // compileStatements() <- let, if, while, do, return
            ...
            return;
        }
        """
        self._eat_symbol("{")
        # varDec*
        while self.tokenizer.current_token == 'var':
            self.compileVarDec()

        # function ClassName.functionName
        func_name = f"{className}.{subroutineName}"
        n_locals = self.symbol_table.var_count
        self.vm_writer.writeFunction(func_name, n_locals)

        if subroutineKind == 'constructor':
            n_fields = self.symbol_table.field_count
            self.vm_writer.writePush('constant', n_fields)
            self.vm_writer.writeCall('Memory.alloc', 1)
            self.vm_writer.writePop('pointer', 0)
        elif subroutineKind == 'method':
            self.vm_writer.writePush('argument', 0)
            self.vm_writer.writePop('pointer', 0)

        # statements
        self.compileStatements()
        self._eat_symbol("}")

    def compileExpression(self):
        """
        term (op term)*
        """
        self.compileTerm()
        op_table = {"+": "add", "-": "sub", "/": "Math.divide", "*": "Math.multiply", "&": "and", "|": "or", "<": "lt", ">": "gt", "=": "eq"}
        while self.tokenizer.current_token in op_table:
            op = self.tokenizer.current_token
            self._eat_symbol(op)
            self.compileTerm()
            if op in ["*", "/"]:
                self.vm_writer.writeCall(op_table[op], 2)
            else:
                self.vm_writer.writeArithmetic(op_table[op])

    def compileTerm(self):
        """
        5, 'Hello', true, x, (x+y), ...
        """
        token_type = self.tokenizer.tokenType()
        token_value = self.tokenizer.current_token
        
        if token_type == INT_CONST:
            self.vm_writer.writePush('constant', self.tokenizer.intVal())
            self.tokenizer.advance()

        elif token_type == STRING_CONST:
            # "Hello"
            string_val = self.tokenizer.stringVal()
            self.vm_writer.writePush('constant', len(string_val))
            # stack에 올라간 길이를 인자로 받아, 그 길이만큼
            # 메모리를 할당하고, String 객체의 시작 주소를 반환 
            self.vm_writer.writeCall('String.new', 1)

            for char in (string_val):
                self.vm_writer.writePush('constant', ord(char))
                # String 객체의 시작 주소와
                # 추가할 문자의 ASCII 값을 인자로 받는다.
                self.vm_writer.writeCall('String.appendChar', 2)

            self.tokenizer.advance()

        elif token_type == KEYWORD:
            # true, false, null, this
            if token_value in ['false', 'null']:
                self.vm_writer.writePush('constant', 0)
            elif token_value in ['true']:
                self.vm_writer.writePush('constant', 0)
                self.vm_writer.writeArithmetic('not')
            elif token_value == 'this':
                self.vm_writer.writePush('pointer', 0)
            else:
                raise ValueError(f"expected: 'true', 'false', 'null', 'this', found: {token_value}")
            self._eat_keyword(token_value)

        elif token_type == IDENTIFIER:
            # varName, array, call subroutine
            # name = 
            name = self._eat_identifier()

            if self.tokenizer.current_token == "[":
                # array - num[expression]
                kind = self.symbol_table.kindOf(name)
                index = self.symbol_table.indexOf(name)

                segment = 'this' if kind == 'field' else kind
                self.vm_writer.writePush(segment, index)

                self._eat_symbol('[')
                self.compileExpression()
                self._eat_symbol(']')
                # 주소 + index의 결과를 THAT 포인터에 저장,
                # THAT이 가리키는 곳의 값을 push
                self.vm_writer.writeArithmetic('add')
                self.vm_writer.writePop('pointer', 1)
                self.vm_writer.writePush('that', 0)

            elif self.tokenizer.current_token == '.':
                # className.subroutineName | varName.methodName
                self._eat_symbol('.')
                subroutine_name = self._eat_identifier()
                kind = self.symbol_table.kindOf(name)

                n_args = 0
                if kind is not None:
                    # varName.methodName. ex. ball.move()
                    n_args = 1
                    index = self.symbol_table.indexOf(name)
                    var_type = self.symbol_table.typeOf(name)
                    segment = 'this' if kind == 'field' else kind
                    self.vm_writer.writePush(segment, index)
                    full_name = f"{var_type}.{subroutine_name}"
                else:
                    # className.subroutineName. ex. Screen.draw()
                    full_name = f"{name}.{subroutine_name}"

                # (expressionList)
                self._eat_symbol('(')
                n_args += self.compileExpressionList()
                self._eat_symbol(')')
                self.vm_writer.writeCall(full_name, n_args)

                
            # 같은 클래스 내 메서드 호출
            elif self.tokenizer.current_token == '(':
                # draw() <- this.draw()
                # this를 첫 번째 인자로
                self.vm_writer.writePush('pointer', 0)
                subroutine_name = name

                self._eat_symbol('(')
                # (expression)
                n_args = self.compileExpressionList()
                self._eat_symbol(')')
                # ex. call Ball.draw
                full_name = f"{self.className}.{subroutine_name}"
                self.vm_writer.writeCall(full_name, n_args + 1)

            else: # 일반 변수
                kind = self.symbol_table.kindOf(name)
                index = self.symbol_table.indexOf(name)
                segment = 'this' if kind == 'field' else kind
                self.vm_writer.writePush(segment, index)
            
        elif token_value == '(':
            # ( expression )
            self._eat_symbol('(')
            self.compileExpression()
            self._eat_symbol(')')

        elif token_value in ['-', '~']:
            """
            unaryOp term
            """
            self._eat_symbol(token_value)
            self.compileTerm()

            if token_value == '-':
                self.vm_writer.writeArithmetic('neg')
            elif token_value == '~':
                self.vm_writer.writeArithmetic('not')

    def compileLet(self):
        ''' let varName ('[', expression, ']')? = expression ;
        let num = 10;
        let arr[num + 2] = 3 + 5;
        
        오른쪽부터 왼쪽으로 처리한다.
        pop 연산이 일어남
        '''
        self._eat_keyword('let')
        name = self._eat_identifier()
        is_arr = False
        # if Array -> [ expression ]
        if self.tokenizer.current_token == '[':
            is_arr = True
            
            kind = self.symbol_table.kindOf(name)
            index = self.symbol_table.indexOf(name)
            self.vm_writer.writePush(kind, index)

            self._eat_symbol('[')
            self.compileExpression()
            self._eat_symbol(']')

            self.vm_writer.writeArithmetic('add')

        self._eat_symbol('=')
        self.compileExpression()
        self._eat_symbol(';')

        if is_arr:
            self.vm_writer.writePop('temp', 0)
            self.vm_writer.writePop('pointer', 1)
            self.vm_writer.writePush('temp', 0)
            self.vm_writer.writePop('that', 0)
        else:
            kind = self.symbol_table.kindOf(name)
            index = self.symbol_table.indexOf(name)
            segment = 'this' if kind == 'field' else kind
            self.vm_writer.writePop(segment, index)

    def compileIf(self):
        else_label = f"IF_ELSE_{self.label_index}"
        end_label = f"IF_END_{self.label_index}"
        self.label_index += 1

        # if (expression)
        self._eat_keyword('if')
        self._eat_symbol('(')
        self.compileExpression()
        self._eat_symbol(')')

        self.vm_writer.writeArithmetic('not')
        self.vm_writer.writeIf(else_label)

        # { statements }
        self._eat_symbol('{')
        self.compileStatements()
        self._eat_symbol('}')
        self.vm_writer.writeGoto(end_label)

        self.vm_writer.writeLabel(else_label)

        # else block
        if self.tokenizer.current_token == "else":
            self._eat_keyword('else')
            self._eat_symbol('{')
            self.compileStatements()
            self._eat_symbol('}')

        self.vm_writer.writeLabel(end_label)

    def compileWhile(self):
        """
        while (expression) { statements }
        """
        loop_start = f"LOOP_START_{self.label_index}"
        loop_end = f"LOOP_END_{self.label_index}"
        self.label_index += 1

        # while (expression)
        self.vm_writer.writeLabel(loop_start)

        self._eat_keyword('while')
        self._eat_symbol('(')
        self.compileExpression()
        self._eat_symbol(')')
        
        self.vm_writer.writeArithmetic('not')
        self.vm_writer.writeIf(loop_end)
        # { statements }
        self._eat_symbol('{')
        self.compileStatements()
        self._eat_symbol('}')
        self.vm_writer.writeGoto(loop_start)

        self.vm_writer.writeLabel(loop_end)
        
    def compileExpressionList(self) -> int:
        """
        expression (, expression)*
        """
        nArgs = 0
        if self.tokenizer.current_token != ")":
            nArgs += 1
            self.compileExpression()
            while self.tokenizer.current_token == ',':
                self._eat_symbol(',')
                self.compileExpression()
                nArgs += 1

        return nArgs

    def compileDo(self):
        """do subroutineCall
        ex. do Screen.draw();
        """
        self._eat_keyword('do')
        name = self._eat_identifier()
        n_args = 0

        cur_token = self.tokenizer.current_token
        if cur_token == '.':
            # Screen.draw() | ball.move()
            self._eat_symbol('.')
            subroutine_name = self._eat_identifier()
            kind = self.symbol_table.kindOf(name)

            if kind is not None:
                n_args = 1
                # varName.methodName(), ex. square.dispose()
                var_type = self.symbol_table.typeOf(name)
                index = self.symbol_table.indexOf(name)

                segment = 'this' if kind == 'field' else kind
                self.vm_writer.writePush(segment, index)

                full_name = f"{var_type}.{subroutine_name}"
            else:
                # className.subroutineName(), ex. Screen.drawRectangle()
                full_name = f"{name}.{subroutine_name}"
        else:
            # methodName(), ex. draw()
            n_args = 1
            self.vm_writer.writePush('pointer', 0)
            full_name = f"{self.className}.{name}"

        self._eat_symbol('(')
        n_args += self.compileExpressionList()
        self._eat_symbol(')')
        self._eat_symbol(';')

        self.vm_writer.writeCall(full_name, n_args)

        # do 문은 반환 값을 버린다.
        self.vm_writer.writePop('temp', 0)

    def compileReturn(self):
        """
        return;
        return expression;
        """
        self._eat_keyword('return')

        if self.tokenizer.current_token != ';':
            self.compileExpression()
        else:
            # return; -> 0을 반환함
            self.vm_writer.writePush('constant', 0)

        self._eat_symbol(';')
        self.vm_writer.writeReturn()

    def close(self):
        self.vm_writer.close()

