class SemanticAnalyzer:
    def __init__(self):
        
        # Cada escopo é uma tabela de variáveis.
        self.scopes = [{}]
        
        # Onde guardamos erros e avisos semânticos
        self.errors = []
        self.warnings = []
        
        # Para saber em que função estamos neste momento
        self.current_function = None
        
        # Guarda tamanhos de strings atribuídas a variáveis
        self.string_sizes = {}

        # Adiciona função embutida 'length
        self.declare('length', ('function', [('s', 'string')], 'integer'))

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    # Declara uma variável ou função
    def declare(self, name, type_info):
        current_scope = self.scopes[-1]
        
        if name in current_scope:
            self.errors.append(
                f"Erro: variável '{name}' já declarada no scope")
            return False

        # Se for array, verifica limites
        if isinstance(type_info, (list, tuple)) and len(type_info) >= 4 and type_info[0] == 'array':
            try:
                start_idx, end_idx = int(type_info[1]), int(type_info[2])
            except Exception:
                self.errors.append(
                    f"Erro na declaração do array '{name}': índices inválidos")
                return False

            # Índices invertidos não são permitidos
            if start_idx > end_idx:
                self.errors.append(
                    f"Erro na declaração do array '{name}': "
                    f"índice inicial ({start_idx}) maior que índice final ({end_idx})"
                )
                return False

            type_info = ('array', start_idx, end_idx, type_info[3])

        current_scope[name] = type_info
        return True

    # Procura variável nos escopos de dentro para fora
    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    # Tenta avaliar uma expressão constante
    def _get_constant_value(self, node):
        if node is None:
            return None

        # Strings que são números
        if isinstance(node, str):
            if node.isdigit():
                return int(node)
            if node.startswith('-') and node[1:].isdigit():
                return int(node)
            
        # Já tratados
        if isinstance(node, int):
            return node

        # Expressões como ['+', 2, 3]
        if isinstance(node, (list, tuple)) and len(node) > 0:
            node_type = node[0]

            if node_type in ['+', '-', '*', 'div', 'mod']:
                left_val = self._get_constant_value(node[1])
                right_val = self._get_constant_value(node[2])

                # Só calculamos se ambos forem constantes
                if left_val is not None and right_val is not None:
                    if node_type == '+':
                        return left_val + right_val
                    elif node_type == '-':
                        return left_val - right_val
                    elif node_type == '*':
                        return left_val * right_val
                    elif node_type == 'div':
                        return left_val // right_val if right_val != 0 else None
                    elif node_type == 'mod':
                        return left_val % right_val if right_val != 0 else None

            elif node_type == 'neg':
                val = self._get_constant_value(node[1])
                return -val if val is not None else None

        return None

    # Devolve o tamanho da string
    def _get_string_size(self, node):
        if node is None:
            return None

        if isinstance(node, str) and node.startswith("'") and node.endswith("'"):
            return len(node) - 2

        if isinstance(node, (list, tuple)) and len(node) >= 2 and node[0] == 'var':
            var_name = node[1]
            return self.string_sizes.get(var_name)

        if isinstance(node, (list, tuple)) and len(node) >= 3 and node[0] == '+':
            left_size = self._get_string_size(node[1])
            right_size = self._get_string_size(node[2])
            if left_size is not None and right_size is not None:
                return left_size + right_size

        return None
    
    # Devolve o tipo da expressão
    def get_type(self, node):
        if node is None:
            return None

        if isinstance(node, float):
            return 'real'

        if isinstance(node, str):
            if node in ['integer', 'boolean', 'string']:
                return node

            if node.isdigit() or (node.startswith('-') and node[1:].isdigit()):
                return 'integer'

            if node in ['true', 'false']:
                return 'boolean'

            if node.startswith("'") and node.endswith("'"):
                length = len(node) - 2
                if length == 1:
                    return 'char'  # <--- Agora '1' é tratado como Char

                return ('array', 1, length, 'char')
            return None

        if isinstance(node, int):
            return 'integer'

        if isinstance(node, (list, tuple)) and len(node) > 0:
            node_type = node[0]

            if node_type == 'var':
                var_name = node[1]
                var_info = self.lookup(var_name)
                if var_info is None:
                    self.errors.append(
                        f"Erro: variável '{var_name}' não declarada")
                    return None
                return var_info

            elif node_type == 'array_access':
                base = node[1]
                index = node[2]

                base_type = self.get_type(base)
                index_type = self.get_type(index)

                if base_type is None:
                    base_name = base[1] if isinstance(
                        base, (list, tuple)) and len(base) > 1 else str(base)
                    self.errors.append(
                        f"Erro: variável '{base_name}' não declarada")
                    return None

                is_array = isinstance(
                    base_type, (list, tuple)) and base_type[0] == 'array'
                is_string = base_type == 'string'

                if not (is_array or is_string):
                    base_name = base[1] if isinstance(
                        base, (list, tuple)) and len(base) > 1 else str(base)
                    self.errors.append(f"Erro: '{base_name}' não é um array")
                    return None

                if index_type != 'integer':
                    base_name = base[1] if isinstance(
                        base, (list, tuple)) and len(base) > 1 else str(base)
                    self.errors.append(
                        f"Erro: índice do array '{base_name}' deve ser inteiro")
                    return None

                if is_string:
                    if isinstance(base, (list, tuple)) and base[0] == 'var':
                        var_name = base[1]
                        if var_name in self.string_sizes:
                            string_length = self.string_sizes[var_name]
                            index_val = self._get_constant_value(index)

                            if index_val is not None:
                                if index_val < 1 or index_val > string_length:
                                    self.errors.append(
                                        f"Erro: índice {index_val} fora dos limites da string '{var_name}' "
                                        f"(tamanho conhecido: 1..{string_length})"
                                    )
                                    return None
                        else:
                            index_val = self._get_constant_value(index)
                            if index_val is not None and index_val > 255:
                                self.warnings.append(
                                    f"Aviso: índice {index_val} muito grande para string '{var_name}', pode crashar a VM "
                                )
                    return 'char'

                # Para arrays normais
                start_idx, end_idx, elem_type = int(
                    base_type[1]), int(base_type[2]), base_type[3]
                index_val = self._get_constant_value(index)

                if index_val is not None:
                    if not (min(start_idx, end_idx) <= index_val <= max(start_idx, end_idx)):
                        base_name = base[1] if isinstance(
                            base, (list, tuple)) and len(base) > 1 else str(base)

                        if index_val < min(start_idx, end_idx):
                            self.errors.append(
                                f"Erro: índice {index_val} é menor que o limite inferior do array '{base_name}' "
                                f"(limites: {start_idx}..{end_idx})"
                            )
                        else:
                            self.errors.append(
                                f"Erro: índice {index_val} é maior que o limite superior do array '{base_name}' "
                                f"(limites: {start_idx}..{end_idx})"
                            )
                        return None
                else:
                    # Índice não constante
                    base_name = base[1] if isinstance(
                        base, (list, tuple)) and len(base) > 1 else str(base)
                    self.warnings.append(
                        f"Aviso: não foi possível verificar limites do array '{base_name}' (índice não constante)"
                    )

                return elem_type

            elif node_type in ['+', '-', '*', 'div', 'mod', '/']:
                left_type = self.get_type(node[1])
                right_type = self.get_type(node[2])

                if node_type == '+':
                    left_is_string = self._is_string_type(left_type)
                    right_is_string = self._is_string_type(right_type)
                    if left_is_string and right_is_string:
                        return 'string'

                if node_type in ['div', 'mod']:
                    if left_type == 'integer' and right_type == 'integer':
                        return 'integer'
                    else:
                        self.errors.append(
                            f"Erro: operação '{node_type}' requer dois inteiros")
                        return None

                is_left_num = left_type in ['integer', 'real']
                is_right_num = right_type in ['integer', 'real']

                if is_left_num and is_right_num:
                    if node_type == '/' or left_type == 'real' or right_type == 'real':
                        return 'real'
                    return 'integer'

                self.errors.append(
                    f"Erro: operação '{node_type}' inválida entre {left_type} e {right_type}")
                return None

            elif node_type in ['<', '>', '<=', '>=', '=', '<>']:
                left_type = self.get_type(node[1])
                right_type = self.get_type(node[2])

                if left_type and right_type:
                    if node_type in ['<', '>', '<=', '>=']:
                        is_left_num = left_type in ['integer', 'real']
                        is_right_num = right_type in ['integer', 'real']

                        if not (is_left_num and is_right_num):
                            self.errors.append(
                                f"Erro: operador '{node_type}' precisa de valores numéricos")

                    elif node_type in ['=', '<>']:
                        if not self._types_compatible(left_type, right_type):
                            self.errors.append(
                                f"Erro: operador '{node_type}' precisa de tipos compatíveis")

                return 'boolean'

            elif node_type in ['and', 'or']:
                left_type = self.get_type(node[1])
                right_type = self.get_type(node[2])

                if left_type is None or right_type is None:
                    return 'boolean'  

                if left_type == 'boolean' and right_type == 'boolean':
                    return 'boolean'
                else:
                    self.errors.append(
                        f"Erro: operador lógico '{node_type}' só aceita duas expressões booleanas "
                        f"(esquerda: {left_type}, direita: {right_type})"
                    )
                    return None

            elif node_type == 'not':
                next_type = self.get_type(node[1])
                if next_type == 'boolean':
                    return 'boolean'
                else:
                    self.errors.append(
                        f"Erro: operador 'not' só aceita expressão booleana")
                    return None

            elif node_type == 'neg':
                next_type = self.get_type(node[1])
                if next_type in ['integer', 'real']:
                    return next_type
                else:
                    self.errors.append(
                        f"Erro: operador 'neg' só aceita expressões numéricas")
                    return None

            elif node_type == 'call':
                func_name = node[1]
                func_info = self.lookup(func_name)
                if func_info and isinstance(func_info, (list, tuple)) and func_info[0] == 'function':
                    return func_info[2]
                return None

    def _is_string_type(self, type_info):
        if type_info == 'string':
            return True
        if isinstance(type_info, (list, tuple)) and len(type_info) >= 4 and type_info[0] == 'array' and type_info[3] == 'char':
            return True
        return False

    def _types_compatible(self, type1, type2):
        if type1 == type2:
            return True

        if self._is_string_type(type1) and self._is_string_type(type2):
            return True

        if type1 == 'real' and type2 == 'integer':
            return True

        if (type1 == 'char' and type2 == 'string') or (type1 == 'string' and type2 == 'char'):
            return True

        return False

    def analyze(self, ast):
        if ast is None:
            return
        self.visit(ast)
        return len(self.errors) == 0

    
    # Metodos de visita 
    def visit(self, node):
        if node is None:
            return

        if isinstance(node, (list, tuple)) and len(node) > 0 and isinstance(node[0], str):
            node_type = node[0]

            if node_type == 'program':
                self.visit_program(node)
            elif node_type == 'function':
                self.visit_function(node)
            elif node_type == 'procedure':
                self.visit_procedure(node)
            elif node_type == 'main':
                self.visit_main(node)
            elif node_type == 'func':
                self.visit_func_block(node)
            elif node_type == 'assign':
                self.visit_assign(node)
            elif node_type == 'writeln':
                self.visit_writeln(node)
            elif node_type == 'readln':
                self.visit_readln(node)
            elif node_type == 'if':
                self.visit_if(node)
            elif node_type == 'if-else':
                self.visit_if_else(node)
            elif node_type == 'while':
                self.visit_while(node)
            elif node_type == 'for':
                self.visit_for(node)
            elif node_type == 'call':
                self.visit_call(node)
            else:
                self.get_type(node)
            return

        if isinstance(node, list):
            for element in node:
                self.visit(element)
            return

    def visit_program(self, node):
        _, _, funcs, main = node
        if funcs:
            for func in funcs:
                self.visit(func)
        self.visit(main)

    def visit_function(self, node):
        _, func_name, params, return_type, body = node
        self.declare(func_name, ('function', params, return_type))
        self.enter_scope()
        self.current_function = (func_name, return_type)

        if params:
            for param_name, param_type in params:
                self.declare(param_name, param_type)

        self.visit(body)
        self.current_function = None
        self.exit_scope()

    def visit_procedure(self, node):
        if len(node) == 4:
            _, proc_name, params, body = node
        else:
            _, proc_name, params, body = node

        self.declare(proc_name, ('procedure', params))
        self.enter_scope()

        if params:
            for param_name, param_type in params:
                self.declare(param_name, param_type)

        self.visit(body)
        self.exit_scope()

    def visit_func_block(self, node):
        _, declaration, commands = node

        if declaration:
            for decl in declaration:
                if decl:
                    var_list, var_type = decl
                    for var_name in var_list:
                        self.declare(var_name, var_type)

        if commands:
            for cmd in commands:
                self.visit(cmd)

    def visit_main(self, node):
        _, declaration, commands = node

        if declaration:
            for decl in declaration:
                if decl:
                    var_list, var_type = decl
                    for var_name in var_list:
                        self.declare(var_name, var_type)

        if commands:
            for cmd in commands:
                self.visit(cmd)

    def visit_assign(self, node):
        _, lvalue, expression = node

        lvalue_type = self.get_type(lvalue)
        expression_type = self.get_type(expression)

        if lvalue_type is None:
            return

        # Atribuição ao retorno de função
        if isinstance(lvalue_type, (list, tuple)) and lvalue_type[0] == 'function':
            if self.current_function and self.current_function[0] == lvalue[1]:
                expected_return_type = self.current_function[1]
                if not self._types_compatible(expression_type, expected_return_type):
                    self.errors.append(
                        f"Erro: retorno da função '{lvalue[1]}' esperava {expected_return_type}, "
                        f"mas recebeu {expression_type}"
                    )
            else:
                self.errors.append(
                    f"Erro: não é possível atribuir a função '{lvalue[1]}' fora do seu corpo")
            return

        if lvalue_type == 'string' and isinstance(lvalue, (list, tuple)) and lvalue[0] == 'var':
            var_name = lvalue[1]
            size = self._get_string_size(expression)

            if size is not None:
                self.string_sizes[var_name] = size
            else:
                self.string_sizes.pop(var_name, None)

        if expression_type and not self._types_compatible(lvalue_type, expression_type):
            self.errors.append(
                f"Erro: atribuição incompatível - esperado {lvalue_type}, recebeu {expression_type}"
            )

    def visit_writeln(self, node):
        _, expr = node
        if expr:
            for e in expr:
                self.get_type(e)

    def visit_readln(self, node):
        _, expression = node
        if expression:
            for expr in expression:
                expr_type = self.get_type(expr)
                # Perder rastreamento ao ler string
                if expr_type == 'string' and isinstance(expr, (list, tuple)) and expr[0] == 'var':
                    var_name = expr[1]
                    self.string_sizes.pop(var_name, None)

    def visit_if(self, node):
        _, condition, then_block = node
        cond_type = self.get_type(condition)
        if cond_type and cond_type != 'boolean':
            self.errors.append(f"Erro: condição tem de ser um booleano")
        self.visit(then_block)

    def visit_if_else(self, node):
        _, condition, then_block, else_block = node
        cond_type = self.get_type(condition)
        if cond_type and cond_type != 'boolean':
            self.errors.append(f"Erro: condição tem de ser um booleano")
        self.visit(then_block)
        self.visit(else_block)

    def visit_while(self, node):
        _, condition, while_block = node
        cond_type = self.get_type(condition)
        if cond_type and cond_type != 'boolean':
            self.errors.append(
                f"Erro: while está à espera de uma condição booleana")
        self.visit(while_block)

    def visit_for(self, node):
        _, var_name, start, direction, end, body = node
        var_type = self.lookup(var_name)

        if var_type is None:
            self.errors.append(
                f"Erro: variável '{var_name}' não está declarada")
        elif var_type != 'integer':
            self.errors.append(
                f"Erro: variável '{var_name}' tem de ser um inteiro")

        start_type = self.get_type(start)
        end_type = self.get_type(end)

        if start_type != 'integer':
            self.errors.append(
                f"Erro: limite inicial do 'for' deve ser inteiro")
        if end_type != 'integer':
            self.errors.append(f"Erro: limite final do 'for' deve ser inteiro")

        self.visit(body)

    def visit_call(self, node):
        _, func_name, args = node
        func_info = self.lookup(func_name)

        if func_info is None:
            self.errors.append(f"Erro: função '{func_name}' não declarada")
            return

        if isinstance(func_info, (list, tuple)) and func_info[0] in ['function', 'procedure']:
            expected_params = func_info[1] or []
            args_list = args or []
            if len(args_list) != len(expected_params):
                self.errors.append(
                    f"Erro: função '{func_name}' espera {len(expected_params)} "
                    f"argumentos, mas recebeu {len(args_list)}"
                )
            else:
                for i, (arg, (param_name, param_type)) in enumerate(zip(args_list, expected_params)):
                    arg_type = self.get_type(arg)
                    if arg_type and not self._types_compatible(arg_type, param_type):
                        self.errors.append(
                            f"Erro: argumento {i+1} da função '{func_name}' esperava {param_type}, "
                            f"mas recebeu {arg_type}"
                        )

    def print_errors(self):
        if self.warnings:
            print("\n=== AVISOS ===")
            for warning in self.warnings:
                print(warning)

        if self.errors:
            print("\n=== ERROS SEMÂNTICOS ===")
            for error in self.errors:
                print(error)
        else:
            print("\nAnálise semântica concluída sem erros!")

    def print_symbol_table(self):
        print("\n=== TABELA DE SÍMBOLOS ===")
        for i, scope in enumerate(self.scopes):
            print(f"\nEscopo {i}:")
            for name, type_info in scope.items():
                print(f"  {name}: {type_info}")

        return self.scopes
