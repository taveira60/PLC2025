from lexer import lexer, tokens
import ply.yacc as yacc

start = 'S'


def p_empty(p):
    '''empty :'''
    pass


def p_S(p):
    r"""
    S : PROGRAM ID SEMICOLON FDECLS B DOT
    """
    p[0] = ['program', p[2], p[4], p[5]]


def p_fdecls(p):
    r"""
    FDECLS  : FDECLS FUNCTION_DECL
            | FDECLS PROCEDURE_DECL
            | empty
    """
    p[0] = p[1] + [p[2]] if len(p) == 3 else []


def p_function_decl(p):
    r"""
    FUNCTION_DECL : FUNCTION ID PA FPARAMS PF DOUBLEDOT TIPO SEMICOLON FBLOCK
    """
    p[0] = ('function', p[2], p[4], p[7], p[9])


def p_procedure_decl(p):
    r"""
    PROCEDURE_DECL : PROCEDURE ID PA FPARAMS PF SEMICOLON FBLOCK
                   | PROCEDURE ID SEMICOLON FBLOCK
    """
    if len(p) == 8:
        p[0] = ['procedure', p[2], p[4], p[7]]
    else:
        p[0] = ['procedure', p[2], [], p[4]]


def p_fparams(p):
    r"""
    FPARAMS : PARAM_LIST
            | empty
    """
    p[0] = p[1] if len(p) == 2 else []


def p_param_list(p):
    r"""
    PARAM_LIST  : PARAM_LIST COMMA PARAM
                | PARAM
    """
    p[0] = p[1]+[p[3]] if len(p) == 4 else [p[1]]


def p_param(p):
    r"""
    PARAM : ID DOUBLEDOT TIPO
    """
    p[0] = [p[1], p[3]]


def p_fblock(p):
    r"""
    FBLOCK  : VAR DL BEGIN CL END SEMICOLON
            | BEGIN CL END SEMICOLON
    """
    p[0] = ["func", p[2], p[4]] if len(p) == 7 else ["func", None, p[2]]


def p_b(p):
    r'''
    B   : VAR DL BEGIN CL END
        | BEGIN CL END
    '''
    p[0] = ["main", p[2], p[4]] if len(p) == 6 else ["main", None, p[2]]


def p_dl(p):
    r'''
    DL  : DL SEMICOLON D
        | D
    '''
    if len(p) == 4:
        # Só adiciona p[3] se não for None
        if p[3] is not None:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = p[1]
    else:
        # Se D for None (empty), retorna lista vazia
        p[0] = [p[1]] if p[1] is not None else []


def p_d(p):
    r"""
    D : VL DOUBLEDOT TIPO 
      | empty
    """
    p[0] = [p[1], p[3]] if len(p) == 4 else None


def p_tipo(p):
    r"""
    TIPO : BASE_TIPO
         | ARRAY_TIPO
    """
    p[0] = p[1]

# Podemos precisar de Adicionar Mais tipos


def p_base_tipo(p):
    r"""
    BASE_TIPO   : INTEGER
                | BOOLEAN
                | STRING
                | REAL      
                | CHAR           
    """
    p[0] = p[1]


def p_index(p):
    r'''
    INDEX : NUMS
          | MINUS NUMS
          | INDEX MINUS NUMS
          | INDEX PLUS NUMS
          | INDEX MULT NUMS
          | INDEX DIV NUMS
          | INDEX MOD NUMS
    '''
    if len(p) == 2:
        p[0] = int(p[1])
    elif len(p) == 3:
        p[0] = -int(p[2])
    elif len(p) == 4:
        left = p[1]
        op = p[2]
        right = int(p[3])

        if op == '+':
            p[0] = left + right
        elif op == '-':
            p[0] = left - right
        elif op == '*':
            p[0] = left * right
        elif op == '/':
            p[0] = left // right  # Integer division
        elif op == '%':
            p[0] = left % right


def p_array_tipo(p):
    r"""
    ARRAY_TIPO  : ARRAY PRA INDEX RANGE INDEX PRF OF BASE_TIPO
    """
    p[0] = ("array", p[3], p[5], p[8])


def p_vl(p):
    r'''
    VL  : VL COMMA ID
        | ID
    '''
    p[0] = p[1]+[p[3]] if len(p) == 4 else [p[1]]

# Isto deve estar mal ??


def p_cl(p):
    r"""
    CL  : CL SEMICOLON C
        | C
    """
    if len(p) == 4:
        if p[3] is not None:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = p[1]
    else:
        p[0] = [p[1]] if p[1] is not None else []


def p_call(p):
    r"""
    Call : ID PA AL PF
         | ID
    """
    if len(p) == 5:
        p[0] = ['call', p[1], p[3]]
    else:
        p[0] = ['call', p[1], []]


def p_c(p):
    r"""
    C : matched
      | unmatched
    """
    p[0] = p[1]


def p_matched(p):
    r"""
    matched : IF E THEN matched ELSE matched
            | CC
    """
    p[0] = p[1] if len(p) == 2 else ["if-else", p[2], p[4], p[6]]


def p_unmatched(p):
    r"""
    unmatched : IF E THEN C
              | IF E THEN matched ELSE unmatched
    """
    p[0] = ["if", p[2], p[4]] if len(p) == 5 else ["if-else", p[2], p[4], p[6]]


def p_repeat(p):
    r"""
    Repeat : REPEAT C UNTIL E SEMICOLON
    """
    p[0] = ['repeat', p[2], 'until', p[4]]


def p_write(p):
    r'''
    Write  : WRITELN PA AL PF
    '''
    p[0] = ['writeln', p[3]]


def p_read(p):
    r'''
    Read : READLN PA LVALUE_LIST PF
    '''
    p[0] = ['readln', p[3]]


def p_lvalue_list(p):
    r'''
    LVALUE_LIST : LVALUE_LIST COMMA LVALUE
                | LVALUE
    '''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_assign(p):
    r'''
    Assign  : LVALUE DOTEDEQUALS E
    '''
    p[0] = ['assign', p[1], p[3]]


def p_for(p):
    r'''
    For : FOR ID DOTEDEQUALS E FORDIR E DO C
    '''
    p[0] = ['for', p[2], p[4], p[5], p[6], p[8]]


def p_fordir(p):
    r'''
    FORDIR  : TO
            | DOWNTO
    '''
    p[0] = p[1]


def p_while(p):
    r'''
    While : WHILE E DO C
    '''
    p[0] = ["while", p[2], p[4]]


def p_cc(p):
    r"""
    CC   : Write
        | Read
        | Assign
        | For
        | While
        | Call
        | Repeat
        | BEGIN CL END
        | empty
    """
    p[0] = p[2] if len(p) == 4 else p[1]


def p_lvalue(p):
    r'''
    LVALUE : LVALUE PRA E PRF
           | ID
    '''
    if len(p) == 2:
        # Caso base: é apenas um ID (variável simples)
        p[0] = ['var', p[1]]
    else:
        # Caso recursivo: acesso a array (Estrutura, Índice)
        # Ex: ('array_access', ('var', 'm'), 1)
        p[0] = ['array_access', p[1], p[3]]


def p_al(p):
    r'''
    AL  : AL COMMA E
        | E
    '''
    p[0] = p[1]+[p[3]] if len(p) == 4 else [p[1]]


def p_e(p):
    r'''
    E   : E OR E1
        | E1
    '''
    p[0] = ["or", p[1], p[3]] if len(p) == 4 else p[1]


def p_e1(p):
    r'''
    E1 : E1 AND E2
       | E2
    '''
    p[0] = ["and", p[1], p[3]] if len(p) == 4 else p[1]


def p_e2(p):
    r'''
    E2  : A MENOR A
        | A MAIOR A
        | A MAIORIGUAL A
        | A MENORIGUAL A
        | A DIFERENTE A
        | A EQUALS A
        | A
    '''
    if len(p) == 4:
        # Retorna (operador, esquerda, direita)
        p[0] = [p[2], p[1], p[3]]
    else:
        p[0] = p[1]


def p_a(p):
    r'''
    A   : A PLUS T
        | A MINUS T
        | T
    '''
    p[0] = [p[2], p[1], p[3]] if len(p) == 4 else p[1]


def p_t(p):
    r'''
    T   : T MULT F
        | T DIV F
        | T MOD F
        | F
    '''
    p[0] = [p[2], p[1], p[3]] if len(p) == 4 else p[1]


def p_f(p):
    r'''
    F   : ID PA AL PF
        | LVALUE
        | NUMS
        | NUM_REAL
        | STRINGS
        | PA E PF
        | TRUE
        | FALSE
        | NOT F
        | MINUS F
        | PLUS F
    '''

    if len(p) == 5:
        # Chamada de função com argumentos: ID ( ARGS )
        p[0] = ['call', p[1], p[3]]

    elif len(p) == 4:
        # CORREÇÃO AQUI: Parênteses ( E )
        # p[1] é '(', p[2] é a Expressão, p[3] é ')'
        p[0] = p[2]

    elif len(p) == 3:
        # Operadores Unários
        if p[1] == 'not':
            p[0] = ['not', p[2]]
        elif p[1] == '-':
            p[0] = ['neg', p[2]]
        elif p[1] == '+':
            p[0] = p[2]
        # O 'else' que estava aqui para (E) estava errado pois o len é 4

    else:
        # LVALUE, NUMS, STRINGS, TRUE, FALSE
        p[0] = p[1]


def p_error(p):
    print('Erro sintático: ', p)
    parser.success = False


parser = yacc.yacc()


parser.success = True
parser.vars = dict()
