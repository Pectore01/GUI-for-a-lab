import socket

class ChromaLoad:
    def __init__(self, ip, port=5000):
        self.ip = ip
        self.port = port

    def send_command(self, command, expect_response=True):
        full_command = command + '\n'  # Add newline as per protocol
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip, self.port))
            s.sendall(full_command.encode())
            if expect_response:
                return s.recv(1024).decode().strip()
        return None

    def remote_on(self):
        return self.send_command("CONF:REM ON", expect_response=False)
    
    def remote_off(self):
        return self.send_command("CONF:REM OFF", expect_response=False)

    def select_channel(self, ch=3):
        self.send_command(f"CHAN {ch}", expect_response=False)

    def set_voltage_range_high(self):
        return self.send_command("CONF:VOLT:RANG H", expect_response=False)

    def set_run(self):
        return self.send_command("RUN", expect_response=False)
    
    def set_mode_cch(self):
        return self.send_command("MODE CCH", expect_response=False)

    def set_static_current(self, current):
        self.send_command(f"CURR:STAT:L1 {current}", expect_response=False)
        self.send_command(f"CURR:STAT:L2 {current}", expect_response=False)

    def set_slew_rate(self, rise, fall):
        self.send_command(f"CURR:STAT:RISE {rise}", expect_response=False)
        self.send_command(f"CURR:STAT:FALL {fall}", expect_response=False)

    def load_on(self):
        return self.send_command("LOAD:STATe ON", expect_response=False)
        
    def load_off(self):
        return self.send_command("LOAD:STATe OFF", expect_response=False)

    def measure_voltage(self):
        return self.send_command("MEAS:VOLT?", expect_response=True)

    def measure_current(self):
        return self.send_command("MEAS:CURR?", expect_response=True)
    
    def check_load_status(self):
        response = self.send_command("LOAD:STATe?", expect_response=True)
        return response.strip() in ["1"]