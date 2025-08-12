# === [MODULO DE CONTROLADOR TWISTORR 74FSAG] ===
# David Miguel Garcia Palacios
# Universidad Nacional de Colombia Sede Bogota

# [Librerias de Terceros]
import sys
import numpy as np
from PyQt6 import QtWidgets, QtSerialPort, QtCore 

# --- COMUNICACION 74FSAG ---
# Clase backend para comunicaciones y consola del controlador
class Coms74FSAG(QtWidgets.QWidget):
    
    # [Constructor]
    def __init__(self, port_name: str = "COM6"):
        super().__init__()
        self.setWindowTitle("Consola Controlador 74FSAG")

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
        self.serial.readyRead.connect(self.recive_serial)

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
        self.layout_main.addRow(layout_buttons)
        layout_buttons.addWidget(self.button_read)
        layout_buttons.addWidget(self.button_write)
        self.layout_main.addRow(self.text_console)

        # Conexion de funciones handle
        self.button_read.clicked.connect(self.handle_click_read)
        self.button_write.clicked.connect(self.handle_click_write)
    
    # [Funcion de rutina de lectura]
    def bucle_rutine(self):
        self.send_serial(224, False)

    # [Recepcion de mensajes del serial]
    def recive_serial(self):
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
                window = int(line[:3])
                data = line[4:]
                try:
                    self.dict_windows[window].set(data)
                    print(self.dict_windows[window])
                except Exception as e:
                    print(f"Ventana desconocida {window} reporta {data}")
    
    # [Envio de mensajes del serial]
    def send_serial(self, window: int, write: bool, data: str = ""):
        window = str(window).zfill(3).encode()
        write = str(int(write)).encode()
        data = data.encode()
        msg = b"\x80" + window + write + data + b"\x03"
        crc = 0
        for byte in msg: crc ^= byte
        crc = f"{crc:02X}".encode()
        line = b"\x02" + msg + crc
        self.serial.write(line)
    
    # [Handle de click boton de lectura]
    def handle_click_read(self):
        window = int(self.input_window.text())
        self.send_serial(window, False)

    # [Handle de click boton de escritura]
    def handle_click_write(self):
        window = int(self.input_window.text())
        data = self.input_data.text()
        self.send_serial(window, True, data)

# --- WIDGET 74FSAG ---
# Clase para la interfaz de usuario con el controlador 74FSAG
class Widget74FSAG(QtWidgets.QWidget):
    
    # [Constructor]
    def __init__(self, backend: Coms74FSAG):
        super().__init__()
        self.setWindowTitle("Widget 74FSAG")

        # Obtencion del backend de comunicacion
        self.coms = backend
        self.coms.setVisible(False)

        # Elementos graficos del widget
        self.button_pump = QtWidgets.QPushButton("Encender Bomba Turbo")
        self.button_pump.setCheckable(True)
        self.checkbox_console = QtWidgets.QCheckBox("Ver Terminal")
        
        # Ubicacion de elementos en layout
        self.layout_main = QtWidgets.QFormLayout()
        self.setLayout(self.layout_main)
        self.layout_main.addRow(self.button_pump)
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.layout_main.addRow(separator)
        self.layout_main.addRow(self.checkbox_console)
        self.layout_main.addRow(self.coms)

        # Conexion de funciones handle
        self.checkbox_console.toggled.connect(self.coms.setVisible)
    
    # [Handle de click boton de lectura]
    def handle_click_read(self):
        window = int(self.input_window.text())
        self.send_serial(window, False)

# --- DATA WINDOW CLASS ---
# Clase para objetos de almacenamiento de datos del controlador
class DataWindow:

    # [Constructor]
    def __init__(self, name: str, decoder: callable):
        self.name = name
        self.value = ""
        self.decoder = decoder

    # [Call de informacion de la clase]
    def __repr__(self):
        return f"<DataWindow '{self.name}' = {self.decoded()}>"
    
    # [Get de valor decodificado]
    def decoded(self):
        try:
            return self.decoder(self.value)
        except Exception as e:
            print(f"[DataWindow] Error decodificando ventana {self.name}: {e}")
            return None
    
    # [Set de valor en bruto]
    def set(self, raw: str):
        self.value = raw

    # - FUNCIONES DE DECODIFICACION EN LA CLASE -
    
    # [Decodificador a boleano]
    def to_bool(raw: str) -> bool:
        return bool(int(raw))
    
    # [Decodificador a integer]
    def to_float(raw: str) -> int:
        return float(raw)

# --------------------------------------------------------------

# --- INICIALIZADOR ---
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Opciones Esteticas
    QtWidgets.QApplication.setStyle("Fusion")
    
    # Muestra la ventana de herramienta
    coms = Coms74FSAG()
    window = Widget74FSAG(coms)
    window.show()

    # Timer para bucle
    timer_bucle = QtCore.QTimer()
    timer_bucle.timeout.connect(coms.bucle_rutine)
    timer_bucle.start(2000)
    
    # Salida
    sys.exit(app.exec())