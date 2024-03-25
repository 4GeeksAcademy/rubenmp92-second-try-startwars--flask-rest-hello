"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Favorite_Planets, Character, Favorite_Characters
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def handle_hello():

#query para traer todos los usuarios
#SELECT * FROM user: es lo mismo que lo de abajo
    users = User.query.all()
    # for user in users: #para saber que tipo de datos son "type(dato)"
    #     print(type(user))
    #1ª forma de hacerlo con el lambda y map: users_serialized_map = list(map(lambda x: x.serialize(), users))
    #2ª forma de hacerlo con el array vacio y append 
    users_serialized = []
    for user in users:  
        #APPEND Método para agregar elementos a un arreglo en pyhton
        users_serialized.append(user.serialize()) #recorro casa uno de los elementos que están guardados en users con el ciclo for y los serializo y se lo empujo a user_serialized
    # print(users) 
    # print(users_serialized) 
   
    #     print(user.serialize()) #para que te devuelva la info en objetos en vez de modelo
    # print(users) #para probar el query en la terminal


    response_body = { #mensaje que aparece en postman
        "msg": "ok ",
        "result": users_serialized #devolvemos el array donde serializamos los elementos
    }

    return jsonify(response_body), 200

@app.route('/planets', methods = ['GET'])  #metodo para traer los planetas
def get_planets():
    planets = Planet.query.all()
    # print(planets)
    planets_serialized = []
    for xxx in planets:
        planets_serialized.append(xxx.serialize())
    return jsonify({"msg": "OK", "results": planets_serialized}),200

@app.route('/character', methods=['GET'])
def get_character():
    characters = Character.query.all()
    characters_serialized = []
    for yyy in characters:
        characters_serialized.append(yyy.serialize())
    print(characters)
    return jsonify({"msg": "OK", "results": characters_serialized}),200


@app.route('/planet/<int:id>', methods = ['GET'])
def get_single_planet(id): 
    planet = Planet.query.get(id) #el anterior me traia un arreglo y por eso tenía que recorrerlo con el for y serializarlo, este me trae solo 1 id y entonces podemos devolverlo serializado
    print(planet)
    return jsonify({"msg": "OK", "planet": planet.serialize()}), 200


@app.route('/character/<int:id>', methods = ['GET'])
def get_single_character(id):
    character = Character.query.get(id)
    print(character)
    return jsonify({"msg": "OK", "character": character.serialize()}),200


# POST_____________________________________________________________________________________________________________________________________

@app.route('/planet', methods = ['POST'])
def add_planet():  
    body = request.get_json(silent=True)  #para este tipo de post la info se suele recibir en el BODY
    if body is None: #si body está vacio
        return jsonify("Debes enviar infomarción en el body"), 400
    if 'name' not in body:
        return jsonify("El campo name es obligatorio"), 400
    new_planet = Planet()   #instanciamos planeta
    new_planet.name = body['name']      # aqui estamos haciendo que en el nuevo planeta en su nombre que le voy a guardar, pues un string que recibe en el body en la posición name
    new_planet.population = body['population']
    db.session.add(new_planet)
    db.session.commit()
    return jsonify("planeta agregado satisfactoriamente"), 200


@app.route('/user/favorites', methods=['GET'])    
#endpoint que me devuelva todos los planetas, personajes, startships que le han gustado a un usuario
#Me tienen que enviar el user.id dentro del body   #body -> user_id para saber que usuario voy a traer yo sus favoritos
def favorites_user():
    body = request.get_json(silent=True)     #como agarro el body que me está enviando alguien
    if body is None:
        return jsonify({"msg": "Debes enviar informacion en el body"}), 400
    if "user_id" not in body:   #si yo quiero que me envien el id del usuario dentro del body como puedo revisar si si me la enviaron
        return jsonify({"msg": "Debes enviar el campo user_id"}), 400
    user = User.query.get(body['user_id'])  #tengo que coger body en la posicion user id para traer la info del usuario. Siempre que se vaya a traer info del body traer body y la posción
    if user is None:
        return jsonify({"msg": "El usuario con el id: {} no existe".format(body['user_id'])}), 404 #not found  
    favorite_planets = db.session.query(Favorite_Planets, Planet).join(Planet).filter(Favorite_Planets.user_id == body['user_id']).all()
    print(favorite_planets)
    favorite_planets_serialized = []
    for favorite_item, planet_item in favorite_planets: #voy a coger y voy a recorrer todo el arreglo por eso utilizo un for. Los recorre en pares
        #voy a devolverle al usuario el id en favrite planets y la informacion del planeta (el planeta serializado)
        favorite_planets_serialized.append({'favorite_planet_id': favorite_item.id, 'planet': planet_item.serialize()})
    return jsonify({"msg": "OK", "results": favorite_planets_serialized})
    

@app.route('/favorite/planet/<int:planet_id>', methods = ['POST'])
def add_new_favorite_planet(planet_id):
    body = request.get_json(silent=True)
    user_id = body['user_id']
    planet = Planet.query.get(planet_id)
    user = User.query.get(user_id) #esto lo hacemos para porque aunque ya nos envian el id lo traemos para estar seguros de que ese usuario exista y manejar el error aqui
    if body is None:
        return jsonify("Tienes que enviar información en el body"), 400
    if user is None:
        return jsonify("El usuario no existe"), 404
    if planet is None:
        return jsonify("El planeta no existe"), 404
    
    favorite_planet = Favorite_Planets.query.filter_by(user_id = user_id, planet_id = planet_id).first()
    if favorite_planet:
        return jsonify({"msg": "El planeta favorito ya estaba"}), 400
    
    add_new_favorite_planet = Favorite_Planets(planet_id = planet_id, user_id = user_id)
    db.session.add(add_new_favorite_planet)
    db.session.commit()
    return jsonify({"msg": "Planeta favorito añadido correctamente"}), 200


# @app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
# def add_new_favorite_planet(planet_id):
#     user_id = request.json.get('user_id')  #lo primero es encontrar que usuario
    
#     #verificar si es usuario y el planeta existen
#     user = User.query.get(user_id)  #comparamos el user_id de request.json con la busqueda query de esta linea si matchea existe el usuario
#     planet = Planet.query.get(planet_id)   #we get the user and the planet from the database

#     if not user:
#         return jsonify({"msg": "User doesnt exist!!!!"}), 400
#     if not planet:
#         return jsonify({"msg": "Planet doesnt exist"}), 400

#     favorite_planet = Favorite_Planets.query.filter_by(user_id = user_id, planet_id = planet_id).first()
#     print(favorite_planet)  #vamos a comprobar si ya existe como favorito, si existe no lo añadimos sino seguimos bajando

#     if favorite_planet:
#         return jsonify({"msg": "El planeta favorito ya estaba"}), 400
    
#     new_favorite_planet = Favorite_Planets()
#     new_favorite_planet.user_id = user_id
#     new_favorite_planet.planet_id = planet_id
#     db.session.add(new_favorite_planet)
#     db.session.commit()
#     return jsonify({"msg": "Planeta favorito agregado"}), 200

    #verifica si ya es favorito(haciendo un query a favorite planets filter por user id y planet id.)
    #si existe dame un jsonify que diga el planeta ya estaba como favorito
    #si no era favorito va a seguir ejecutando el codigo y lo vamos a agreagar con una nueva variable al favorito con el db session add commit.. 


# PARA ENTENDER COMO SERIA CON DOS INT
# @app.route('/<int:user_id>/favorite/planet/<int:planet_id>', methods=['POST'])
# def add_new_favorite_planet(user_id, planet_id):
#     user_id = request.json.get('user_id')  #lo primero es encontrar que usuario

# 1ª FORMA

# @app.route('/favorite/character/<int:character_id>', methods = ['POST'])
# def add_favorite_character(character_id):
#     user_id = request.json.get('user_id')

#     user = User.query.get(user_id)
#     character = Character.query.get(character_id)

#     if user is None:
#         return jsonify({"msg": "Usuario no encontrado"}), 400
#     if character is None:
#         return jsonify({"msg": "Personaje no encontrado"}), 400

#     favorite_character = Favorite_Characters.query.filter_by(user_id = user_id, character_id = character_id).first()
#     print(favorite_character)
    
#     if favorite_character:
#         return jsonify({"msg": "El personaje favorito ya estaba"}), 400
    
#     new_favorite_character = Favorite_Characters()
#     new_favorite_character.user_id = user_id
#     new_favorite_character.character_id = character_id

#     db.session.add(new_favorite_character)
#     db.session.commit()
#     return jsonify({"msg": "Personaje favorito agregado"}), 200

#2ª FORMA

@app.route('/favorite/character/<int:character_id>', methods = ['POST'])
def add_new_favorite_character(character_id):
    body = request.get_json(silent=True)
    user_id = body['user_id']
    character = Character.query.get(character_id)
    user = User.query.get(user_id)

    if body is None:
        return jsonify({"msg": "Tienes que enviar info en el body"}), 400
    if user is None:
        return jsonify({"msg": "El usuario no existe"}), 400
    if character is None:
        return jsonify({"msg": "El personaje no existe"}), 400
    
    favorite_character = Favorite_Characters.query.filter_by(user_id = user_id, character_id = character_id).first()
    if favorite_character:
        return({"msg": "El personaje favorito ya estaba"}), 400
    
    add_new_favorite_character = Favorite_Characters(user_id = user_id, character_id = character_id)
    db.session.add(add_new_favorite_character)
    db.session.commit()

    return jsonify({"msg": "Personaje favorito añadido correctamente"}), 200

# DELETE _______________________________________________________________________________________________________________________________________

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):

    # user_id = request.json.get('user_id') otra versión
    user_id = request.get_json().get('user_id')  #primero necesitamos pedirle de al usuario que usuario id es para borrar el planeta

    favorite = Favorite_Planets.query.filter_by(user_id = user_id, planet_id = planet_id).first()  #the matchea el user_id del request con el user_id de la base de datos. Si matchea te lo borra
    if not favorite:
        return jsonify({"msg": "Planeta favorito no encontrado"}), 400
    
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"msg": "Planeta favorito eliminado"}), 200


@app.route('/favorite/character/<int:character_id>', methods = ['DELETE'])
def delete_favorite_character(character_id):
    user_id = request.json.get('user_id')

    favorite = Favorite_Characters.query.filter_by(user_id = user_id, character_id = character_id).first()
    if favorite is None:
        return jsonify({"msg": "Personaje favorito no encontrado"}), 400
    
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"msg": "Personaje favorito eliminado"}), 200





# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

