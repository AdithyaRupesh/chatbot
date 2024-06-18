from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_marshmallow import Marshmallow
import pyotp

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/user'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'adithyagnair2000@gmail.com'
app.config['MAIL_PASSWORD'] = 'ksac bykk isjp nnzf'
app.config['SECRET_KEY'] = '521ca85a63664803b13d7300f6beae18'

db = SQLAlchemy(app)
mail = Mail(app)
ma = Marshmallow(app)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    business_name = db.Column(db.String(120), nullable=False)
    verification_otp = db.Column(db.String(6))
    email_verification = db.Column(db.Boolean, default=False)
    login_otp = db.Column(db.String(6))

    def __init__(self, username, email, business_name):
        self.username = username
        self.email = email
        self.business_name = business_name

with app.app_context():
    db.create_all()

class userSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'email', 'business_name')

user_schema = userSchema()
users_schema = userSchema(many=True)

def generate_verification_otp(client):
    totp = pyotp.TOTP(pyotp.random_base32(), digits=6, interval=300)
    otp = totp.now()
    client.verification_otp = otp
    db.session.commit()
    return otp

def send_verification_otp_email(user):
    otp = generate_verification_otp(user)
    msg = Message('OTP Verification', sender=app.config['MAIL_USERNAME'], recipients=[user.email])
    msg.body = f"Hello {user.username},\n\nYour OTP for email verification is: {otp}"
    mail.send(msg)

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    try:
        email = request.json.get('email')
        otp = request.json.get('otp')

        if not email or not otp:
            return jsonify({'error': 'Email and OTP are required'})

        user = Client.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'User not found'})

        if user.email_verification:  # Check if email is already verified
            return jsonify({'message': 'Email already verified'})

        if str(user.verification_otp) != str(otp):
            return jsonify({'error': 'Invalid OTP'})

        user.email_verification = True
        db.session.commit()

        return jsonify({'message': 'Email verified successfully'})

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/registration', methods=['POST'])
def register_with_otp():
    try:
        username = request.json.get('username')
        email = request.json.get('email')
        business_name = request.json.get('business_name')

        if not username or not email or not business_name:
            return jsonify({'error': 'Missing Fields'})

        existing_user = Client.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Email Already Exists'})


        new_user = Client(username=username, email=email, business_name=business_name)
        db.session.add(new_user)
        db.session.commit()

        send_verification_otp_email(new_user)

        return jsonify({
            'message': 'User registered successfully. Check your email for OTP.'
        })

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/login',methods=['POST'])
def login():
    try:
        username=request.json.get('username')
        email=request.json.get('email')

        if not username or not email:
            return jsonify({'error':'Username and Email are required.'})

        client= Client.query.filter_by(email=email,username=username).first()
        if not client:
            return jsonify({'error':'Invalid username or password'})

        if not client.email_verification:
            return jsonify({'error':'Email is not verified'})

        return jsonify({'message':'Logined successfully'})

    except Exception as e:
        return jsonify({'error':str(e)})


@app.route('/update_email/<int:id>',methods=['PUT'])
def update_email(id):
    data=request.get_json()
    current_email=data.get('current_email')
    new_email=data.get('new_email')

    if not current_email or not new_email:
        return jsonify({'Error':'Current email and new email are required'}), 400

    client=Client.query.get(id)

    if not client or client.email!= current_email:
        return jsonify({'Error':'Invalid username or email '}), 400

    client.email=new_email
    db.session.commit()

    return jsonify({'message':'Email updated successfully.'})


@app.route('/update_username/<int:id>',methods=['PUT'])
def update_username(id):
    data=request.get_json()
    current_username=data.get('current_username')
    new_username=data.get('new_username')

    if not current_username or not new_username:
        return jsonify({'Error':'Current username and new username are required.'}), 400

    client=Client.query.get(id)

    if not client or client.username!=current_username:
        return jsonify({'Error':'Invalid username or email'}), 400

    client.username=new_username
    db.session.commit()

    return jsonify({'message':'Username updated successfully.'})


@app.route('/edit_business/<int:id>',methods=['PUT'])
def edit(id):
    data=request.get_json()
    current_businessname=data.get('current_businessname')
    new_businessname=data.get('new_businessname')

    if not current_businessname or not new_businessname:
        return jsonify({'Error':'Current businessname and new businessname are required'}), 400

    client=Client.query.get(id)

    if not client or client.business_name!=current_businessname:
        return jsonify({'Error':'Invalid business name'}), 400

    client. business_name=new_businessname
    db.session.commit()

    return jsonify({'message':'Business name updated successfully.'})



if __name__ == '__main__':
    app.run(debug=True)
