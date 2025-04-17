import os, uuid, io, time, importlib
from flask import Flask, request, jsonify, session, abort, send_file
from flask_cors import CORS
from cryptography.fernet import Fernet
import json

FERNET_KEY = os.environ.get("FERNET_KEY") or Fernet.generate_key()
fernet = Fernet(FERNET_KEY)
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET") or os.urandom(24)
CORS(app, supports_credentials=True)

user_sessions = {}
SESSION_LIFESPAN = 2 * 60 * 60

# Crisis resources & plugins (loadable from files for i18n)
crisis_db = json.load(open("../resources/crisis-hotlines.json"))
CRISIS_KEYWORDS = [k for k in crisis_db["en"]["keywords"]]
CRISIS_RESOURCE = crisis_db["en"]["message"]

# Plugin loader
def load_plugins():
    plugins = {}
    plugin_dir = "./plugins/backend"
    for fname in os.listdir(plugin_dir):
        if fname.endswith(".py"):
            mod_name = fname[:-3]
            plugins[mod_name] = importlib.import_module(f"plugins.backend.{mod_name}")
    return plugins

plugins = load_plugins()

def get_ai_response(user_message, history=None, model='ToqanGPT'):
    # Multi-LLM/AI integration stub
    for plugname, plugin in plugins.items():
        if hasattr(plugin, "ai_override"):
            resp = plugin.ai_override(user_message, history, model)
            if resp: return resp
    # Default fallback:
    return "Thank you for sharing. I'm here to listen. Would you like to talk more or try a wellbeing tool?"

def contains_crisis(text):
    return any(k in text.lower() for k in CRISIS_KEYWORDS)

@app.before_request
def assign_user_id():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())

@app.route('/privacy')
def privacy():
    with open('../docs/PRIVACY.md') as f:
        return f.read()

@app.route('/message', methods=['POST'])
def message():
    user_id = session.get('user_id')
    if not user_id: abort(401)
    user_message = request.json.get('message', '').strip()
    now = int(time.time())
    session_data = user_sessions.get(user_id, [])
    session_data = [(ts, em) for ts, em in session_data if now - ts < SESSION_LIFESPAN]
    enc_msg = fernet.encrypt(user_message.encode())
    session_data.append((now, enc_msg))
    crisis = contains_crisis(user_message)
    history = [fernet.decrypt(m).decode() for _, m in session_data[-10:]]
    ai_reply = get_ai_response(user_message, history=history)
    session_data.append((now, fernet.encrypt(ai_reply.encode())))
    user_sessions[user_id] = session_data
    if crisis: ai_reply += "<br><br>" + CRISIS_RESOURCE
    # Plugins: check post-processing (mood tracking, journaling etc)
    for plugname, plugin in plugins.items():
        if hasattr(plugin, "after_ai_reply"):
            ai_reply = plugin.after_ai_reply(user_message, ai_reply, user_id)
    return jsonify({'reply': ai_reply, 'crisis': crisis})

@app.route('/history', methods=['GET'])
def history():
    user_id = session.get('user_id')
    if not user_id: abort(401)
    history = [(ts, fernet.decrypt(m).decode()) for ts, m in user_sessions.get(user_id, [])]
    messages = [{"timestamp": ts, "message": msg, "sender": "user" if i % 2 == 0 else "ai"} for i, (ts, msg) in enumerate(history)]
    return jsonify({'history': messages})

@app.route('/plugins', methods=['GET'])
def plugin_info():
    return jsonify({'available_plugins': list(plugins.keys())})

@app.route('/download', methods=['GET'])
def download():
    user_id = session.get('user_id')
    if not user_id:
        abort(401)
    history = [fernet.decrypt(m).decode() for _, m in user_sessions.get(user_id, [])]
    output = '
'.join(history)
    return send_file(
        io.BytesIO(output.encode('utf-8')),
        as_attachment=True,
        download_name=f'ai_safe_space_session.txt',
        mimetype='text/plain'
    )

@app.route('/logout', methods=['POST'])
def logout():
    user_id = session.pop('user_id', None)
    if user_id: user_sessions.pop(user_id, None)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
