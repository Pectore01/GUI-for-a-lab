from abc import ABC, abstractmethod

class PowerSupplyInterface(ABC):
    @abstractmethod
    def connect(self): pass

    @abstractmethod
    def disconnect(self): pass

    @abstractmethod
    def get_id(self): pass

    @abstractmethod
    def set_voltage(self, channel: int, voltage: float): pass

    @abstractmethod
    def set_current(self, channel: int, current: float): pass

    @abstractmethod
    def output_on(self, channel: int): pass

    @abstractmethod
    def output_off(self, cahnnel: int): pass

    @abstractmethod
    def read_voltage(self, channel: int): pass

    @abstractmethod
    def read_current(self, channel: int): pass