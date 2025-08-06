# === [INTERFAZ DE USUARIO DE SISTEMA DE PRESION DEL INM] ===
# David Miguel Garcia Palacios
# Universidad Nacional de Colombia Sede Bogota

# [Librerias de Terceros]
import sys
import pyqtgraph
import pandas as pd
from PyQt6 import QtCore, QtWidgets

# [Clases de herramientas]
from app.module_74fsag import Tool74FSAG
from Tool_XGS600 import ToolXGS600

# --- APLICACION PRINCIPAL ---
class MainWindow(QtWidgets.QMainWindow):

    # [Constructor]
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interfaz Presion INM")
        self.resize(1280, 720)

        # Creacion de dataframe de presion
        self.dataframe = pd.DataFrame(
            columns = ["XGS600_T1", "XGS600_T2", "XGS600_T3", "XGS600_T4", "74FS"])
        self.dataframe.index = pd.to_datetime(self.dataframe.index)

        # Creacion de herramientas
        self.widget_74FSAG = Tool74FSAG("COM6")
        self.widget_XGS600 = ToolXGS600("COM10")
        self.widget_plot = pyqtgraph.PlotWidget()

        # Creacion de timer para bucle
        self.timer_read = QtCore.QTimer()
        self.timer_read.timeout.connect(self.read_rutine)
        
        # Creacion de elementos
        self.widget_main = QtWidgets.QWidget()
        self.layout_main = QtWidgets.QVBoxLayout()
        self.splitter = QtWidgets.QSplitter()
        self.tab_panel = QtWidgets.QTabWidget()

        # Agrega elementos al menubar
        self.menu_bar = self.menuBar()
        self.menu_save = self.menu_bar.addAction("Guardar Grafico")

        # Ubicacion y enlazado de elementos
        self.setCentralWidget(self.widget_main)
        self.widget_main.setLayout(self.layout_main)
        self.layout_main.addWidget(self.splitter)
        self.splitter.addWidget(self.tab_panel)
        self.splitter.addWidget(self.widget_plot)
        self.tab_panel.addTab(self.widget_74FSAG, "74FSAG")
        self.tab_panel.addTab(self.widget_XGS600, "XGS600")

        # Configuracion inicial de elementos
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.widget_plot.setLogMode(x=False, y=True)
        self.widget_plot.showGrid(x=True, y=True, alpha=0.3)
        self.plot_aux3 = self.widget_plot.plot([], [], pen=pyqtgraph.mkPen("r", width=1))
        self.plot_aux4 = self.widget_plot.plot([], [], pen=pyqtgraph.mkPen("g", width=1))
        self.plot_ref1 = self.widget_plot.plot([], [], pen=pyqtgraph.mkPen("y", width=1))

        # Conexion de funciones a elementos
        self.menu_save.triggered.connect(self.save_plot)

        # Conexion a señales de herramientas
        self.widget_XGS600.signal_preasure.connect(self.han_preasure)

        # Inicia timer de rutina de lectura de presion
        self.timer_read.start(1000)
    
    # [Funcion del timer bucle]
    def read_rutine(self):
        self.widget_XGS600.serial.write(b"#000F\r")
        self.widget_74FSAG.serial.write(b"\x02\x802240\x0387")
        
    # [Funcion handle de señal presion XGS600]
    def han_preasure(self):
        self.dataframe.loc[self.widget_XGS600.timestamp] = (
            self.widget_XGS600.values_preasure + [self.widget_74FSAG.dict_windows[224].decoded()])
        self.plot_aux3.setData(self.dataframe.index.values, self.dataframe["XGS600_T3"].values)
        self.plot_aux4.setData(self.dataframe.index.values, self.dataframe["XGS600_T4"].values)
        self.plot_ref1.setData(self.dataframe.index.values, self.dataframe["74FS"].values)     

    # [Funcion guardar plot]
    def save_plot(self):
        print("boop!")
        if self.dataframe.empty:
            QtWidgets.QMessageBox.warning(self,"", "No hay datos en el grafico para guardar")
            return
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self)
        if file_path:
            if not file_path.endswith(".csv"):
                file_path += ".csv"
                # Add xls
            self.dataframe.to_csv(file_path, index=True)

# --- INICIALIZADOR ---
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Opciones Esteticas
    QtWidgets.QApplication.setStyle("Fusion")
    
    # Muestra la ventana principal
    window = MainWindow()
    window.show()
    sys.exit(app.exec())