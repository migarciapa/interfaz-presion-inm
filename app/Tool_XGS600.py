# === [HERRAMIENTA DE COMUNICACION PARA CONTROLADOR XGS-600] ===
# David Miguel Garcia Palacios
# Universidad Nacional de Colombia Sede Bogota

# [Librerias de Terceros]
import sys
import numpy as np
from PyQt6 import QtWidgets, QtSerialPort, QtCore, QtGui

# --- HERRAMIENTA XGS600 ---
class ToolXGS600(QtWidgets.QWidget):

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
        
        # Creacion de timer para bucle
        self.timer_bucle = QtCore.QTimer()
        self.timer_bucle.timeout.connect(self.bucle_rutine)

        # Creacion y configuracion de elementos
        self.slider_time = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider_time.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        self.slider_time.setMinimum(1)
        self.slider_time.setMaximum(60)
        self.slider_time.setTickInterval(10)
        self.slider_time.setValue(1)

        self.label_sensor_1 = QtWidgets.QLabel("--")
        self.label_sensor_1.setFont(QtGui.QFont("Courier New", 24, QtGui.QFont.Weight.Bold))
        self.label_sensor_1.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.label_sensor_2 = QtWidgets.QLabel("--")
        self.label_sensor_2.setFont(QtGui.QFont("Courier New", 24, QtGui.QFont.Weight.Bold))
        self.label_sensor_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.label_sensor_3 = QtWidgets.QLabel("--")
        self.label_sensor_3.setFont(QtGui.QFont("Courier New", 24, QtGui.QFont.Weight.Bold))
        self.label_sensor_3.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.label_sensor_4 = QtWidgets.QLabel("--")
        self.label_sensor_4.setFont(QtGui.QFont("Courier New", 24, QtGui.QFont.Weight.Bold))
        self.label_sensor_4.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        self.input_command = QtWidgets.QLineEdit()
        self.button_command = QtWidgets.QPushButton("Enviar")
        self.text_console = QtWidgets.QPlainTextEdit()
        self.text_console.setReadOnly(True)
        
        # Ubicacion y enlazado de elementos
        self.layout_main = QtWidgets.QFormLayout()
        self.setLayout(self.layout_main)
        self.layout_main.addRow("Intervalo de Lectura", self.slider_time)
        self.layout_main.addRow("Sensor en [T1]: ", self.label_sensor_1)
        self.layout_main.addRow("Sensor en [T2]: ", self.label_sensor_2)
        self.layout_main.addRow("Sensor en [T3]: ", self.label_sensor_3)
        self.layout_main.addRow("Sensor en [T4]: ", self.label_sensor_4)
        self.layout_main.addRow("Comando ASCII", self.input_command)
        self.layout_main.addRow(self.button_command)
        self.layout_main.addRow(self.text_console)

        # Conexion de las funciones a elementos
        self.serial.readyRead.connect(self.recive_serial_data)
        self.slider_time.valueChanged.connect(lambda x: self.show_tooltip(x,"s"))
        self.slider_time.valueChanged.connect(lambda x: self.timer_bucle.setInterval(x * 1000))
        self.button_command.clicked.connect(self.send_command)

    # [Funcion del timer bucle]
    def bucle_rutine(self):
        self.serial.write(("#000F\r").encode())

    # [Recepcion de mensajes del serial]
    def recive_serial_data(self):
        self.buffer += bytes(self.serial.readAll())
        if b'\r' in self.buffer:
            try:
                line = self.buffer.decode(errors = "ignore").strip()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error en la decodificacion", e)
                self.buffer = bytes()
                return
            self.timestamp = np.datetime64("now")
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
                try:
                    self.label_sensor_1.setText(str(self.values_preasure[0]))
                    self.label_sensor_2.setText(str(self.values_preasure[1]))
                    self.label_sensor_3.setText(str(self.values_preasure[2]))
                    self.label_sensor_4.setText(str(self.values_preasure[3]))
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self,"", "[XGS600] Error en el display de valores\n" + str(e))
    
    # [Envio de mensajes del serial]
    def send_command(self):
        message = (self.input_command.text() + "\r").encode()
        self.serial.write(message)
        self.text_console.appendPlainText("".join(map(str, [">>", message])))

    # [Mostrar valor tooltip]
    def show_tooltip(self, value, unit = ""):
        QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), str(value) + unit)

# --- INICIALIZADOR ---
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Opciones Esteticas
    QtWidgets.QApplication.setStyle("Fusion")
    
    # Muestra la ventana de herramienta
    window = ToolXGS600()
    window.show()

    # Timer para bucle
    timer_bucle = QtCore.QTimer()
    timer_bucle.timeout.connect(window.bucle_rutine)
    timer_bucle.start(1000)
    
    # Salida
    sys.exit(app.exec())