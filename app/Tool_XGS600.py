# === [HERRAMIENTA DE COMUNICACION PARA CONTROLADOR XGS-600] ===
# David Miguel Garcia Palacios
# Universidad Nacional de Colombia Sede Bogota

# [Librerias de Terceros]
import sys
from PyQt6 import QtWidgets, QtSerialPort, QtCore

# --- HERRAMIENTA XGS600 ---
class ToolXGS600(QtWidgets.QWidget):
    
    # [Constructor]
    def __init__(self, port_name: str = "COM4"):
        super().__init__()
        self.setWindowTitle("Herramienta XGS600")

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
            print("Puerto serial abierto correctamente!")
        else:
            print("No se pudo abrir el puerto serial.")
            print("Error:", self.serial.errorString())

        # Creacion de elementos
        self.input_command = QtWidgets.QLineEdit()
        self.button_command = QtWidgets.QPushButton("Enviar")
        self.text_console = QtWidgets.QPlainTextEdit()
        
        # Ubicacion y enlazado de elementos
        self.layout_main = QtWidgets.QFormLayout()
        self.setLayout(self.layout_main)
        self.layout_main.addRow("Comando ASCII", self.input_command)
        self.layout_main.addRow(self.button_command)
        self.layout_main.addRow(self.text_console)

        # Configuracion inicial de elementos
        self.text_console.setReadOnly(True)

        # Conexion de las funciones a elementos
        self.serial.readyRead.connect(self.recive_serial_data)
        self.button_command.clicked.connect(self.send_command)
    
    # [Recepcion de mensajes del serial]
    def recive_serial_data(self):
        self.buffer += self.serial.readAll()
        if True:
            self.text_console.appendPlainText("".join(map(str, [">>", self.buffer])))
            self.buffer = bytes()
    
    # [Envio de mensajes del serial]
    def send_command(self):
        message = self.input_command.text().encode()
        self.serial.write(message)
        self.text_console.appendPlainText("".join(map(str, [">>", message])))

# --- INICIALIZADOR ---
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Opciones Esteticas
    QtWidgets.QApplication.setStyle("Fusion")
    
    # Muestra la ventana de herramienta
    window = ToolXGS600()
    window.show()
    sys.exit(app.exec())