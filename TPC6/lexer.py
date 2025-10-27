import ply.lex as lex

tokens = ('NUM', 'PLUS', 'MINUS', 'MUL', 'DIV', 'PA', 'PF')

t_PLUS  = r'\+'
t_MINUS = r'-'
t_MUL   = r'\*'
t_DIV   = r'/'
t_PA    = r'\('
t_PF    = r'\)'

t_NUM = r'\d+'

t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print('Carácter desconhecido:', t.value[0], 'Linha:', t.lexer.lineno)
    t.lexer.skip(1)

lexer = lex.lex()