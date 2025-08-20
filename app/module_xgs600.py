# === [MODULO DE CONTROLADOR XGS-600] ===
# David Miguel Garcia Palacios
# Universidad Nacional de Colombia Sede Bogota

# [Librerias de Terceros]
import sys
import datetime
import numpy as np
from PyQt6 import QtWidgets, QtSerialPort, QtCore

# --- COMUNICACION XGS600 ---
# Clase backend para comunicaciones y consola del controlador
class ComsXGS600(QtWidgets.QWidget):

    # Señales de salida
    signal_preasure = QtCore.pyqtSignal()
    
    # [Constructor]
    def __init__(self, port_name: str = "COM6"):
        super().__init__()
        self.setWindowTitle("Consola Controlador XGS600")

        # Creacion del puerto serial y buffer de comunicacion
        self.buffer = bytes()
        self.serial = QtSerialPort.QSerialPort()
        self.serial.setBaudRate(9600)
        self.serial.setDataBits(QtSerialPort.QSerialPort.DataBits.Data8)
        self.serial.setParity(QtSerialPort.QSerialPort.Parity.NoParity)
        self.serial.setStopBits(QtSerialPort.QSerialPort.StopBits.OneStop)
        self.serial.setFlowControl(QtSerialPort.QSerialPort.FlowControl.NoFlowControl)
        self.select_port(port_name)

        # Conexion a recepcion de datos
        self.serial.readyRead.connect(self.recive_serial)

        # Creacion array de datos presion y tiempo
        self.values_preasure = []
        self.timestamp = None
        
        # Elementos graficos para consola
        self.input_number = QtWidgets.QLineEdit()
        self.input_data = QtWidgets.QLineEdit()
        self.button_send = QtWidgets.QPushButton("Enviar")
        self.text_console = QtWidgets.QPlainTextEdit()
        self.text_console.setReadOnly(True)
        
        # Ubicacion de elementos en layout
        self.layout_main = QtWidgets.QFormLayout()
        self.setLayout(self.layout_main)
        self.layout_main.addRow("Comando (HH) [Hex]:", self.input_number)
        self.layout_main.addRow("Dato:", self.input_data)
        self.layout_main.addRow(self.button_send)
        self.layout_main.addRow(self.text_console)

        # Conexion de las funciones handle
        self.button_send.clicked.connect(self.handle_click_send)
        
    # [Metodo para seleccionar o cambiar puerto serial]
    def select_port(self, port_name: str):
        if self.serial.isOpen():
            self.serial.close()
            print("[XGS600] Puerto serial cerrado.")
        self.serial.setPortName(port_name)
        if self.serial.open(QtCore.QIODevice.OpenModeFlag.ReadWrite):
            print(f"[XGS600] Puerto {port_name} abierto correctamente!")
        else:
            print(f"[XGS600] No se pudo abrir el puerto {port_name}. Error:", self.serial.errorString())

    # [Recepcion de mensajes del serial]
    def recive_serial(self):
        self.buffer += bytes(self.serial.readAll())
        idx = self.buffer.find(b'\r')

        # Procesado de mensaje
        if idx != -1:
            self.timestamp = datetime.datetime.now()
            line = self.buffer[:idx].decode(errors = "ignore")
            self.buffer = self.buffer[idx:]
            line = line.strip()
            self.text_console.appendPlainText(line)

            # Conversion a datos presion
            if "," in line:
                line = line[1:].split(",")
                values = []
                for item in line:
                    item = item.strip()
                    try:
                        values.append(float(item))
                    except ValueError:
                        values.append(np.nan)
                
                # Guarda valores y emite señal
                self.values_preasure = values
                self.signal_preasure.emit()
    
    # [Envio de mensajes del serial]
    def send_serial(self, comand: str, data: str = ""):
        comand = comand.encode()
        data = data.encode()
        line = b'#00' + comand + data + b'\r'
        self.serial.write(line)
        self.text_console.appendPlainText(repr(line))

    # [Handle de click boton de lectura]
    def handle_click_send(self):
        comand = self.input_number.text()
        data = self.input_data.text()
        self.send_serial(comand, data)

# --- WIDGET XGS600 ---
# Clase para la interfaz de usuario con el controlador XGS600
class WidgetXGS600(QtWidgets.QWidget):

    # [Constructor]
    def __init__(self, backend: ComsXGS600):
        super().__init__()
        self.setWindowTitle("Widget 74FSAG")

        # Obtencion del backend de comunicacion
        self.coms = backend
        self.coms.setVisible(False)

        # Elementos graficos del widget
        self.checkbox_console = QtWidgets.QCheckBox("Ver Terminal")
        
        # Ubicacion de elementos en layout
        self.layout_main = QtWidgets.QFormLayout()
        self.setLayout(self.layout_main)
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.layout_main.addRow(separator)
        self.layout_main.addRow(self.checkbox_console)
        self.layout_main.addRow(self.coms)

        # Conexion de funciones handle
        self.checkbox_console.toggled.connect(self.coms.setVisible)

# --------------------------------------------------------------

# --- INICIALIZADOR ---
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Opciones Esteticas
    QtWidgets.QApplication.setStyle("Fusion")
    
    # Muestra la ventana de herramienta
    window = ComsXGS600()
    window.show()

    def rutine():
        window.send_serial("0F")

    # Timer para bucle
    timer_bucle = QtCore.QTimer()
    timer_bucle.timeout.connect(rutine)
    timer_bucle.start(2000)
    
    # Salida
    sys.exit(app.exec())