# backend/app.py
import os
import uuid
import json
import time
import shlex
import subprocess
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import ipaddress

# ---------- Config ----------
ENABLE_REAL = os.getenv('ENABLE_REAL', 'false').lower() in ('1', 'true', 'yes')
MSFCLI_PATH = os.getenv('MSFCLI_PATH', 'msfconsole')   # path to msfconsole if available
JOB_STORE_DIR = os.getenv('JOB_STORE_DIR', '/tmp/cmf_jobs')  # simple storage
ALLOWED_NETWORKS = os.getenv('ALLOWED_NETWORKS', '127.0.0.0/8').split(',')  # CSV of CIDR ranges
MAX_SUBPROCESS_TIMEOUT = int(os.getenv('MAX_SUBPROCESS_TIMEOUT', '120'))  # seconds

# Ensure job dir
os.makedirs(JOB_STORE_DIR, exist_ok=True)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # * for dev; restrict in production

# ---------- Helpers ----------
def nowts():
    return datetime.utcnow().isoformat() + "Z"

def new_job_id():
    return str(uuid.uuid4())

def save_job(job_id, payload):
    path = os.path.join(JOB_STORE_DIR, f"{job_id}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)

def is_ip_allowed(rhost):
    try:
        ip = ipaddress.ip_address(rhost)
    except Exception:
        return False
    for net in ALLOWED_NETWORKS:
        net = net.strip()
        if not net:
            continue
        try:
            if ip in ipaddress.ip_network(net):
                return True
        except Exception:
            # net might be a single IP
            try:
                if ip == ipaddress.ip_address(net):
                    return True
            except:
                pass
    return False

# ---------- Simulators (server-side) ----------
def sim_portscan_text(rhost, start, end):
    # small nmap-like textual output and structured ports
    lines = []
    lines.append(f"Starting Nmap 7.80 ( https://nmap.org ) at {nowts()}")
    lines.append(f"Nmap scan report for {rhost}")
    lines.append(f"Host is up (0.0{int(time.time())%90}s latency).")
    lines.append("PORT     STATE    SERVICE")
    ports = []
    # add a few common ports within range
    common = [22, 80, 443, 445, 3306, 8080]
    for p in common:
        if start <= p <= end:
            ports.append((p, 'open'))
    # add a few random ports
    for p in range(start, min(end, start+60)):
        if len(ports) > 12:
            break
        if p % 97 == 0 or p % 11 == 0:
            ports.append((p, 'open'))
    ports = sorted(set(ports), key=lambda x: x[0])
    for p, state in ports:
        svc = "unknown"
        try:
            svc = {22:'ssh',80:'http',443:'https',445:'microsoft-ds',3306:'mysql',8080:'http-proxy'}[p]
        except KeyError:
            pass
        lines.append(f"{str(p).ljust(8)} {state.ljust(8)} {svc}")
    lines.append("")
    lines.append(f"Nmap done: 1 IP address (1 host up) scanned in {max(1, (end-start)//10)}.00 seconds")
    port_list = [{"port": p, "state": s, "service": ( 'ssh' if p==22 else 'http' if p==80 else 'unknown' )} for p, s in ports]
    return "\n".join(lines), port_list

def sim_http_info(url):
    status = 200 if "localhost" in url or "http" in url else 200
    headers = {
        "Server": "nginx/1.18.0",
        "Content-Type": "text/html; charset=UTF-8",
        "Date": nowts()
    }
    body_snippet = "<html><head><title>Simulated</title></head><body>Simulated response</body></html>"
    return status, headers, body_snippet

def sim_ping(rhost):
    return f"PING {rhost} ({rhost}) 56(84) bytes of data.\n64 bytes from {rhost}: icmp_seq=1 ttl=64 time=0.{int(time.time())%200} ms\n\n--- {rhost} ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss"

def sim_exploit_output(payload, rhost, rport, lhost, lport, exploit_name):
    # short simulated msf-like output
    success = True if hash((exploit_name, rhost, time.time())) % 3 else False
    lines = []
    lines.append(f"[*] Using exploit module: {exploit_name}")
    lines.append(f"[*] Setting RHOST => {rhost}")
    if rport:
        lines.append(f"[*] Setting RPORT => {rport}")
    if payload:
        lines.append(f"[*] Using payload: {payload}")
    lines.append("[*] Running module...")
    if success:
        lines.append(f"[+] Exploit completed successfully at {nowts()}")
        lines.append(f"[+] Session opened on {rhost}:{(int(rport) if rport else 4444)}")
        exit_code = 0
    else:
        lines.append(f"[-] Exploit failed: target did not respond as expected")
        exit_code = 1
    return "\n".join(lines), exit_code

# ---------- Endpoints ----------
@app.route("/api/aux/portscan_tcp", methods=["POST"])
def api_portscan_tcp():
    data = request.get_json(force=True)
    rhost = data.get("rhost")
    start = int(data.get("start_port", 1))
    end = int(data.get("end_port", min(1024, start+1023)))
    mode = data.get("mode", "").lower() or ('simulate' if not ENABLE_REAL else 'real')
    job_id = new_job_id()
    meta = {"job_id": job_id, "rhost": rhost, "start_port": start, "end_port": end, "mode": mode, "time": nowts()}
    save_job(job_id, {"meta": meta})
    if mode == "simulate" or not ENABLE_REAL or not is_ip_allowed(rhost):
        text, ports = sim_portscan_text(rhost, start, end)
        payload = {"job_id": job_id, "output": text, "ports": ports, "exit_code": 0}
        save_job(job_id, {"meta": meta, "result": payload})
        return jsonify(payload)
    # REAL path: run nmap (requires nmap installed) - careful
    try:
        cmd = ["nmap", "-p", f"{start}-{end}", rhost]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=MAX_SUBPROCESS_TIMEOUT)
        text = proc.stdout + "\n" + proc.stderr
        payload = {"job_id": job_id, "output": text, "exit_code": proc.returncode}
        save_job(job_id, {"meta": meta, "result": payload})
        return jsonify(payload)
    except Exception as e:
        return jsonify({"job_id": job_id, "error": str(e), "exit_code": -1}), 500

@app.route("/api/aux/http_version", methods=["POST"])
def api_http_version():
    data = request.get_json(force=True)
    url = data.get("url")
    mode = data.get("mode", "").lower() or ('simulate' if not ENABLE_REAL else 'real')
    job_id = new_job_id()
    meta = {"job_id": job_id, "url": url, "mode": mode, "time": nowts()}
    save_job(job_id, {"meta": meta})
    if mode == "simulate" or not ENABLE_REAL:
        status, headers, body = sim_http_info(url)
        payload = {"job_id": job_id, "status": status, "headers": headers, "body_snippet": body}
        save_job(job_id, {"meta": meta, "result": payload})
        return jsonify(payload)
    # REAL HTTP fetch
    try:
        r = requests.get(url, timeout=10)
        headers = dict(r.headers)
        body_snippet = r.text[:800]
        payload = {"job_id": job_id, "status": r.status_code, "headers": headers, "body_snippet": body_snippet}
        save_job(job_id, {"meta": meta, "result": payload})
        return jsonify(payload)
    except Exception as e:
        return jsonify({"job_id": job_id, "error": str(e)}), 500

@app.route("/api/aux/ping", methods=["POST"])
def api_ping():
    data = request.get_json(force=True)
    rhost = data.get("rhost")
    mode = data.get("mode", "").lower() or ('simulate' if not ENABLE_REAL else 'real')
    job_id = new_job_id()
    meta = {"job_id": job_id, "rhost": rhost, "mode": mode, "time": nowts()}
    save_job(job_id, {"meta": meta})
    if mode == "simulate" or not ENABLE_REAL or not is_ip_allowed(rhost):
        text = sim_ping(rhost)
        payload = {"job_id": job_id, "output": text, "exit_code": 0}
        save_job(job_id, {"meta": meta, "result": payload})
        return jsonify(payload)
    # REAL ping - platform dependent (Linux shown)
    try:
        cmd = ["ping", "-c", "1", rhost]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        output = proc.stdout + "\n" + proc.stderr
        payload = {"job_id": job_id, "output": output, "exit_code": proc.returncode}
        save_job(job_id, {"meta": meta, "result": payload})
        return jsonify(payload)
    except Exception as e:
        return jsonify({"job_id": job_id, "error": str(e)}), 500

@app.route("/api/exploit/run", methods=["POST"])
def api_exploit_run():
    data = request.get_json(force=True)
    exploit = data.get("exploit")
    rhost = data.get("rhost")
    rport = data.get("rport")
    payload = data.get("payload")
    lhost = data.get("lhost")
    lport = data.get("lport")
    mode = data.get("mode", "").lower() or ('simulate' if not ENABLE_REAL else 'real')

    job_id = new_job_id()
    meta = {
        "job_id": job_id,
        "exploit": exploit,
        "rhost": rhost,
        "rport": rport,
        "payload": payload,
        "lhost": lhost,
        "lport": lport,
        "mode": mode,
        "time": nowts()
    }
    save_job(job_id, {"meta": meta})

    # Simulate path or safety check
    if mode == "simulate" or not ENABLE_REAL or not is_ip_allowed(rhost):
        out, exit_code = sim_exploit_output(payload, rhost, rport, lhost, lport, exploit or "unknown")
        result = {"job_id": job_id, "output": out, "exit_code": exit_code}
        save_job(job_id, {"meta": meta, "result": result})
        return jsonify(result)

    # REAL path: construct msfconsole commands safely
    try:
        # Build msf commands list - be careful to avoid unsanitized shell strings
        # This uses -x "<commands>; exit" style; we build a safe string but you should further sanitize
        commands = []
        if exploit:
            commands.append(f"use {exploit}")
        if rhost:
            commands.append(f"set RHOST {rhost}")
        if rport:
            commands.append(f"set RPORT {rport}")
        if payload:
            commands.append(f"set PAYLOAD {payload}")
        if lhost:
            commands.append(f"set LHOST {lhost}")
        if lport:
            commands.append(f"set LPORT {lport}")
        commands.append("exploit -j -z")  # run in background and exit? adjust as needed
        command_str = "; ".join(commands) + "; exit"
        # run msfconsole
        msf_cmd = [MSFCLI_PATH, "-q", "-x", command_str]
        proc = subprocess.run(msf_cmd, capture_output=True, text=True, timeout=MAX_SUBPROCESS_TIMEOUT)
        output_text = proc.stdout + "\n" + proc.stderr
        result = {"job_id": job_id, "output": output_text, "exit_code": proc.returncode}
        save_job(job_id, {"meta": meta, "result": result})
        return jsonify(result)
    except subprocess.TimeoutExpired as te:
        return jsonify({"job_id": job_id, "error": "timeout", "detail": str(te), "exit_code": -1}), 500
    except Exception as e:
        return jsonify({"job_id": job_id, "error": str(e), "exit_code": -1}), 500

# Basic health endpoint
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "now": nowts(), "enable_real": ENABLE_REAL})

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    # dev server only — use gunicorn for production
    app.run(host="0.0.0.0", port=port, debug=False)
