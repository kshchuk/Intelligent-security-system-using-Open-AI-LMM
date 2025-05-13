import network
import socket
import ure
import time


class WiFiManager:
    """
    WiFi configuration manager for ESP32 (MicroPython).
    """
    HTML_PAGE = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>ESP32 Wi-Fi Setup</title>
          <style>
            body {{ font-family: Arial, sans-serif; background: #f4f4f4; color: #333; }}
            .container {{ max-width: 400px; margin: 50px auto; padding: 20px; background: #fff;
                         border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            h1 {{ text-align: center; color: #007acc; }}
            form {{ display: flex; flex-direction: column; }}
            label {{ margin: 10px 0 5px; }}
            input[type=text], input[type=password] {{ padding: 8px; border: 1px solid #ccc; border-radius: 4px; }}
            input[type=submit] {{ margin-top: 20px; padding: 10px; background: #007acc; color: white;
                                 border: none; border-radius: 4px; cursor: pointer; }}
            input[type=submit]:hover {{ background: #005fa3; }}
            .ssid-list {{ list-style: none; padding: 0; }}
            .ssid-list li {{ margin: 5px 0; }}
          </style>
        </head>
        <body>
          <div class="container">
            <h1>ESP32 Wi-Fi Setup</h1>
            <form action="/configure" method="post">
              <label for="ssid">Select Network:</label>
              <ul class="ssid-list">{ssid_options}</ul>
              <label for="password">Password:</label>
              <input id="password" name="password" type="password" placeholder="Enter password" required>
              <input type="submit" value="Connect">
            </form>
          </div>
        </body>
        </html>
        """

    def __init__(self, ap_ssid, ap_password, authmode=3, profile_file='wifi.dat', port=80):
        print("[INIT] Initializing WiFiManager...")
        self.ap_ssid = ap_ssid
        self.ap_password = ap_password
        self.authmode = authmode
        self.profile_file = profile_file
        self.port = port

        self.wlan_ap = network.WLAN(network.AP_IF)
        self.wlan_sta = network.WLAN(network.STA_IF)
        self.server_socket = None
        print(f"[INIT] AP SSID: {self.ap_ssid}, File: {self.profile_file}, Port: {self.port}")

    def read_profiles(self):
        print("[PROFILES] Reading profiles from file...")
        try:
            with open(self.profile_file) as f:
                lines = f.readlines()
            print(f"[PROFILES] Found {len(lines)} entries")
        except OSError:
            print("[PROFILES] Profile file not found, returning empty dict")
            return {}
        profiles = {}
        for line in lines:
            ssid, pwd = line.strip().split(';')
            profiles[ssid] = pwd
        return profiles

    def write_profiles(self, profiles):
        print(f"[PROFILES] Writing {len(profiles)} profiles to file...")
        with open(self.profile_file, 'w') as f:
            for ssid, pwd in profiles.items():
                f.write(f"{ssid};{pwd}\n")
        print("[PROFILES] Write complete")

    def connect_sta(self, ssid, password=None, timeout=20):
        print(f"[STA] Activating station interface")
        self.wlan_sta.active(True)
        if self.wlan_sta.isconnected():
            print("[STA] Already connected")
            return True

        print(f"[STA] Connecting to SSID: {ssid}, Password: {password}")
        self.wlan_sta.connect(ssid, password)
        for i in range(timeout * 10):
            if self.wlan_sta.isconnected():
                print('[STA] Connection successful:', self.wlan_sta.ifconfig())
                return True
            time.sleep(0.1)
            if i % 10 == 0:
                print('.', end='')
        print(f"\n[STA] Failed to connect to {ssid}")
        return False

    def scan_and_connect(self):
        print("[SCAN] Scanning for saved networks...")
        profiles = self.read_profiles()
        print("[SCAN] Activating station for scanning")
        self.wlan_sta.active(True)
        nets = sorted(self.wlan_sta.scan(), key=lambda x: x[3], reverse=True)
        print(f"[SCAN] {len(nets)} networks found")
        for ssid_bytes, *_ in nets:
            ssid = ssid_bytes.decode()
            print(f"[SCAN] Checking SSID: {ssid}")
            if ssid in profiles:
                print(f"[SCAN] Known SSID, attempting connect")
                if self.connect_sta(ssid, profiles[ssid]):
                    return True
        print("[SCAN] No known networks connected")
        return False

    def start_ap(self):
        print(f"[AP] Starting access point: {self.ap_ssid}")
        self.wlan_ap.active(True)
        self.wlan_ap.config(essid=self.ap_ssid, password=self.ap_password, authmode=self.authmode)
        print(f"[AP] AP active: {self.ap_ssid} / {self.ap_password}")

    def stop_ap(self):
        print("[AP] Deactivating access point")
        self.wlan_ap.active(False)

    def send_response(self, client, payload, status=200):
        print(f"[HTTP] Sending response, status {status}, length {len(payload)}")
        client.sendall(f"HTTP/1.0 {status} OK\r\nContent-Type: text/html\r\nContent-Length: {len(payload)}\r\n\r\n")
        client.sendall(payload)
        client.close()

    def handle_root(self, client):
        print("[HTTP] Handling root page request")
        ssids = sorted(ssid.decode() for ssid, *_ in self.wlan_sta.scan())
        print(f"[HTTP] Available SSIDs: {ssids}")
        options = ''.join([f"<li><label><input type=\"radio\" name=\"ssid\" value=\"{s}\" required>{s}</label></li>" for s in ssids])
        page = self.HTML_PAGE.format(ssid_options=options)
        self.send_response(client, page)

    def handle_configure(self, client, request):
        print("[HTTP] Handling configuration submission")
        match = ure.search(b'ssid=([^&]*)&password=(.*)', request)
        if not match:
            print("[HTTP] Invalid form data")
            return self.send_response(client, 'Bad Request', status=400)
        ssid = match.group(1).decode()
        pwd = match.group(2).decode()
        print(f"[HTTP] Received SSID: {ssid}")
        if self.connect_sta(ssid, pwd):
            print(f"[HTTP] Connected, saving profile: {ssid}")
            profiles = self.read_profiles()
            profiles[ssid] = pwd
            self.write_profiles(profiles)
            return self.send_response(client, f'<h1>Connected to {ssid}!</h1>')
        else:
            print(f"[HTTP] Connection failed for {ssid}")
            return self.send_response(client, f'<h1>Connect failed for {ssid}.</h1><p><a href=\"/\">Try again</a></p>')

    def serve(self):
        addr = socket.getaddrinfo('0.0.0.0', self.port)[0][-1]
        print(f"[HTTP] Binding server to {addr}")
        self.server_socket = socket.socket()
        self.server_socket.bind(addr)
        self.server_socket.listen(1)
        print(f"[HTTP] Server listening on {addr}")

        while True:
            print("[HTTP] Waiting for client connection...")
            client, remote_addr = self.server_socket.accept()
            print(f"[HTTP] Client connected from {remote_addr}")
            client.settimeout(5)
            try:
                req = b''
                while b'\r\n\r\n' not in req:
                    req += client.recv(512)
            except Exception as e:
                print(f"[HTTP] Receive error: {e}")
            # Parse request line
            try:
                first_line = req.split(b'\r\n', 1)[0]
                parts = first_line.split(b' ')
                method = parts[0]
                path = parts[1]
                url = path.lstrip(b'/').decode()
                print(f"[HTTP] Method: {method.decode()}, URL: /{url}")
            except Exception as e:
                print(f"[HTTP] Failed to parse request: {e}")
                client.close()
                continue

            if url == '':
                self.handle_root(client)
            elif url == 'configure' and method == b'POST':
                data = req.split(b'\r\n\r\n', 1)[1]
                self.handle_configure(client, data)
            else:
                print(f"[HTTP] Not found or invalid method: {method.decode()} /{url}")
                self.send_response(client, '<h1>404 Not Found</h1>', status=404)

    def run(self):
        print("[RUN] Starting WiFiManager run sequence")
        if not self.scan_and_connect():
            print("[RUN] No existing Wi-Fi, entering AP mode")
            self.start_ap()
            self.serve()
        else:
            print('Using existing Wi-Fi connection.')


# Example usage:
# mgr = WiFiManager(ap_ssid='ESP_32_node', ap_password='12345678')
# mgr.run()