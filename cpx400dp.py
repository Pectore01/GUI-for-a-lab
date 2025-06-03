import socket
import time
from power_supply_interface import PowerSupplyInterface

class CPX400DP(PowerSupplyInterface):
    def __init__(self, ip: str, port: int = 9221):
        self.ip = ip
        self.port = port
       
        self.socket = None
        if "192.168.0.103" in ip:
            self.name = f"CPX400DP Right {ip}"  # Add this line
        elif "192.168.0.105" in ip:
            self.name = f"CPX400DP Left {ip}"  # Add this line
        else:
            self.name = f"CPX400DP-{ip}"  # Add this line

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))
        print(f"Connected to {self.ip}:{self.port}")

    def disconnect(self):
        if self.socket:
            self.socket.close()
            self.socket = None
            print(f"Disconnected from {self.ip}")

    def send_command(self, command: str, expect_response: bool = False):
        if not self.socket:
            raise ConnectionError("Not connected to device.")
        print(f"[{self.ip}] >> {command}")
        self.socket.send((command + '\n').encode())
        if expect_response:
            time.sleep(0.1)
            response = self.socket.recv(1024).decode().strip()
            print(f"[{self.ip}] << {response}")
            return response
        return None

    def get_id(self):
        return self.send_command("*IDN?", expect_response=True)

    def set_voltage(self, channel: int, voltage: float):
        self.send_command(f"V{channel} {voltage:.3f}")

    def set_current(self, channel: int, current: float):
        self.send_command(f"I{channel} {current:.3f}")

    def output_on(self, channel: int):
        self.send_command(f"OP{channel} 1")

    def output_off(self, channel: int):
        self.send_command(f"OP{channel} 0")

    def read_voltage(self, channel: int):
        return self.send_command(f"V{channel}?", expect_response=True)

    def read_current(self, channel: int):
        return self.send_command(f"I{channel}?", expect_response=True)
