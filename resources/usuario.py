# -*- coding: utf-8 -*-
#tudo que for sobre recursos de hotel eu colono nesse arquivo
from flask_restful import Resource, reqparse
from models.usuario import UserModel
from sql_alchemy import banco
from flask_jwt_extended import create_access_token, jwt_required, get_jwt #create_access_token: usado em autenticao | jwt_required: para requerer usuario logado 
from werkzeug.security import safe_str_cmp #usado em autenticao
from blacklist import BLACKLIST


#instanciando - para pegar os dados do corpo da
#requisao enviado pelo usuario
#sao variaveis globais
argumentos = reqparse.RequestParser()
argumentos.add_argument('login', type=str, required=True, help="The field 'login' cannot be left blank ") 
argumentos.add_argument('senha', type=str, required=True, help="The field 'senha' cannot be left blank") 

#esse recurso eh sobre UM hotel
class User(Resource):
# -->  /usuarios/{user_id}

    #obter um usuario
    def get(self, user_id):

        user = UserModel.find_user(user_id)

        if user is not None: # igual a: if hotel
            return user.json()
        return {'message':'User not found'}, 404 #not found

    @jwt_required() #necessario estar logado
    #deletar usuario
    def delete(self, user_id):
        
        user = UserModel.find_user(user_id)
        if user:
            try:
                user.delete_user()
            except:
                return {'message': 'An error ocurred trying to delete hotel.'}, 500 #internal server error
            return {'message': 'User deleted'}, 200 #sucesso

        return {'message': 'User not found.'}, 404

#cadastra usuario
class UserRegister(Resource):
    # --> /cadastro
    def post(self):
        
        dados = argumentos.parse_args() 
        #por fim ele guarda os 'dados' que em uma variavel dados (que eh uma lista)

        if UserModel.find_by_login(dados['login']):
            return {'message': "The login '{}' already exist. ".format(dados['login'])}

        #caso nao exista usuario com o login, entao crie novo usuario
        user = UserModel(**dados)
        user.save_user()
        return {'message': 'User created successfully!'}, 201 #Created

#A cada recurso um classe, pois dentro das classes temos os metodos
#http que podem se repetir, ex: login de user usa post e cadastrar user tbm usa post

class UserLogin(Resource):
    def post(cls):
        dados = argumentos.parse_args()

        user = UserModel.find_by_login(dados['login'])

#para realizar comparação de senha usamos o funcao safe_str_cmp() 
#Pois eh uma fora mais segura devido a senha ter caracteres especiais. 
# Mais seguro do que == 
        # se usuario for encontrado manda token gerado com base na id_usuario
        #JWT: bibliotca que vamos usar para fazer autenticao de usuario (login e logout)
        #pip install flask-jwt-extended
        if user and safe_str_cmp(user.senha, dados ['senha']): #(compara senha do usuario no encontrado no bd com a senha do argumento passado )
            token_de_acesso = create_access_token(identity=user.user_id)
            return {'access_token': token_de_acesso},200
        return {'message': 'The username or password is incorrect.'}, 401 #Unathorize

class UserLogout(Resource):
    
    @jwt_required()
    def post(self):
        jwt_id = get_jwt()['jti']# sgnifica: JWT, Token, Identifier - pega o token da sessao do usuario
        #apos pegar o toque da sessao inserimos ele em um arquivo de blacklist local
        
        BLACKLIST.add(jwt_id)
        return {'message':'Logged out successfully!.'}, 200

