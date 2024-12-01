from flask import Flask, jsonify, request
import mysql.connector
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from flask_mail import Mail, Message
import random
import string
import traceback
from flask_cors import cross_origin
import requests
import logging
import subprocess
import sys
import time
import os
from shutil import which


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)


Hugging_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-1B"  # You can change the model
API_TOKEN = "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"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config.from_object(Config)

# Initialize Flask-Mail
mail = Mail(app)

JDoodle_API_URL = "https://api.jdoodle.com/v1/execute"
CLIENT_ID = "317b1d2295d5d1fea1edd77acefe7f8a"
CLIENT_SECRET = "1533326c028675c24eda0623d61c58f02454c6f82da10f7e83bd4f5a1706ce71"



# Initialize MySQL connection
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Sharayu@151569",
        database="project101",
        auth_plugin='mysql_native_password'
    )
    return connection

def check_ollama_installation():
    """Check if Ollama is installed and running."""
    try:
        process = subprocess.run(
            ["ollama", "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return True, process.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Ollama not properly installed: {str(e)}"
    except FileNotFoundError:
        return False, "Ollama is not installed"
    except Exception as e:
        return False, f"Error checking Ollama: {str(e)}"
    
def query_huggingface(prompt, timeout=30):
    """Send a query to Hugging Face Inference API."""
    try:
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 500,  # Adjust based on your needs
                "temperature": 0.7,  # Adjust for creativity vs consistency
                "top_p": 0.9,
                "do_sample": True
            }
        }
        
        response = requests.post(
            Hugging_API_URL,
            headers=HEADERS,
            json=payload,
            timeout=timeout
        )
        
        response.raise_for_status()  # Raise exception for bad status codes
        return response.json(), None
        
    except requests.exceptions.Timeout:
        return None, "API request timed out"
    except requests.exceptions.RequestException as e:
        return None, f"API request failed: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"


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
@cross_origin(origins="http://localhost:8080")
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
    

@app.route('/generate-questions', methods=['POST'])
def generate_questions():
    try:
        # Log incoming request
        logger.debug(f"Received request with data: {request.data}")

        # Validate request data
        data = request.json
        if not data:
            logger.error("No data provided in request")
            return jsonify({"error": "No data provided"}), 400

        topic = data.get('topic')
        difficulty = data.get('difficulty', 'basic')

        if not topic:
            logger.error("No topic provided in request")
            return jsonify({"error": "Topic is required"}), 400

        # Generate the prompt
        prompt = f"Generate 3 {difficulty} level strictly programming questions about {topic}. Format each question on a new line."
        logger.debug(f"Generated prompt: {prompt}")

        # Query Hugging Face API
        response, error = query_huggingface(prompt)
        
        if error:
            logger.error(f"API Error: {error}")
            return jsonify({"error": error}), 500

        # Process the output - adjust based on the actual API response format
        try:
            # The exact processing will depend on the model's output format
            # This is a basic example - adjust based on actual response structure
            output_text = response[0].get('generated_text', '')
            
            # Split into questions and clean up
            questions = [
                q.strip() for q in output_text.strip().split('\n')
                if q.strip() and len(q.strip()) > 10  # Basic validation of questions
            ]

            # Validate questions
            if not questions:
                logger.error("No valid questions generated")
                return jsonify({"error": "No valid questions generated"}), 500

            # Limit to 3 questions and format them
            final_questions = questions[:3]
            logger.debug(f"Generated questions: {final_questions}")

            return jsonify({
                "questions": final_questions,
                "count": len(final_questions)
            }), 200

        except Exception as e:
            logger.error(f"Error processing API response: {str(e)}")
            return jsonify({"error": f"Error processing response: {str(e)}"}), 500

    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500
    

@app.route('/execute', methods=['POST'])
def execute_code():
    try:
        data = request.json
        payload = {
            "clientId": CLIENT_ID,
            "clientSecret": CLIENT_SECRET,
            "script": data["script"],
            "language": data.get("language", "python3"),
            "versionIndex": data.get("versionIndex", "3"),
        }
        response = requests.post(JDoodle_API_URL, json=payload)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == '__main__':
    try:
        #subprocess.run(["ollama", "pull", "llama3.2:1b"], check=True)
        logger.info("Successfully pulled Ollama model")
        app.run(debug=True)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
