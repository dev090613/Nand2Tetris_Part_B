class SymbolTable:
    def __init__(self):
        self.class_scope_table = {}
        self.subroutine_scope_table = {}

        # n: [t, k, i]
        self.field_count = 0
        self.static_count = 0
        self.var_count = 0
        self.arg_count = 0

    def define(self, n, t, k):
        """
        변수(식별자)의 종류를 파악하고, 
        해당 스코프의 테이블에 속해있지 않다면,
        테이블에 심볼을 등록한다.
        """
        if k in ["field", "static"]:
            idx_count = self.field_count if k == "field"\
                    else self.static_count
            if n not in self.class_scope_table:
                self.class_scope_table[n] = [t, k, idx_count]
                if k == 'field':
                    self.field_count += 1
                else:
                    self.static_count += 1
        elif k in ["local", "argument"]:
            idx_count = self.var_count if k == "local"\
                    else self.arg_count
            if n not in self.subroutine_scope_table:
                self.subroutine_scope_table[n] = [t, k, idx_count]
                if k == 'local':
                    self.var_count += 1
                else:
                    self.arg_count += 1
        else:
            print("This var is not in virtual memory segments.")
            return

    def kindOf(self, name):
        """
        서브루틴 스코프 먼저 조회한다.
        """
        if name in self.subroutine_scope_table:
            return self.subroutine_scope_table[name][1]
        elif name in self.class_scope_table:
            return self.class_scope_table[name][1]
        else:
            return

    def typeOf(self, name):
        if name in self.subroutine_scope_table:
            return self.subroutine_scope_table[name][0]
        elif name in self.class_scope_table:
            return self.class_scope_table[name][0]
        else:
            print(f"{name} is not in symbol_table")
            return

    def indexOf(self, name):
        """
        n 이라는 심볼에 할당된 인덱스를 반환
        """
        if name in self.subroutine_scope_table:
            return self.subroutine_scope_table[name][2]
        elif name in self.class_scope_table:
            return self.class_scope_table[name][2]
        else:
            print(f"{name} is not in symbol_table")
            return

    def startSubroutine(self):
        self.subroutine_scope_table = {}
        self.var_count = 0
        self.arg_count = 0
