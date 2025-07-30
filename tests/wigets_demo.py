import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QLCDNumber, QProgressBar, QPushButton, QDial,
    QSlider, QCheckBox, QComboBox, QSpinBox, QDoubleSpinBox,
    QGroupBox, QTextEdit, QTabWidget
)
from PyQt6.QtCore import Qt


class VacuumSystemDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Vacuum System UI Demo")
        self.setMinimumSize(1000, 700)
        layout = QVBoxLayout()
        tabs = QTabWidget()

        # Tabs
        tabs.addTab(self.create_display_tab(), "Display")
        tabs.addTab(self.create_controls_tab(), "Controls")
        tabs.addTab(self.create_logs_tab(), "Logs")

        layout.addWidget(tabs)
        self.setLayout(layout)

    def create_display_tab(self):
        tab = QWidget()
        layout = QHBoxLayout()

        # Vacuum Pressure Display
        pressure_display = QGroupBox("Vacuum Pressure (mbar)")
        pressure_layout = QVBoxLayout()
        lcd = QLCDNumber()
        lcd.display(0.0045)
        pressure_layout.addWidget(lcd)
        pressure_display.setLayout(pressure_layout)

        # Temperature Display
        temp_display = QGroupBox("Temperature (°C)")
        temp_layout = QVBoxLayout()
        temp_lcd = QLCDNumber()
        temp_lcd.display(22.3)
        temp_layout.addWidget(temp_lcd)
        temp_display.setLayout(temp_layout)

        # System Load (Progress Bar)
        load_display = QGroupBox("System Load")
        load_layout = QVBoxLayout()
        progress = QProgressBar()
        progress.setValue(65)
        load_layout.addWidget(progress)
        load_display.setLayout(load_layout)

        # Sensor Status
        status_box = QGroupBox("Sensor Status")
        status_layout = QVBoxLayout()
        status_layout.addWidget(QLabel("Pressure Sensor: OK"))
        status_layout.addWidget(QLabel("Temp Sensor: OK"))
        status_layout.addWidget(QLabel("Vacuum Pump: RUNNING"))
        status_box.setLayout(status_layout)

        # Arrange
        layout.addWidget(pressure_display)
        layout.addWidget(temp_display)
        layout.addWidget(load_display)
        layout.addWidget(status_box)
        tab.setLayout(layout)
        return tab

    def create_controls_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Manual Controls Group
        manual_group = QGroupBox("Manual Controls")
        manual_layout = QHBoxLayout()

        # Dial control for pump speed
        dial = QDial()
        dial.setValue(50)
        dial.setNotchesVisible(True)
        manual_layout.addWidget(QLabel("Pump Speed"))
        manual_layout.addWidget(dial)

        # Slider for valve opening
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setValue(30)
        manual_layout.addWidget(QLabel("Valve Opening"))
        manual_layout.addWidget(slider)

        # SpinBox for pressure setpoint
        pressure_spin = QDoubleSpinBox()
        pressure_spin.setSuffix(" mbar")
        pressure_spin.setDecimals(4)
        pressure_spin.setMaximum(1.0)
        pressure_spin.setValue(0.0100)
        manual_layout.addWidget(QLabel("Setpoint"))
        manual_layout.addWidget(pressure_spin)

        manual_group.setLayout(manual_layout)

        # System Options Group
        options_group = QGroupBox("System Options")
        options_layout = QHBoxLayout()
        check_vacuum = QCheckBox("Enable Vacuum")
        check_temp = QCheckBox("Enable Temp Monitor")
        combo_mode = QComboBox()
        combo_mode.addItems(["Auto", "Manual", "Standby"])

        options_layout.addWidget(check_vacuum)
        options_layout.addWidget(check_temp)
        options_layout.addWidget(QLabel("Mode:"))
        options_layout.addWidget(combo_mode)

        options_group.setLayout(options_layout)

        # Input Fields Group
        input_group = QGroupBox("Configuration Inputs")
        input_layout = QVBoxLayout()
        input_layout.addWidget(QLabel("Vacuum Target Name:"))
        input_layout.addWidget(QLineEdit("MainChamber01"))
        input_layout.addWidget(QLabel("Calibration Constant:"))
        input_layout.addWidget(QLineEdit("0.9832"))

        input_group.setLayout(input_layout)

        # Buttons Group
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(QPushButton("Start System"))
        buttons_layout.addWidget(QPushButton("Stop System"))
        buttons_layout.addWidget(QPushButton("Emergency Shutdown"))

        # Add to main layout
        layout.addWidget(manual_group)
        layout.addWidget(options_group)
        layout.addWidget(input_group)
        layout.addLayout(buttons_layout)

        tab.setLayout(layout)
        return tab

    def create_logs_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("System Log:"))
        log_box = QTextEdit()
        log_box.setReadOnly(True)
        log_box.setPlainText("04:22:03 - System booted.\n04:22:05 - Vacuum pump ON.\n04:22:10 - Pressure at 0.0045 mbar.")
        layout.addWidget(log_box)
        tab.setLayout(layout)
        return tab


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VacuumSystemDemo()
    window.show()
    sys.exit(app.exec())
