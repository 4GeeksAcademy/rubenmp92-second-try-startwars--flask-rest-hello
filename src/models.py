from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  

class User(db.Model):
    __tablename__="user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        # 1º manera return '<User %r>' % self.email
        #2º manera sirve para cuando imprimas users en el app.py
        return f"Usuario con id {self.id} y email: {self.email}"

    def serialize(self): #función que permite convertir los modelos que tiene sql alchemy a objetos y traer la info
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active
            # do not serialize the password, its a security breach
        }
    
class Planet(db.Model):
    __tablename__="planet"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    population = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return "Planeta {} de nombre {}".format(self.id, self.name)
        # return f"Planeta con id {self.id} y nombre {self.nombre}"  ---este es el otro formato posible 
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population
        }


class Character(db.Model):
    __tablename__="character"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    height = db.Column(db.Integer, nullable=False)
    mass = db.Column(db.Integer)

    def __repr__(self):
         return "Personaje {} de nombre {} con altura de {} y peso de {}".format(self.id, self.name, self.height, self.mass)

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "mass": self.mass
        }


class Favorite_Planets(db.Model):
    __tablename___="favorite_planets"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) #el que va en la llave foranea va con el nombre de tablename en minuscula
    user_id_relationship = db.relationship(User)  #esto le sirve a SQL alq para crear las relaciones.Aqui se pone el de la clase con mayuscula
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'), nullable=False)
    planet_id_relationship = db.relationship(Planet) 


    def __repr__(self): #función que sirve para: cuando hagamos un print de un usuario o de un fav dentro de python lo que pongamos en repr es lo que va a salir
        return "Al usuario {} le gusta el planeta {}".format(self.user_id, self.planet_id)
 
    def serialize(self): #el tipo de dato cuando hacemos un query va a ser un dato tipo model y no se puede enviar 
                        #este tipo de dato al frontend por eso hay que convertirlo a un diccionario/objetos y ese diccionario 
                        #si lo podemos convertir en JSON para enviarlo hacia el fronted. Ya que con las APIS siempre nos comunicamos con tipos JSON
        return{
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id
        }

class Favorite_Characters(db.Model):
    __tablename__="favorite_character"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_id_relationship = db.relationship(User)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=False)
    character_id_relationship = db.relationship(Character)

    def __repr__(self):
        return "Al usuario {} le gusta el personaje {}".format(self.user_id, self.character_id)
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id
        }