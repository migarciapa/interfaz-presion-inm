# === [HERRAMIENTA DE COMUNICACION PARA CONTROLADOR 74 FS AG] ===
# David Miguel Garcia Palacios
# Universidad Nacional de Colombia Sede Bogota

# [Librerias de Terceros]
import sys
from PyQt6 import QtWidgets, QtSerialPort, QtCore 

# [Clases a importar]
from Class_DataWindow import DataWindow

# --- HERRAMIENTA 74FSAG ---
class Tool74FSAG(QtWidgets.QWidget):

    # Señales de salida
    signal_preasure = QtCore.pyqtSignal()
    
    # [Constructor]
    def __init__(self, port_name: str = "COM6"):
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

        # Creacion del diccionario de ventanas para el mapeo de datos
        self.dict_windows = {
            000: DataWindow("Maquina encendida", DataWindow.decode_bool),
            100: DataWindow("Arranque suave", DataWindow.decode_bool),
        }

        # Creacion y configuracion de elementos
        self.button_pump_start = QtWidgets.QPushButton("Encendido")
        self.button_pump_stop = QtWidgets.QPushButton("Apagado")
        self.checkbox_soft_start = QtWidgets.QCheckBox()
        self.slider_frequency = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.lcd_frequency = QtWidgets.QLCDNumber()

        self.text_console = QtWidgets.QPlainTextEdit()
        self.text_console.setReadOnly(True)
        
        # Ubicacion y enlazado de elementos
        self.layout_main = QtWidgets.QFormLayout()
        self.setLayout(self.layout_main)
        self.layout_main.addRow(self.button_pump_start)
        self.layout_main.addRow(self.button_pump_stop)
        self.layout_main.addRow("Encendido suave", self.checkbox_soft_start)
        self.layout_main.addRow("Frecuencia bomba", self.lcd_frequency)
        self.layout_main.addRow(self.slider_frequency)
        self.layout_main.addRow(self.text_console)

        # Conexion de las funciones a elementos
        self.serial.readyRead.connect(self.recive_serial_data)
    
    # [Funcion del timer bucle]
    def bucle_rutine(self):
        self.serial.write(b"\x02\x802240\x0387")

    # [Recepcion de mensajes del serial]
    def recive_serial_data(self):
        while self.serial.bytesAvailable():
            self.buffer += bytes(self.serial.readAll())
        if (len(self.buffer) >= 3) and (b'\x03' in self.buffer[:-2]):
            try:
                line = self.buffer.decode(errors = "ignore")
                line = line[line.find('\x02')+1:line.find('\x03')].strip()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error en la decodificacion", e)
                self.buffer = bytes()
                return
            self.text_console.appendPlainText(line)
            self.buffer = bytes()

            # Conversion a ventana y dato
            try:
                if len(line) < 5: raise Exception(repr(line.encode()))
            except Exception as e:
                QtWidgets.QMessageBox.critical(self,"", "[74FSAG] Respuesta error\n" + str(e))

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