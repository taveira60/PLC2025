import re
import ply.lex as lex

# Dicionario de palavras reservadas 
reservadas = {
    'program': 'PROGRAM',
    'function': 'FUNCTION',
    'var': 'VAR',
    'begin': 'BEGIN',
    'end': 'END',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'while': 'WHILE',
    'do': 'DO',
    'for': 'FOR',
    'to': 'TO',
    'downto': 'DOWNTO',
    'true': 'TRUE',
    'false': 'FALSE',
    'integer': 'INTEGER',
    'boolean': 'BOOLEAN',
    'real': 'REAL',
    'char': 'CHAR',
    'string': 'STRING',
    'array': 'ARRAY',
    'of': 'OF',
    'readln': 'READLN',
    'writeln': 'WRITELN',
    'div': 'DIV',
    'mod': 'MOD',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    'procedure': 'PROCEDURE',
    'until': 'UNTIL',
    'repeat': 'REPEAT'
}

# Lista que junta o resto dos tokens ao restaste das palavras reservadas
tokens = [
    'ID', 'NUMS', 'NUM_REAL', 'STRINGS', 
    'DOT', 'DOUBLEDOT', 'SEMICOLON', 'COMMA',
    'PA', 'PF', 'PRA', 'PRF',
    'EQUALS', 'MULT', 'PLUS', 'MINUS', 'MENOR', 'MAIOR', 'DOTEDEQUALS',
    'RANGE', 'MAIORIGUAL', 'MENORIGUAL', 'DIFERENTE'
] + list(reservadas.values())

t_DOTEDEQUALS = r':='
t_RANGE = r'\.\.'
t_DOT = r'\.'
t_DOUBLEDOT = r':'
t_SEMICOLON = r';'
t_COMMA = r','
t_PA = r'\('
t_PF = r'\)'
t_PRA = r'\['
t_PRF = r'\]'
t_EQUALS = r'='
t_MULT = r'\*'
t_PLUS = r'\+'
t_MINUS = r'-'
t_MENOR = r'<'
t_MAIOR = r'>'
t_MAIORIGUAL = r'>='
t_MENORIGUAL = r'<='
t_DIFERENTE = r'<>'


t_STRINGS = r"'[^']*'"


t_NUMS = r'\d+'



def t_NUM_REAL(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t


def t_COMMENT(t):
    r'\{[^}]*\}'
    t.lexer.lineno += t.value.count('\n')
    pass


def t_COMMENT_LINE(t):
    r'//.*'
    pass


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.value = t.value.lower()
    t.type = reservadas.get(t.value, 'ID')
    return t


t_ignore = ' \t'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print(f"Caractere ilegal: {t.value[0]!r}")
    t.lexer.skip(1)


lexer = lex.lex()
