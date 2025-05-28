import tkinter as tk
from tkinter import messagebox
from cpx400dp import CPX400DP

class PSUControlPanel:
    def __init__(self, parent, psu: CPX400DP):
        self.psu = psu
        self.frame = tk.LabelFrame(parent, text=psu.name, padx=10, pady=10)

        self.status_var = tk.StringVar(value="Disconnected")

        self.live_voltage_labels = {}
        self.live_current_labels = {}

        self.voltage_entries = {}
        self.current_entries = {}
        self.output_buttons = {}

        # Headers
        tk.Label(self.frame, text="Channel").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(self.frame, text="Voltage (V)").grid(row=0, column=1, padx=5, pady=5)
        tk.Label(self.frame, text="Current (A)").grid(row=0, column=2, padx=5, pady=5)
        tk.Label(self.frame, text="Live Voltage").grid(row=0, column=3, padx=5, pady=5)
        tk.Label(self.frame, text="Live Current").grid(row=0, column=4, padx=5, pady=5)

        for ch in [1]:
            tk.Label(self.frame, text=f"CH{ch}").grid(row=ch, column=0, padx=5, pady=5)

            ve = tk.Entry(self.frame, width=8)
            ve.grid(row=ch, column=1, padx=5, pady=5)
            self.voltage_entries[ch] = ve

            ce = tk.Entry(self.frame, width=8)
            ce.grid(row=ch, column=2, padx=5, pady=5)
            self.current_entries[ch] = ce

            lv = tk.Label(self.frame, text="0.00 V", fg="blue")
            lv.grid(row=ch, column=3, padx=5, pady=5)
            self.live_voltage_labels[ch] = lv

            lc = tk.Label(self.frame, text="0.00 A", fg="blue")
            lc.grid(row=ch, column=4, padx=5, pady=5)
            self.live_current_labels[ch] = lc

            btn = tk.Button(self.frame, text=f"Turn CH{ch} ON", state="disabled", command=lambda c=ch: self.toggle_output(c))
            btn.grid(row=ch+3, column=0, columnspan=2, pady=5, padx=5, sticky="snew")
            self.output_buttons[ch] = btn

        for ch in [2]:
            tk.Label(self.frame, text=f"CH{ch}").grid(row=ch, column=0, padx=5, pady=5)

            ve = tk.Entry(self.frame, width=8)
            ve.grid(row=ch, column=1, padx=5, pady=5)
            self.voltage_entries[ch] = ve

            ce = tk.Entry(self.frame, width=8)
            ce.grid(row=ch, column=2, padx=5, pady=5)
            self.current_entries[ch] = ce

            lv = tk.Label(self.frame, text="0.00 V", fg="blue")
            lv.grid(row=ch, column=3, padx=5, pady=5)
            self.live_voltage_labels[ch] = lv

            lc = tk.Label(self.frame, text="0.00 A", fg="blue")
            lc.grid(row=ch, column=4, padx=5, pady=5)
            self.live_current_labels[ch] = lc

            btn = tk.Button(self.frame, text=f"Turn CH{ch} ON", state="disabled", command=lambda c=ch: self.toggle_output(c))
            btn.grid(row=ch+2, column=2, columnspan=2, pady=5, padx=5, sticky="snew")
            self.output_buttons[ch] = btn

        tk.Button(self.frame, text="Apply Settings", command=self.apply_settings).grid(row=5, column=2, columnspan=2, sticky="snew", padx=5, pady=5)
        tk.Button(self.frame, text="Read Values", command=self.read_values).grid(row=5, column=0, columnspan=2, sticky="snew", padx=5, pady=5)

        tk.Button(self.frame, text="Connect", command=self.connect, fg="green").grid(row=6, column=0, columnspan=2, sticky="snew", padx=5, pady=5)
        tk.Button(self.frame, text="Disconnect", command=self.disconnect, fg="red").grid(row=6, column=2, columnspan=2, sticky="snew", padx=5, pady=5)

        tk.Label(self.frame, textvariable=self.status_var).grid(row=7, column=0, columnspan=5, sticky="snew", padx=5, pady=5)

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