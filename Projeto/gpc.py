import makecode
from lexer import lexer, tokens
import ply.yacc as yacc
import webauto
from parser import parser
from semantics import SemanticAnalyzer
import testes

result = parser.parse(testes.exemplo5, lexer=lexer)

if parser.success:
    print(result)
    analyzer = SemanticAnalyzer()

    # Verifica se a semântica aprova
    if analyzer.analyze(result):
        print("\nAnálise Semântica: Passou.")
        print("="*40)
       # analyzer.print_symbol_table();

        codigo_final = makecode.gerar_codigo(result)

        # Gravar em ficheiro
        with open("programa_final.txt", "w") as f:
            f.write(codigo_final)
            webauto.abrir_e_colar(codigo_final)

    else:
        print("\nFalha na Semântica. Código não gerado.")
        analyzer.print_errors()
        analyzer.print_symbol_table()
else:
    print("Erro no Parsing.")
