import tkinter as tk
from tkinter import messagebox
from keithleyDMM6500 import DMM6500
from PSUcontrol import PSUControlPanel
from chroma_load import ChromaLoad
from SerialConnection import Stk500Controller,  ComplexSdfProvider
import threading

MODES = ["CCL", "CCH", "CCDL", "CCDH", "CRL", "CRH", "CV"]

class GUI:
    def __init__(self, root, psus: dict, dmm_ip: str = None):
        self.root = root
        self.psus = psus  # {"PSU 1": CPX400DP, "PSU 2": CPX400DP}
        self.chroma = ChromaLoad(ip="192.168.0.10", port=5000)
        self.stk500 = None

        self.root.title("Service tools for PCBA")
        self.root.resizable(True, True)

        self.build_psu_panels()   
        self.build_dmm_section(dmm_ip)
        self.build_chroma_section()
        self.build_stk500_section()
     
        self.update_live_readings()
        self.monitor_load()

    def build_psu_panels(self):
        self.psu_panels = []
        for i, (name, psu) in enumerate(self.psus.items()):
            panel = PSUControlPanel(self.root, psu)
            panel.frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            self.psu_panels.append(panel)

        for i in range(len(self.psus)):
            self.root.columnconfigure(i, weight=1)
        self.root.rowconfigure(0, weight=1)


    def build_dmm_section(self, dmm_ip):
        # DMM controls under PSU panels
        self.dmm = None
        self.dmm_measure_mode = tk.StringVar(value="Voltage")
        self.dmm_measurement_var = tk.StringVar(value="--")

        dmm_frame = tk.Frame(self.root)
        dmm_frame.grid(row=1, column=0, columnspan= 1, padx=10, pady=10, sticky="nsew")

        if dmm_ip:
            try:
                self.dmm = DMM6500(dmm_ip)
                row = 1
                tk.Label(dmm_frame, text="Keithley DMM6500 Readings", font=("Arial", 10, "bold")).grid(row=row, column=0, pady=(10, 0), sticky="ns", padx=5)
                row += 2
                tk.Label(dmm_frame, text="Measure:").grid(row=row, column=0, sticky="ns", padx=5, pady=5)
                measure_options = ["Voltage", "Resistance", "Continuity"]  # Add Current if supported
                tk.OptionMenu(dmm_frame, self.dmm_measure_mode, *measure_options).grid(row=row, column=1, sticky="nsew", padx=5, pady=5)
                row += 1
                self.dmm_measurement_label = tk.Label(dmm_frame, textvariable=self.dmm_measurement_var, font=("Arial", 12))
                self.dmm_measurement_label.grid(row=row, column=0, pady=(5, 0), sticky="ns", padx=5)
                self.root.after(1000, self.update_dmm_readings)
            except Exception as e:
                messagebox.showerror("DMM Connection Error", f"Failed to connect to DMM: {e}")


        # Configure columns and rows for DMM

    def update_live_readings(self):
        for panel in self.psu_panels:
            panel.update_live_readings()
        self.root.after(500, self.update_live_readings)  # update every 2 seconds

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
            self.root.after(500, self.update_dmm_readings)

    def build_chroma_section(self, ip="192.168.0.10", port=5000):
        self.chroma = ChromaLoad(ip, port)
        chroma_frame = tk.LabelFrame(self.root, text="Chroma Load Control")
        chroma_frame.grid(row=0, rowspan= 2, column=2, columnspan=2, padx=10, pady=10, sticky="nsew")
        row = 0
        def btn(text, cmd):
            nonlocal row
            b = tk.Button(chroma_frame, text=text, width=30, command=cmd)
            b.grid(row=row, column=0, pady=2, sticky="ew")
            row += 1

        btn("Pump", self.initialize_load_pumps)
        btn("Heater", self.initialize_load_heater)
        btn("Measure Voltage", self.measure_voltage)
        btn("Measure Current", self.measure_current)
        btn("Turn load off", self.load_off)
        btn("Disable Remote Mode", self.remote_off)
        
        self.output = tk.Text(chroma_frame, height=10, width=50, state='disabled')
        self.output.grid(row=row, column=0, pady=5, sticky="nsew")
        chroma_frame.columnconfigure(0, weight=1)

    def log(self, text):
        self.output.configure(state='normal')
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.output.configure(state='disabled')
    
    def remote_off(self):
        self.chroma.load_off()
        self.log("Load turned OFF")        
        self.chroma.remote_off()
        self.log("Remote mode disabled")

    def load_off(self):
        self.chroma.load_off()
        self.log("Load turned OFF")

    def measure_voltage(self):
        val = self.chroma.measure_voltage()
        self.log(f"Measured Voltage: {val} V")

    def measure_current(self):
        val = self.chroma.measure_current()
        self.log(f"Measured Current: {val} A")

    def initialize_load_pumps(self):
        def task():
            try:             
                self.log("Initializing Chroma Load...")
                self.chroma.remote_on()
                self.log("Remote mode enabled.")
                self.chroma.select_channel(3)
                self.log("Channel 3 selected.")
                self.chroma.set_mode_cch()
                self.log("Mode set to CCH.")
                self.chroma.set_static_current(1)
                self.log("Static current set to 1 A.")
                self.chroma.set_slew_rate("0.5", "0.5")
                self.log("Slew rate rise/fall set to 0.5 A/µS.")
                self.chroma.load_on()
                self.log("Load turned ON.")
            except Exception as e:
                self.log(f"Failed to initialize: {e}")
        threading.Thread(target=task).start()

    def initialize_load_heater(self):
        def task():
            try:             
                self.log("Initializing Chroma Load...")
                self.chroma.remote_on()
                self.log("Remote mode enabled.")
                self.chroma.select_channel(3)
                self.log("Channel 3 selected.")
                self.chroma.set_mode_cch()
                self.log("Mode set to CCH.")
                self.chroma.set_static_current(10)
                self.log("Static current set to 10 A.")
                self.chroma.set_slew_rate("1.5", "1.5")
                self.log("Slew rate rise/fall set to 1.5 A/µS.")
                self.chroma.load_on()
                self.log("Load turned ON.")
            except Exception as e:
                self.log(f"Failed to initialize: {e}")
        threading.Thread(target=task).start()

    def monitor_load(self):
        if self.chroma.check_load_status():
            state = self.chroma.check_load_status()
            self.log(f"state of load:{state}")
            self.measure_voltage()
            self.measure_current()

        # Schedule the next check after 1000 ms (1 second)
        self.root.after(1000, self.monitor_load)

    def build_stk500_section(self):
        self.stk500 = None  # Initialize with None until connected

        stk_frame = tk.LabelFrame(self.root, text="STK500 Interface")
        stk_frame.grid(row=2, column=1, columnspan=3, padx=10, pady=10, sticky="nsew")
        row = 0

        # BooleanVars
        self.manual_mode_var = tk.BooleanVar()
        self.heater_var = tk.BooleanVar()
        self.dhw_pump_var = tk.BooleanVar()
        self.ch_pump_var = tk.BooleanVar()
        self.aux_pump_var = tk.BooleanVar()

        # Connect STK500 Button
        connect_btn = tk.Button(stk_frame, text="Connect STK500", width=30, command=self.connect_stk500)
        connect_btn.grid(row=row, column=0, columnspan=2, pady=5)
        self.disconnect_btn = tk.Button(stk_frame, text="Disconnect STK500", width=30, command=self.disconnect_stk500, state="disabled")
        self.disconnect_btn.grid(row=row, column=1, columnspan=2, pady=5)
        row += 1

        # Toggle buttons (disabled by default)
        def create_toggle(label, var_name, command_name):
            nonlocal row
            cb = tk.Checkbutton(
                stk_frame, text=label,
                variable=var_name,
                onvalue=True, offvalue=False,
                state="disabled",
                command=lambda: getattr(self.stk500, command_name)(int(var_name.get()))
            )
            cb.grid(row=row, column=0, sticky="w", padx=5, pady=2)
            row += 1
            return cb

        self.manual_mode_cb = create_toggle("Manual Mode", self.manual_mode_var, "manual_mode")
        self.heater_cb = create_toggle("Heater", self.heater_var, "activate_heater")
        self.dhw_pump_cb = create_toggle("DHW Pump", self.dhw_pump_var, "activate_DHW_pump")
        self.ch_pump_cb = create_toggle("CH Pump", self.ch_pump_var, "activate_CH_pump")
        self.aux_pump_cb = create_toggle("AUX Pump", self.aux_pump_var, "activate_AUX_pump")

        # Device info button (disabled initially)
        self.read_info_btn = tk.Button(
            stk_frame, text="Read Device Info", width=30,
            command=lambda: self.stk500.print_device_info(self.stk_log),
            state="disabled"
        )
        self.read_info_btn.grid(row=row, column=0, pady=5)
        row += 1

        # Output log box
        self.stk_output = tk.Text(stk_frame, height=10, width=60, state='disabled')
        self.stk_output.grid(row=row, column=0, columnspan= 2, pady=5, sticky="nsew")
        stk_frame.columnconfigure(0, weight=1)

    def stk_log(self, text):
        self.stk_output.configure(state='normal')
        self.stk_output.insert(tk.END, text + "\n")
        self.stk_output.see(tk.END)
        self.stk_output.configure(state='disabled')

    def connect_stk500(self):
        try:
            self.stk500 = Stk500Controller(com_port="COM9", sdf_provider_class=ComplexSdfProvider)
            self.stk_log("STK500 connected successfully.")
            self.enable_stk_controls()
            self.disconnect_btn.config(state="normal")  # <-- Enable the disconnect button
        except Exception as e:
            messagebox.showerror("STK500 Connection Error", f"Failed to connect: {e}")
    
    def enable_stk_controls(self):
        self.manual_mode_cb.config(state="normal")
        self.heater_cb.config(state="normal")
        self.dhw_pump_cb.config(state="normal")
        self.ch_pump_cb.config(state="normal")
        self.aux_pump_cb.config(state="normal")
        self.read_info_btn.config(state="normal")

    def disconnect_stk500(self):
        if self.stk500 and hasattr(self.stk500.interface, "communication"):
            try:
                self.stk500.interface.communication.stop = True
                self.stk_log("STK500 disconnected.")
            except Exception as e:
                self.stk_log(f"Error disconnecting STK500: {e}")
        else:
            self.stk_log("STK500 was not connected.")

        # Disable controls
        for cb in [self.manual_mode_cb, self.heater_cb, self.dhw_pump_cb, self.ch_pump_cb, self.aux_pump_cb]:
            cb.config(state="disabled")
        self.read_info_btn.config(state="disabled")