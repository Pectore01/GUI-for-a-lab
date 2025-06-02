import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from keithleyDMM6500 import DMM6500
from PSUcontrol import PSUControlPanel
from SerialSTM32 import STM32
import time

class GUI:
    def __init__(self, root, psus: dict, dmm_ip: str = None):
        self.root = root
        self.psus = psus  # {"PSU 1": CPX400DP, "PSU 2": CPX400DP}
        self.stm32_serial = STM32()

        self.root.title("Service tools for PCBA")
        self.root.resizable(True, True)

        self.build_psu_panels()   
        self.build_dmm_section(dmm_ip)
        self.build_serial_section()

        self.update_live_readings()
        self.root.after(100, self.poll_serial)

    def build_psu_panels(self):
        self.psu_panels = []
        for i, (name, psu) in enumerate(self.psus.items()):
            panel = PSUControlPanel(self.root, psu)
            panel.frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            self.psu_panels.append(panel)

        for i in range(len(self.psus)):
            self.root.columnconfigure(i, weight=1)
        self.root.rowconfigure(0, weight=1)

        # STM32-related setup
    def build_serial_section(self):
        self.serial_frame = tk.LabelFrame(self.root, text="STM32 Serial")
        self.serial_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        tk.Label(self.serial_frame, text="Port:").grid(row=0, column=0)
        self.port_combo = ttk.Combobox(self.serial_frame, values=STM32.list_available_ports(), state="readonly")
        self.port_combo.grid(row=0, column=1, padx=5)
        self.refresh_ports()

        tk.Button(self.serial_frame, text="Refresh", command=self.refresh_ports).grid(row=0, column=2)
        tk.Button(self.serial_frame, text="Connect", command=self.connect_serial).grid(row=0, column=3)
        tk.Button(self.serial_frame, text="Disconnect", command=self.disconnect_serial).grid(row=0, column=4)

        self.serial_output = scrolledtext.ScrolledText(self.serial_frame, height=10, state='disabled')
        self.serial_output.grid(row=1, column=0, columnspan=5, pady=5, sticky="nsew")

        input_frame = tk.Frame(self.serial_frame)
        input_frame.grid(row=2, column=0, columnspan=5, sticky="nsew")

        self.input_entry = tk.Entry(input_frame)
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        tk.Button(input_frame, text="Send", command=self.send_serial_command).pack(side="left")

        self.reset_active = False
        self.reset_button = tk.Button(self.serial_frame, text="Reset", command=self.toggle_reset)
        self.reset_button.grid(row=3, column=0, columnspan=5, pady=5, sticky="nsew")
        self.reset_button.config(state="disabled")

    def build_dmm_section(self, dmm_ip):
        # DMM controls under PSU panels
        self.dmm = None
        self.dmm_measure_mode = tk.StringVar(value="Voltage")
        self.dmm_measurement_var = tk.StringVar(value="--")

        if dmm_ip:
            try:
                self.dmm = DMM6500(dmm_ip)
                row = 1
                tk.Label(self.root, text="Keithley DMM6500 Readings", font=("Arial", 10, "bold")).grid(row=row, column=0, pady=(10, 0), sticky="ns", padx=5)
                row += 2
                tk.Label(self.root, text="Measure:").grid(row=row, column=0, sticky="ns", padx=5, pady=5)
                measure_options = ["Voltage", "Resistance", "Continuity"]  # Add Current if supported
                tk.OptionMenu(self.root, self.dmm_measure_mode, *measure_options).grid(row=row, column=1, sticky="nsew", padx=5, pady=5)
                row += 1
                self.dmm_measurement_label = tk.Label(self.root, textvariable=self.dmm_measurement_var, font=("Arial", 12))
                self.dmm_measurement_label.grid(row=row, column=0, pady=(5, 0), sticky="ns", padx=5)
                self.root.after(1000, self.update_dmm_readings)
            except Exception as e:
                messagebox.showerror("DMM Connection Error", f"Failed to connect to DMM: {e}")


        # Configure columns and rows for DMM
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        for i in range(row + 1):
            self.root.rowconfigure(i, weight=1)

    def update_live_readings(self):
        for panel in self.psu_panels:
            panel.update_live_readings()
        self.root.after(2000, self.update_live_readings)  # update every 2 seconds

    def update_dmm_readings(self):
        if self.dmm:        
            try:
                mode = self.dmm_measure_mode.get()
                self.dmm_measurement_label.config(fg="black")
                if mode == "Voltage":
                    val = self.dmm.read_voltage()
                    self.dmm_measurement_var.set(f"{val:.5f} V")
        #                elif mode == "Current":  # Uncomment if supported
        #                    val = self.dmm.read_current()
        #                    self.dmm_measurement_var.set(f"{val:.6f} A")
                elif mode == "Resistance":
                    val = self.dmm.read_resistance()
                    self.dmm_measurement_var.set(f"{val:.2f} Ω")
                elif mode == "Continuity":
                    val = self.dmm.read_continuity()
                    if val < 10:
                        self.dmm_measurement_var.set(f"Closed ({val:.2f} Ω)")
                        self.dmm_measurement_label.config(fg="green")
                    else:
                        self.dmm_measurement_var.set(f"Open ({val:.2f} Ω)")
                        self.dmm_measurement_label.config(fg="red")
            except Exception as e:
                # You could also log this instead of spamming the status bar
                print(f"DMM error: {e}")
            self.root.after(1000, self.update_dmm_readings)

    def connect_serial(self):
        port = self.port_combo.get()
        if "COM" in port:
            try:
                self.stm32_serial.connect(port=port)
                self.log_serial(f"Connected to {port}")
                self.reset_button.config(state="normal")
            except Exception as e:
                self.log_serial(f"Connection failed: {e}")
        else:
            self.log_serial("No valid COM port selected.")

    def disconnect_serial(self):
        self.stm32_serial.disconnect()
        self.log_serial("Disconnected")
        self.reset_button.config(state="disabled")

    def poll_serial(self):
        line = self.stm32_serial.get_line()
        while line:
            self.log_serial(line)
            line = self.stm32_serial.get_line()
        self.root.after(100, self.poll_serial)

    def log_serial(self, text):
        self.serial_output.configure(state='normal')
        self.serial_output.insert(tk.END, text + "\r\n")
        self.serial_output.see(tk.END)
        self.serial_output.configure(state='disabled')

    def toggle_reset(self):
        if not self.stm32_serial or not self.stm32_serial.serial or not self.stm32_serial.serial.is_open:
            self.log_serial("Not connected to STM32")
            return

        self.reset_active = not self.reset_active

        if self.reset_active:
            self.reset_button.config(text="Stop Auto Reset")
            self.log_serial("Auto reset started")
            self.log_serial("Sent reset")            
            self.perform_auto_reset()
        else:
            self.stm32_serial.serial.break_condition = False
            self.reset_button.config(text="Start Auto Reset")
            self.log_serial("Auto reset stopped")

    def perform_auto_reset(self):
        if self.reset_active and self.stm32_serial.serial and self.stm32_serial.serial.is_open:
            try:
                self.stm32_serial.serial.break_condition = True
            except Exception as e:
                self.log_serial(f"Auto reset failed: {e}")
        if self.reset_active:
            self.root.after(1, self.perform_auto_reset)

    def refresh_ports(self):
        ports = STM32.list_available_ports()
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.set(ports[0])
        else:
            self.port_combo.set("")
    
    def send_serial_command(self):
        cmd = self.input_entry.get()
        if cmd and self.stm32_serial.serial and self.stm32_serial.serial.is_open:
            self.stm32_serial.write(cmd + "\r\n")
            self.input_entry.delete(0, tk.END)
        else:
            self.log_serial("Not connected to STM32")
        print(f"Sending command: {cmd}")
        self.log_serial(f">>> {cmd}")