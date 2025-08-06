# === [CLASE DE ALMACENAMIENTO DE DATOS DE VENTANA] ===
# David Miguel Garcia Palacios
# Universidad Nacional de Colombia Sede Bogota

# --- CLASE DATA WINDOW ---
class DataWindow:

    # [Constructor]
    def __init__(self, name: str, decoder: callable):
        self.name = name
        self.value = ""
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
    
    # [Decodificador a integer]
    def to_float(raw: str) -> int:
        return float(raw)