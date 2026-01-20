code = []  # Codigo gerado
global_var_map = {}  # Dicionario das variaveis globais nome e endereço
global_var_count = 0  # Numero de variaveis globais
global_type_map = {}   # Dicionario de tipos de cada variavel global

function_labels = {}  # Dicionario com Nome das funções e o label que as mesmas tem
current_scope = None    # Nome da função atual
local_var_map = {}  # Dicionario das variaveis locais
local_var_count = 0  # Numero de variaveis locais
local_type_map = {}  # Dicionario de tipos de cada variavel local

label_count = 0  # Variavel que garante que as labels sao unicas


def emite(instr):
    code.append(instr)

# Adiciona uma linha vazia para o codigo ficar mais organizado


def emite_nova_linha():
    code.append("")

# Gera os labels mas não para funções


def new_label():
    global label_count
    l = f"label{label_count}"
    label_count += 1
    return l


def get_var_addr_info(name):
    # Dentro de uma função procuramos primeiro variaveis locais e depois globais
    if current_scope is not None and name in local_var_map:
        return ('L', local_var_map[name])
    if name in global_var_map:
        return ('G', global_var_map[name])
    raise Exception(f"Variável '{name}' não encontrada")


def get_var_type(name):
    if current_scope is not None and name in local_type_map:
        return local_type_map[name]
    if name in global_type_map:
        return global_type_map[name]
    return None

# Para cada variavel e string declara as mesmas começam com um valor padrão


def inicializar_variaveis(var_map, type_map, scope='G'):
    for nome, addr in var_map.items():
        if addr < 0:
            continue  # Ignora argumentos
        tipo = type_map.get(nome)

        if isinstance(tipo, (list, tuple)) and tipo[0] == 'array':
            inicio, fim = tipo[1], tipo[2]
            tam = fim - inicio + 1
            emite(f"PUSHI {tam}")
            emite("ALLOCN")
            if scope == 'G':
                emite(f"STOREG {addr}")
            else:
                emite(f"STOREL {addr}")

        elif tipo == 'string':
            emite('PUSHS ""')
            if scope == 'G':
                emite(f"STOREG {addr}")
            else:
                emite(f"STOREL {addr}")

# Se o array não começar a 0 ele e arranjado


def corrigir_offset_array(var_name):
    t = get_var_type(var_name)
    if isinstance(t, (list, tuple)) and t[0] == 'array':
        inicio = t[1]
        if inicio != 0:
            emite(f"PUSHI {inicio}")
            emite("SUB")


def gen_length(args):
    arg = args[0]
    if isinstance(arg, (list, tuple)) and len(arg) > 0 and arg[0] == 'var':
        nome = arg[1]
        t = get_var_type(nome)
        if isinstance(t, (list, tuple)) and t[0] == 'array':
            tam = t[2]-t[1]+1
            emite(f"PUSHI {tam}")
            return
    visit(arg)
    emite("STRLEN")


def gen_int(args):
    visit(args[0])
    emite("ATOI")


def gen_str(args):
    visit(args[0])
    emite("STRI")


builtin_generators = {'length': gen_length, 'int': gen_int, 'str': gen_str}

# Começa os arrays todos a vazios de novo


def gerar_codigo(ast):
    global code, global_var_map, global_var_count, global_type_map
    global function_labels, current_scope, local_var_map, local_var_count, local_type_map, label_count

    code = []
    global_var_map = {}
    global_var_count = 0
    global_type_map = {}
    function_labels = {}
    current_scope = None
    local_var_map = {}
    local_var_count = 0
    local_type_map = {}
    label_count = 0

    try:
        visit(ast)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[ERRO NO CODEGEN] {e}")
    return "\n".join(code)

# Função que percorre a AST


def visit(node):
    global current_scope, local_var_map, local_type_map, local_var_count, global_var_count

    if node is None:
        return

    if isinstance(node, (list, tuple)):
        if len(node) > 0 and isinstance(node[0], str):
            tipo = node[0]

            if tipo == 'program':
                _, _, funcs, main_block = node

                emite("START")
                emite_nova_linha()

                if funcs:
                    for f in funcs:
                        # O label passa a ser exatamente o nome da função
                        function_labels[f[1]] = f[1]

                # Gerar MAIN
                visit(main_block)

                emite("STOP")
                emite_nova_linha()

                # Gerar FUNÇÕES
                if funcs:
                    for f in funcs:
                        visit(f)
                        emite_nova_linha()

                return

            if tipo in ('function', 'procedure'):
                name = node[1]
                params = node[2]
                body = node[4] if tipo == 'function' else node[3]
                ret_type = node[3] if tipo == 'function' else None

                current_scope = name
                local_var_map = {}
                local_type_map = {}
                local_var_count = 0

                emite(f"{function_labels[name]}:")

                if params:
                    idx = -(len(params))
                    for p_name, p_type in reversed(params):
                        local_var_map[p_name] = idx
                        local_type_map[p_name] = p_type
                        idx += 1
                        

                if tipo == 'function':
                    local_var_map[name] = local_var_count
                    local_type_map[name] = ret_type
                    local_var_count += 1

                if body[0] == 'func':
                    decls = body[1]
                    stats = body[2]

                    if decls:
                        for d in decls:
                            if d:
                                vars_list, t_var = d
                                for v in vars_list:
                                    if v not in local_var_map:
                                        local_var_map[v] = local_var_count
                                        local_type_map[v] = t_var
                                        local_var_count += 1

                    if local_var_count > 0:
                        emite(f"PUSHN {local_var_count}")

                    inicializar_variaveis(
                        local_var_map, local_type_map, scope='L')

                    if stats:
                        visit(stats)

                if tipo == 'function':
                    ret_addr = local_var_map[name]
                    emite(f"PUSHL {ret_addr}")
                    pass

                emite("RETURN")
                current_scope = None
                local_var_map = {}
                local_type_map = {}
                local_var_count = 0
                return

            if tipo == 'main':
                decls = node[1]
                stats = node[2]
                if decls:
                    for d in decls:
                        if d:
                            vars_list, t_var = d
                            for v in vars_list:
                                if v not in global_var_map:
                                    global_var_map[v] = global_var_count
                                    global_type_map[v] = t_var
                                    global_var_count += 1
                if global_var_count > 0:
                    emite(f"PUSHN {global_var_count}")
                    inicializar_variaveis(
                        global_var_map, global_type_map, scope='G')
                visit(stats)
                return

            if tipo == 'call':
                func_name = node[1]
                args = node[2]
                fl = func_name.lower()
                if fl in builtin_generators:
                    builtin_generators[fl](args)
                elif func_name in function_labels:
                    if args:
                        for a in args:
                            visit(a)
                    emite(f"PUSHA {function_labels[func_name]}")
                    emite("CALL")
                else:
                    print(f" Chamada desconhecida {func_name}")
                return

            if tipo == 'assign':
                lvalue = node[1]
                expr = node[2]
                if lvalue[0] == 'var':
                    nome = lvalue[1]
                    scope, addr = get_var_addr_info(nome)
                    visit(expr)
                    if scope == 'G':
                        emite(f"STOREG {addr}")
                    else:
                        emite(f"STOREL {addr}")
                elif lvalue[0] == 'array_access':

                    var_node = lvalue[1]
                    idx_node = lvalue[2]
                    nome = var_node[1]
                    scope, addr = get_var_addr_info(nome)

                    if scope == 'G':
                        emite(f"PUSHG {addr}")
                    else:
                        emite(f"PUSHL {addr}")

                    t = get_var_type(nome)
                    if t == 'string':
                        visit(idx_node)
                        emite("PUSHI 1")
                        emite("SUB")
                    else:
                        visit(idx_node)
                        corrigir_offset_array(nome)

                    visit(expr)

                    emite("STOREN")
                return

            if tipo == 'var':
                nome = node[1]
                scope, addr = get_var_addr_info(nome)
                if scope == 'G':
                    emite(f"PUSHG {addr}")
                else:
                    emite(f"PUSHL {addr}")
                return

            if tipo == 'array_access':
                var_node = node[1]
                idx_node = node[2]
                nome = var_node[1] if isinstance(
                    var_node, (list, tuple)) and var_node[0] == 'var' else var_node
                t = get_var_type(nome)
                scope, addr = get_var_addr_info(nome)

                if t == 'string':
                    if scope == 'G':
                        emite(f"PUSHG {addr}")
                    else:
                        emite(f"PUSHL {addr}")
                    visit(idx_node)
                    emite("PUSHI 1")
                    emite("SUB")
                    emite("CHARAT")
                else:
                    if scope == 'G':
                        emite(f"PUSHG {addr}")
                    else:
                        emite(f"PUSHL {addr}")
                    visit(idx_node)
                    corrigir_offset_array(nome)
                    emite("LOADN")
                return

            if tipo == 'writeln':
                for expr in node[1]:  
                    if isinstance(expr, str) and expr.startswith("'") and expr.endswith("'"):
                        texto = expr.strip("'")
                        if len(texto) == 1:
                            emite(f"PUSHI {ord(texto)}")
                            emite("WRITECHR")
                        else:
                            emite(f'PUSHS "{texto}"')
                            emite("WRITES")
                    elif isinstance(expr, (list, tuple)) and expr[1][0] == 'var':
                        var_name = expr[1][1]
                        t = get_var_type(var_name)
                        visit(expr)
                        if t in ('integer', 'boolean'):
                            emite("WRITEI")
                        elif t == 'real':
                            emite("WRITEF")
                        elif t == 'string':
                            emite("WRITECHR")
                        else:
                            #emite("Erro de tipo")
                            
                            emite("WRITEI")
                           
                    else:
                        visit(expr)
                        emite("WRITEI")
                emite("WRITELN")
                return

            if tipo == 'readln':
                for lvalue in node[1]:
                    if lvalue[0] == 'var':
                        var_name = lvalue[1]
                        t = get_var_type(var_name)
                        emite("READ")
                        elem_type = t
                        if isinstance(t, (list, tuple)) and t[0] == 'array':
                            elem_type = t[3]
                        if elem_type == 'integer':
                            emite("ATOI")
                        elif elem_type == 'real':
                            emite("ATOF")

                        scope, addr = get_var_addr_info(var_name)
                        if scope == 'G':
                            emite(f"STOREG {addr}")
                        else:
                            emite(f"STOREL {addr}")

                    elif lvalue[0] == 'array_access':
                        # Ordem para STOREN [Array, Indice, Valor]

                        var_node = lvalue[1]
                        idx_node = lvalue[2]
                        nome = var_node[1]
                        scope, addr = get_var_addr_info(nome)

                        if scope == 'G':
                            emite(f"PUSHG {addr}")
                        else:
                            emite(f"PUSHL {addr}")

                        visit(idx_node)
                        corrigir_offset_array(nome)

                        emite("READ")
                        t = get_var_type(nome)
                        elem_type = t[3] if (isinstance(
                            t, (list, tuple)) and len(t) > 3) else 'integer'
                        if elem_type == 'integer':
                            emite("ATOI")
                        elif elem_type == 'real':
                            emite("ATOF")

                        emite("STOREN")
                return

            if tipo == 'for':
                var_name = node[1]
                start_expr = node[2]
                direction = node[3]
                end_expr = node[4]
                body = node[5]
                scope, addr = get_var_addr_info(var_name)
                loop_label = new_label()
                exit_label = new_label()
                visit(start_expr)
                if scope == 'G':
                    emite(f"STOREG {addr}")
                else:
                    emite(f"STOREL {addr}")
                emite(f"{loop_label}:")
                if scope == 'G':
                    emite(f"PUSHG {addr}")
                else:
                    emite(f"PUSHL {addr}")
                visit(end_expr)
                if direction == 'to':
                    emite("INFEQ")
                else:
                    emite("SUPEQ")
                emite(f"JZ {exit_label}")
                visit(body)
                if scope == 'G':
                    emite(f"PUSHG {addr}")
                else:
                    emite(f"PUSHL {addr}")
                emite("PUSHI 1")
                if direction == 'to':
                    emite("ADD")
                else:
                    emite("SUB")
                if scope == 'G':
                    emite(f"STOREG {addr}")
                else:
                    emite(f"STOREL {addr}")
                emite(f"JUMP {loop_label}")
                emite(f"{exit_label}:")
                return

            if tipo == 'if':
                cond = node[1]
                then_block = node[2]
                end_label = new_label()
                visit(cond)
                emite(f"JZ {end_label}")
                visit(then_block)
                emite(f"{end_label}:")
                return

            if tipo == 'if-else':
                cond = node[1]
                then_block = node[2]
                else_block = node[3]
                else_label = new_label()
                end_label = new_label()
                visit(cond)
                emite(f"JZ {else_label}")
                visit(then_block)
                emite(f"JUMP {end_label}")
                emite(f"{else_label}:")
                visit(else_block)
                emite(f"{end_label}:")
                return

            if tipo == 'while':
                cond = node[1]
                body = node[2]
                start_label = new_label()
                end_label = new_label()
                emite(f"{start_label}:")
                visit(cond)
                emite(f"JZ {end_label}")
                visit(body)
                emite(f"JUMP {start_label}")
                emite(f"{end_label}:")
                return

            if tipo in ['+', '-', '*', 'div', 'mod']:
                if tipo == '+':
                    left = node[1]
                    right = node[2]
                    visit(left)
                    visit(right)
                    emite("ADD")
                else:
                    visit(node[1])
                    visit(node[2])
                    ops = {'-': 'SUB', '*': 'MUL', 'div': 'DIV', 'mod': 'MOD'}
                    emite(ops[tipo])
                return

            if tipo in ['=', '<>', '<', '>', '<=', '>=']:
                visit(node[1])
                visit(node[2])
                if tipo == '<>':
                    emite("EQUAL")
                    emite("NOT")
                else:
                    ops = {'=': 'EQUAL', '<': 'INF', '>': 'SUP','<=': 'INFEQ', '>=': 'SUPEQ'}
                    emite(ops[tipo])
                return

            if tipo == 'and':
                visit(node[1])
                visit(node[2])
                emite("AND")
                return

            if tipo == 'or':
                visit(node[1])
                visit(node[2])
                emite("OR")
                return

            if tipo == 'not':
                visit(node[1])
                emite("NOT")
                return

            if tipo == 'neg':
                emite("PUSHI 0")
                visit(node[1])
                emite("SUB")
                return

            for sub in node[1:]:
                visit(sub)
            return

        for sub in node:
            visit(sub)
        return

    if isinstance(node, int):
        emite(f"PUSHI {node}")

    elif isinstance(node, float):
        emite(f"PUSHF {node}")

    elif isinstance(node, str):

        if node.isdigit() or (node.startswith('-') and node[1:].isdigit()):
            emite(f"PUSHI {node}")

        elif node.lower() == 'true':
            emite("PUSHI 1")

        elif node.lower() == 'false':
            emite("PUSHI 0")

        elif node.startswith("'") and node.endswith("'"):
            texto = node.strip("'")

            if len(texto) == 1:
                emite(f"PUSHI {ord(texto)}")
            else:
                emite(f'PUSHS "{texto}"')

    elif isinstance(node, tuple) and len(node) > 0 and node[0] == 'call':
        visit(['call', node[1], node[2]])
