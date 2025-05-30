import serial
import threading

class STM32:
    def __init__(self, port="COM3", baudrate=115200, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.read_thread = None
        self.keep_reading = False
        self.callback = None  # Function to call with received data

    def connect(self):
        self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        self.keep_reading = True
        self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.read_thread.start()

    def disconnect(self):
        self.keep_reading = False
        if self.serial and self.serial.is_open:
            self.serial.close()

    def send(self, data: str):
        if self.serial and self.serial.is_open:
            self.serial.write(data.encode('utf-8'))

    def _read_loop(self):
        while self.keep_reading and self.serial and self.serial.is_open:
            try:
                line = self.serial.readline().decode('utf-8').strip()
                if line and self.callback:
                    self.callback(line)
            except Exception as e:
                print(f"Serial read error: {e}")