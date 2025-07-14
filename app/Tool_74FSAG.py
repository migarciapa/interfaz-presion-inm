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

        # Creacion del diccionario de ventanas para el mapeo de datos
        self.dict_windows = {
            000: DataWindow("Maquina encendida", DataWindow.decode_bool),
            100: DataWindow("Arranque suave", DataWindow.decode_bool),
        }

        # Creacion de elementos graficos
        self.button_pump_start = QtWidgets.QPushButton("Encendido")
        self.button_pump_stop = QtWidgets.QPushButton("Apagado")
        self.checkbox_soft_start = QtWidgets.QCheckBox()
        self.slider_frequency = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.lcd_frequency = QtWidgets.QLCDNumber()
        
        # Ubicacion y enlazado de elementos
        self.layout_form = QtWidgets.QFormLayout()
        self.setLayout(self.layout_form)
        self.layout_form.addRow(self.button_pump_start)
        self.layout_form.addRow(self.button_pump_stop)
        self.layout_form.addRow("Encendido suave", self.checkbox_soft_start)
        self.layout_form.addRow("Frecuencia bomba", self.lcd_frequency)
        self.layout_form.addRow(self.slider_frequency)

        # Configuracion inicial de elementos

        # Conexion de las funciones a elementos
        self.button_pump_start.clicked.connect(self.error_message)
    
    # [Funcion cliked del boton]
    def error_message(self):
        QtWidgets.QMessageBox.critical(self, "Error", "No se pudo conectar con el dispositivo.")

# --- INICIALIZADOR ---
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Opciones Esteticas
    QtWidgets.QApplication.setStyle("Fusion")
    
    # Muestra la ventana de herramienta
    window = Tool74FSAG()
    window.show()
    sys.exit(app.exec())