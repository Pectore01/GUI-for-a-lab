import tkinter as tk
from cpx400dp import CPX400DP
from GUIinterface import GUI

def main():
    root = tk.Tk()

    # Create PSU instances (use actual IPs or mock)
    psuL = CPX400DP("192.168.0.105")
    psuR = CPX400DP("192.168.0.103")
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
