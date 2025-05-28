import tkinter as tk
from tkinter import messagebox
from cpx400dp import CPX400DP
from keithleyDMM6500 import DMM6500
from PSUcontrol import PSUControlPanel

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

    def build_dmm_section(self):
        # DMM controls under PSU panels
        row = 1
        tk.Label(self.root, text="Keithley DMM6500 Readings", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, pady=(10, 0), sticky="ew", padx=5)
        row += 2
        tk.Label(self.root, text="Measure:").grid(row=row, column=0, sticky="nsew", padx=5, pady=5)
        measure_options = ["Voltage", "Resistance", "Continuity"]  # Add Current if supported
        tk.OptionMenu(self.root, self.dmm_measure_mode, *measure_options).grid(row=row, column=1, sticky="nsew", padx=5, pady=5)
        row += 1
        self.dmm_measurement_label = tk.Label(self.root, textvariable=self.dmm_measurement_var, font=("Arial", 12))
        self.dmm_measurement_label.grid(row=row, column=0, columnspan=2, pady=(5, 0), sticky="nsew", padx=5)

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