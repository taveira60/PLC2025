from expr_aritm_analex import lexer

prox_simb = None

def parserError(simb):
    print("Erro sintático, token inesperado:", simb)

def rec_term(simb):
    global prox_simb
    if prox_simb and prox_simb.type == simb:
        prox_simb = lexer.token()
    else:
        parserError(prox_simb)

# Ideia da gramática:
'''
E  → T E2
E2 → + T E2 
    | - T E2 
    | ε
T  → F T2
T2 → * F T2 
    | / F T2 
    | ε
F  → NUM 
    | ( E )
'''       

# ---------- Produções ----------

def rec_E():
    print("Derivando por: E → T E2")
    rec_T()
    rec_E2()
    print("Reconheci: E → T E2")

def rec_E2():
    global prox_simb
    if prox_simb and prox_simb.type == 'PLUS':
        print("Derivando por: E2 → + T E2")
        rec_term('PLUS')
        rec_T()
        rec_E2()
        print("Reconheci: E2 → + T E2")
    elif prox_simb and prox_simb.type == 'MINUS':
        print("Derivando por: E2 → - T E2")
        rec_term('MINUS')
        rec_T()
        rec_E2()
        print("Reconheci: E2 → - T E2")
    else:
        print("Derivando por: E2 → ε (vazio)")

def rec_T():
    print("Derivando por: T → F T2")
    rec_F()
    rec_T2()
    print("Reconheci: T → F T2")

def rec_T2():
    global prox_simb
    if prox_simb and prox_simb.type == 'MUL':
        print("Derivando por: T2 → * F T2")
        rec_term('MUL')
        rec_F()
        rec_T2()
        print("Reconheci: T2 → * F T2")
    elif prox_simb and prox_simb.type == 'DIV':
        print("Derivando por: T2 → / F T2")
        rec_term('DIV')
        rec_F()
        rec_T2()
        print("Reconheci: T2 → / F T2")
    else:
        print("Derivando por: T2 → ε (vazio)")

def rec_F():
    global prox_simb
    if prox_simb is None:
        parserError(prox_simb)
        return
    if prox_simb.type == 'NUM':
        print("Derivando por: F → NUM")
        rec_term('NUM')
        print("Reconheci: F → NUM")
    elif prox_simb.type == 'PA':
        print("Derivando por: F → ( E )")
        rec_term('PA')
        rec_E()
        rec_term('PF')
        print("Reconheci: F → ( E )")
    else:
        parserError(prox_simb)

def rec_Parser(data):
    global prox_simb
    lexer.input(data)
    prox_simb = lexer.token()
    rec_E()
    print("Análise concluída!")