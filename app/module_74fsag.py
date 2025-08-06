# === [MODULO DE CONTROLADOR TWISTORR 74FSAG] ===
# David Miguel Garcia Palacios
# Universidad Nacional de Colombia Sede Bogota

# [Librerias de Terceros]
import sys
import numpy as np
from PyQt6 import QtWidgets, QtSerialPort, QtCore 

# [Clases a importar]
from Class_DataWindow import DataWindow

# --- COMUNICACION 74FSAG ---
# Clase para comunicaciones y consola del controlador
class Coms74FSAG(QtWidgets.QWidget):
    
    # [Constructor]
    def __init__(self, port_name: str = "COM4"):
        super().__init__()
        self.setWindowTitle("Herramienta 74FSAG")

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
            print("[74FSAG] Puerto serial abierto correctamente!")
        else:
            print("[74FSAG] No se pudo abrir el puerto serial. Error:", self.serial.errorString())

        # Conexion a recepcion de datos
        self.serial.readyRead.connect(self.recive_serial_data)

        # Creacion del diccionario de ventanas para el mapeo de datos
        self.dict_windows = {
            000: DataWindow("Maquina encendida", DataWindow.to_bool),
            100: DataWindow("Arranque suave", DataWindow.to_bool),
            224: DataWindow("Lectura presion", DataWindow.to_float)
        }

        # Elementos graficos para consola
        self.input_window = QtWidgets.QLineEdit()
        self.input_data = QtWidgets.QLineEdit()
        self.button_read = QtWidgets.QPushButton("Leer")
        self.button_write = QtWidgets.QPushButton("Escribir")
        self.text_console = QtWidgets.QPlainTextEdit()
        self.text_console.setReadOnly(True)
        
        # Ubicacion de elementos en layout
        self.layout_main = QtWidgets.QFormLayout()
        self.setLayout(self.layout_main)
        self.layout_main.addRow("Ventana:", self.input_window)
        self.layout_main.addRow("Dato:", self.input_data)
        layout_buttons = QtWidgets.QHBoxLayout()
        layout_buttons.addWidget(self.button_read)
        layout_buttons.addWidget(self.button_write)
        self.layout_main.addRow(layout_buttons)
        self.layout_main.addRow(self.text_console)
    
    # [Funcion de rutina de lectura]
    def bucle_rutine(self):
        self.serial.write(b"\x02\x802240\x0387")

    # [Recepcion de mensajes del serial]
    def recive_serial_data(self):
        self.buffer += bytes(self.serial.readAll())
        idx = self.buffer.find(b'\x03')

        # Procesado de mensaje
        if idx != -1 and len(self.buffer) >= idx + 3:
            self.timestamp = np.datetime64("now")
            idx += 3
            line = self.buffer[:idx].decode(errors = "ignore")
            self.buffer = self.buffer[idx:]
            line = line[line.find('\x02') + 1 :line.find('\x03')].strip()
            self.text_console.appendPlainText(line)

            # Asignacion a ventana
            if len(line) >= 5:
                win = int(line[:3])
                data = line[4:]
                self.dict_windows[win].set(data)
                print(self.dict_windows[win])




# --- INICIALIZADOR ---
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Opciones Esteticas
    QtWidgets.QApplication.setStyle("Fusion")
    
    # Muestra la ventana de herramienta
    window = Tool74FSAG()
    window.show()

    # Timer para bucle
    timer_bucle = QtCore.QTimer()
    timer_bucle.timeout.connect(window.bucle_rutine)
    timer_bucle.start(1000)
    
    # Salida
    sys.exit(app.exec())