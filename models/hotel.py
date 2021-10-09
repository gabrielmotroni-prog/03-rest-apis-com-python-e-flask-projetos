#classe modelo
from sql_alchemy import banco

class HotelModel(banco.Model):
    #mapeamento para o sqlAlchemy que essa classe eh  tabela no banco de dados
    __tablename__ = 'hoteis'
    hotel_id = banco.Column(banco.String, primary_key=True)
    nome = banco.Column(banco.String(80))
    estrelas = banco.Column(banco.Float(precision=1)) #precision eh quantos numeros apos a virgula
    diaria = banco.Column(banco.Float(precision=2))
    cidade = banco.Column(banco.String(40))

    #construtor
    def __init__(self, hotel_id, nome, estrelas, diaria, cidade):
        self.hotel_id = hotel_id
        self.nome = nome
        self.estrelas = estrelas
        self.diaria = diaria
        self.cidade = cidade

    #classe dentro da classe modelo que transforma o objeto criado pelo onstrutor em
    #em um dicionario (que eh convertido para json automaticamente)
    def json (self):
        return {
            'hotel_id': self.hotel_id,
            'nome': self.nome,
            'estrelas': self.estrelas,
            'diaria': self.diaria,
            'cidade': self.cidade
        }

    @classmethod
    def find_hotel(cls, hotel_id): #cls eh como self, porem, ele representa como a propria HoteModel
        hotel = cls.query.filter_by(hotel_id=hotel_id).first() #cls eh hotelModel. / isso eh: SELECT * FROM hoteis WHERE hotel_id = $hotel_id limit=1
        if hotel: # igual a:se existe hotel 
            return hotel
        return None
        #para utilizar o metodo filter_by demandouo @classmethod - metodo da clase

    def save_hotel(self): # ele eh auto inteligente, ja pega o objeto pelo self
        banco.session.add(self)
        banco.session.commit()
   
    def update_hotel(self, nome, estrelas, diaria, cidade): #**dados passa os dados ele desembrula
        self.nome = nome 
        self.estrelas = estrelas 
        self.diaria = diaria  
        self.cidade = cidade 
        #perceba que o metodo eh bem restrito a somente atualizar os atributos sem salvvar nem nada
        # a inteligecia de pegar atualizar os dados com base no self ele sabe examente qual alterar

    def delete_hotel(self):
        banco.session.delete(self)
        banco.session.commit()
    #mt parecido com save_hotel
