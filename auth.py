from flask import Blueprint, render_template, redirect, url_for, request

from ormmodels import *

from main import app, session


@app.route('/login', methods=['POST'])
def login():
    nickname, password = request.args.get('name'), request.args.get('password')
    if not nickname:
        return "No \"nickname\" argument was provided."
    if not password:
        return "No \"password\" argument was provided."

    user = session.execute(select(User).where(nickname=nickname)).one()

    if not user:
        return "Such username does not exist."

    if user.password == password:
        return redirect(url_for('main.profile'))
    else:
        return "Wrong password."


@app.route('/signup', methods=['POST'])
def signup_post():
    nickname, password = request.args.get('name'), request.args.get('password')
    if not nickname:
        return "No \"nickname\" argument was provided."
    if not password:
        return "No \"password\" argument was provided."

    if session.execute(select(User).where(nickname=nickname)).one():
        return "Such username already exists."

    user = User(username=nickname, password=password)

    session.add(user)
    session.commit()

    return f"New user #{user.ID} was created with the nickname {user.username} and password {user.password}."


@app.route('/logout')
def logout():
    return 'Logout'
