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
    def __init__(self, port_name: str = "COM10"):
        super().__init__()
        self.setWindowTitle("Herramienta XGS600")

        # Creacion array de datos presion y tiempo
        self.values_preasure = []
        self.timestamp = None

        # Creacion del puerto serial y buffer de comunicacion
        self.buffer = bytes()
        self.serial = QtSerialPort.QSerialPort()
        self.serial.setPortName(port_name)
        self.serial.setBaudRate(9600)
        self.serial.setDataBits(QtSerialPort.QSerialPort.DataBits.Data8)
        self.serial.setParity(QtSerialPort.QSerialPort.Parity.NoParity)
        self.serial.setStopBits(QtSerialPort.QSerialPort.StopBits.OneStop)
        self.serial.setFlowControl(QtSerialPort.QSerialPort.FlowControl.NoFlowControl)
        if self.serial.open(QtCore.QIODevice.OpenModeFlag.ReadWrite):
            print("[XGS600] Puerto serial abierto correctamente!")
        else:
            print("[XGS600] No se pudo abrir el puerto serial. Error:", self.serial.errorString())

        # Conexion a recepcion de datos
        self.serial.readyRead.connect(self.recive_serial)
        
        # Creacion de timer para bucle
        self.timer_bucle = QtCore.QTimer()
        self.timer_bucle.timeout.connect(self.bucle_rutine)
        
        # Elementos graficos para consola
        self.input_command = QtWidgets.QLineEdit()
        self.button_command = QtWidgets.QPushButton("Enviar")
        self.text_console = QtWidgets.QPlainTextEdit()
        self.text_console.setReadOnly(True)
        
        # Ubicacion de elementos en layout
        self.layout_main = QtWidgets.QFormLayout()
        self.setLayout(self.layout_main)
        self.layout_main.addRow("Comando ASCII", self.input_command)
        self.layout_main.addRow(self.button_command)
        self.layout_main.addRow(self.text_console)

        # Conexion de las funciones handle
        self.serial.readyRead.connect(self.recive_serial)
        self.button_command.clicked.connect(self.send_command)

    # [Funcion del timer bucle]
    def bucle_rutine(self):
        self.serial.write(("#000F\r").encode())

    # [Recepcion de mensajes del serial]
    def recive_serial(self):
        self.buffer += bytes(self.serial.readAll())
        idx = self.buffer.find(b'r')
        if b'\r' in self.buffer:
            self.timestamp = np.datetime64(datetime.datetime.now())
            try:
                line = self.buffer.decode(errors = "ignore").strip()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error en la decodificacion", e)
                self.buffer = bytes()
                return
            self.text_console.appendPlainText(line)
            self.buffer = bytes()

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
                
                # Envia alerta y cambia labels
                self.values_preasure = values
                self.signal_preasure.emit()
    
    # [Envio de mensajes del serial]
    def send_command(self):
        message = (self.input_command.text() + "\r").encode()
        self.serial.write(message)
        self.text_console.appendPlainText("".join(map(str, [">>", message])))

# --------------------------------------------------------------

# --- INICIALIZADOR ---
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Opciones Esteticas
    QtWidgets.QApplication.setStyle("Fusion")
    
    # Muestra la ventana de herramienta
    window = ComsXGS600()
    window.show()

    # Timer para bucle
    timer_bucle = QtCore.QTimer()
    timer_bucle.timeout.connect(window.bucle_rutine)
    timer_bucle.start(2000)
    
    # Salida
    sys.exit(app.exec())