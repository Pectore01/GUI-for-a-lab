import tkinter as tk
from tkinter import messagebox
from cpx400dp import CPX400DP

psuL = CPX400DP("192.168.0.103")
psuR = CPX400DP("192.168.0.105")

class PowerSupplyGUI:
    def __init__(self, root, psus: dict):
        self.root = root
        self.psus = psus  # Dictionary of PSUs, e.g., {"PSU 1": psu1, "PSU 2": psu2}
        self.psu = None
        self.root.title("Power Supply Control")

        self.selected_psu_name = tk.StringVar()
        self.selected_psu_name.set(next(iter(psus)))  # Default to first PSU
        self.selected_psu_name.trace("w", self.switch_psu)

        self.status_var = tk.StringVar()
        self.status_var.set("Select a power supply.")

        self.build_gui()
        self.switch_psu()  # Initialize selection

    def build_gui(self):

        tk.Label(self.root, text="Select PSU:").grid(row=0, column=1)
        tk.Label(self.root, text="Channel").grid(row=0, column=2)
        tk.Label(self.root, text="Voltage (V)").grid(row=1, column=1)
        tk.Label(self.root, text="Current (A)").grid(row=1, column=2)

        self.voltage_entries = {}
        self.current_entries = {}
        for ch in [1, 2]:
            tk.Label(self.root, text=f"CH{ch}").grid(row=ch+1, column=0)
            self.voltage_entries[ch] = tk.Entry(self.root)
            self.current_entries[ch] = tk.Entry(self.root)
            self.voltage_entries[ch].grid(row=ch+1, column=1)
            self.current_entries[ch].grid(row=ch+1, column=2)

        self.output_buttons = {}
        for ch in [1]:
         btn = tk.Button(self.root, text=f"Turn CH{ch} ON", command=lambda ch=ch: self.toggle_output(ch))
         btn.grid(row=5, column=-1 + ch, columnspan=2, pady=5)
         self.output_buttons[ch] = btn

        for ch in [2]:
         btn = tk.Button(self.root, text=f"Turn CH{ch} ON", command=lambda ch=ch: self.toggle_output(ch))
         btn.grid(row=5, column=0 + ch, columnspan=2, pady=5)
         self.output_buttons[ch] = btn

        tk.OptionMenu(self.root, self.selected_psu_name, *self.psus.keys()).grid(row=0, column=1, columnspan=2)
        tk.Button(self.root, text="Apply Settings", command=self.apply_settings).grid(row=4, column=2, columnspan=2)
        tk.Button(self.root, text="Read Values", command=self.read_values).grid(row=4, column=0, columnspan=2)

        tk.Button(self.root, text="Connect", command=self.connect).grid(row=6, column=0, columnspan=2)
        tk.Button(self.root, text="Disconnect", command=self.disconnect).grid(row=6, column=2, columnspan=2)

        tk.Label(self.root, textvariable=self.status_var).grid(row=7, column=0, columnspan=3)

    def connect(self):
        try:
            self.psu.connect()
            self.status_var.set("Connected")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {e}")

    def disconnect(self):
        try:
            self.psu.disconnect()
            self.status_var.set("Disconnected")
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


def main():
    root = tk.Tk()

    # Create PSU instances (use actual IPs or mock)
    psuL = CPX400DP("192.168.0.103")
    psuR = CPX400DP("192.168.0.105")

    # ✅ Define the psus dictionary
    psus = {
        "PSU Left": psuL,
        "PSU Right": psuR
    }

    # ✅ Now pass it into the GUI
    app = PowerSupplyGUI(root, psus)
    root.mainloop()

if __name__ == "__main__":
    main()
