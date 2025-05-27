import tkinter as tk
from tkinter import messagebox
from cpx400dp import CPX400DP
from keithleyDMM6500 import DMM6500

class GUI:
    def __init__(self, root, psus: dict, dmm_ip: str = None):
        self.root = root
        self.psus = psus  # Dictionary of PSUs, e.g., {"PSU 1": psu1, "PSU 2": psu2}
        self.psu = None
        self.root.title("Service tools for PCBA") 
        self.root.resizable(True, True)

        self.status_var = tk.StringVar()
        self.status_var.set("Select a power supply.")

        self.dmm_measure_mode = tk.StringVar(value="Voltage")


        self.build_gui()
        self.update_live_readings()
        self.switch_psu()  # Initialize selection

        if dmm_ip:
            try:
                self.dmm = DMM6500(dmm_ip)
                self.update_dmm_readings()
            except Exception as e:
                self.status_var.set(f"Failed to connect to DMM: {e}")

    def build_gui(self):
        self.selected_psu_name = tk.StringVar()
        self.selected_psu_name.set(next(iter(self.psus)))  # Default selection
        self.selected_psu_name.trace("w", self.switch_psu)

        tk.Label(self.root, text="Select PSU:").grid(row=0, column=1, sticky="snew", padx=5, pady=5)
        tk.Label(self.root, text="Channel").grid(row=1, column=0, padx=5, pady=5)
        tk.Label(self.root, text="Voltage (V)").grid(row=1, column=1, padx=5, pady=5)
        tk.Label(self.root, text="Current (A)").grid(row=1, column=2, padx=5, pady=5)

        self.live_voltage_labels = {}
        self.live_current_labels = {}

        for ch in [1, 2]:
            self.live_voltage_labels[ch] = tk.Label(self.root, text="0.00 V", fg="blue")
            self.live_current_labels[ch] = tk.Label(self.root, text="0.00 A", fg="blue")
            self.live_voltage_labels[ch].grid(row=ch + 1, column=3, sticky="snew", padx=5, pady=5)
            self.live_current_labels[ch].grid(row=ch + 1, column=4, sticky="snew", padx=5, pady=5)

        tk.Label(self.root, text="Live Voltage").grid(row=1, column=3, padx=5, pady=5)
        tk.Label(self.root, text="Live Current").grid(row=1, column=4, padx=5, pady=5)

        self.voltage_entries = {}
        self.current_entries = {}

        for ch in [1, 2]:
            tk.Label(self.root, text=f"CH{ch}").grid(row=ch+1, column=0, padx=5, pady=5)
            self.voltage_entries[ch] = tk.Entry(self.root)
            self.current_entries[ch] = tk.Entry(self.root)
            self.voltage_entries[ch].grid(row=ch+1, column=1, sticky="snew", padx=5, pady=5)
            self.current_entries[ch].grid(row=ch+1, column=2, sticky="snew", padx=5, pady=5)

        self.output_buttons = {}
        for ch in [1]:
            btn = tk.Button(self.root, text=f"Turn CH{ch} ON", command=lambda ch=ch: self.toggle_output(ch))
            btn.grid(row=5, column=-1 + ch, columnspan=2, pady=5, padx=5, sticky="snew")
            btn.config(state="disabled")
            self.output_buttons[ch] = btn

        for ch in [2]:
            btn = tk.Button(self.root, text=f"Turn CH{ch} ON", command=lambda ch=ch: self.toggle_output(ch))
            btn.grid(row=5, column=0 + ch, columnspan=2, pady=5, padx=5, sticky="snew")
            btn.config(state="disabled")
            self.output_buttons[ch] = btn

        tk.OptionMenu(self.root, self.selected_psu_name, *self.psus.keys()).grid(row=0, column=2, sticky="snew", padx=5, pady=5)
        tk.Button(self.root, text="Apply Settings", command=self.apply_settings).grid(row=4, column=2, columnspan=2, sticky="snew", padx=5, pady=5)
        tk.Button(self.root, text="Read Values", command=self.read_values).grid(row=4, column=0, columnspan=2, sticky="snew", padx=5, pady=5)

        tk.Button(self.root, text="Connect", command=self.connect, fg="green").grid(row=6, column=0, columnspan=2, sticky="snew", padx=5, pady=5)
        tk.Button(self.root, text="Disconnect", command=self.disconnect, fg="red").grid(row=6, column=2, columnspan=2, sticky="snew", padx=5, pady=5)

        tk.Label(self.root, textvariable=self.status_var).grid(row=7, column=0, columnspan=4, sticky="ew", padx=5, pady=5)

        tk.Label(self.root, text="Keithley DMM6500 Readings", font=("Arial", 10, "bold")).grid(row=8, column=0, columnspan=4, pady=(10, 0), sticky="snew", padx=5)

        tk.Label(self.root, text="Measure:").grid(row=9, column=0, sticky="snew", padx=5, pady=5)
        measure_options = ["Voltage", "Resistance", "Continuity"]  # Add "Current" if supported
        tk.OptionMenu(self.root, self.dmm_measure_mode, *measure_options).grid(row=9, column=1, sticky="snew", padx=5, pady=5)

        self.dmm_measurement_var = tk.StringVar(value="--")
        self.dmm_measurement_label = tk.Label(self.root, textvariable=self.dmm_measurement_var, font=("Arial", 12))
        self.dmm_measurement_label.grid(row=10, column=0, columnspan=2, pady=(5, 0), sticky="snew", padx=5)

        # Allow column expansion
        for i in range(5):  # Adjust based on the number of columns used
            self.root.columnconfigure(i, weight=1)

        # Allow row expansion
        for i in range(12):  # Adjust as needed
            self.root.rowconfigure(i, weight=1)


    def connect(self):
        try:
            self.psu.connect()
            self.status_var.set("Connected")
            for btn in self.output_buttons.values():
                btn.config(state="normal")  # Enable buttons
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {e}")

    def disconnect(self):
        try:
            self.psu.disconnect()
            self.status_var.set("Disconnected")
            for btn in self.output_buttons.values():
                btn.config(state="disabled")  # Disable buttons again
        except Exception as e:
            messagebox.showerror("Error", f"Failed to disconnect: {e}")  

    def toggle_output(self, channel: int):
        btn = self.output_buttons[channel]
        if "ON" in btn["text"]:
            self.psu.output_on(channel)
            btn["text"] = f"Turn CH{channel} OFF"
        else:
            self.psu.output_off(channel)
            btn["text"] = f"Turn CH{channel} ON"

    def apply_settings(self):
        try:
            for ch in [1, 2]:
                voltage = float(self.voltage_entries[ch].get())
                current = float(self.current_entries[ch].get())
                self.psu.set_voltage(ch, voltage)
                self.psu.set_current(ch, current)
        except Exception as e:
            messagebox.showerror("Input Error", str(e))

    def read_values(self):
        try:
            values = []
            for ch in [1, 2]:
                v = self.psu.read_voltage(ch)
                i = self.psu.read_current(ch)
                values.append(f"CH{ch}: {v} V / {i} A")
            messagebox.showinfo("Read Values", "\n".join(values))
        except Exception as e:
            messagebox.showerror("Read Error", str(e))

    def switch_psu(self, *args):
        selected_name = self.selected_psu_name.get()
        self.psu = self.psus[selected_name]
        self.status_var.set(f"Selected {self.psu.name}")
        self.root.title(f"Power Supply Control - {self.psu.name}")

    def update_live_readings(self):
        if self.psu is not None:
            try:
                for ch in [1, 2]:
                    voltage = self.psu.read_voltage(ch)
                    current = self.psu.read_current(ch)
                    self.live_voltage_labels[ch].config(text=f"{voltage:} V")
                    self.live_current_labels[ch].config(text=f"{current:} A")
            except Exception as e:
                # Show error only once or log it, otherwise it will spam the GUI.
                self.status_var.set(f"Error reading PSU: {e}")

        # Schedule next update
        self.root.after(5000, self.update_live_readings)  # Update every 5 seconds
    
    def update_dmm_readings(self):
        if self.dmm:
            try:
                mode = self.dmm_measure_mode.get()
                self.dmm_measurement_label.config(fg="black")
                if mode == "Voltage":
                    val = self.dmm.read_voltage()
                    self.dmm_measurement_var.set(f"{val:.5f} V")
#                elif mode == "Current":                                            #remove comments to active current reading
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
                self.status_var.set(f"DMM Error: {e}")
        self.root.after(1000, self.update_dmm_readings)