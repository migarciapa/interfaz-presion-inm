# === [INTERFAZ DE USUARIO DE SISTEMA DE PRESION DEL INM] ===
# David Miguel Garcia Palacios
# Universidad Nacional de Colombia Sede Bogota

# [Librerias de Terceros]
import os, sys, pyqtgraph, datetime
import pandas as pd
import numpy as np
from PyQt6 import QtCore, QtWidgets, QtGui
from pyqtgraph import exporters

# [Modulos importados]
import module_74fsag, module_xgs600, module_tools

# --- APLICACION PRINCIPAL ---
class MainWindow(QtWidgets.QMainWindow):

    # [Constructor]
    def __init__(self, ports):
        super().__init__()

        # Creacion de dataframe de presion
        self.dataframe = pd.DataFrame(
            columns = ["TT_74FS", "XGS600_T1", "XGS600_T2", "XGS600_T3", "XGS600_T4"],
            index = pd.DatetimeIndex([], tz = datetime.datetime.now().astimezone().tzinfo))

        # Widgets preconfigurados
        self.coms_74FSAG = module_74fsag.Coms74FSAG(ports[0])
        self.widget_74FSAG = module_74fsag.Widget74FSAG(self.coms_74FSAG)
        self.coms_XGS600 = module_xgs600.ComsXGS600(ports[1])
        self.widget_XGS600 = module_xgs600.WidgetXGS600(self.coms_XGS600)
        self.widget_display = module_tools.WidgetDisplay()
        self.widget_controls = module_tools.WidgetGraphControls()

        # Configuracion del widget de grafico
        time_axis = module_tools.TimeAxis(orientation='bottom')
        self.widget_plot = pyqtgraph.PlotWidget(axisItems={'bottom': time_axis})
        self.widget_plot.setLogMode(x=False, y=True)
        self.widget_plot.showGrid(x=True, y=True, alpha=0.3)
        self.line_plot = []
        self.line_plot.append(self.widget_plot.plot([], [], pen=pyqtgraph.mkPen("#FFFFFF", width=1)))
        self.line_plot.append(self.widget_plot.plot([], [], pen=pyqtgraph.mkPen("#FF0000", width=1)))
        self.line_plot.append(self.widget_plot.plot([], [], pen=pyqtgraph.mkPen("#00FF00", width=1)))
        self.line_plot.append(self.widget_plot.plot([], [], pen=pyqtgraph.mkPen("#0000FF", width=1)))
        self.line_plot.append(self.widget_plot.plot([], [], pen=pyqtgraph.mkPen("#FF00FF", width=1)))
        
        # Elementos graficos de organizacion
        self.widget_main = QtWidgets.QWidget()
        self.splitter_main = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.splitter_sidebar = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.splitter_graph = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.tab_panel = QtWidgets.QTabWidget()

        # Ubicacion de elementos en el layout
        self.setCentralWidget(self.widget_main)
        self.layout_main = QtWidgets.QVBoxLayout()
        self.widget_main.setLayout(self.layout_main)
        self.layout_main.addWidget(self.splitter_main)
        self.splitter_main.addWidget(self.splitter_sidebar)
        self.splitter_sidebar.addWidget(self.widget_display)
        self.splitter_sidebar.addWidget(self.tab_panel)
        self.splitter_main.addWidget(self.splitter_graph)
        self.splitter_graph.addWidget(self.widget_plot)
        self.splitter_graph.addWidget(self.widget_controls)
        self.tab_panel.addTab(self.widget_74FSAG, "74FSAG")
        self.tab_panel.addTab(self.widget_XGS600, "XGS600")

        # Configura condiciones iniciales de tamaño para la ventana
        self.resize(1280, 720)
        self.splitter_main.setSizes([300, 980])
        self.splitter_main.setStretchFactor(0, 0)
        self.splitter_main.setStretchFactor(1, 1)
        self.splitter_sidebar.setStretchFactor(0, 0)
        self.splitter_sidebar.setStretchFactor(1, 1)
        self.splitter_graph.setStretchFactor(0, 1)
        self.splitter_graph.setStretchFactor(1, 0)

        # Agrega elementos al menubar
        self.menu_bar = self.menuBar()
        self.menu_save = self.menu_bar.addAction("Guardar Datos")
        self.menu_save_image = self.menu_bar.addAction("Guardar Vista")
        self.menu_ports = self.menu_bar.addAction("Seleccionar Puertos")

        # Prepara la barra de estados
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Autosave: En espera")

        # Conexion de funciones a elementos
        self.menu_save.triggered.connect(self.handle_save_plot)
        self.menu_save_image.triggered.connect(self.handle_save_image)
        self.menu_ports.triggered.connect(self.handle_select_ports)

        # Conexion a señales de herramientas
        self.coms_XGS600.signal_preasure.connect(self.handle_preasure)
        self.widget_controls.signal_reset.connect(self.handle_plot_reset)
        self.widget_controls.signal_timeset.connect(self.handle_set_interval)

        # Timers para rutinas de lectura actualizacion y autoguardado
        self.timer_read = QtCore.QTimer()
        self.timer_read.timeout.connect(self.read_rutine)
        self.timer_read.start(1000)
        self.timer_changes = QtCore.QTimer()
        self.timer_changes.timeout.connect(self.coms_74FSAG.read_changes)
        self.timer_changes.start(2000)
        self.timer_autosave = QtCore.QTimer()
        self.timer_autosave.timeout.connect(self.autosave)
        self.timer_autosave.start(120000)
    
    # [Funcion del timer de lectura]
    def read_rutine(self):
        self.coms_XGS600.send_serial("0F")
        self.coms_74FSAG.send_serial(224, False)
    
    # [Funcion del timer de autoguardado]
    def autosave(self):
        if self.dataframe.empty:
            self.status_bar.showMessage("Autosave: No hay datos en el grafico")
            return
        filename = os.path.dirname(sys.argv[0]) + r"\pressure_autosave.csv"
        self.dataframe.to_csv(filename, index = True)
        time = datetime.datetime.now().strftime("%H:%M:%S")
        self.status_bar.showMessage(f"Autosave: Guardado [{time}] en {filename}")
        
    # [Funcion handle de señal presion XGS600]
    def handle_preasure(self):
        if self.coms_74FSAG.active:
            data = [self.coms_74FSAG.dict_windows[224].decoded()] + self.coms_XGS600.values_preasure
        else:
            data = [np.nan] + self.coms_XGS600.values_preasure

        # Añade datos al dataframe
        ts = pd.Timestamp(self.coms_XGS600.timestamp, tz = datetime.datetime.now().astimezone().tzinfo)
        self.dataframe.loc[ts] = data
        self.widget_display.update_labels(data)

        # Actualiza el grafico
        x = self.dataframe.index.view("int64") // 10**9
        self.line_plot[0].setData(x, self.dataframe["TT_74FS"].values)
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
                df = self.dataframe.copy()
                df.index = df.index.tz_localize(None)
                df.to_excel(file_path, index=True)
            elif format.startswith("XML") or file_path.lower().endswith(".xml"):
                if not file_path.lower().endswith(".xml"):
                    file_path += ".xml"
                self.dataframe.to_xml(file_path, index=True)
            QtWidgets.QMessageBox.information(self, "", f"Archivo guardado en:\n{file_path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "", f"No se pudo guardar el archivo:\n{e}")

    # [Funcion handle de guardado de imagen]
    def handle_save_image(self):
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Guardar Imagen", "",
        "Imagen PNG (*.png);;Imagen JPG (*.jpg);;Imagen TIFF (*.tiff);;Imagen BMP (*.bmp)")

        # Procesado del guardado
        if file_path:
            exporter = exporters.ImageExporter(self.widget_plot.plotItem)
            exporter.export(file_path)
            QtWidgets.QMessageBox.information(self, "", f"Archivo guardado en:\n{file_path}")

    # [Funcion handle de seleccionar puertos]
    def handle_select_ports(self):
        dialog_selector = module_tools.PortSelector()
        if dialog_selector.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            puertos = dialog_selector.get_selected_ports()
            self.coms_74FSAG.select_port(puertos[0])
            self.coms_XGS600.select_port(puertos[1])

    # [Funcion handle limpiar el grafico]
    def handle_plot_reset(self):
        response = QtWidgets.QMessageBox.question(self, "",
            "¿Esta seguro que desea limpiar los datos del grafico?")
        if response == QtWidgets.QMessageBox.StandardButton.Yes:
            self.dataframe = self.dataframe.iloc[0:0]

    # [Funcion handle cambair el tiempo de intervalo entre medidas]
    def handle_set_interval(self):
        seconds = self.widget_controls.spinbox_time.value()
        self.timer_read.setInterval(1000 * seconds)

# --------------------------------------------------------------

# --- INICIALIZADOR PRINCIPAL ---
app = QtWidgets.QApplication(sys.argv)
app.setApplicationName("UI-Presion-INM")
app.setApplicationDisplayName("Interfaz Sistema de Presion INM")

# [Funcion para la obtencion de rutas relativas]
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Opciones Esteticas
icon_path = resource_path("app/resources/app_icon.ico")
app.setWindowIcon(QtGui.QIcon(icon_path))
QtWidgets.QApplication.setStyle("Fusion")
qss_path = resource_path("app/resources/stylesheet.qss")
style = open(qss_path, "r", encoding="utf-8")
app.setStyleSheet(style.read())

# Pregunta por puertos inciales
dialog_selector = module_tools.PortSelector()
if dialog_selector.exec() == QtWidgets.QDialog.DialogCode.Accepted:
    puertos = dialog_selector.get_selected_ports()
else: sys.exit(0)
    
# Muestra la ventana principal
window = MainWindow(puertos)
window.show()
window.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
window.showMaximized()

sys.exit(app.exec())