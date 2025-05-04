import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout,
    QLabel, QPushButton, QComboBox, QLineEdit, QSlider,
    QDial, QProgressBar, QSpinBox, QDoubleSpinBox, QLCDNumber,
    QCheckBox, QRadioButton, QPlainTextEdit, QDateTimeEdit,
    QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout
)
from PyQt6.QtCore import Qt, QDateTime

# Para gráficos Matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=4, height=3, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(fig)
        self.setParent(parent)
        self.plot()

    def plot(self):
        x = np.linspace(0, 2 * np.pi, 100)
        y = np.sin(x)
        ax = self.figure.add_subplot(111)
        ax.plot(x, y)
        ax.set_title('Señal Senoidal de Ejemplo')
        ax.grid(True)
        self.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo PyQt6: Vacío, Presión y Más")
        central = QWidget()
        layout = QGridLayout()

        # Elementos Vacío
        dial = QDial()
        dial.setValue(30)
        layout.addWidget(QLabel("Nivel de Vacío (Dial):"), 0, 0)
        layout.addWidget(dial, 0, 1)

        lcd = QLCDNumber()
        lcd.display(420)
        layout.addWidget(QLabel("Lectura Vacío (LCD):"), 1, 0)
        layout.addWidget(lcd, 1, 1)

        pump_combo = QComboBox()
        pump_combo.addItems(["Bomba A", "Bomba B", "Bomba C"])
        pump_combo.setCurrentIndex(1)
        layout.addWidget(QLabel("Seleccionar Bomba:"), 2, 0)
        layout.addWidget(pump_combo, 2, 1)

        fine_tune = QDoubleSpinBox()
        fine_tune.setRange(0.0, 1.0)
        fine_tune.setSingleStep(0.1)
        fine_tune.setValue(0.5)
        layout.addWidget(QLabel("Ajuste Fino (0-1):"), 3, 0)
        layout.addWidget(fine_tune, 3, 1)

        # Elementos Presión
        slider = QSlider(Qt.Orientation.Vertical)
        slider.setRange(0, 100)
        slider.setValue(75)
        layout.addWidget(QLabel("Presión (Slider Vertical):"), 0, 2)
        layout.addWidget(slider, 1, 2, 3, 1)

        spin = QSpinBox()
        spin.setRange(0, 200)
        spin.setValue(120)
        layout.addWidget(QLabel("SpinBox Presión:"), 4, 0)
        layout.addWidget(spin, 4, 1)

        bar = QProgressBar()
        bar.setOrientation(Qt.Orientation.Vertical)
        bar.setRange(0, 100)
        bar.setValue(60)
        layout.addWidget(QLabel("Indicador de Presión:"), 4, 2)
        layout.addWidget(bar, 5, 2)

        valve_combo = QComboBox()
        valve_combo.addItems(["Válvula X", "Válvula Y"])
        valve_combo.setCurrentIndex(0)
        layout.addWidget(QLabel("Selector de Válvula:"), 5, 0)
        layout.addWidget(valve_combo, 5, 1)

        # Elementos Generales
        line = QLineEdit()
        line.setText("Demo texto")
        layout.addWidget(QLabel("Entrada de Texto:"), 6, 0)
        layout.addWidget(line, 6, 1)

        button = QPushButton("Click Demo")
        layout.addWidget(QLabel("Botón:"), 7, 0)
        layout.addWidget(button, 7, 1)

        checkbox = QCheckBox("Activado")
        checkbox.setChecked(True)
        layout.addWidget(QLabel("Checkbox:"), 8, 0)
        layout.addWidget(checkbox, 8, 1)

        radio = QRadioButton("Opción 1")
        radio.setChecked(True)
        layout.addWidget(QLabel("RadioButton:"), 9, 0)
        layout.addWidget(radio, 9, 1)

        text = QPlainTextEdit()
        text.setPlainText("Texto de demostración en PLAINTEXT")
        layout.addWidget(QLabel("Editor de Texto:"), 10, 0)
        layout.addWidget(text, 10, 1, 2, 1)

        dt = QDateTimeEdit()
        dt.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(QLabel("Fecha y Hora:"), 12, 0)
        layout.addWidget(dt, 12, 1)

        # Tabla
        table = QTableWidget(2, 2)
        table.setItem(0, 0, QTableWidgetItem("A"))
        table.setItem(0, 1, QTableWidgetItem("B"))
        table.setItem(1, 0, QTableWidgetItem("C"))
        table.setItem(1, 1, QTableWidgetItem("D"))
        layout.addWidget(QLabel("Tabla 2x2:"), 13, 0)
        layout.addWidget(table, 13, 1)

        # Árbol
        tree = QTreeWidget()
        tree.setHeaderLabels(["Elementos"])
        root = QTreeWidgetItem(tree, ["Raíz"])
        child1 = QTreeWidgetItem(root, ["Hijo 1"])
        child2 = QTreeWidgetItem(root, ["Hijo 2"])
        tree.expandAll()
        layout.addWidget(QLabel("Vista de Árbol:"), 14, 0)
        layout.addWidget(tree, 14, 1)

        # Gráfico embebido
        plot = PlotCanvas(self, width=4, height=3)
        layout.addWidget(QLabel("Gráfico de Ejemplo:"), 6, 2)
        layout.addWidget(plot, 7, 2, 5, 1)

        # DIAL grande estilo galvanómetro
        galvo = QDial()
        galvo.setMinimum(0)
        galvo.setMaximum(100)
        galvo.setValue(50)
        galvo.setNotchesVisible(True)
        layout.addWidget(QLabel("Galvanómetro (Dial):"), 15, 0)
        layout.addWidget(galvo, 15, 1)

        central.setLayout(layout)
        self.setCentralWidget(central)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
