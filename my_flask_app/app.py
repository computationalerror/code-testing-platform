from flask import Flask, jsonify, request
import mysql.connector
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from flask_mail import Mail, Message
import random
import string
import traceback

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# Initialize Flask-Mail
mail = Mail(app)


# Initialize MySQL connection
def get_db_connection():
    connection = mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )
    return connection


# Store verification codes (in a real application, use a more secure method)
verification_codes = {}
@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the Coding Test Platform'})

@app.route('/HomePage', methods=['GET'])
def home():
    try:
        return jsonify({'message': 'Coding Test Platform'})
    except Exception as e:
        app.logger.error(f"Error in /HomePage: {str(e)}")
        return jsonify({'error': str(e)}), 500

import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/RegisterPage', methods=['POST'])
def register():
    data = request.json
    full_name = data['full_name']
    email = data['email']
    password = generate_password_hash(data['password'])

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Check if the email already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 400

        cursor.execute("INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)",
                       (full_name, email, password))
        connection.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400
    finally:
        cursor.close()
        connection.close()



@app.route('/LoginPage', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if user and check_password_hash(user['password'], password):
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401


@app.route('/send-verification-code', methods=['POST'])
def send_verification_code():
    try:
        email = request.json.get('email')

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if not user:
            return jsonify({'success': False, 'message': 'No account found with this email address.'}), 404

        # Generate a random 6-digit code
        code = ''.join(random.choices(string.digits, k=6))
        verification_codes[email] = code

        # Send email
        msg = Message('Password Reset Verification Code',
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[email])
        msg.body = f'Your verification code is: {code}'
        mail.send(msg)
        return jsonify({'success': True, 'message': 'Verification code sent to your email.'}), 200
    except Exception as e:
        app.logger.error(f"Error in send_verification_code: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'}), 500


@app.route('/verify-code', methods=['POST'])
def verify_code():
    email = request.json.get('email')
    code = request.json.get('verificationCode')

    if email not in verification_codes or verification_codes[email] != code:
        return jsonify({'success': False, 'message': 'Invalid verification code.'}), 400

    return jsonify({'success': True, 'message': 'Code verified successfully.'}), 200


@app.route('/reset-password', methods=['POST'])
def reset_password():
    email = request.json.get('email')
    code = request.json.get('verificationCode')
    new_password = request.json.get('newPassword')

    if email not in verification_codes or verification_codes[email] != code:
        return jsonify({'success': False, 'message': 'Invalid verification code.'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        hashed_password = generate_password_hash(new_password)
        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
        connection.commit()

        # Clear the verification code
        del verification_codes[email]

        return jsonify({'success': True, 'message': 'Password reset successfully.'}), 200
    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': str(err)}), 400
    finally:
        cursor.close()
        connection.close()

@app.route('/save_preferences', methods=['POST'])
def save_preferences():
    try:
        data = request.json
        email = data['email']
        print(f"Received email for saving preferences: {email}")
        preferred_language = data['preferredLanguage']
        experience_level = data['experienceLevel']

        # Save preferences to database
        connection = get_db_connection()
        cursor = connection.cursor()

        # Assuming you have a table named 'preferences'
        cursor.execute("""
            INSERT INTO preferences (email, preferred_language, experience_level) 
            VALUES (%s, %s, %s) 
            ON DUPLICATE KEY UPDATE 
                preferred_language = VALUES(preferred_language), 
                experience_level = VALUES(experience_level)
        """, (email, preferred_language, experience_level))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({'success': True, 'message': 'Preferences saved successfully'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/get_preferences', methods=['GET'])
def get_preferences():
    email = request.args.get('email')

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary=True to get results as dictionaries

    query = "SELECT preferred_language, experience_level FROM preferences WHERE email = %s"
    cursor.execute(query, (email,))
    preferences = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(preferences), 200


@app.route('/update_preference', methods=['POST'])
def update_preference():
    try:
        data = request.json
        email = data['email']

        # Check which preference is being updated
        if 'preferredLanguage' in data:
            preference = 'preferred_language'
            value = data['preferredLanguage']
        elif 'experienceLevel' in data:
            preference = 'experience_level'
            value = data['experienceLevel']
        else:
            return jsonify({'success': False, 'message': 'Invalid preference'}), 400

        # Update the preference in the database
        connection = get_db_connection()
        cursor = connection.cursor()

        query = f"UPDATE preferences SET {preference} = %s WHERE email = %s"
        cursor.execute(query, (value, email))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({'success': True, 'message': f'{preference} updated successfully'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/logout', methods=['POST'])
def logout():
    try:
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/send-password-reset-link', methods=['POST'])
def send_password_reset_link():
    try:
        email = request.json.get('email')

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if not user:
            return jsonify({'success': False, 'message': 'No account found with this email address.'}), 404

        # Generate a random token
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

        # Save the token to the database
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO password_reset_tokens (email, token) VALUES (%s, %s)", (email, token))
        connection.commit()
        cursor.close()
        connection.close()

        # Send the password reset link to the user's email
        msg = Message('Password Reset Link',
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[email])
        msg.body = f'Click this link to reset your password: http://localhost:5000/reset-password/{token}'
        mail.send(msg)

        return jsonify({'success': True, 'message': 'Password reset link sent to your email.'}), 200
    except Exception as e:
        app.logger.error(f"Error in send_password_reset_link: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'}), 500
@app.route('/change-password', methods=['POST'])
def change_password():
    try:
        data = request.json
        email = data['email']
        current_password = data['currentPassword']
        new_password = data['newPassword']
        confirm_password = data['confirmPassword']

        if new_password != confirm_password:
            return jsonify({'success': False, 'message': 'New passwords do not match'}), 400

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], current_password):
            hashed_password = generate_password_hash(new_password)
            cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
            connection.commit()

            return jsonify({'success': True, 'message': 'Password changed successfully'}), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        connection.close()
        
if __name__ == '__main__':
    app.run(debug=True)
