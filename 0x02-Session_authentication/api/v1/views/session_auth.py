#!/usr/bin/env python3
""" Module of Session authentication """
from api.v1.views import app_views
from flask import abort, jsonify, request
import os


@app_views.route("/auth_session/login", methods=["POST"],
                 strict_slashes=False)
def login() -> str:
    """ POST /api/v1/auth_session/login """
    email = request.form.get("email")
    if email is None:
        return jsonify({"error": "email missing"}), 400
    password = request.form.get("password")
    if password is None:
        return jsonify({"error": "password missing"}), 400
    from models.user import User
    try:
        user = User.search({"email": email})
    except Exception:
        return jsonify({"error": "no user found for this email"}), 404

    if len(user) == 0:
        return jsonify({"error": "no user found for this email"}), 404
    if not user[0].is_valid_password(password):
        return jsonify({"error": "wrong password"}), 401
    from api.v1.app import auth
    session_id = auth.create_session(user[0].id)
    response = jsonify(user[0].to_json())
    response.set_cookie(os.getenv("SESSION_NAME"), session_id)
    return response


@app_views.route("/auth_session/logout", methods=["DELETE"],
                 strict_slashes=False)
def logout() -> str:
    """ DELETE /api/v1/auth_session/logout """
    from api.v1.app import auth
    if auth.destroy_session(request):
        return jsonify({}), 200
    else:
        abort(404)
