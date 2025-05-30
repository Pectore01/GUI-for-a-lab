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

    def connect_stm32(self):
        port = self.com_port_var.get()
        try:
            self.serial_port = serial.Serial(port, baudrate=115200, timeout=1)
            self.serial_running = True
            self.serial_status_var.set(f"STM32: Connected on {port}")
            self.serial_thread = threading.Thread(target=self.read_from_serial, daemon=True)
            self.serial_thread.start()
        except Exception as e:
            self.serial_status_var.set(f"STM32: Failed to connect ({e})")

    def disconnect_stm32(self):
        self.serial_running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.serial_status_var.set("STM32: Disconnected")

    def reset_stm32(self):
        self.send_serial_command("RESET")

    def ping_stm32(self):
        self.send_serial_command("PING")

    def send_serial_command(self, command: str):
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.write((command + "\n").encode())
                self.serial_status_var.set(f"Sent: {command}")
            except Exception as e:
                self.serial_status_var.set(f"Failed to send command: {e}")
        else:
            self.serial_status_var.set("STM32 not connected")

    def read_from_serial(self):
        while self.serial_running:
            try:
                if self.serial_port.in_waiting > 0:
                    line = self.serial_port.readline().decode(errors="ignore").strip()
                    if line:
                        self.root.after(0, self.log_serial_output, f"[STM32] {line}")
            except Exception as e:
                self.root.after(0, self.log_serial_output, f"[Serial Error] {e}")
                break

    def log_serial_output(self, msg):
        self.serial_output.config(state="normal")
        self.serial_output.insert("end", msg + "\n")
        self.serial_output.see("end")
        self.serial_output.config(state="disabled")