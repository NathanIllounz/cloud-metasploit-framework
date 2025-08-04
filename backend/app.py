from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

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

    # Example command (you'll customize it later)
    cmd = f"msfconsole -q -x 'use {payload}; set RHOST {target_ip}; exploit;'"

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return jsonify({'output': result.stdout})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
