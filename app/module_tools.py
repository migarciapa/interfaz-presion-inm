# === [MODULO DE HERRAMIENTAS Y WIDGETS VARIOS] ===
# David Miguel Garcia Palacios
# Universidad Nacional de Colombia Sede Bogota

# [Librerias de Terceros]
import sys
from PyQt6 import QtWidgets, QtSerialPort

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

# --------------------------------------------------------------

# --- INICIALIZADOR ---
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Opciones Esteticas
    QtWidgets.QApplication.setStyle("Fusion")
    
    # Muestra la ventana de herramienta
    window = PortSelector()
    window.show()
    
    # Salida
    sys.exit(app.exec())