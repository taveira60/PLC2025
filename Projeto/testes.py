
exemplo1 = ''' 
program HelloWorld;
begin
    writeln('Ola, Mundo!');
end.
'''

exemplo2 = ''' 
program Fatorial;
var
    n, i, fat: integer;
begin
    writeln('Introduza um número inteiro positivo:');
    readln(n);
    fat := 1;
    for i := 1 to n do
    fat := fat * i;
    writeln('Fatorial de ', n, ': ', fat);
end.
'''

exemplo3 = '''
program NumeroPrimo;
var
    num, i: integer;
    primo: boolean;
begin
    writeln('Introduza um número inteiro positivo:');
    readln(num);
    primo := true;
    i := 2;
    while (i <= (num div 2)) and primo do
    begin
    if (num mod i) = 0 then
        primo := false;
        i := i + 1;
    end;
    if primo then
    writeln(num, ' é um número primo')
    else
    writeln(num, ' não é um número primo')
end.
'''

exemplo4 = '''
program SomaArray;
var
    numeros: array[1..5] of integer;
    i, soma: integer;
begin
    soma := 0;
    writeln('Introduza 5 números inteiros:');
    for i := 1 to 5 do
    begin
        readln(numeros[i]);
        soma := soma + numeros[i];
    end;
    writeln('A soma dos números é: ', soma);
end.
'''

exemplo5 = '''
program BinarioParaInteiro;
function BinToInt(bin: string): integer;
var
i, valor, potencia: integer;
begin
valor := 0;
potencia := 1;
for i := length(bin) downto 1 do
begin
if bin[i] = '1' then
valor := valor + potencia;
potencia := potencia * 2;
end;
BinToInt := valor;
end;
var
bin: string;
valor: integer;
begin
writeln('Introduza uma string binária:');
readln(bin);
valor := BinToInt(bin);
writeln('O valor inteiro correspondente é: ', valor);
end.
'''

teste_de_ifs = '''
program TestDangling;
var 
    a, b, d: integer;
    c : array[1*2..1*3+2] of integer;
begin
  a := 15;
  b := 0;
  c[3] := 1;
  d := 2;
  if a > 0 then
  begin
      if b > 0 then
      begin
         b := 1;
         if b < 2 then 
         else 
            writeln('3')
      end
      else
        writeln('2');
  end
  else 
    writeln('1');
  a := 20;      
  b := 2 + 2;
end.
'''

teste_de_arrays = '''
program test_array_range;

var
    arr : array[3..10] of integer;
    i   : integer;

begin
    { inicializar o array }
    arr[3] := 30;
    arr[4] := 40;
    arr[5] := 50;
    arr[6] := 60;
    arr[7] := 70;
    arr[8] := 80;
    arr[9] := 90;
    arr[10] := 100;

    writeln('O valor na posição 9 é: ', arr[9]);
end.

'''

teste_bubblesort= '''
program BubbleSort;
var
    nums: array[1..5] of integer;
    i, j, temp: integer;
begin
    writeln('--- Teste de Arrays e Sort ---');
    writeln('Insira 5 numeros inteiros:');
    

    for i := 1 to 5 do
    begin
        writeln('Numero ', i, ': ');
        readln(nums[i]);
    end;

    
    for i := 1 to 4 do
    begin
        for j := 1 to 5 - i do
        begin
            if nums[j] > nums[j+1] then
            begin
                temp := nums[j];
                nums[j] := nums[j+1];
                nums[j+1] := temp;
            end;
        end;
    end;

    writeln('Ordenado: ');
    for i := 1 to 5 do
    begin
        writeln(nums[i]);
        writeln(' ');
    end;
    writeln('');
end.
'''

teste_erros_de_tipos= '''
program ErroTipo;
var
    x: integer;
    s: string;
begin
    writeln('--- Teste de Erro Semantico (Tipos) ---');
    x := 10;
    s := 'ola';

    x := x + s; 
    writeln(x);
end.
'''

teste_out_of_bounds= '''
program OutOfBounds;
var
    lista: array[1..3] of integer;
begin
    writeln('--- Teste de Erro Runtime (Limites) ---');
    lista[1] := 10;
    lista[2] := 20;
    lista[3] := 30;
    
    writeln('A tentar aceder ao indice 10 num array de 3...');
    lista[10] := 999; 
    
    writeln('ERRO: A VM nao detetou o acesso ilegal!');
end.
'''

teste_downto= '''
program ContagemDecrescente;

var
  i: integer;

begin
  writeln('Contagem de 10 até 1:');

  for i := 10 downto 1 do
    writeln(i);

  writeln('Fim da contagem!');
end.

'''

exemplo_s1 = '''
program Hello;
var 
    word : string;
begin
    word := 'asgdsahjdgsahjdgsahjgdshjagdhjsagdhjsagdhjsagdjshagdhjsagdsahj';
    writeln(word[1]);
end.
'''

exemplo_s = '''
program Hello;
var 
    word : string;
begin
    word := 'asgdsahjdgsahjdgsahjgdshjagdhjsagdhjsagdhjsagdjshagdhjsagdsahjgdsjhagdsajhgdhsajgdsahjdgsahjgdajhgdsjhagdhjsagdsahjdgsahjdgsahjdgsahjdgsahdgajhdsgajhdgsahjdgsajdhasgdhsagdhsajgdsahjdgashdgahjdgahjsgadhasgdjhagdhsajdgsahjdgashdgjsagdhsjadgjashdgjhadgshjadgsajhgdsahjdgsahdgsjadghasjdgajhdgsajhdgashjdgsahjdgajhdgahdsgahdgajshdgajhsdghjadasjhdgajdshajdgsahdgsajhgdahsjgdajshdgsajdgajshdsag';
    writeln(word[300]);
end.
'''

teste_rec = '''
program DowntoRecursivo10;

function ContarDownto(n: integer): integer;
begin
  if n >= 1 then
  begin
    writeln(n);
    ContarDownto := ContarDownto(n - 1);
  end
  else
    ContarDownto := 0;
end;

begin
  ContarDownto(10);
  writeln('Fim!');
end.
'''
