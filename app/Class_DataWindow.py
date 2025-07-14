# === [CLASE DE ALMACENAMIENTO DE DATOS DE VENTANA] ===
# David Miguel Garcia Palacios
# Universidad Nacional de Colombia Sede Bogota

# --- CLASE DATA WINDOW ---
class DataWindow:

    # [Constructor]
    def __init__(self, name: str, decoder: callable):
        self.name = name
        self.value = bytes()
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
    def set(self, raw: bytes):
        self.value = raw

    # - FUNCIONES DE DECODIFICACION EN LA CLASE -
    
    # [Decodificador de ASCII a boleano]
    def decode_bool(raw: bytes) -> bool:
        return raw.strip() == b"1"