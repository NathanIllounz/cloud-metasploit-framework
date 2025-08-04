#!/bin/bash

echo "Updating system..."
sudo apt update && sudo apt upgrade -y

echo "Installing Metasploit..."
curl https://raw.githubusercontent.com/rapid7/metasploit-framework/master/msfinstall | sudo bash

echo "Installation complete. You can now run 'msfconsole'."
