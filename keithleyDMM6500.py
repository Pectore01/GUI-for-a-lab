import socket

class DMM6500:
    def __init__(self, ip: str, port=5025, timeout=2):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.sock = None
        self.connect()

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect((self.ip, self.port))

    def send_command(self, command):
        full_command = command + '\n'
        self.sock.sendall(full_command.encode())

    def query(self, command):
        self.send_command(command)
        return self.sock.recv(1024).decode().strip()

    def read_voltage(self):
        return float(self.query("MEAS:VOLT:DC?"))

    def read_current(self):
        return float(self.query("MEAS:CURR:DC?"))

    def read_resistance(self):
        return float(self.query("MEAS:RES?"))

    def close(self):
        if self.sock:
            self.sock.close()