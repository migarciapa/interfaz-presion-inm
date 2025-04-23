# === [PRUEBA DE COMUNCACION CONTROLADOR TWISTORR 74FS AG] ===
# David Miguel Garcia Palacios
# Universidad Nacional de Colombia Sede Bogota

# --- LIBRERIAS ---
from PyQt6 import QtCore, QtWidgets, QtSerialPort
import sys

# --- CONFIGURACION ---
PORT = 'COM3'
BAUDRATE = 9600
ADDR = b'\x80'

# --- FUNCIONES PUBLICAS ---

# [Constructor de mensajes]
def build_message(window: int, write: bool, data: str = None):
    window = f"{window:03d}".encode()
    if write: msg = ADDR + window + b'1' + data.encode() + b'\x03'
    else: msg = ADDR + window + b'0' + b'\x03'
    crc = 0
    for byte in msg: crc ^= byte
    crc = f"{crc:02X}".encode()
    return b'\x02' + msg + crc

# --- WIDGET SERIAL ---
class WigetSerial(QtWidgets.QWidget):

    # [Constructor]
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controller Comunication")



# --- INICIALIZADOR ---
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = WigetSerial()
    widget.show()
    print(build_message(000,1,"1"))
    sys.exit(app.exec())
