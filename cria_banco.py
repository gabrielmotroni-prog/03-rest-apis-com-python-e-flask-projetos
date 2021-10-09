#usamos esse arquivo so para aprender criar uma conexao na mao criando banco de dados sqlite3

import sqlite3 # nao eh necessario pip install pois ja esta dentro doo python

connection = sqlite3.connect('banco.db') #variavel de conexao, a qual informamos tbm o nome do banco de dados, no caso, `banco.db`
cursor = connection.cursor() #variavel cursos que `seleciona` as coisas no banco de dados

# \ a contra barra eh formade falar que o conteudo eh continuacao da lnha de cima,
#vaiavel com scipt da criacao da tabela
cria_tabela = "CREATE TABLE IF NOT EXISTS hoteis (hotel_id text PRIMARY KEY,\
    nome text, estrelas real, diaria real, cidade text)"

#vaiavel com scipt da criacao da hotel 
cria_hotel = "INSERT INTO hoteis VALUES ('alpha', 'Alpha Hotel', 4.3, 345.30, 'Rio de Janeiro' )"

#criando a tabela
cursor.execute(cria_tabela)
#insere valor hotel na tabela
cursor.execute(cria_hotel)

#efetua e fecha conexao
connection.commit()
connection.close()


