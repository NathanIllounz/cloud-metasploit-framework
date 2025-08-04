# Project Architecture - Cloud Metasploit Framework

## Components
1. **Frontend UI** – A simple HTML form where the user selects target IP and payload.
2. **Backend API (Flask)** – Receives requests and triggers Metasploit commands.
3. **Kali Linux Server** – Executes Metasploit commands.
4. **Target Machine (Metasploitable2)** – The vulnerable machine to attack.

## Flow
User → Frontend (HTML Form) → Backend (Flask API) → Kali/Metasploit → Target VM
