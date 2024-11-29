from flask import Flask, session, redirect, request, jsonify
import mysql.connector
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from flask_mail import Mail, Message
import secrets
import datetime
import random
import string
import traceback
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

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Initialize Flask-Mail
mail = Mail(app)

# initiate a class for all database functions
class DatabaseManager:
    def __init__(self):
        """
        Initialize database connection with robust configuration
        Recommend using environment variables for sensitive connection details
        """
        self.connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'your_username'),
            password=os.getenv('MYSQL_PASSWORD', 'your_password'),
            database=os.getenv('MYSQL_DATABASE', 'session_management')
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def create_tables(self):
        """
        Create necessary tables for session management
        Idempotent design ensures no duplicate table creation
        """
        create_user_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )"""

        create_session_table = """
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            token VARCHAR(64) UNIQUE NOT NULL,
            ip_address VARCHAR(45) NOT NULL,
            user_agent VARCHAR(256) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )"""

        self.cursor.execute(create_user_table)
        self.cursor.execute(create_session_table)
        self.connection.commit()

    def create_user_session(self, user_id, ip_address, user_agent):
        """
        Create a new user session with advanced management
        
        Args:
            user_id (int): Authenticated user's ID
            ip_address (str): Client's IP address
            user_agent (str): Browser/client user agent
        
        Returns:
            str: Generated session token
        """
        # First, clean up old sessions
        cleanup_query = """
        DELETE FROM user_sessions 
        WHERE user_id = %s AND 
        created_at < DATE_SUB(NOW(), INTERVAL 30 DAY)
        """
        self.cursor.execute(cleanup_query, (user_id,))

        # Check and limit concurrent sessions
        count_query = "SELECT COUNT(*) as session_count FROM user_sessions WHERE user_id = %s"
        self.cursor.execute(count_query, (user_id,))
        session_count = self.cursor.fetchone()['session_count']

        if session_count >= 2:
            # Remove oldest session if limit exceeded
            remove_oldest = """
            DELETE FROM user_sessions 
            WHERE user_id = %s 
            ORDER BY created_at ASC 
            LIMIT 1
            """
            self.cursor.execute(remove_oldest, (user_id,))

        # Generate secure token
        token = secrets.token_urlsafe(32)

        # Insert new session
        insert_query = """
        INSERT INTO user_sessions 
        (user_id, token, ip_address, user_agent) 
        VALUES (%s, %s, %s, %s)
        """
        self.cursor.execute(insert_query, (user_id, token, ip_address, user_agent))
        self.connection.commit()

        return token

    def validate_session(self, token):
        """
        Comprehensive session validation
        
        Args:
            token (str): Session authentication token
        
        Returns:
            dict: Validation result with user details
        """
        query = """
        SELECT u.id, u.username, s.created_at 
        FROM user_sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.token = %s AND 
        s.created_at > DATE_SUB(NOW(), INTERVAL 30 DAY)
        """
        
        self.cursor.execute(query, (token,))
        session_data = self.cursor.fetchone()

        if not session_data:
            return {'valid': False, 'reason': 'Session not found or expired'}

        # Update last activity
        update_query = """
        UPDATE user_sessions 
        SET last_activity = CURRENT_TIMESTAMP 
        WHERE token = %s
        """
        self.cursor.execute(update_query, (token,))
        self.connection.commit()

        return {
            'valid': True, 
            'user_id': session_data['id'],
            'username': session_data['username']
        }

    def invalidate_session(self, token):
        """
        Explicitly terminate a user session
        
        Args:
            token (str): Session token to invalidate
        """
        delete_query = "DELETE FROM user_sessions WHERE token = %s"
        self.cursor.execute(delete_query, (token,))
        self.connection.commit()

    def close_connection(self):
        """Properly close database connections"""
        self.cursor.close()
        self.connection.close()

db_manager = DatabaseManager()
db_manager.create_tables()
@app.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and create session
    Note: Assumes password validation is already handled
    """
    username = request.json.get('username')
    user_id = request.json.get('user_id')  # Assuming pre-validated user_id
    
    try:
        token = db_manager.create_user_session(
            user_id, 
            request.remote_addr, 
            str(request.user_agent)
        )
        
        return jsonify({
            'success': True, 
            'token': token
        }), 200
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': str(e)
        }), 500

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

@app.route('/validate_token', methods=['POST'])
def validate_token():
    """Validate user session token"""
    token = request.json.get('token')
    result = db_manager.validate_session(token)
    
    if result['valid']:
        return jsonify({
            'valid': True, 
            'user_id': result['user_id'],
            'username': result['username']
        }), 200
    
    return jsonify({
        'valid': False, 
        'reason': result.get('reason', 'Invalid session')
    }), 401

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
        """Terminate user session"""
        token = request.json.get('token')
        db_manager.invalidate_session(token)
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
            return jsonify({'error': str(e)}), 500

def check_ollama_installation():
    """Check if Ollama is properly installed and running"""
    try:
        # First, check if Ollama is installed
        if sys.platform == "win32":
            ollama_path = "ollama.exe"
        else:
            ollama_path = "ollama"
            
        # Try to find ollama in PATH
        from shutil import which
        ollama_executable = which(ollama_path)
        if not ollama_executable:
            return False, "Ollama executable not found in PATH"
            
        # Try to start Ollama service if not running
        if sys.platform == "win32":
            start_process = subprocess.run(
                ["ollama", "serve"],
                capture_output=True,
                text=True,
                timeout=5
            )
        else:
            # For Unix-like systems, check if ollama service is running
            ps_process = subprocess.run(
                ["ps", "-ef", "|", "grep", "ollama"],
                capture_output=True,
                text=True,
                shell=True
            )
            if "ollama serve" not in ps_process.stdout:
                start_process = subprocess.run(
                    ["ollama", "serve", "&"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    shell=True
                )
        
        # Wait for service to start
        time.sleep(2)
        
        # Check version to verify it's running
        version_process = subprocess.run(
            ["ollama", "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if version_process.returncode != 0:
            return False, f"Ollama service check failed: {version_process.stderr}"
            
        return True, "Ollama is running properly"
        
    except subprocess.TimeoutExpired:
        return False, "Timeout while checking Ollama service"
    except Exception as e:
        return False, f"Error checking Ollama: {str(e)}"

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
        prompt = f"Generate 3 {difficulty} level programming questions about {topic}. Format each question on a new line."
        logger.debug(f"Generated prompt: {prompt}")
        
        # Check if ollama is installed and running
        try:
            version_process = subprocess.run(
                ["ollama", "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            logger.debug(f"Ollama version check output: {version_process.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Ollama not properly installed: {str(e)}")
            return jsonify({"error": "Ollama is not properly installed"}), 500
        except FileNotFoundError:
            logger.error("Ollama command not found")
            return jsonify({"error": "Ollama is not installed"}), 500
        
        # Interact with Ollama
        try:
            # Start the Ollama process
            process = subprocess.Popen(
                ["ollama", "run", "llama3.2:1b"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Set timeout for the entire process
            stdout, stderr = process.communicate(input=prompt, timeout=30)
            
            # Log the raw output
            logger.debug(f"Raw stdout: {stdout}")
            logger.debug(f"Raw stderr: {stderr}")
            
            # Check for errors in stderr
            if stderr:
                logger.error(f"Ollama error output: {stderr}")
                return jsonify({"error": f"Model error: {stderr}"}), 500
            
            # Process the output
            questions = [
                q.strip() for q in stdout.strip().split('\n') 
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
            
        except subprocess.TimeoutExpired as e:
            logger.error(f"Process timeout: {str(e)}")
            return jsonify({"error": "Question generation timed out"}), 504
            
        except Exception as e:
            logger.error(f"Error during Ollama interaction: {str(e)}")
            return jsonify({"error": f"Model error: {str(e)}"}), 500
            
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# Add a health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Check if Ollama is responsive
        subprocess.run(["ollama", "version"], capture_output=True, timeout=5)
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == '__main__':
    try:
        subprocess.run(["ollama", "pull", "llama3.2:1b"], check=True)
        logger.info("Successfully pulled Ollama model")
        app.run(debug=True)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")