#tudo que for sobre recursos de hotel eu colono nesse arquivo
from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from flask_jwt_extended import jwt_required # ele vai auxiliar que somente usuario logado acesse certos recursos/operacoes


#classe herdando os metodos de Resource
# recurso hoteis tem dentro metodo get
#recurso hotel que retorna LISTA-COLECAO de hoteis
class Hoteis(Resource):
    def get(self):
        #lembre o json: {chave:valor}
        #nos retornamos esse dicionario mas resource converte automaticamente em em json
        #isso seria um SELECT * FROM hoteis
        hoteis_retornados = HotelModel.query.all()
        return {'hoteis': [hoteis.json() for hoteis in hoteis_retornados] }, #200  #list comprehesion

#recurso hotel com metodos CRUD
#esse recurso eh sobre UM hotel
class Hotel(Resource):
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