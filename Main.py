import tkinter as tk
from tkinter import messagebox
from cpx400dp import CPX400DP
from keithleyDMM6500 import DMM6500
from GUIinterface import GUI
from PSUcontrol import PSUControlPanel

def main():
    root = tk.Tk()

    # Create PSU instances (use actual IPs or mock)
    psuL = CPX400DP("192.168.0.103")
    psuR = CPX400DP("192.168.0.105")
    dmm_ip = "192.168.0.104"
    # ✅ Define the psus dictionary
    psus = {
        "PSU Left": psuL,
        "PSU Right": psuR
    }

    # ✅ Now pass it into the GUI
    app = GUI(root, psus, dmm_ip=dmm_ip)
    root.mainloop()

if __name__ == "__main__":
    main()
