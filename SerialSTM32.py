import serial
import serial.tools.list_ports
import threading
import queue

class STM32:
    def __init__(self):
        self.serial = None
        self.rx_queue = queue.Queue()
        self.rx_thread = None
        self.running = False

    def connect(self, port, baudrate=9600, timeout=0.1):
        self.serial = serial.Serial(port, baudrate, timeout=timeout)
        self.running = True
        self.rx_thread = threading.Thread(target=self._read_serial, daemon=True)
        self.rx_thread.start()

    def disconnect(self):
        self.running = False
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.serial = None

    def write(self, data):
        if self.serial and self.serial.is_open:
            if not isinstance(data, bytes):
                data = data.encode('utf-8')
            self.serial.write(data)

    def get_line(self):
        try:
            return self.rx_queue.get_nowait()
        except queue.Empty:
            return None

    def _read_serial(self):
        while self.running and self.serial and self.serial.is_open:
            try:
                line = self.serial.readline()
                if line:
                    decoded = line.decode(errors='replace').strip()
                    self.rx_queue.put(decoded)
            except Exception:
                pass  # Optional: log errors here

    @staticmethod
    def list_available_ports():
        return [port.device for port in serial.tools.list_ports.comports()]