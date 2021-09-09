#classe modelo
from sql_alchemy import banco

class UserModel(banco.Model):
    #mapeamento para o sqlAlchemy que essa classe eh  tabela no banco de dados
    __tablename__ = 'usuarios'
    user_id = banco.Column(banco.Integer, primary_key=True) # banco e sqlalchemy  vai atribuir automaticamente sabendo que eh int e primary key
    login = banco.Column(banco.String(40))
    senha = banco.Column(banco.String(40))


    #construtor
    def __init__(self, login, senha):
        self.login = login
        self.senha = senha
   

    #classe dentro da classe modelo que transforma o objeto criado pelo onstrutor em
    #em um dicionario (que eh convertido para json automaticamente)
    def json (self):
        return {
            'user_id': self.user_id,
            'login': self.login
        }

    @classmethod
    def find_user(cls, user_id): #cls eh como self, porem, ele representa como a propria HoteModel
        user = cls.query.filter_by(user_id=user_id).first() #cls eh hotelModel. / isso eh: SELECT * FROM hoteis WHERE hotel_id = $hotel_id limit=1
        if user: # igual a:se existe hotel 
            return user
        return None
        #para utilizar o metodo filter_by demandou @classmethod - metodo da clase

    def save_user(self): # ele eh auto inteligente, ja pega o objeto pelo self
        banco.session.add(self)
        banco.session.commit()
    ''' #no cursoele nao implementou mas basta criarmos
    def update_user(self, nome, estrelas, diaria, cidade): #**dados passa os dados ele desembrula
        self.nome = nome 
        self.estrelas = estrelas 
        self.diaria = diaria  
        self.cidade = cidade 
        #perceba que o metodo eh bem restrito a somente atualizar os atributos sem salvvar nem nada
        # a inteligecia de pegar atualizar os dados com base no self ele sabe examente qual alterar
    '''
    def delete_user(self):
        banco.session.delete(self)
        banco.session.commit()
    #mt parecido com save_hotel

    @classmethod
    def find_by_login(cls, login): #cls eh como self, porem, ele representa como a propria HoteModel
        user = cls.query.filter_by(login=login).first() #cls eh hotelModel. / isso eh: SELECT * FROM hoteis WHERE hotel_id = $hotel_id limit=1
        if user: # igual a:se existe hotel 
            return user
        return None
