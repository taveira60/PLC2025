import json
import ply.lex as lex

states=(('moeda','exclusive'),('selecting','exclusive'))

tokens=(
    'LISTAR',
    'E_MOEDA',
    'SELECIONAR',
    'SAIR',
    'VALOR_EURO',
    'VALOR_CENT',
    'F_MOEDA',
    'VIRG_MOEDA'    
)

t_ANY_ignore=' \t\n'

t_moeda_VIRG_MOEDA=r','

def t_LISTAR(t):
    r'LISTAR'
    return t

def t_E_MOEDA(t):
    r'MOEDA'
    t.lexer.begin('moeda')
    return t

def t_moeda_VALOR_EURO(t):
    r'\d+e'
    return t

def t_moeda_VALOR_CENT(t):
    r'\d+c'
    return t

def t_moeda_F_MOEDA(t):
    r'\.'
    t.lexer.begin('INITIAL')
    return t

def t_SELECIONAR(t):
    r'SELECIONAR'
    t.lexer.begin('selecting')
    return t

def t_selecting_CODIGO(t):
    r'[A-Z]\d+'
    t.lexer.begin('INITIAL')
    return t

def t_ANY_error(t): 
    print(f"Carácter ilegal: {t.value[0]}")
    t.lexer.skip(1)

def t_SAIR(t):
    r'SAIR'
    return t


lexer = lex.lex() 
