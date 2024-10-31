from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_socketio import SocketIO, send, emit
import datetime

app = Flask(__name__)
app.secret_key = 'mysecret'
socketio = SocketIO(app)

messages = []

active_users = set()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/chat', methods=['POST'])
def chat():
    username = request.form['username']

    if username in active_users:
        flash("Kullanıcı zaten mevcut")
        return redirect(url_for('index'))

    session['username'] = username
    active_users.add(username)
    print(f"'{username}' giriş yaptı.")
    return redirect(url_for('chat_page', username=username))

@app.route('/chat_page')
def chat_page():
    username = session.get('username')
    if not username:
        return redirect(url_for('index'))
    return render_template('chat.html', username=username)

@socketio.on('message')
def handle_message(msg):
    username = session.get('username', 'Bilinmeyen')
    full_message = f"{username}: {msg}"
    print(datetime.datetime.now().strftime("%H:%M:%S - ") + full_message)

    messages.append(full_message)

    with open('history.txt', 'a', encoding='utf-8') as file:
        file.write(datetime.datetime.now().strftime("%H:%M:%S - ") + full_message + '\n')

    send(full_message, broadcast=True)

@socketio.on('connect')
def handle_connect():
    username = session.get('username')
    if username:
        for message in messages:
            emit('message', message)

@socketio.on('disconnect')
def handle_disconnect():
    username = session.get('username')
    if username and username in active_users:
        active_users.remove(username)
        print(f"'{username}' çıkış yaptı.")

if __name__ == '__main__':
    socketio.run(app, host="192.168.1.105", port=2626, debug=True)
