# Message Encryption Project 🔐

This project demonstrates a **secure message transmission system** between multiple nodes using **AES encryption** and **shortest path routing**.  

## 🚀 Features
- 🔑 AES encryption & decryption for secure communication  
- 📡 Multi-node network (10 nodes supported)  
- 🛣 Shortest path routing with cost calculation  
- 📊 Real-time logs for sent and received messages  
- 🌐 Flask-based backend (can be extended with UI)  

## 📂 Project Structure
project/
│
├── app.py # Main program (Flask server / CLI entry)
├── encryption/ # Encryption modules (AES, RSA, DES)
├── network/ # Network graph, adjacency matrix, routing logic
├── data/ # Stores keys and logs
└── README.md # Project documentation
