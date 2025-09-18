# TPC1

Neste TPC, foi-nos proposto criar uma expressão regular que representasse números binários que **não contivessem a subcadeia "011" em nenhuma posição**.  

Com base nos conhecimentos adquiridos nas disciplinas lecionadas, mais especificamente em *Autómatos e Linguagens Formais*, comecei por construir o [autómato](automato_rotation.pdf).  

Seguidamente, tentei convertê-lo para a linguagem formal da mesma forma que fazíamos na disciplina anterior, obtendo a seguinte expressão regular:  
***`1*0*(0|1)(0*|01)*`***  

Após a realização de alguns [testes com regex](testes_regex.png), foi possível concluir que esta expressão engloba todas as cadeias binárias que **não contêm a subcadeia "011"**.
