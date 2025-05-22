# === [HERRAMIENTA DE COMUNICACION PARA CONTROLADOR 74 FS AG] ===
# David Miguel Garcia Palacios
# Universidad Nacional de Colombia Sede Bogota

# [Librerias de Terceros]
import sys
from PyQt6 import QtWidgets

# --- HERRAMIENTA 74FSAG ---
class Tool74FSAG(QtWidgets.QWidget):
    
    # [Constructor]
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Herramienta 74FSAG")

        # Elemento de boton enendido apagado
        self.button_pump = QtWidgets.QPushButton("Apagado")
        self.button_pump.setCheckable(True)
        self.button_pump.setChecked(False)
        
        
        # Ubicacion y enlazado de elementos
        self.layout_form = QtWidgets.QFormLayout()
        self.setLayout(self.layout_form)
        self.layout_form.addRow(self.button_pump)

# --- INICIALIZADOR ---
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Opciones Esteticas
    QtWidgets.QApplication.setStyle("Fusion")
    
    # Muestra la ventana de herramienta
    window = Tool74FSAG()
    window.show()
    sys.exit(app.exec())