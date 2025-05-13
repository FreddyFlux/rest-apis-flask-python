from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt

from db import db
from models import UserModel
from schemas import UserSchema
from models.blocklist import BlocklistModel

blp = Blueprint("Users", "users", description="Operations on users")

# REGISTER A USER
@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(400, message="A user with that username already exists.")
        
        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"])
        )
        db.session.add(user)
        db.session.commit()
        access_token = create_access_token(identity=user.id)
        return {"message": "User created successfully. You are now logged in.", "access_token": access_token}, 201
    
# AUTHENTICATE A USER
@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.username == user_data["username"]).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200
        
        abort(401, message="Invalid credentials.")

# CREATE A REFRESH TOKEN
@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity() # Get the identity of the current user
        if not current_user:
            abort(401, message="Invalid credentials.")
        jti = get_jwt()["jti"]
        blocklist_entry = BlocklistModel(jti=jti)
        db.session.add(blocklist_entry)
        db.session.commit()
        print(jti)
        new_token = create_access_token(identity=current_user, fresh=False) 
        return {"access_token": new_token}, 200

# LOGOUT A USER
@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        blocklist_entry = BlocklistModel(jti=jti)
        db.session.add(blocklist_entry)
        db.session.commit()
        return {"message": "Successfully logged out."}
        

# GET A USER BY ID
@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

# DELETE A USER BY ID
@blp.response(202, description="Deletes a user by id.", example={"message": "User deleted."})
@blp.alt_response(404, description="User not found.")
def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}, 200

# SHOW ALL BLOCKED TOKENS
@blp.route("/blocklist")
class Blocklist(MethodView):
    def get(self):
        blocklist = BlocklistModel.query.all()
        return {"blocklist": [block.jti for block in blocklist]}


