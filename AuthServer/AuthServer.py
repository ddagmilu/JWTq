from flask import Flask, request, jsonify
import jwt
import datetime
import mysql.connector
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ZO2rgM0OD1nh2RIG3OSn5tTH7v3z5AIpxT'

# MySQL configuration
db_config = {
    'user': 'root',
    'password': 'root',
    'host': '127.0.0.1',
    'database': 'jwtq_db'
}

def create_token(payload):
    token = jwt.encode(
        {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            **payload
        },
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    store_token(payload)
    return token

def store_token(payload):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tokens (code, role, messages_class, publish_right, sub_topic, pub_topic)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (payload['code'], payload['role'], payload['messages_class'], payload['publish_right'], json.dumps(payload['sub_topic']), json.dumps(payload['pub_topic'])))
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/token/issue', methods=['POST'])
def issue_token():
    data = request.get_json()
    token = create_token(data)
    return jsonify({'token': token})

@app.route('/token/renew', methods=['POST'])
def renew_token():
    token = request.headers.get('Authorization').split()[1]
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'], options={"verify_exp": False})
        new_token = create_token(payload)
        return jsonify({'token': new_token})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

@app.route('/token/revoke', methods=['POST'])
def revoke_token():
    # Implement token revocation logic here (e.g., storing revoked tokens in a database)
    return jsonify({'message': 'Token revoked'}), 200

@app.route('/token/list', methods=['GET'])
def list_tokens():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tokens")
    tokens = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(tokens)



@app.route('/token/check_code/<code>', methods=['GET'])
def check_code(code):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT EXISTS(SELECT 1 FROM tokens WHERE code=%s)", (code,))
    exists = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return jsonify({'exists': bool(exists)})


@app.route('/token/info/<code>', methods=['GET'])
def get_token_info(code):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tokens WHERE code = %s", (code,))
    token_info = cursor.fetchone()
    cursor.close()
    conn.close()
    if token_info:
        return jsonify(token_info)
    else:
        return jsonify({'error': 'Token not found'}), 404



if __name__ == '__main__':
    app.run(debug=True)
