# Cloud Metasploit Framework

**Cloud Metasploit Framework (CMF)** — a lightweight, web-based frontend and Python backend to teach and demo Metasploit workflows in a safe, controlled environment.  
Supports two modes:

- **Simulate** — generates realistic, structured fake outputs (Nmap-like scans, HTTP headers, msfconsole-style exploit results) for classroom exercises with **no real network traffic**. (Default.)
- **Real** — forwards requests to a backend that runs `msfconsole` on a controlled lab host (use only on isolated lab VMs).

---

## Contents

- `frontend/` — static web UI (HTML, CSS, JS, `exploits.json`)  
- `backend/` — Flask API that wraps `msfconsole` (optional for Real mode)  
- `docs/` — diagrams, poster, slides (optional)  
- `README.md` — this file

---

## Quickstart

### 1. Clone the repo
```bash
git clone git@github.com:NathanIllounz/cloud-metasploit-framework.git
cd cloud-metasploit-framework
```

### 2. Frontend (static)
```bash
cd frontend
# create frontend/config.json from the example below (DO NOT commit)
python3 -m http.server 8000
# open http://localhost:8000/index.html in your browser
```

Create `frontend/config.json` (local copy — DO NOT commit):
```json
{
  "apiBase": "http://<BACKEND_HOST>:5000"
}
```

### 3. Backend (optional — Real mode)
```bash
cd backend
python3 -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows PowerShell
# .\venv\Scripts\Activate.ps1

pip install -r requirements.txt

# run (development):
python3 app.py

# For production, use gunicorn or systemd. Example:
# gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Notes**
- Default mode is **Simulate** (safe). Real mode will POST to backend to run `msfconsole`.
- **Do not commit** `frontend/config.json`. Add it to `.gitignore`.
- Always use isolated lab VMs (e.g., Metasploitable) for real exploit testing. Never target systems you don't own or have permission to test.

---

## Project summary

CMF helps instructors and students practice penetration testing concepts safely by providing simulated outputs for exercises and an option to run real modules against allow-listed lab targets. The frontend includes an adaptive attack form (only required fields enabled per exploit), an exploit catalog, and auxiliary tools (port scan, HTTP fingerprint, ping).

---

## Key features

- Adaptive attack form — fields enabled only when required by the selected exploit template.  
- Exploit catalog (`exploits.json`) with detailed descriptions and payload lists.  
- Auxiliary tools: TCP port scan, HTTP fingerprinting, ping checks (simulate & real).  
- Realistic simulate-mode outputs (multiple randomized templates per exploit).  
- Downloadable job output, copy-to-clipboard and job history hooks for the backend.  
- Easy to configure `frontend/config.json` for API base URL.

---

## Architecture (short)

Frontend (static) → Backend API (Flask) → `msfconsole` runner (isolated EC2/VM) → Lab victim VM(s)

See `docs/architecture_diagram.png` or `docs/architecture.md` for full diagrams and Mermaid/PlantUML sources.

---

## Usage

1. Start the frontend static server and backend (if using Real mode).  
2. Open the frontend (`index.html`).  
3. Select an **Exploit** from the catalog — the form enables only required fields.  
4. Use the global header toggle or the Mode dropdown to choose `Simulate` (default) or `Real`.  
5. Click **Run** — outputs appear in the right pane. In Simulate mode outputs are realistic but synthetic.

### Auxiliary tools
- Choose a scan type (TCP / HTTP / Ping) on the Auxiliary page.  
- In Simulate mode the site returns plausible Nmap/HTTP/ping outputs; in Real mode the backend is queried.

---

## Testing & Lab setup

- Use an isolated, private network for integration testing (VirtualBox/VMware host-only or a private VLAN).  
- For Real reverse shells configure the backend’s LHOST and firewall rules (on AWS use an Elastic IP if needed).  
- Run backend under a dedicated non-root user and consider containerizing msfconsole for extra isolation.  
- Prefer `gunicorn` + `systemd` for production rather than Flask dev server.

---

## Security & legal notice

- This repository is for **educational use only**. You are responsible for having permission to test any targets. Unauthorized testing may be illegal.  
- Restrict backend access (VPN, firewall rules, or SSH tunnels). Add authentication before exposing the API.  
- Avoid storing credentials or secrets in the repo. Use environment variables or secret stores.  
- If `frontend/config.json` was committed accidentally, remove it and rotate any exposed secrets.

Add to `.gitignore`:
```
frontend/config.json
venv/
__pycache__/
*.pyc
.DS_Store
Thumbs.db
```

---

## Exploit catalog

`frontend/exploits.json` entries include:
- `id` — internal identifier  
- `title` — human title  
- `exploit` — msf module path (for Real mode)  
- `description` — 25–50 words explaining the exploit and usage  
- `required_fields` — fields the form will enable (e.g., `rhost`, `rport`, `lhost`, `lport`, `payload`)  
- `payloads` — recommended payloads  
- `notes` — lab/use notes

You can extend the catalog by editing `exploits.json`.

---

## Contributing

1. Fork the repo.  
2. Create a feature branch:
```bash
git checkout -b feat/my-change
```
3. Make changes, test, commit.  
4. Push branch and open a Pull Request.

**Do not** commit `frontend/config.json` or any secrets.

---

## Example commit & PR steps
```bash
git checkout -b docs/readme-update
git add README.md
git commit -m "docs: improved README"
git push -u origin docs/readme-update
# then open a PR on GitHub
```

---

## License

This project is provided for educational purposes. Add a license file (e.g., MIT) if you want to release it under a permissive license.

---

## Authors / Contact

Nathan Illouz — project author / student

If you have questions or issues, open an issue in this repository.

---

## Final notes

- Default mode is Simulate to keep classroom sessions safe.  
- Consider adding authentication and an allowlist of allowed target IPs before enabling Real mode in shared or public environments.
