from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__, static_folder='static')
app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key')

# Папка для данных
DATA_DIR = 'data'
DATA_FILE = os.path.join(DATA_DIR, 'registrations.json')

# Создаём папку при запуске
os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)

def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['name', 'email', 'phone', 'participants']):
            return jsonify({'error': 'Alle Pflichtfelder ausfüllen!'}), 400
        
        registration = {
            'id': datetime.now().strftime('%Y%m%d%H%M%S%f'),
            'name': data['name'].strip(),
            'email': data['email'].strip(),
            'phone': data['phone'].strip(),
            'participants': int(data['participants']),
            'comments': data.get('comments', '').strip(),
            'timestamp': datetime.now().isoformat()
        }
        
        regs = load_data()
        regs.append(registration)
        save_data(regs)
        
        return jsonify({'success': True, 'message': 'Anmeldung erfolgreich!'})
    
    except Exception as e:
        return jsonify({'error': 'Fehler beim Speichern'}), 500

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if (username == os.getenv('ADMIN_USERNAME') and 
        password == os.getenv('ADMIN_PASSWORD')):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Falscher Benutzername oder Passwort'}), 401

@app.route('/api/admin/registrations', methods=['GET'])
def get_registrations():
    auth = request.headers.get('Authorization')
    if not auth:
        return jsonify({'error': 'Nicht autorisiert'}), 401
    
    username, password = auth.split(':')
    if (username != os.getenv('ADMIN_USERNAME') or 
        password != os.getenv('ADMIN_PASSWORD')):
        return jsonify({'error': 'Nicht autorisiert'}), 401
    
    regs = load_data()
    return jsonify({
        'registrations': regs,
        'stats': {
            'total_registrations': len(regs),
            'total_participants': sum(r['participants'] for r in regs)
        }
    })

@app.route('/api/admin/export', methods=['GET'])
def export_data():
    auth = request.headers.get('Authorization')
    if not auth:
        return jsonify({'error': 'Nicht autorisiert'}), 401
    
    username, password = auth.split(':')
    if (username != os.getenv('ADMIN_USERNAME') or 
        password != os.getenv('ADMIN_PASSWORD')):
        return jsonify({'error': 'Nicht autorisiert'}), 401
    
    regs = load_data()
    return jsonify(regs)

if __name__ == '__main__':
    print("🚀 Server startet auf http://localhost:5000")
    print(f"👤 Admin: {os.getenv('ADMIN_USERNAME')}")
    print(f"🔒 Passwort: {os.getenv('ADMIN_PASSWORD')}")
    app.run(debug=True, host='0.0.0.0', port=5000)