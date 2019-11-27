from flask import Flask, request, jsonify, session
from datetime import date
from dataclasses import dataclass
from functools import wraps

last_message_id = 0

@dataclass
class Message:
    sender: str
    receiver: str
    message: str
    subject: str
    creation_date: date
    is_read: bool
    id: int

app = Flask(__name__)

messages = []
messages.append(Message("ori","ori","hello","Today",date.today(),
                             False,
                             last_message_id +1))
last_message_id +=1

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'username' in session:
            return f(*args, **kwargs)
        else:
            return "Login required"
    return wrap

@app.route('/login', methods=['POST'])
def login():
    #req_data = request.get_json()
    if session.get('username') == request.args.get('username'):
        return "You are already logged in"
    session['username'] = request.args.get('username')
    # No signup so no password needed
    return "Login successfully"



@app.route('/logout')
@login_required
def logout():
    if 'username' in session:
        del session['username']
    return "Logout successfully"

@app.route('/write_message')
@login_required
def write_message():
    global messages
    global last_message_id
    #req_data = request.get_json()
    messages.append(Message(session['username'],
                            request.args.get('receiver'),
                            request.args.get('message'),
                            request.args.get('subject'),
                             date.today(),
                             False,
                             last_message_id + 1))
    last_message_id += 1
    return "Message received"

@app.route('/get_all_messages')
@login_required
def get_all_messages():
    global messages
    return jsonify(list(filter(lambda message: message.receiver == session['username'], messages)))

@app.route('/get_all_unread_messages')
@login_required
def get_all_unread_messages():
    global messages
    filters_messages = list(filter(lambda message:
                not message.is_read and message.receiver == session['username'],
                messages))
    for message in filters_messages:
        message.is_read = True
    return jsonify(filters_messages)

@app.route('/read_message')
@login_required
def read_message():
    global messages
    filters_messages = list(filter(lambda message:
                                   not message.is_read and message.receiver == session['username'],
                                   messages))
    if len(filters_messages) > 0:
        filters_messages[0].is_read = True
        return jsonify(filters_messages[0])
    else:
        return "No unread messages"

@app.route('/delete_message')
@login_required
def delete_message():
    #req_data = request.get_json()
    message_to_delete = list(filter(lambda message:
                                    (message.receiver == session['username']
                                     or message.sender == session['username'])
                                    and message.id ==  int(request.args.get("id")),
                                    messages))

    if len(message_to_delete) > 0:
        messages.remove(message_to_delete[0])
        return "Message deleted"
    else:
        return "Message not found"

if __name__ == '__main__':
    app.secret_key = 'super secret keyy'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host='0.0.0.0', port=80)
