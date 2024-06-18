from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_socketio import SocketIO,emit

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:root@localhost/user'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USE_SSL']=True
app.config['MAIL_USE_TLS']=False
app.config['MAIL_DEBUG']=True
app.config['MAIL_USERNAME']='adithyagnair2000@gmail.com'
app.config['MAIL_PASSWORD'] = 'ksac bykk isjp nnzf'
app.config['SECRET_KEY'] = '521ca85a63664803b13d7300f6beae18'
app.config['SQLALCHEMY_TRACK_MODIFICATION']= False
mail=Mail(app)
db=SQLAlchemy(app)

class Client(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(80),nullable=False)
    email=db.Column(db.String(120),nullable=False,unique=True)
    business_name=db.Column(db.String(120),nullable=False)
    verification_otp=db.Column(db.String(6))
    email_verification=db.Column(db.Boolean,default=False)
    login_otp=db.Column(db.String(6))

    def __init__(self, username, email, business_name):
        self.username = username
        self.email = email
        self.business_name = business_name


class Chatbot:
    def __init__(self):
        self.state = 'initial'
        self.user_data = {}

    def get_response(self, message):
        message = message.lower()

        if self.state == 'initial':
            if "hello" in message or "hi" in message:
                self.state = 'options'
                return "Hello! How can I help you today? You can say 'book a demo' or 'talk to chatbot'."
            elif "bye" in message or "goodbye" in message:
                return "Goodbye! Have a nice day!"
            elif "how are you" in message:
                return "I'm a bot, but I'm here to help you!"
            else:
                return "I'm sorry, I don't understand that. Can you please rephrase?"

        elif self.state == 'options':
            if "book a demo" in message:
                self.state = 'get_name'
                return "Great! What's your name?"
            elif "talk to chatbot" in message:
                return "Sure, I'm here to chat. Ask me anything!"
            else:
                return "Please choose an option: 'book a demo' or 'talk to chatbot'."

        elif self.state == 'get_name':
            self.user_data['name'] = message
            self.state = 'get_email'
            return "Thanks! Can I have your email address?"

        elif self.state == 'get_email':
            if self.validate_email(message):
                self.user_data['email'] = message
                self.state = 'get_business_name'
                return "Great! Now, can you provide your business name?"
            else:
                return "That doesn't look like a valid email. Please try again."

        elif self.state == 'get_business_name':
            self.user_data['business_name'] = message
            self.state = 'complete'
            return f"Cheers! Your details has been forwarded to concerned team & we will be in touch soon.In the meantime, if you want to share more details, Please write to us at contact@autointelli.com "

        elif self.state == 'complete':
            return "You have already booked a demo. If you need anything else, just let me know."

        return "I'm sorry, I don't understand that. Can you please rephrase?"

    def validate_email(self, email):
        import re
        regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.match(regex, email) is not None


chatbot = Chatbot()

@app.route('/chat', methods=['GET'])
def chat():
    message = request.args.get('message')

    if not message :
        return jsonify({'error': 'Invalid input'}), 400

    response = chatbot.get_response(message)

    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)