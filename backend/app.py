from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "Metasploit Cloud Controller API is running!"

@app.route('/run_exploit', methods=['POST'])
def run_exploit():
    data = request.get_json()
    target_ip = data.get('target_ip')
    payload = data.get('payload')

    if not target_ip or not payload:
        return jsonify({'error': 'Missing target_ip or payload'}), 400

    # Fake Response Simulation
    fake_output = f"""
    [+] Connecting to target {target_ip}
    [+] Using payload: {payload}
    [+] Exploit launched successfully!
    [+] Session opened with {target_ip}
    [+] Meterpreter prompt: >
    """

    return jsonify({'output': fake_output})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
