from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)

@app.route('/run_exploit', methods=['POST'])
def run_exploit():
    data = request.get_json()
    target_ip = data.get('target_ip')
    payload = data.get('payload')

    if not target_ip or not payload:
        return jsonify({'error': 'Missing target_ip or payload'}), 400

    cmd = f"msfconsole -q -x 'use {payload}; set RHOST {target_ip}; exploit; exit'"

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        print("=== Real Attack Output ===")
        print(result.stdout)
        print("==========================")
        return jsonify({'output': result.stdout})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/simulate_attack', methods=['POST'])
def simulate_attack():
    data = request.get_json()
    target_ip = data.get('target_ip')
    payload = data.get('payload')

    fake_output = f"""
    [+] Connecting to target {target_ip}
    [+] Using payload: {payload}
    [+] Exploit launched successfully!
    [+] Simulated Session opened with {target_ip}
    [+] Meterpreter prompt: >
    """
    print("=== Simulated Attack ===")
    print(fake_output)
    print("========================")
    return jsonify({'output': fake_output})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
