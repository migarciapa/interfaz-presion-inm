# === [MODULO DE HERRAMIENTAS Y WIDGETS VARIOS] ===
# David Miguel Garcia Palacios
# Universidad Nacional de Colombia Sede Bogota

# [Librerias de Terceros]
import sys, datetime, pyqtgraph
from PyQt6 import QtWidgets, QtSerialPort, QtCore, QtGui

# --- SELECTOR DE PUERTOS DE COMUNICACION ---
# Ventana de dialogo para la obtencion de puertos seriales
class PortSelector(QtWidgets.QDialog):
    
    # [Constructor]
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Selector de Puertos")

        # Elementos graficos del widget
        self.combo_1 = QtWidgets.QComboBox()
        self.combo_2 = QtWidgets.QComboBox()
        self.button_accept = QtWidgets.QPushButton("Aceptar")
        self.button_cancel = QtWidgets.QPushButton("Cancelar")

        # Ubicacion de elementos en layout
        self.layout_main = QtWidgets.QFormLayout()
        self.setLayout(self.layout_main)
        self.layout_main.addRow("Puerto [74FSAG]:", self.combo_1)
        self.layout_main.addRow("Puerto [XGS600]:", self.combo_2)
        layout_buttons = QtWidgets.QHBoxLayout()
        self.layout_main.addRow(layout_buttons)
        layout_buttons.addWidget(self.button_cancel)
        layout_buttons.addWidget(self.button_accept)

        # Llamado a hallar los puertos
        self.fill_ports()

        # Conexion de funciones handle
        self.button_accept.clicked.connect(self.accept)
        self.button_cancel.clicked.connect(self.reject)

    # [Obtencion y poblacion de puertos seriales]
    def fill_ports(self):
        ports = QtSerialPort.QSerialPortInfo.availablePorts()
        if not ports:
            self.combo_1.addItem("No hay puertos disponibles", None)
            self.combo_2.addItem("No hay puertos disponibles", None)
            self.combo_1.setEnabled(False)
            self.combo_2.setEnabled(False)
            self.button_accept.setEnabled(False)
            return
        for port in ports:
            display_text = f"{port.portName()} - {port.description()}"
            self.combo_1.addItem(display_text, port.portName())
            self.combo_2.addItem(display_text, port.portName())
    
    # [Obtencion de la seleccion del usuario]
    def get_selected_ports(self):
        return [self.combo_1.currentData(), self.combo_2.currentData()]
    
# --- WIDGET DISPLAY MEDIDAS ---
# Widget para la visulaizacion de medidas de presion
class WidgetDisplay(QtWidgets.QWidget):
    
    # [Constructor]
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Widget Display")

        # Labels y chechbox para el display
        self.label_value = []
        self.checkbox_show = []
        for i in range(5):
            label = QtWidgets.QLabel("--")
            label.setFont(QtGui.QFont("Courier New", 24, QtGui.QFont.Weight.Bold))
            label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
            self.label_value.append(label)
            checkbox = QtWidgets.QCheckBox()
            checkbox.setChecked(True)
            self.checkbox_show.append(checkbox)
        
        # Ajsutar colores de los label
        self.label_value[1].setStyleSheet("color: #FF0000")
        self.label_value[2].setStyleSheet("color: #00FF00")
        self.label_value[3].setStyleSheet("color: #0000FF")
        self.label_value[4].setStyleSheet("color: #FF00FF")

        # Ubicacion de elementos en el layout
        self.layout_main = QtWidgets.QGridLayout()
        self.layout_main.setColumnStretch(0, 0)
        self.layout_main.setColumnStretch(1, 0)
        self.layout_main.setColumnStretch(2, 1)
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.checkbox_show[0], 0, 0)
        self.layout_main.addWidget(QtWidgets.QLabel("Sensor 74FS"), 0, 1)
        self.layout_main.addWidget(self.label_value[0], 0, 2)
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.layout_main.addWidget(separator, 1, 0, 1, 3)
        self.layout_main.addWidget(self.checkbox_show[1], 2, 0)
        self.layout_main.addWidget(self.checkbox_show[2], 3, 0)
        self.layout_main.addWidget(self.checkbox_show[3], 4, 0)
        self.layout_main.addWidget(self.checkbox_show[4], 5, 0)
        self.layout_main.addWidget(QtWidgets.QLabel("Sensor XGS600 [T1]"), 2, 1)
        self.layout_main.addWidget(QtWidgets.QLabel("Sensor XGS600 [T2]"), 3, 1)
        self.layout_main.addWidget(QtWidgets.QLabel("Sensor XGS600 [T3]"), 4, 1)
        self.layout_main.addWidget(QtWidgets.QLabel("Sensor XGS600 [T4]"), 5, 1)
        self.layout_main.addWidget(self.label_value[1], 2, 2)
        self.layout_main.addWidget(self.label_value[2], 3, 2)
        self.layout_main.addWidget(self.label_value[3], 4, 2)
        self.layout_main.addWidget(self.label_value[4], 5, 2)

    # [Funcion para actualizacion de los labels]    
    def update_labels(self, data):
        for idx in range(len(data)):
            self.label_value[idx].setText(str(data[idx]))

    # [Funcion get para los valores booleanos de checkbox]
    def get_visible(self):
        return [cb.isChecked() for cb in self.checkbox_show]

# --- EJES DE TIEMPO ---
# Widget para la visulaizacion de medidas de presion
class TimeAxis(pyqtgraph.AxisItem):

    # [Constructor]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    # [Obtencion de ejes de tiempo]
    def tickStrings(self, values, scale, spacing):
        return [datetime.datetime.fromtimestamp(v).strftime("%H:%M:%S") for v in values]
    
# --- CONTROLES DE GRAFICO ---
# Widget para la visualizacion de controles del grafico
class WidgetGraphControls(QtWidgets.QWidget):

    # Señales de salida
    signal_reset = QtCore.pyqtSignal()
    signal_timeset = QtCore.pyqtSignal()
        
    # [Constructor]
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Widget Controles")

        # Labels para el display
        self.button_reset = QtWidgets.QPushButton("Limpiar Datos")
        self.spinbox_time = QtWidgets.QSpinBox()
        self.spinbox_time.setRange(1, 60)
        self.spinbox_time.setSingleStep(1)

        # Ubicacion de elementos en el layout
        self.layout_main = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.button_reset)
        label = QtWidgets.QLabel("Tiempo intervalo entre medidas [s]")
        self.layout_main.addWidget(label)
        self.layout_main.addWidget(self.spinbox_time)
        self.layout_main.addStretch()

        # Conexion de funciones señal
        self.button_reset.clicked.connect(self.signal_reset.emit)
        self.spinbox_time.editingFinished.connect(self.signal_timeset.emit)

# --------------------------------------------------------------

# --- INICIALIZADOR ---
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Opciones Esteticas
    QtWidgets.QApplication.setStyle("Fusion")
    
    # Muestra la ventana de herramienta
    window = WidgetDisplay()
    window.show()
    
    # Salida
    sys.exit(app.exec())