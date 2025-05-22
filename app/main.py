# === [INTERFAZ DE USUARIO DE SISTEMA DE PRESION DEL INM] ===
# David Miguel Garcia Palacios
# Universidad Nacional de Colombia Sede Bogota

# [Librerias de Terceros]
import sys
from PyQt6 import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as MpFigureCanvas

# [Clases de herramientas]
from Tool_74FSAG import Tool74FSAG
from Tool_XGS600 import ToolXGS600

# --- APLICACION PRINCIPAL ---
class MainWindow(QtWidgets.QMainWindow):

    # [Constructor]
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interfaz Presion INM")
        self.resize(1280, 720)
        
        # Creacion de elementos
        self.widget_main = QtWidgets.QWidget()
        self.layout_main = QtWidgets.QVBoxLayout()
        self.splitter = QtWidgets.QSplitter()
        self.tab_panel = QtWidgets.QTabWidget()

        # Creacion de herramientas
        self.widget_74FSAG = Tool74FSAG()
        self.widget_XGS600 = ToolXGS600()
        self.widget_graph = MpFigureCanvas()
        self.plot_graph = self.widget_graph.figure.add_subplot()

        # Ubicacion y enlazado de elementos
        self.setCentralWidget(self.widget_main)
        self.widget_main.setLayout(self.layout_main)
        self.layout_main.addWidget(self.splitter)
        self.splitter.addWidget(self.tab_panel)
        self.splitter.addWidget(self.widget_graph)
        self.tab_panel.addTab(self.widget_74FSAG, "74FSAG")
        self.tab_panel.addTab(self.widget_XGS600, "XGS600")

        # Configuracion inicial de elementos
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.widget_graph.figure.tight_layout()
        self.plot_graph.plot([1,2,3],[1,4,9])

# --- INICIALIZADOR ---
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Opciones Esteticas
    QtWidgets.QApplication.setStyle("Fusion")
    
    # Muestra la ventana principal
    window = MainWindow()
    window.show()
    sys.exit(app.exec())