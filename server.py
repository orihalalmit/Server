from flask import Flask, request, jsonify, session
from datetime import datetime
from dataclasses import dataclass
from functools import wraps



# Class for storing A single Message
@dataclass
class Message:
    sender: str
    receiver: str
    message: str
    subject: str
    creation_date: datetime 
    is_read: bool
    id: int

# App initialization 
app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

# Global variable to store the messages from the clients
messages = []
last_message_id = 0

# Authentication check 
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'username' in session:
            return f(*args, **kwargs)
        else:
            return "Login required"
    return wrap


# Login
@app.route('/login', methods=['POST'])
def login():
    if session.get('username') == request.args.get('username'):
        return "You are already logged in"
    session['username'] = request.args.get('username')
    # No signup so no password needed
    return "Login successfully"


# Logout
@app.route('/logout')
@login_required
def logout():
    if 'username' in session:
        del session['username']
    return "Logout successfully"

# Write a message
# adds to messages the new messages 
# each message gets unique id
@app.route('/write_message')
@login_required
def write_message():
    global messages
    global last_message_id
    messages.append(Message(session['username'],
                            request.args.get('receiver'),
                            request.args.get('message'),
                            request.args.get('subject'),
                             datetime.now(),
                             False,
                             last_message_id + 1))
    last_message_id += 1
    return "Message received"

# Return to the user all the read and unread messages with json format
@app.route('/get_all_messages')
@login_required
def get_all_messages():
    global messages
    return jsonify(list(filter(lambda message: message.receiver == session['username'], messages)))

# Return only unread messages
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

# Return next unread message (if exists)
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

# Delete a message by message id
# only receiver or sender can delete
@app.route('/delete_message')
@login_required
def delete_message():
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

# runs the app
if __name__ == '__main__':
    app.run(port=80)
