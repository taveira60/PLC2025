import json
import sys

import lexer as lex

f=open("stock.json","r")
stock=json.load(f)

saldo=0
open=True

def cai_troco(saldo):
    moedas=[200,100,50,20,10,5,2,1]
    resultado=[]
    for moeda in moedas:
        qtd=saldo//moeda
        if qtd>0:
            saldo-=qtd*moeda
            resultado.append(f"{qtd}x {moeda//100}e")
        else:
            resultado.append(f"{qtd}x {moeda}c")
            
    return "Retire o troco: " + ", ".join(resultado) + "."

def getSaldo(saldo):
    buf = 0
    while saldo >= 100:
        buf += 1
        saldo -= 100
    return f'{int(buf)}e{int(saldo)}c'


print("maq: Bom dia. Estou disponível para atender o seu pedido.")

for linha in sys.stdin:
    
    lex.lexer.input(linha)
    
    
    for tok in lex.lexer:
            
        if(tok.type == 'LISTAR'):
            r'^LISTAR'
            saida = "maq:\n"
            saida += "cod  | nome         | quantidade |  preço\n"
            saida += "------------------------------------------------------\n"
            for prod in stock["stock"]:
                saida += f"{prod['cod']}     {prod['nome']}    {prod['quant']}         {prod['preco']}\n"
            saida += "\nSaldo = " + getSaldo(saldo) + "\n" 
            print(saida)
        
        if(tok.type=='VALOR_EURO'):
            saldo += int(tok.value[:-1])*100
            
        if(tok.type == 'VALOR_CENT'):
            saldo += int(tok.value[:-1])
        
        if(tok.type == 'F_MOEDA'):
            print("maq: Saldo = "+ getSaldo(saldo))

        if(tok.type == 'SELECIONAR'):
            pass

        if(tok.type == 'CODIGO'):
            found = False
            for prod in stock["stock"]:
                if prod['cod'] == tok.value and prod['quant'] > 0:
                    found = True
                    if prod['preco'] <= saldo:
                        saldo -= prod['preco']*100
                        prod['quant'] -= 1
                        print("maq: Pode retirar o produto dispensado " +  prod['nome'])
                        print('maq: Saldo = ' + getSaldo(saldo))
                    else:
                        print("maq: Saldo insufuciente para satisfazer o seu pedido")
                        print("Saldo = " + getSaldo(saldo) + "; Pedido = " + getSaldo(prod['preco']*100))
                    break
            
            if not found:
                print("maq: Produto inexistente")
            

        if(tok.type == 'SAIR'):
            print("maq: " + cai_troco(saldo))
            print("maq: OBRIGADO!")
            open = False

            
    if not open:
        break
