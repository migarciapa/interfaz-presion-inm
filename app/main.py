# === [INTERFAZ DE USUARIO DE SISTEMA DE PRESION DEL INM] ===
# David Miguel Garcia Palacios
# Universidad Nacional de Colombia Sede Bogota

# [Librerias de Terceros]
import sys, pyqtgraph, datetime
import pandas as pd
from PyQt6 import QtCore, QtWidgets

# [Modulos importados]
import module_74fsag, module_xgs600, module_tools

# --- APLICACION PRINCIPAL ---
class MainWindow(QtWidgets.QMainWindow):

    # [Constructor]
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interfaz Presion INM")

        # Creacion de dataframe de presion
        self.dataframe = pd.DataFrame(
            columns = ["74FS", "XGS600_T1", "XGS600_T2", "XGS600_T3", "XGS600_T4"],
            index = pd.DatetimeIndex([], tz = datetime.datetime.now().astimezone().tzinfo))

        # Widgets preconfigurados
        self.coms_74FSAG = module_74fsag.Coms74FSAG("COM6")
        self.widget_74FSAG = module_74fsag.Widget74FSAG(self.coms_74FSAG)
        self.coms_XGS600 = module_xgs600.ComsXGS600("COM10")
        self.widget_XGS600 = module_xgs600.WidgetXGS600(self.coms_XGS600)
        self.widget_display = module_tools.WidgetDisplay()

        # Configuracion del widget de grafico
        time_axis = module_tools.TimeAxis(orientation='bottom')
        self.widget_plot = pyqtgraph.PlotWidget(axisItems={'bottom': time_axis})
        self.widget_plot.setLogMode(x=False, y=True)
        self.widget_plot.showGrid(x=True, y=True, alpha=0.3)
        self.line_plot = []
        self.line_plot.append(self.widget_plot.plot([], [], pen=pyqtgraph.mkPen("white", width=1)))
        self.line_plot.append(self.widget_plot.plot([], [], pen=pyqtgraph.mkPen("red", width=1)))
        self.line_plot.append(self.widget_plot.plot([], [], pen=pyqtgraph.mkPen("green", width=1)))
        self.line_plot.append(self.widget_plot.plot([], [], pen=pyqtgraph.mkPen("blue", width=1)))
        self.line_plot.append(self.widget_plot.plot([], [], pen=pyqtgraph.mkPen("purple", width=1)))
        
        # Elementos graficos de organizacion
        self.widget_main = QtWidgets.QWidget()
        self.splitter_side = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.splitter_nums = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.tab_panel = QtWidgets.QTabWidget()

        # Timer para bucle
        self.timer_read = QtCore.QTimer()
        self.timer_read.timeout.connect(self.read_rutine)

        # Ubicacion de elementos en el layout
        self.setCentralWidget(self.widget_main)
        self.layout_main = QtWidgets.QVBoxLayout()
        self.widget_main.setLayout(self.layout_main)
        self.layout_main.addWidget(self.splitter_side)
        self.splitter_side.addWidget(self.splitter_nums)
        self.splitter_side.addWidget(self.widget_plot)
        self.splitter_nums.addWidget(self.widget_display)
        self.splitter_nums.addWidget(self.tab_panel)
        self.tab_panel.addTab(self.widget_74FSAG, "74FSAG")
        self.tab_panel.addTab(self.widget_XGS600, "XGS600")

        # Configura condiciones iniciales de tamaño para la ventana
        self.resize(1280, 720)
        self.splitter_side.setSizes([300, 980])
        self.splitter_side.setStretchFactor(0, 0)
        self.splitter_side.setStretchFactor(1, 1)
        self.splitter_nums.setStretchFactor(0, 0)
        self.splitter_nums.setStretchFactor(1, 1)

        # Agrega elementos al menubar
        self.menu_bar = self.menuBar()
        self.menu_save = self.menu_bar.addAction("Guardar")
        self.menu_ports = self.menu_bar.addAction("Seleccionar Puertos")

        # Conexion de funciones a elementos
        self.menu_save.triggered.connect(self.handle_save_plot)
        self.menu_ports.triggered.connect(self.handle_select_ports)

        # Conexion a señales de herramientas
        self.coms_XGS600.signal_preasure.connect(self.handle_preasure)

        # Inicia timer de rutina de lectura de presion
        self.timer_read.start(1000)
    
    # [Funcion del timer bucle]
    def read_rutine(self):
        self.coms_XGS600.send_serial("0F")
        self.coms_74FSAG.send_serial(224, False)
        
    # [Funcion handle de señal presion XGS600]
    def handle_preasure(self):
        data = [self.coms_74FSAG.dict_windows[224].decoded()] + self.coms_XGS600.values_preasure

        # Añade datos al dataframe
        ts = pd.Timestamp(self.coms_XGS600.timestamp, tz = datetime.datetime.now().astimezone().tzinfo)
        self.dataframe.loc[ts] = data
        self.widget_display.update_labels(data)

        # Actualiza el grafico
        x = self.dataframe.index.view("int64") // 10**9
        self.line_plot[0].setData(x, self.dataframe["74FS"].values)
        self.line_plot[1].setData(x, self.dataframe["XGS600_T1"].values)
        self.line_plot[2].setData(x, self.dataframe["XGS600_T2"].values)
        self.line_plot[3].setData(x, self.dataframe["XGS600_T3"].values)
        self.line_plot[4].setData(x, self.dataframe["XGS600_T4"].values)   

    # [Funcion handle de guardar plot]
    def handle_save_plot(self):
        if self.dataframe.empty:
            QtWidgets.QMessageBox.warning(self,"", "No hay datos en el grafico para guardar")
            return
        
        # Abre dialogo de guaradado con opciones de formato
        file_path, format = QtWidgets.QFileDialog.getSaveFileName(self, "Guardar datos", "",
            "CSV (*.csv);;Excel (*.xlsx);;XML (*.xml)")
        
        # Procesado del guardado
        if not file_path: return
        try:
            if format.startswith("CSV") or file_path.lower().endswith(".csv"):
                if not file_path.lower().endswith(".csv"):
                    file_path += ".csv"
                self.dataframe.to_csv(file_path, index=True)
            elif format.startswith("Excel") or file_path.lower().endswith(".xlsx"):
                if not file_path.lower().endswith(".xlsx"):
                    file_path += ".xlsx"
                self.dataframe.to_excel(file_path, index=True)
            elif format.startswith("XML") or file_path.lower().endswith(".xml"):
                if not file_path.lower().endswith(".xml"):
                    file_path += ".xml"
                self.dataframe.to_xml(file_path, index=True)
            QtWidgets.QMessageBox.information(self, "", f"Archivo guardado en:\n{file_path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "", f"No se pudo guardar el archivo:\n{e}")

    # [Funcion handle de seleccionar puertos]
    def handle_select_ports(self):
        dialog_selector = module_tools.PortSelector()
        if dialog_selector.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            puertos = dialog_selector.get_selected_ports()
            self.coms_74FSAG.select_port(puertos[0])
            self.coms_XGS600.select_port(puertos[1])

# --------------------------------------------------------------

# --- INICIALIZADOR ---
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Opciones Esteticas
    QtWidgets.QApplication.setStyle("Fusion")
    
    # Muestra la ventana principal
    window = MainWindow()
    window.show()
    window.showMaximized()
    sys.exit(app.exec())