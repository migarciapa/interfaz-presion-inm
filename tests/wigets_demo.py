import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGroupBox, QLabel

class CollapsibleGroupBoxDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Panel Expandible con colapso real")
        self.resize(300, 200)

        layout = QVBoxLayout()

        label_encima = QLabel("Esto está encima del panel expandible")
        layout.addWidget(label_encima)

        self.group_box = QGroupBox("Panel Expandible")
        self.group_box.setCheckable(True)
        self.group_box.setChecked(True)

        self.inner_widget = QWidget()  # contenedor interno para contenido
        inner_layout = QVBoxLayout()
        inner_layout.addWidget(QLabel("Contenido del panel"))
        inner_layout.addWidget(QLabel("Más contenido"))
        self.inner_widget.setLayout(inner_layout)

        group_layout = QVBoxLayout()
        group_layout.addWidget(self.inner_widget)
        self.group_box.setLayout(group_layout)

        layout.addWidget(self.group_box)
        self.setLayout(layout)

        # Conectamos toggle para mostrar/ocultar contenido
        self.group_box.toggled.connect(self.inner_widget.setVisible)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CollapsibleGroupBoxDemo()
    window.show()
    sys.exit(app.exec())