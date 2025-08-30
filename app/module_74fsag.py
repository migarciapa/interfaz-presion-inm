# === [MODULO DE CONTROLADOR TWISTORR 74FSAG] ===
# David Miguel Garcia Palacios
# Universidad Nacional de Colombia Sede Bogota

# [Librerias de Terceros]
import sys
from PyQt6 import QtWidgets, QtSerialPort, QtCore

# --- COMUNICACION 74FSAG ---
# Clase backend para comunicaciones y consola del controlador
class Coms74FSAG(QtWidgets.QWidget):
    
    # [Constructor]
    def __init__(self, port_name: str = "COM11"):
        super().__init__()
        self.setWindowTitle("Consola Controlador 74FSAG")

        # Creacion de boleano para la obtencion del estado de respuestas
        self.active = False

        # Creacion del diccionario de ventanas para el mapeo de datos
        self.dict_windows = {
            000: DataWindow("Maquina encendida", DataWindow.to_bool),
            100: DataWindow("Arranque suave", DataWindow.to_bool),
            120: DataWindow("Setpoint frecuencia de la bomba", DataWindow.to_int),
            157: DataWindow("Gas cargado", DataWindow.to_int),
            163: DataWindow("Unidades de presion", DataWindow.to_int),
            200: DataWindow("Corriente de la bomba", DataWindow.to_int),
            201: DataWindow("Voltaje de la bomba", DataWindow.to_int),
            202: DataWindow("Potencia de la bomba", DataWindow.to_int),
            203: DataWindow("Frecuencia de la bomba", DataWindow.to_int),
            204: DataWindow("Temperatura de la bomba", DataWindow.to_int),
            205: DataWindow("Estado de la bomba", DataWindow.to_state_pump),
            224: DataWindow("Lectura presion", DataWindow.to_float),
            257: DataWindow("Estado del indicador", DataWindow.to_state_gauge),
            300: DataWindow("Tiempo activo de la bomba", DataWindow.to_int),
            301: DataWindow("Numero de ciclo", DataWindow.to_int),
            302: DataWindow("Tiempo activo total", DataWindow.to_int)
        }

        # Elementos de control de cola de mensajes
        self.queue = []
        self.waiting_response = False
        self.timer_response = QtCore.QTimer()
        self.timer_response.setInterval(1000)
        self.timer_response.timeout.connect(self.handle_timeout_response)

        # Elementos graficos para consola
        self.input_window = QtWidgets.QLineEdit()
        self.input_data = QtWidgets.QLineEdit()
        self.button_read = QtWidgets.QPushButton("Leer")
        self.button_write = QtWidgets.QPushButton("Escribir")
        self.text_console = QtWidgets.QPlainTextEdit()
        self.text_console.setReadOnly(True)

        # Creacion del puerto serial y buffer de comunicacion
        self.buffer = bytes()
        self.serial = QtSerialPort.QSerialPort()
        self.serial.setBaudRate(9600)
        self.serial.setDataBits(QtSerialPort.QSerialPort.DataBits.Data8)
        self.serial.setParity(QtSerialPort.QSerialPort.Parity.NoParity)
        self.serial.setStopBits(QtSerialPort.QSerialPort.StopBits.OneStop)
        self.serial.setFlowControl(QtSerialPort.QSerialPort.FlowControl.NoFlowControl)
        self.select_port(port_name)

        # Conexion a recepcion de datos
        self.serial.readyRead.connect(self.recive_serial)
        
        # Ubicacion de elementos en layout
        self.layout_main = QtWidgets.QFormLayout()
        self.setLayout(self.layout_main)
        self.layout_main.addRow("Ventana (###) [Int]:", self.input_window)
        self.layout_main.addRow("Dato:", self.input_data)
        layout_buttons = QtWidgets.QHBoxLayout()
        self.layout_main.addRow(layout_buttons)
        layout_buttons.addWidget(self.button_read)
        layout_buttons.addWidget(self.button_write)
        self.layout_main.addRow(self.text_console)

        # Conexion de funciones handle
        self.button_read.clicked.connect(self.handle_click_read)
        self.button_write.clicked.connect(self.handle_click_write)

    # [Metodo para seleccionar o cambiar puerto serial]
    def select_port(self, port_name: str):
        if self.serial.isOpen():
            self.serial.close()
            print("[74FSAG] Puerto serial cerrado.")
        self.serial.setPortName(port_name)
        if self.serial.open(QtCore.QIODevice.OpenModeFlag.ReadWrite):
            print(f"[74FSAG] Puerto {port_name} abierto correctamente!")
            self.read_all()
        else:
            QtWidgets.QMessageBox.warning(self, "",
                f"[74FSAG] No se pudo abrir el puerto {port_name}.\n"
                f"Error: {self.serial.errorString()}")
            self.active = False

    # [Recepcion de mensajes del serial]
    def recive_serial(self):
        self.buffer += bytes(self.serial.readAll())
        idx = self.buffer.find(b'\x03')

        # Procesado de mensaje
        if idx != -1 and len(self.buffer) >= idx + 3:
            idx += 3
            line = self.buffer[:idx].decode(errors = "ignore")
            self.buffer = self.buffer[idx:]
            line = line[line.find('\x02') + 1 :line.find('\x03')].strip()
            self.text_console.appendPlainText(line)

            # Aviso de llegada del mensaje
            self.timer_response.stop()
            self.waiting_response = False
            self.next_queue()

            # Asignacion a ventana
            if len(line) >= 5:
                window = int(line[:3])
                data = line[4:]
                try:
                    self.dict_windows[window].set(data)
                    self.active = True
                except Exception as e:
                    print(f"Ventana desconocida {window} reporta {data}")

            # Caso de respuesta error
            else:
                if line == "2": QtWidgets.QMessageBox.warning(self, "",
                    "[74FSAG] 0x32 = La ventana ingresada no es valida")
                if line == "3": QtWidgets.QMessageBox.warning(self, "",
                    "[74FSAG] 0x33 = El formato del dato ingresado no es adecudado")
                if line == "4": QtWidgets.QMessageBox.warning(self, "",
                    "[74FSAG] 0x34 = El dato ingresado esta fuera de rango")
                if line == "5": QtWidgets.QMessageBox.warning(self, "",
                    "[74FSAG] 0x35 = La ventana ingresada esta bloqueada\n"
                    "Por favor verifique que el controlador este en modo serial")
    
    # [Envio de mensajes del serial]
    def send_serial(self, window: int, write: bool, data: str = ""):
        window = str(window).zfill(3).encode()
        write = str(int(write)).encode()
        data = data.encode()
        msg = b"\x80" + window + write + data + b"\x03"
        crc = 0
        for byte in msg: crc ^= byte
        crc = f"{crc:02X}".encode()
        line = b"\x02" + msg + crc
        self.queue.append(line)
        if not self.waiting_response:
            self.next_queue()

    # [Control de cola de mensajes]
    def next_queue(self):
        if not self.queue:
            self.waiting_response = False
            return
        line = self.queue.pop(0)
        try: self.serial.write(line)
        except Exception as e: self.active = False
        self.text_console.appendPlainText(repr(line))
        self.waiting_response = True
        self.timer_response.start()

    # [Handle de timeout de la respuesta]
    def handle_timeout_response(self):
        self.text_console.appendPlainText("Timeout sin respuesta - Limpiando Cola")
        self.waiting_response = False
        self.queue = []
        self.active = False

    # [Solicitud lectura de cambios rapidos]
    def read_changes(self):
        windows = [200, 201, 202, 203, 204, 205, 257, 300, 301, 302]
        for window in windows: self.send_serial(window, False)

    # [Solicitud lectura de todas las ventanas disponibles]
    def read_all(self):
        for window in self.dict_windows.keys():
            self.send_serial(window, False)
    
    # [Handle de click boton de lectura]
    def handle_click_read(self):
        window = int(self.input_window.text())
        self.send_serial(window, False)

    # [Handle de click boton de escritura]
    def handle_click_write(self):
        window = int(self.input_window.text())
        data = self.input_data.text()
        self.send_serial(window, True, data)

# --- WIDGET 74FSAG ---
# Clase para la interfaz de usuario con el controlador 74FSAG
class Widget74FSAG(QtWidgets.QWidget):
    
    # [Constructor]
    def __init__(self, backend: Coms74FSAG):
        super().__init__()
        self.setWindowTitle("Widget 74FSAG")

        # Obtencion del backend de comunicacion
        self.coms = backend
        self.coms.setVisible(False)

        # Elementos graficos del widget
        self.label_status = QtWidgets.QLabel("●")
        self.button_pump = QtWidgets.QPushButton("Encender Bomba Turbo")
        self.button_pump.setCheckable(True)
        self.checkbox_soft_start = QtWidgets.QCheckBox("Arranque suave")
        self.spinbox_frequency = QtWidgets.QSpinBox()
        self.spinbox_frequency.setRange(1100, 1167)
        self.spinbox_frequency.setSingleStep(1)
        self.combobox_loaded_gas = QtWidgets.QComboBox()
        self.combobox_loaded_gas.addItem("N₂", 0)
        self.combobox_loaded_gas.addItem("Ar₂", 1)
        self.combobox_units = QtWidgets.QComboBox()
        self.combobox_units.addItem("mBar", 0)
        self.combobox_units.addItem("Pa", 1)
        self.combobox_units.addItem("Torr", 2)
        self.label_current = QtWidgets.QLabel("- mA")
        self.label_current.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.label_voltage = QtWidgets.QLabel("- V")
        self.label_voltage.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.label_power = QtWidgets.QLabel("- W")
        self.label_power.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.label_frequency = QtWidgets.QLabel("- Hz")
        self.label_frequency.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.label_temperature = QtWidgets.QLabel("- °C")
        self.label_temperature.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.label_pump_status = QtWidgets.QLabel("Null")
        self.label_pump_status.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.label_gauge_status = QtWidgets.QLabel("Null")
        self.label_gauge_status.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.label_pump_on_time = QtWidgets.QLabel("- min")
        self.label_pump_on_time.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.label_pump_cicle = QtWidgets.QLabel("#-")
        self.label_pump_cicle.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.label_pump_active_time = QtWidgets.QLabel("- h")
        self.label_pump_active_time.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.checkbox_console = QtWidgets.QCheckBox("Ver Terminal")
        
        # Ubicacion de elementos en layout
        self.layout_main = QtWidgets.QFormLayout()
        self.setLayout(self.layout_main)
        self.layout_main.addRow(self.label_status)
        separator_1 = QtWidgets.QFrame()
        separator_1.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        separator_1.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.layout_main.addRow(separator_1)
        self.layout_main.addRow(self.button_pump)
        self.layout_main.addRow(self.checkbox_soft_start)
        self.layout_main.addRow("Setetpoint frecuencia [Hz]", self.spinbox_frequency)
        self.layout_main.addRow("Gas cargado", self.combobox_loaded_gas)
        self.layout_main.addRow("Unidades del controlador", self.combobox_units)
        self.layout_main.addRow("Corriente de la bomba", self.label_current)
        self.layout_main.addRow("Voltaje de la bomba", self.label_voltage)
        self.layout_main.addRow("Potencia DC de la bomba", self.label_power)
        self.layout_main.addRow("Frecuencia de la bomba", self.label_frequency)
        self.layout_main.addRow("Temepratura de la bomba", self.label_temperature)
        self.layout_main.addRow("Estado de la bomba: ", self.label_pump_status)
        self.layout_main.addRow("Estado del indicador: ", self.label_gauge_status)
        self.layout_main.addRow("Tiempo desde encendido", self.label_pump_on_time)
        self.layout_main.addRow("Ciclo de la bomba",  self.label_pump_cicle)
        self.layout_main.addRow("Tiempo activo total",  self.label_pump_active_time)
        separator_2 = QtWidgets.QFrame()
        separator_2.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        separator_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.layout_main.addRow(separator_2)
        self.layout_main.addRow(self.checkbox_console)
        self.layout_main.addRow(self.coms)

        # Conexion de funciones handle
        self.checkbox_console.toggled.connect(self.coms.setVisible)
        self.button_pump.clicked.connect(self.handle_button_pump)
        self.checkbox_soft_start.clicked.connect(self.handle_checkbox_soft_start)
        self.spinbox_frequency.editingFinished.connect(self.handle_spinbox_frequency)
        self.combobox_loaded_gas.activated.connect(self.handle_combobox_loaded_gas)
        self.combobox_units.activated.connect(self.handle_combobox_units)

        # Timer para refrescar valores
        self.timer_update = QtCore.QTimer()
        self.timer_update.setInterval(500)
        self.timer_update.timeout.connect(self.update_values)
        self.timer_update.start()
    
    # [Handle de refresco de valores]
    def update_values(self):
        if self.coms.active:
            self.label_status.setText("● Respuesta activa")
            self.label_status.setStyleSheet("color: green;")
        else:
            self.label_status.setText("● Sin respuesta")
            self.label_status.setStyleSheet("color: red;")
        self.button_pump.setChecked(self.coms.dict_windows[000].decoded())
        self.checkbox_soft_start.setChecked(self.coms.dict_windows[100].decoded())
        if not self.spinbox_frequency.hasFocus():
            self.spinbox_frequency.setValue(self.coms.dict_windows[120].decoded())
        self.combobox_loaded_gas.setCurrentIndex(self.coms.dict_windows[157].decoded())
        self.combobox_units.setCurrentIndex(self.coms.dict_windows[163].decoded())
        self.label_current.setText(str(self.coms.dict_windows[200].decoded()) + " mA")
        self.label_voltage.setText(str(self.coms.dict_windows[201].decoded()) + " V")
        self.label_power.setText(str(self.coms.dict_windows[202].decoded()) + " W")
        self.label_frequency.setText(str(self.coms.dict_windows[203].decoded()) + " Hz")
        self.label_temperature.setText(str(self.coms.dict_windows[204].decoded()) + " °C")
        self.label_pump_status.setText(self.coms.dict_windows[205].decoded())
        self.label_gauge_status.setText(self.coms.dict_windows[257].decoded())
        self.label_pump_on_time.setText(str(self.coms.dict_windows[300].decoded()) + " min")
        self.label_pump_cicle.setText("#" + str(self.coms.dict_windows[301].decoded()))
        self.label_pump_active_time.setText(str(self.coms.dict_windows[302].decoded()) + " h")

    # [Handle click boton de encendido de la bomba]
    def handle_button_pump(self, state: bool):
        if state: self.coms.send_serial(000, True, "1")
        else: self.coms.send_serial(000, True, "0")
        self.coms.send_serial(000, False)

    # [Handle click para arranque suave]
    def handle_checkbox_soft_start(self, state: bool):
        if state: self.coms.send_serial(100, True, "1")
        else: self.coms.send_serial(100, True, "0")
        self.coms.send_serial(100, False)

    # [Handle cambio de setpoint de frecuencia]
    def handle_spinbox_frequency(self):
        value = self.spinbox_frequency.value()
        self.coms.send_serial(120, True, f"{value:06d}")
        self.coms.send_serial(120, False)
    
    # [Handle cambio de gas cargado]
    def handle_combobox_loaded_gas(self, value: int):
        self.coms.send_serial(157, True, f"{value:01d}")
        self.coms.send_serial(157, False)

    # [Handle cambio de unidades de medida]
    def handle_combobox_units(self, value: int):
        response = QtWidgets.QMessageBox.question(self, "",
            "Cambiar las unidades del controlador puede alterar los datos registrados.\n"
            "¿Esta seguro que desea cambiar las unidades nativas del controlador?")
        if response == QtWidgets.QMessageBox.StandardButton.Yes:
            self.coms.send_serial(163, True, f"{value:06d}")
            self.coms.send_serial(163, False)    

# --- DATA WINDOW CLASS ---
# Clase para objetos de almacenamiento de datos del controlador
class DataWindow:

    # [Constructor]
    def __init__(self, name: str, decoder: callable):
        self.name = name
        self.value = "0"
        self.decoder = decoder

    # [Call de informacion de la clase]
    def __repr__(self):
        return f"<DataWindow '{self.name}' = {self.decoded()}>"
    
    # [Get de valor decodificado]
    def decoded(self):
        try:
            return self.decoder(self.value)
        except Exception as e:
            print(f"[DataWindow] Error decodificando ventana {self.name}: {e}")
            return None
    
    # [Set de valor en bruto]
    def set(self, raw: str):
        self.value = raw

    # - FUNCIONES DE DECODIFICACION EN LA CLASE -
    
    # [Decodificador a boleano]
    def to_bool(raw: str) -> bool:
        return bool(int(raw))
    
    # [Decodificador a float]
    def to_float(raw: str) -> float:
        return float(raw)
    
    # [Decodificador a integer]
    def to_int(raw: str) -> int:
        return int(raw)
    
    # [Decodificador a estado de bomba]
    def to_state_pump(raw: str) -> str:
        states = {
            0: "Detenido",
            1: "Esperando INTLK",
            2: "Arrancando",
            3: "Autoajustando",
            4: "Frenando",
            5: "Normal",
            6: "Fallo"
        }
        return states.get(int(raw))
    
    # [Decodificador a estado del indicador]
    def to_state_gauge(raw: str) -> str:
        states = {
            0: "Sin conexion",
            1: "Conectado",
            2: "Bajo Rango",
            3: "Sobre Rango",
            4: "Desconocido"
        }
        return states.get(int(raw))

# --------------------------------------------------------------

# --- INICIALIZADOR ---
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Opciones Esteticas
    QtWidgets.QApplication.setStyle("Fusion")
    
    # Muestra la ventana de herramienta
    coms = Coms74FSAG()
    window = Widget74FSAG(coms)
    window.show()
    window.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)

    # lectura de todos los registros
    coms.read_all()

    # Timer de lectura de cambios
    timer_bucle = QtCore.QTimer()
    timer_bucle.timeout.connect(coms.read_changes)
    #timer_bucle.start(2000)
    
    # Salida
    sys.exit(app.exec())