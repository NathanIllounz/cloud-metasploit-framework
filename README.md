# Cloud Metasploit Framework ☁️💥

A cloud-based system that provides a web interface to run Metasploit payloads remotely via a Kali Linux server.  
This project is designed for cybersecurity labs, penetration testing practice, and automation of exploit workflows.

---

## 📚 Project Overview

### Components:
1. **Frontend UI** – Simple HTML form for selecting payloads and target IPs.
2. **Backend API (Python Flask)** – Receives requests and triggers Metasploit commands.
3. **Kali Linux Server (Cloud)** – Executes Metasploit on a remote cloud machine (AWS EC2).
4. **Target VM (Metasploitable2 / Windows XP)** – The vulnerable machine being attacked.

---

## ⚙️ Technologies Used
- Python 3.x + Flask
- HTML + JavaScript (Vanilla)
- AWS EC2 (Kali Linux)
- Metasploit Framework
- Git + GitHub

---

## 🛠️ Project Structure
cloud-metasploit-framework/
│
├── backend/ # Flask API Server
│ ├── app.py
│ └── requirements.txt
│
├── frontend/ # HTML Form Interface
│ └── index.html
│
├── deployment/ # Kali EC2 setup scripts
│ └── setup_kali.sh
│
├── docs/ # Architecture & Threat Models
│ ├── architecture.md
│ └── threats_stride.md
│
├── .gitignore
├── README.md
└── LICENSE


---

## 🚀 How to Run Locally

### 1. Clone the repository:
```bash
git clone https://github.com/your-username/cloud-metasploit-framework.git
cd cloud-metasploit-framework

