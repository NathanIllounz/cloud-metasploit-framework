from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid, os, json, time

from msf_wrapper import run_msfconsole_safe
import validators
import jobs

app = Flask(__name__)
CORS(app)

# Load config from config.json or fallback to example
cfg_path = os.path.join(os.path.dirname(__file__), 'config.json')
example_path = os.path.join(os.path.dirname(__file__), 'config.example.json')
if os.path.exists(cfg_path):
    with open(cfg_path, 'r') as f:
        CONFIG = json.load(f)
else:
    with open(example_path, 'r') as f:
        CONFIG = json.load(f)

ALLOWLIST = CONFIG.get('allowed_target_ranges', [])
TIMEOUT = int(CONFIG.get('timeout_seconds', 300))

def make_job_id():
    return time.strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]

@app.route('/api/exploit/run', methods=['POST'])
def api_exploit_run():
    data = request.get_json(force=True) or {}
    mode = data.get('mode', 'simulate').lower()
    exploit = data.get('exploit') or data.get('EXPLOIT') or data.get('exploit_name')
    rhost = data.get('rhost') or data.get('RHOST') or data.get('RHOSTS') or data.get('rhosts')
    rport = data.get('rport') or data.get('RPORT') or ''
    lhost = data.get('lhost') or data.get('LHOST') or ''
    lport = data.get('lport') or data.get('LPORT') or ''
    payload = data.get('payload') or data.get('PAYLOAD') or ''

    # Basic validation
    if not exploit or not rhost:
        return jsonify({'error': 'Missing exploit or rhost'}), 400
    if not validators.is_valid_ip(rhost):
        return jsonify({'error': 'Invalid rhost IP'}), 400

    job_id = make_job_id()
    params = {'exploit': exploit, 'rhost': rhost, 'rport': rport, 'lhost': lhost, 'lport': lport, 'payload': payload, 'mode': mode}
    jobs.create_job(job_id, params, mode, status='running')

    # Simulation mode - return fake output quickly
    if mode == 'simulate' or CONFIG.get('simulate_mode_default', True):
        fake = f"""[SIMULATION] Would run: use {exploit}\nset RHOST {rhost}\nset RPORT {rport}\nset PAYLOAD {payload}\nrun\n[SIMULATION] No network traffic sent."""
        jobs.update_job_output(job_id, 'done', 0, fake)
        return jsonify({'success': True, 'job_id': job_id, 'output': fake})

    # Real mode - check allowlist
    if not validators.is_ip_in_allowlist(rhost, ALLOWLIST):
        jobs.update_job_output(job_id, 'denied', 0, 'Target not in allowlist')
        return jsonify({'error': 'Target not allowed'}, 403)

    # Build msf commands
    parts = [f"use {exploit}", f"set RHOST {rhost}"]
    if rport: parts.append(f"set RPORT {rport}")
    if lhost: parts.append(f"set LHOST {lhost}")
    if lport: parts.append(f"set LPORT {lport}")
    if payload: parts.append(f"set PAYLOAD {payload}")
    parts.append('exploit')
    msf_cmds = "\n".join(parts)

    exit_code, stdout, stderr = run_msfconsole_safe(msf_cmds, timeout=TIMEOUT)
    combined = stdout if stdout else stderr
    status = 'done' if exit_code == 0 else 'error'
    jobs.update_job_output(job_id, status, exit_code, combined)
    return jsonify({'success': exit_code == 0, 'job_id': job_id, 'exit_code': exit_code, 'output': combined})

@app.route('/api/job/<job_id>', methods=['GET'])
def api_get_job(job_id):
    rec = jobs.get_job(job_id)
    if not rec:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(rec)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
