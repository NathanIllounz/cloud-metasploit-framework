Cloud Metasploit Framework - Backend 
===========================================

Contents:
- app.py (improved Flask app)
- msf_wrapper.py (safe msfconsole runner)
- validators.py (IP/allowlist checks)
- jobs.py (sqlite job store)
- config.example.json (example configuration)
- tests/ (unit tests for validators)

Quick start (on Ubuntu EC2):
1. Install msfconsole (recommended): sudo snap install metasploit-framework
2. Ensure Python 3.10+ is installed.
3. In backend folder:
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirement_new.txt
4. Copy config.example.json to config.json and edit allowed_target_ranges, apiBase, timeout_seconds.
5. Run the server:
   python3 app.py
6. The API will be available on port 5000. Use the frontend config.json to point to this API.

Safety notes:
- Do NOT expose this API to the public internet without authentication.
- Ensure allowed_target_ranges includes only lab/host-only IP ranges.
- Keep config.json out of version control.
