import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from keithleyDMM6500 import DMM6500
from PSUcontrol import PSUControlPanel
from SerialSTM32 import STM32
import serial

class GUI:
    def __init__(self, root, psus: dict, dmm_ip: str = None):
        self.root = root
        self.psus = psus  # {"PSU 1": CPX400DP, "PSU 2": CPX400DP}

        self.root.title("Service tools for PCBA")
        self.root.resizable(True, True)

        # Create PSU control panels side by side
        self.psu_panels = []
        for i, (name, psu) in enumerate(self.psus.items()):
            panel = PSUControlPanel(root, psu)
            panel.frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            self.psu_panels.append(panel)

        # Configure columns to expand
        for i in range(len(self.psus)):
            self.root.columnconfigure(i, weight=1)
        self.root.rowconfigure(0, weight=1)

        # DMM related setup
        self.dmm = None
        self.dmm_measure_mode = tk.StringVar(value="Voltage")
        self.dmm_measurement_var = tk.StringVar(value="--")

        if dmm_ip:
            try:
                self.dmm = DMM6500(dmm_ip)
                self.build_dmm_section()
            except Exception as e:
                messagebox.showerror("DMM Connection Error", f"Failed to connect to DMM: {e}")

        self.update_live_readings()
        if self.dmm:
            self.update_dmm_readings()

        # STM32-related setup
        self.stm32_serial = STM32()  # doesn't auto-select anymore

        # Serial port UI
        self.serial_frame = tk.LabelFrame(root, text="STM32 Serial")
        self.serial_frame.grid(row=6, column=0, padx=10, pady=10, sticky="nsew")

        tk.Label(self.serial_frame, text="Port:").grid(row=0, column=0, sticky="nsew")

        # Get list of available COM ports
        ports = [port.device for port in serial.tools.list_ports.comports()]
        if not ports:
            ports = ["No COM ports found"]

        # Dropdown menu for selecting port
        self.port_combo = ttk.Combobox(self.serial_frame, values=ports, state="readonly")
        self.port_combo.grid(row=0, column=1, padx=5, sticky="nsew")
        self.refresh_ports()
        # Select the first port by default if available
        if ports and ports[0] != "No COM ports found":
            self.port_combo.current(0)

        tk.Button(self.serial_frame, text="Refresh", command=self.refresh_ports).grid(row=0, column=2, padx=5, sticky="nsew")

        # Connect / Disconnect buttons
        tk.Button(self.serial_frame, text="Connect", command=self.connect_serial).grid(row=0, column=3, padx=5, sticky="nsew")
        tk.Button(self.serial_frame, text="Disconnect", command=self.disconnect_serial).grid(row=0, column=4, padx=5, sticky="nsew")

        # Serial output box
        self.serial_output = scrolledtext.ScrolledText(self.serial_frame, height=10, state='disabled')
        self.serial_output.grid(row=1, column=0, columnspan=4, pady=5, sticky="nsew")

        # Serial input box
        self.input_frame = tk.Frame(self.serial_frame)
        self.input_frame.grid(row=1, column=2, columnspan=4, pady=5, sticky="nsew")

        self.input_entry = tk.Entry(self.input_frame)
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_serial_command)
        self.send_button.pack(side="left")

        # Reset button
        self.reset_button = tk.Button(self.serial_frame, text="Reset STM32", command=self.reset_stm32)
        self.reset_button.grid(row=2, column=0, columnspan=4, pady=5, sticky="nsew")
        self.reset_button.config(state="disabled")  # Disable until connected

        # Poll for serial input
        self.root.after(100, self.poll_serial)


    def build_dmm_section(self):
        # DMM controls under PSU panels
        row = 1
        tk.Label(self.root, text="Keithley DMM6500 Readings", font=("Arial", 10, "bold")).grid(row=row, column=0, pady=(10, 0), sticky="ns", padx=5)
        row += 2
        tk.Label(self.root, text="Measure:").grid(row=row, column=0, sticky="ns", padx=5, pady=5)
        measure_options = ["Voltage", "Resistance", "Continuity"]  # Add Current if supported
        tk.OptionMenu(self.root, self.dmm_measure_mode, *measure_options).grid(row=row, column=1, sticky="nsew", padx=5, pady=5)
        row += 1
        self.dmm_measurement_label = tk.Label(self.root, textvariable=self.dmm_measurement_var, font=("Arial", 12))
        self.dmm_measurement_label.grid(row=row, column=0, pady=(5, 0), sticky="ns", padx=5)

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
        selected_port = self.port_combo.get()
        if selected_port and "COM" in selected_port:
            try:
                self.stm32_serial.connect(port=selected_port)
                self.serial_output_insert(f"Connected to {selected_port}\n")
                self.reset_button.config(state="normal")  # Enable reset button
            except Exception as e:
                self.serial_output_insert(f"Connection failed: {e}\n")
        else:
            self.serial_output_insert("No valid COM port selected.\n")

    def disconnect_serial(self):
        if self.stm32_serial:
            self.stm32_serial.disconnect()
            self.stm32_serial = None
            self.log_serial("Disconnected from serial port")
            self.reset_button.config(state="disabled")  # Disable reset button

    def poll_serial(self):
        if self.stm32_serial:
            line = self.stm32_serial.get_line()
            while line:
                self.log_serial(line)
                line = self.stm32_serial.get_line()
        self.root.after(100, self.poll_serial)

    def log_serial(self, text):
        self.serial_output.configure(state='normal')
        self.serial_output.insert(tk.END, text + "\n")
        self.serial_output.see(tk.END)
        self.serial_output.configure(state='disabled')

    def reset_stm32(self):
        if self.stm32_serial:
            self.stm32_serial.write("reset")
            self.log_serial("Sent reset command")
        else:
            messagebox.showwarning("Warning", "Serial port not connected.")

    def serial_output_insert(self, text):
        self.serial_output.configure(state='normal')
        self.serial_output.insert(tk.END, text)
        self.serial_output.configure(state='disabled')
        self.serial_output.see(tk.END)

    def refresh_ports(self):
        ports = STM32.list_available_ports()
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.set(ports[0])  # Auto-select first port
        else:
            self.port_combo.set("")
    
    def send_serial_command(self):
        cmd = self.input_entry.get()
        if cmd and self.stm32_serial and self.stm32_serial.serial and self.stm32_serial.serial.is_open:
            self.stm32_serial.write(cmd + "\n")  # add newline or format as needed
            self.input_entry.delete(0, tk.END)
        else:
            # Optionally show error if not connected
            print("Serial port not connected")