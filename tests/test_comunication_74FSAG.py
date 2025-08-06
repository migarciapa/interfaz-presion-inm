# === [PRUEBA DE COMUNCACION CONTROLADOR TWISTORR 74FSAG] ===
# David Miguel Garcia Palacios
# Universidad Nacional de Colombia Sede Bogota

# --- LIBRERIAS ---
from PyQt6 import QtCore, QtWidgets, QtSerialPort, QtGui
import sys

# --- CONFIGURACION ---
PORT_NAME = 'COM6'
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
class WidgetSerial(QtWidgets.QWidget):

    # [Constructor]
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controller Comunication")

        # Creacion de elementos
        self.label_window = QtWidgets.QLabel("Ventana:")
        self.input_window = QtWidgets.QLineEdit()
        self.label_data = QtWidgets.QLabel("Dato:")
        self.input_data = QtWidgets.QLineEdit()
        self.button_read = QtWidgets.QPushButton("Leer")
        self.button_write = QtWidgets.QPushButton("Escribir")

        # Ubicacion de elementos
        self.layout_grid = QtWidgets.QGridLayout()
        self.setLayout(self.layout_grid)
        self.layout_grid.addWidget(self.label_window, 0, 0)
        self.layout_grid.addWidget(self.input_window, 0, 1)
        self.layout_grid.addWidget(self.label_data, 1, 0)
        self.layout_grid.addWidget(self.input_data, 1, 1)
        self.layout_grid.addWidget(self.button_read, 2, 0)
        self.layout_grid.addWidget(self.button_write, 2, 1)

        # Creacion del puerto serial
        self.serial = QtSerialPort.QSerialPort()
        self.serial.setBaudRate(BAUDRATE)
        self.serial.setPortName(PORT_NAME)
        self.serial.setDataBits(QtSerialPort.QSerialPort.DataBits.Data8)
        self.serial.setParity(QtSerialPort.QSerialPort.Parity.NoParity)
        self.serial.setStopBits(QtSerialPort.QSerialPort.StopBits.OneStop)
        self.serial.setFlowControl(QtSerialPort.QSerialPort.FlowControl.NoFlowControl)

        if self.serial.open(QtCore.QIODevice.OpenModeFlag.ReadWrite):
            print("Puerto serial abierto correctamente!")
        else:
            print("No se pudo abrir el puerto serial.")
            print("Error:", self.serial.errorString())

        # Creacion del buffer de lectura
        self.buffer = bytes()

        # Conectar las funciones de elementos
        self.button_read.clicked.connect(self.send_read_command)
        self.button_write.clicked.connect(self.send_write_command)
        self.serial.readyRead.connect(self.recive_serial_data)

    # [Funciones de los elementos]

    # Funcion comando para lectura
    def send_read_command(self):
        window = int(self.input_window.text())
        message = build_message(window, write=False)
        self.serial.write(message)
        print(">>", message)
    
    # Funcion comando para escritura
    def send_write_command(self):
        window = int(self.input_window.text())
        data = self.input_data.text()
        message = build_message(window, write=True, data=data)
        self.serial.write(message)
        print(">>", message)
    
    # Funcion para la recepcion del serial
    def recive_serial_data(self):
        while self.serial.bytesAvailable():
            self.buffer += bytes(self.serial.readAll())
        if len(self.buffer) >= 3:
            if b'\x03' in self.buffer[:-2]:
                print("<<", self.buffer)
                self.buffer = bytes()

# --- INICIALIZADOR ---
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Opciones Esteticas
    QtWidgets.QApplication.setStyle('Fusion')
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor("#70e0e0"))
    app.setPalette(palette)

    # Muestra la ventana del widget
    widget = WidgetSerial()
    widget.show()
    sys.exit(app.exec())
