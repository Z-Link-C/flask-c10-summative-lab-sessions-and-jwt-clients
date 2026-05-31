
from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Tasks, UserSchema, TaskSchema

class Signup(Resource):
    def post(self):
        d=request.get_json(force=True)
        try:
            u=User(username=d['username'])
            u.password_hash=d['password']
            db.session.add(u)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return{'error':str(e)},422
        session['user_id']=u.id
        return UserSchema().dump(u),201


class CheckSession(Resource):
    def get(self):
        u_id=session.get('user_id')
        if not u_id:
            return {},401
        u=User.query.get(u_id)
        if not u:
            return{'error':'User not found'},404
        u_schem=UserSchema()
        return u_schem.dump(u),200

class Login(Resource):
    def post(self):
        d=request.get_json(force=True)
        u=User.query.filter_by(username=d['username']).first()
        if u and u.authenticate(d['password']):
            session['user_id']=u.id
            u_schem=UserSchema()
            return u_schem.dump(u),200
        return{'error':'Invalid username or password'},401    

class Logout(Resource):
    def delete(self):
        u_id = session.get('user_id')
        if not u_id:
            return {'error': 'Unauthorized'}, 401
        session.pop('user_id',None)
        return{},204
    
class TaskIndex(Resource):
    def get(self):
        u_id = session.get('user_id')
        if not u_id:
            return {'error': 'Unauthorized'}, 401
        p=request.args.get('page',1,type=int)
        per_p=request.args.get('per_page',10,type=int)
        pgn=Tasks.query.filter_by(user_id=u_id).paginate(
            page=p,per_page=per_p,error_out=False
        )
        return{
            'tasks':TaskSchema(many=True).dump(pgn.items),
            'total':pgn.total,
            'pages':pgn.pages,
            'page':pgn.page,
            'has_next':pgn.has_next,
            'has_prev':pgn.has_prev,
        },200
    def post(self):
        u_id = session.get('user_id')
        if not u_id:
            return {'error': 'Unauthorized'}, 401
        d=request.get_json(force=True)
        try:
            t=Tasks(
                title=d['title'],
                details=d.get('details'),
                due_date=d.get('due_date'),
                user_id=u_id
            )
            db.session.add(t)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return{'error':str(e)},422
        return TaskSchema().dump(t),201
    
class TaskDetail(Resource):
    def get(self, id):
        u_id = session.get('user_id')
        if not u_id:
            return {'error': 'Unauthorized'}, 401
        t = Tasks.query.filter_by(id=id, user_id=u_id).first()
        if not t:
            return {'error': 'Task not found'}, 404
        return TaskSchema().dump(t), 200
    
    def patch(self, id):
        u_id = session.get('user_id')
        if not u_id:
            return {'error': 'Unauthorized'}, 401
        t = Tasks.query.filter_by(id=id, user_id=u_id).first()
        if not t:
            return {'error': 'Task not found'}, 404
        d = request.get_json(force=True)
        for field in ['title', 'details', 'completed', 'due_date']:
            if field in d:
                setattr(t, field, d[field])
        db.session.commit()
        return TaskSchema().dump(t), 200
 
    def delete(self, id):
        u_id = session.get('user_id')
        if not u_id:
            return {'error': 'Unauthorized'}, 401
        t = Tasks.query.filter_by(id=id, user_id=u_id).first()
        if not t:
            return {'error': 'Task not found'}, 404
        db.session.delete(t)
        db.session.commit()
        return {}, 204
        
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(TaskIndex, '/tasks', endpoint='tasks')
api.add_resource(TaskDetail, '/tasks/<int:id>', endpoint='task_detail')

if __name__ == '__main__':
    app.run(port=5555, debug=True)