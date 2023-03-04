from flask import Blueprint , request , make_response , current_app
import bson.json_util as json_util
from database import  users_collections
import json
from passlib.hash import pbkdf2_sha256
import bcrypt
import jwt
import datetime

auth_bp = Blueprint("auth_bp", __name__)
auth_bp.secret_key = 'my_secret_key'



@auth_bp.post("/register")
def register():
    body = json.loads(request.data)
    secret_key = current_app.config['SECRET_KEY']
    users = {
        "username": body["username"],
        "password":body["password"],        
    }
    
    if not users["username"] and users["password"]:
       return make_response({"message":"Please enter above details"} , 401)
        
    password = body['password']
    hashed_pwd = pbkdf2_sha256.hash(password)
    body['password'] = hashed_pwd
    
    registered_user = users_collections.find_one(
        {"username":body["username"]}
    )
    
    if registered_user:
       return make_response({"message":"This username is taken please provide a unique username"},400)
        
    savedUsers = users_collections.insert_one(users).inserted_id
    jsonVersin = json_util.dumps(savedUsers)
    return make_response({ "message":"User has been registered succesfully" , "User":jsonVersin} , 200)

@auth_bp.post("/login")
def login():
    body = json.loads(request.data)
    user = {
        "username": body["username"],
        "password": body["password"]
    }
    existing_user = users_collections.find_one({"username": user["username"]})
    if not existing_user:
        return make_response({"message": "Invalid username"}, 401)
    
    correct_password = users_collections.find_one({"password": user["password"]})
    if not correct_password:
        return make_response({'message':'Invalid Password'} , 400)
    
    
    bytes = user["password"].encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw( bytes , salt)
    login_password = user["password"]
    login_bytes = login_password.encode('utf-8')
    check_hash_password = bcrypt.checkpw(login_bytes , hash)
    
    json_serialize = json.loads(json_util.dumps(existing_user["_id"]))
    
    if check_hash_password == True:
        token = jwt.encode({"_id": json_serialize, "exp": datetime.datetime.utcnow(
        ) + datetime.timedelta(minutes=1) } , 'secret_key')
        return make_response({'token':token},200)
    
    if check_hash_password == False:
        return make_response({'message':"Could not verify"} , 400)
    




