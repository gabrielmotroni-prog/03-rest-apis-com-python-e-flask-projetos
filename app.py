# -*- coding: utf-8 -*-
#aqui eo o arquiv/pagina principal
from blacklist import BLACKLIST
from flask import Flask, jsonify# no pacote flask import a classe Flask
from flask_restful import Api
from resources.hotel import Hoteis, Hotel 
from resources.usuario import User, UserLogin, UserLogout, UserRegister, UserLogin
from flask_jwt_extended import JWTManager # gerenciar toda parte de autenticao para nos
from blacklist import BLACKLIST

#importando do pacote/modulo resource o arquivo hotel o qual importamos a Classe/biblioteca/o recurso Hoteis

# no pacote flask import a classe Flask
#__init__.py dentro de uma pasta significa  que aquela pasta eh um repositorio/ um modulo
#resource == recurso
# recursos sao disponibilizados via endpoints
#flask restful e suas classes vamos nos ajudar

#dentro da pasta resources(recursos) vamos colocar todos recursos que nossa
#api vai ter

#A chave secreta é necessária para manter as sessões do lado do cliente seguras. 
# Você pode gerar alguma chave aleatória como abaixo:
#import os
#os.urandom(24)
#'\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
#SECRET_KEY = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
#garante que a aplicao vai ter criptografia

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///banco.db' #aqui defimos o caminho e nome do nosso banco / 
#basta alterar a linha acima para alterar o banco de dados. O resto o sqlalchemy faz pra nos
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #tira o aviso que fica sobrecarregando o app
app.config['JWT_SECRET_KEY'] = "b'\xdb{WN\xa3v\x9e\xc7\xe5fW\xbe_\x8e\xdf\x8d\xc1\xfc\xbc^\xd9G\xe5\xda'"
app.config['JWT_BLACKLIST_ENABLE'] = True #ativa lista negra jwt possibilidando invalidar algum id
api = Api(app)
jwt = JWTManager(app)#gerenciar toda parte de autenticao para nos

#decorador signifca: antes da primeira requisao
@app.before_first_request
def cria_banco():
    banco.create_all() # variavel sqlalchemy que importamos - verifia se existe o banco e cria as tabelas

#funcao verifica se um token esta ou nao na blacklist
@jwt.token_in_blocklist_loader
def verifica_blacklist(self,token):
    return token['jti'] in BLACKLIST

# acesso revogado: pega se alguem tenta acessar com token invalidado
#se estiver na blacklist oq fazer
#jsonify transform dicionario em json
@jwt.revoked_token_loader
def token_de_acesso_invalidado(jwt_header, jwt_payload):
    return jsonify({'message':'You have been logged out.'}), 401 #Unathorized

#adicionado o nosso recurso na api informando como 
# queremos chama-lo  - vinculando recurso com endpoint
#vinculando recurso com endpoint (criando tbm o endpoint)
api.add_resource(Hoteis, '/hoteis') #recurso get lista de hoteis
api.add_resource(Hotel, '/hoteis/<string:hotel_id>') #recurso hotel CRUD
api.add_resource(User, '/usuarios/<int:user_id>') #recurso hotel CRUD
api.add_resource(UserRegister, '/cadastro')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')

#-- para heroku
import os
# ----- 

if __name__ == '__main__':
    # restringe a fazer a uninica chamada e iniciaizaxao aqui, so vai ser execudado pelo app.py
    # evita importacoes de todos arquivos, so precisa importar daqui do arquivo principal
    from sql_alchemy import banco
    banco.init_app(app)
    
    port = int(os.environ.get("PORT", 5000))
    #app.run(debug=True, host='0.0.0.0')
    app.run(threaded=True, host='0.0.0.0', port=port) #threaded - muitas sessoes ao mesmo tempo

#post : precisamos receber todos os dados via json