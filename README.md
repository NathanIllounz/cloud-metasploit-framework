# Cloud Metasploit Framework

A Cloud-based Metasploit Automation Framework that allows you to launch real penetration tests or simulated attacks via a web interface.

## 🚀 Features:
- Frontend interface to trigger attacks (Real / Simulated)
- Simulate Mode for safe demonstrations
- Real Mode that connects to Metasploit Framework in AWS EC2
- Payload Selection Dropdown (10+ famous exploits)
- Full Backend-Frontend communication over HTTP
- Cloud-Based architecture (AWS EC2 + Flask + Metasploit)

## 🖥️ Architecture:
1. **Frontend (HTML+JS):** User selects target IP and payload, with a Simulate Mode toggle.
2. **Backend (Flask API on EC2):** Receives commands and runs Metasploit commands (or returns simulated output).
3. **Metasploit Framework (on EC2):** Executes real exploits and returns output to the frontend.

## 🛠️ Technologies Used:
- Python3 + Flask + Flask-CORS
- Metasploit Framework (Snap Install)
- HTML, CSS, JavaScript (Frontend)
- AWS EC2 (Ubuntu 22.04)

## ⚙️ How to Deploy:
1. Launch Ubuntu EC2 in AWS (ports 22, 5000, 4444 open).
2. Install Metasploit & Flask on the instance.
3. Clone this repo and run:
    ```bash
    python3 app.py
    ```
4. Open `frontend/index.html` locally and connect to your EC2 Public IP.
5. Toggle Simulate Mode ON/OFF and select Payloads to trigger attacks.

## 📋 Future Improvements:
- LHOST dynamic configuration
- Persistent Deploy Mode (tmux/supervisor)
- Frontend design upgrade (Dashboard look)
- Logs & Session Tracking

## ⚠️ Legal Notice:
This project is for educational purposes only. Do not perform unauthorized attacks on systems you do not own or have explicit permission to test.

---

## Author:
Nathan Illounz
