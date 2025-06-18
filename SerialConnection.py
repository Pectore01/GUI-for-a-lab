import os
import sys

from stk500.STK500_interface import STK500_interface
from stk500.SDF_read import SDF_read
from pathlib import Path


class SimpleSdfProvider(SDF_read):
    def __init__(self, communication=None, sdf_path=None):
        # Getting the location of this folder to find the example sdf included
        Main_folder = Path(__file__).parent.resolve()
        Resources_folder = Main_folder / 'Resources'
        #SDF_file = Resources_folder / 'bridge_v0.4.0.sdf'
        super(SimpleSdfProvider, self).__init__(communication, Resources_folder)

class ComplexSdfProvider(SDF_read):
    def __init__(self, communication=None, sdf_path=None):
        super(ComplexSdfProvider, self).__init__(communication, sdf_path)

    def get_sdf(self, file_path):
        # Optionally process or validate here
        print(f"Selected SDF file: {file_path}")
        return file_path

    def prepare_sdf(self):
        resources_folder = get_resources_path()
        if not resources_folder.exists():
            raise FileNotFoundError(f"Resources folder not found at {resources_folder}")

        matching_sdf = None
        for sdf_file in resources_folder.glob('*.sdf'):
            matching_sdf = sdf_file
            break

        if matching_sdf is None:
            raise FileNotFoundError("No matching .sdf file found in Resources folder.")

        self.sdf_path = self.get_sdf(matching_sdf)

        self.sdf_path = self.get_sdf(matching_sdf)

def get_resources_path():
    if hasattr(sys, '_MEIPASS'):
        # Running inside PyInstaller bundle
        base_path = Path(sys._MEIPASS)
    else:
        # Running in normal environment
        base_path = Path(__file__).parent.resolve()
    return base_path / 'Resources'


class Stk500Controller:
    def __init__(self, com_port, sdf_provider_class):
        self.interface = STK500_interface(SDF_class=sdf_provider_class, com=com_port)
        self.interface.initialize_connection()

    def print_device_info(self, log=print):
        log(f'Attached SN: {self.interface.read_sn()}')
        log(f'HW version: {self.interface.read_hardware_version()}')
        log(f'SW version: {self.interface.read_software_version()}')
        log(f'Factory settings: {self.interface.read_factory_settings()}')

    def manual_mode(self, value):
        return self.interface.write_value(["o_control_state"], [value])

    def activate_heater(self, value):
        return self.interface.write_value(["ElecHeater_manual_request"], [value])   

    def activate_DHW_pump(self, value):
        return self.interface.write_value(["Pump_dhw_manual_request"], [value])

    def activate_CH_pump(self, value):
        return self.interface.write_value(["Pump_water_manual_request"], [value])
        
    def activate_AUX_pump(self, value):
        return self.interface.write_value(["Pump_floor_manual_request"], [value])

#print(f'{stk500_interface.write_table(table = "V", values = [63])}')

#stk500_interface.close()