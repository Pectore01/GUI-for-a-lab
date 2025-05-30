import serial
import threading
import serial.tools.list_ports

class STM32:
    def __init__(self):
        self.serial = None
        self.read_callback = None

    def connect(self, port, baudrate=9600, timeout=1):
        import serial
        self.serial = serial.Serial(port, baudrate, timeout=timeout)

    def disconnect(self):
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.serial = None

    def write(self, data: str):
        if self.serial and self.serial.is_open:
            self.serial.write((data + '\n').encode('utf-8'))

    def read(self):
        if self.serial and self.serial.is_open:
            return self.serial.readline().decode('utf-8').strip()
        return ""

    def set_read_callback(self, callback):
        self.read_callback = callback

    def start_reading(self):
        import threading
        def loop():
            while self.serial and self.serial.is_open:
                try:
                    line = self.serial.readline().decode('utf-8').strip()
                    if line and self.read_callback:
                        self.read_callback(line)
                except:
                    break
        threading.Thread(target=loop, daemon=True).start()

    def get_line(self):
        if self.serial and self.serial.in_waiting > 0:
            line = self.serial.readline().decode('utf-8').strip()
            return line
        return None

    @staticmethod
    def list_available_ports():
        import serial.tools.list_ports
        return [port.device for port in serial.tools.list_ports.comports()]