# === [INTERFAZ DE USUARIO DE SISTEMA DE PRESION DEL INM] ===
# David Miguel Garcia Palacios
# Universidad Nacional de Colombia Sede Bogota

# [Librerias de Terceros]
import sys, datetime
import pyqtgraph
import pandas as pd
import numpy as np
from PyQt6 import QtCore, QtWidgets, QtGui

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
            columns = ["74FS", "XGS600_T1", "XGS600_T2", "XGS600_T3", "XGS600_T4"])
        self.dataframe.index = pd.to_datetime(self.dataframe.index)

        # Widgets preconfigurados
        self.coms_74FSAG = module_74fsag.Coms74FSAG("COM6")
        self.widget_74FSAG = module_74fsag.Widget74FSAG(self.coms_74FSAG)
        self.coms_XGS600 = module_xgs600.ComsXGS600("COM10")
        self.widget_display = WidgetDisplay()

        # Configuracion del widget de grafico
        time_axis = TimeAxis(orientation='bottom')
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
        self.tab_panel.addTab(self.coms_XGS600, "XGS600")

        # Configura condiciones iniciales de tamaño para la ventana
        self.resize(1280, 720)
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
        self.dataframe.loc[self.coms_XGS600.timestamp] = (data)
        self.widget_display.update_labels(data)

        # Actualiza el grafico
        self.line_plot[0].setData(self.dataframe.index.values, self.dataframe["74FS"].values)
        self.line_plot[1].setData(self.dataframe.index.values, self.dataframe["XGS600_T1"].values)
        self.line_plot[2].setData(self.dataframe.index.values, self.dataframe["XGS600_T2"].values)
        self.line_plot[3].setData(self.dataframe.index.values, self.dataframe["XGS600_T3"].values)
        self.line_plot[4].setData(self.dataframe.index.values, self.dataframe["XGS600_T4"].values)   

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
        print("boop!")
        dialog_selector = module_tools.PortSelector()
        if dialog_selector.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            puertos = dialog_selector.get_selected_ports()
            self.coms_74FSAG.select_port(puertos[0])
            self.coms_XGS600.select_port(puertos[1])

# --- WIDGET DISPLAY MEDIDAS ---
# Widget para la visulaizacion de medidas de presion
class WidgetDisplay(QtWidgets.QWidget):
    
    # [Constructor]
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Widget Display")

        # Labels para el display
        self.label_preasure = []
        for i in range(5):
            label = QtWidgets.QLabel("--")
            label.setFont(QtGui.QFont("Courier New", 24, QtGui.QFont.Weight.Bold))
            label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
            self.label_preasure.append(label)
        
        # Ajsutar colores de los label
        self.label_preasure[0].setStyleSheet("color: black")
        self.label_preasure[1].setStyleSheet("color: red")
        self.label_preasure[2].setStyleSheet("color: green")
        self.label_preasure[3].setStyleSheet("color: blue")
        self.label_preasure[4].setStyleSheet("color: purple")

        # Ubicacion de elementos en el layout
        self.layout_main = QtWidgets.QFormLayout()
        self.setLayout(self.layout_main)
        self.layout_main.addRow("Sensor 74FS", self.label_preasure[0])
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.layout_main.addRow(separator)
        self.layout_main.addRow("Sensor XGS600 [T1]", self.label_preasure[1])
        self.layout_main.addRow("Sensor XGS600 [T2]", self.label_preasure[2])
        self.layout_main.addRow("Sensor XGS600 [T3]", self.label_preasure[3])
        self.layout_main.addRow("Sensor XGS600 [T4]", self.label_preasure[4])

    # [Funcion para actualizacion de los labels]    
    def update_labels(self, data):
        for idx in range(len(data)):
            self.label_preasure[idx].setText(str(data[idx]))

# --- EJES DE TIEMPO ---
# Widget para la visulaizacion de medidas de presion
class TimeAxis(pyqtgraph.AxisItem):

    # [Constructor]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    # [Obtencion de ejes de tiempo]
    def tickStrings(self, values, scale, spacing):
        return [datetime.datetime.fromtimestamp(v / 1e9).strftime("%H:%M:%S") for v in values]



# --- INICIALIZADOR ---
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Opciones Esteticas
    QtWidgets.QApplication.setStyle("Fusion")
    
    # Muestra la ventana principal
    window = MainWindow()
    window.show()
    sys.exit(app.exec())