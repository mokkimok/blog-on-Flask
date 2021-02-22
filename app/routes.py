from app import db, api, auth
from app.models import User, Post, Comment
from flask_restful import Resource
from flask import jsonify, request, redirect, url_for, Response


@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return username


class UserAPI(Resource):
    def post(self):
        data = request.get_json()
        password = data.pop('password')
        new_user = User(**data)
        new_user.set_password_hash(password)
        db.session.add(new_user)
        db.session.commit()
        return Response(f"User {new_user.username} created", status=201)


class PostListAPI(Resource):
    def get(self):
        posts = Post.query.all()
        serialized = []
        for post in posts:
            serialized.append(post.serialized())
        return jsonify(serialized)

    @auth.login_required
    def post(self):
        data = request.get_json()
        new_post = Post(**data)
        new_post.author = \
            User.query.filter_by(username=auth.current_user()).first()
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('post', post_id=new_post.id))


class PostAPI(Resource):
    def get(self, post_id):
        post = Post.query.get(post_id)
        if post:
            serialized = post.serialized()
            return jsonify(serialized)
        else:
            return Response('Page not found', status=404)

    @auth.login_required
    def put(self, post_id):
        post = Post.query.get(post_id)
        if post:
            if post.author.username == auth.current_user():
                data = request.get_json()
                data.pop('author_id', None)
                if data:
                    Post.query.filter_by(id=post_id).update(data)
                    db.session.commit()
                return redirect(url_for('post', post_id=post_id))
            else:
                return Response('Unauthorized Access', status=401)
        else:
            return Response('Page not found', status=404)

    @auth.login_required
    def delete(self, post_id):
        post = Post.query.get(post_id)
        if post:
            if post.author.username == auth.current_user():
                db.session.delete(post)
                db.session.commit()
                return 'Post has been successfully deleted.'
            else:
                return Response('Unauthorized Access', status=401)
        else:
            return Response('Page not found', status=404)


class CommentListAPI(Resource):
    def get(self, post_id):
        post = Post.query.get(post_id)
        if post:
            comments = Comment.query.filter_by(post_id=post_id)
            serialized = []
            for comment in comments:
                serialized.append(comment.serialized())
            return jsonify(serialized)
        else:
            return Response('Page not found', status=404)

    @auth.login_required
    def post(self, post_id):
        post = Post.query.get(post_id)
        if post:
            data = request.get_json()
            data['post_id'] = post_id
            new_comment = Comment(**data)
            new_comment.author = \
                User.query.filter_by(username=auth.current_user()).first()
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for('comment', post_id=post_id,
                                    comment_id=new_comment.id))
        else:
            return Response('Page not found', status=404)


class CommentAPI(Resource):
    def get(self, post_id, comment_id):
        comment = Comment.query.get(comment_id)
        if comment and comment.post_id == post_id:
            serialized = comment.serialized()
            return jsonify(serialized)
        else:
            return Response('Page not found', status=404)

    @auth.login_required
    def put(self, post_id, comment_id):
        comment = Comment.query.get(comment_id)
        if comment and comment.post_id == post_id:
            if comment.author.username == auth.current_user():
                data = request.get_json()
                data.pop('author_id', None)
                if data:
                    Comment.query.filter_by(id=comment_id).update(data)
                    db.session.commit()
                return redirect(url_for('comment', post_id=post_id,
                                        comment_id=comment_id))
            else:
                return Response('Unauthorized Access', status=401)
        else:
            return Response('Page not found', status=404)

    @auth.login_required
    def delete(self, post_id, comment_id):
        comment = Comment.query.get(comment_id)
        if comment and comment.post_id == post_id:
            if comment.author.username == auth.current_user():
                db.session.delete(comment)
                db.session.commit()
                return 'Comment has been successfully deleted.'
            else:
                return Response('Unauthorized Access', status=401)
        else:
            return Response('Page not found', status=404)


# Users
api.add_resource(UserAPI, '/api/users/registration', endpoint='registration')

# Posts
api.add_resource(PostListAPI, '/api/posts', endpoint='posts')
api.add_resource(PostAPI, '/api/posts/<int:post_id>', endpoint='post')

# Comments
api.add_resource(CommentListAPI, '/api/posts/<int:post_id>/comments',
                 endpoint='comments')
api.add_resource(CommentAPI,
                 '/api/posts/<int:post_id>/comments/<int:comment_id>',
                 endpoint='comment')




