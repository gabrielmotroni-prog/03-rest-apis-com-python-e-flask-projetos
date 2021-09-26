#tudo que for sobre recursos de hotel eu colono nesse arquivo
from sqlite3.dbapi2 import connect
from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from flask_jwt_extended import jwt_required # ele vai auxiliar que somente usuario logado acesse certos recursos/operacoes
import sqlite3 # vamos usar para consultas mais robustas

#normaliza a falta de parametros passados pelo usuario (ou com cidade ou sem cidade);
#os valores default sao os parametros para entrar em acao
#caso dados nao sejam passados
def normalize_path_params(cidade=None,
                         estrelas_min=0,
                         estrelas_max=5,
                         diaria_min=0,
                         diaria_max=10000,
                         limit=50,
                         offset=0, **dados):
    
    #normaliza duas situacoes:
    # se o usuario passou cidade
    if cidade:
        return{
            'estrelas_min': estrelas_min,
            'estrelas_max': estrelas_max,
            'diaria_min':diaria_min,
            'diaria_max':diaria_max,
            'cidade':cidade,
            'limit':limit,
            'offset':offset
        }
    return{ #se o usuario NAO passou cidade
        'estrelas_min': estrelas_min,
        'estrelas_max': estrelas_max,
        'diaria_min':diaria_min,
        'diaria_max':diaria_max,
        'limit':limit,
        'offset':offset
    }


# path /hoteis?cidade=Rio de Janeiro&estrelas_min=4&diaria_max=400
#parametros do path, que ficam na url
#nosso construtorpara o path_params - parametros da path
path_params = reqparse.RequestParser()
#add argumentos
path_params.add_argument('cidade', type=str)
path_params.add_argument('estrelas_min', type = float)
path_params.add_argument('estrelas_max',type=float)
path_params.add_argument('diaria_min',type=float)
path_params.add_argument('diaria_max',type=float)
path_params.add_argument('limit',type=float) #qtd de itens q queremos exixibor por pagina
path_params.add_argument('offset',type=float) #qtd de elemento q queremos pular

#classe herdando os metodos de Resource
# recurso hoteis tem dentro metodo get
#recurso hotel que retorna LISTA-COLECAO de hoteis
class Hoteis(Resource):
    def get(self):
        #lembre o json: {chave:valor}

        #abrindo conexao com banco
        #usando forma sql, pois sqlalchemy nao da conta dos muitos parametros que passaremos
        connection = sqlite3.connect('banco.db')
        cursor = connection.cursor()
    
        #pegando  os dados passados ao path (url) e colocando no objeto dados
        dados = path_params.parse_args()

        #pegando somente os dados validos ( que nao tenham nulo, pois com nulo n da pra filtrar)
        #usando compreensao de lista
        #explicando o compressando de lista usada:
        #1-dados validados receba o valor de cada  -> chave:dados[chave]
        #2-para cada chave em dados
        #3- se o valor nao for nulo
        dados_validos = {chave:dados[chave] for chave in dados if dados[chave] is not None }
        print(dados)
        #parametros usando o a funcao normalize dados para tratar parametros de filtro: com cidade ou sem cidade
        parametros = normalize_path_params(**dados_validos)

        # trata filtro SEM cidade
        #.get('') eh a forma melhorada de parametros['cidade'] -> alternativa para pegar os dados do parametro para  codigo n quebrar com nulo
        if not parametros.get('cidade'):
            consulta = "SELECT * FROM hoteis \
            WHERE (estrelas >= ? and estrelas <= ? ) \
            and (diaria >= ? and diaria <= ?) \
            LIMIT ? OFFSET ?"
            #queremos usar so os valores que serao convertidos em tuplas para serem usados com cursor
            tupla = tuple([parametros[chave] for chave in parametros])
            #consulta feita pelo sql + tupla
            
            resultado = cursor.execute(consulta, tupla)
        else: # trata filtro COM cidade (os parametros precisam estar na msm ordem do metodo normalize)
            consulta = "SELECT * FROM hoteis \
            WHERE (estrelas >= ? and estrelas <= ? ) \
            and (diaria >= ? and diaria <= ?) \
            and cidade = ? LIMIT ? OFFSET ?"
            #queremos usar so os valores que serao convertidos em tuplas para serem usados com cursor
            tupla = tuple([parametros[chave] for chave in parametros])
            #consulta feita pelo: sql + tupla
            resultado = cursor.execute(consulta, tupla)

        hoteis = []
        for linha in resultado:
            #com for, acesso as colunas da linha de registro retorna;
            #monto um objeto a cada volta do for e faco append em hoteis
            #cuidado! siga a ordem do contrutoor da classe
            hoteis.append(
                {
                'hotel_id': linha[0],
                'nome': linha[1],
                'estrelas': linha[2],
                'diaria': linha[3],
                'cidade': linha[4]
                }
            )
        #o restAPi retorna o dicionario automaticamente em json
        return {'hoteis': hoteis }, #200  

#recurso hotel com metodos CRUD
#esse recurso eh sobre UM hotel
class Hotel(Resource):

    # se a pessoa nao passa UM dos argumentos em path_retornados, ele retorna tudo null


    #post : precisamos receber todos os dados via json pois post eh um insercao
    #para no nosso codigo coneguir receber os dados para fzr o post(criacao) nosx
    #usamos bibilioca reqparte: ele vai receber todos os elementos da requisicao
    #construtor
    argumentos = reqparse.RequestParser()# instanciando 
    argumentos.add_argument('nome', type=str, required=True, help="The field 'nome' cannot be left blank ") #capturando os argumetos que a pessoa enviou (somente acesita os discriminados por mim)
    argumentos.add_argument('estrelas', type=float, required=True, help="The field 'estrelas' cannot be left blank") 
    argumentos.add_argument('diaria')
    argumentos.add_argument('cidade')
    # Refinando os dados, eu consigo obrigar o tipo, se ele eh requerido e uma mensagem de ajuda
    #type=str, required=True, help=" mensagem"

    #dessa forma todos os dados serao {chave:valor}

    # alerta: o codigo se repete varias vezes? crie uma funcao
        
    def get(self, hotel_id):
        #hotel = Hotel.find_hotel(hotel_id)
        hotel = HotelModel.find_hotel(hotel_id)

        if hotel is not None: # igual a: if hotel
            return hotel.json()
        return {'message':'Hotel not found'}, 404 #not found

    # ele vai auxiliar que somente usuario logado acesse certos recursos/operacoes
    #ou seja, vai ter que passar o token de acesso
    @jwt_required()
    def post(self, hotel_id):

        #verifica se id ja existe, caso sim, interrompe. O metodo find criamos na model hotel
        if HotelModel.find_hotel(hotel_id):
            return {"message":"Hotel id '{}' already exists.".format(hotel_id)}, 400 #bad request

        #o arguments (o contrutor) esta na classe pq eh utilizado muitas vezes
        # nesse momento abaixo recebe os atribudos passados
        dados = Hotel.argumentos.parse_args()#criar um construtor o qual eu passo todos argumentos

        #instanciando hotel
        #hote_id esta sendo passado via url
        hotel = HotelModel(hotel_id, **dados) #primeiro argumento(hotel_id), dps os kwargs
        
        #tratamento de erros: quando mexemos com banco existe possiblidade de falhar. entao, com o python
        #usamos try e except para nosso codigo nao quebrar
        #os eventos de salvar, atualizar e deletar sao criticos pq mexem com obanco
        try:
            #metodo save tbm criado no model hotel
            hotel.save_hotel() #save pq para o sqlachemy a ideia eh salvar nao criar(so cria a id)
        except:
            return {'message': 'An internal error ocurrred trying to save hotel.'}, 500 #internal server error
            #retornamos esse erro caso de algum prblema com banco de dados ou algo assim
        return hotel.json(), 200 #creat #json metodo no model criado por nos

        

        

    @jwt_required()
    def put (self, hotel_id):

        #captura a requisao e deixa monta ela para atulizar ou criar
        dados = Hotel.argumentos.parse_args()  
        hotel_encontrado = HotelModel.find_hotel(hotel_id) #busca o hotel com id_hotel passada

        if hotel_encontrado:
            #se hotel existe alterar se nao existir ele vai criar
            hotel_encontrado.update_hotel(**dados) #passa os parametros 
            try: #tenta salvar
                #metodo save tbm criado no model hotel
                hotel_encontrado.save_hotel() #salva no banco
            except: #se nao der certo:
                return {'message': 'An internal error ocurrred trying to save hotel.'}, 500 #internal server error

            return hotel_encontrado.json(), 200 #atualizado

        #caso nao entrado entao cria um objeto com os dados e salva
        hotel = HotelModel(hotel_id,**dados)
        hotel.save_hotel()

        return hotel.json(),201 #criado - created

    @jwt_required()
    def delete(self, hotel_id):
        
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            try:
                hotel.delete_hotel()
            except:
                return {'message': 'An error ocurred trying to delete hotel.'}, 500 #internal server error
            return {'message': 'Hotel deleted'}, 200 #sucesso

        return {'message': 'Hotel not found.'}, 404

#codigo old - sessao api local sem banco
''' 
    global hoteis # para o python diferencial a variavevl a baixo da lista ja existente chamadas `hoteis`
    #ele forma uma lista sem o hotel_id passado 

        hotel_encontrado = Hotel.find_hotel(hotel_id)
        if hotel_encontrado: #tratamento
            hoteis = [x_hotel for x_hotel in hoteis if x_hotel['hotel_id']!= hotel_id] # conceito de list comprehension
                    #hoteis recebe x_hotel - para cada x_hotel in hoteis - em que id_hotel seja diferente do parametro id_hotel
            return {'message': 'Hotel deleted.'}
        else:
            return {'message': 'Hotel not found.'}, 404
'''