# [ARDUINO SERIAL TESTER]
# David Miguel Garcia Palacios
# Universidad Nacional de Colombia Sede Bogota

# Bibliotecas a usar
import serial
import threading

# Funcion de lectura del puerto serial
def leer_serial(puerto):
    while True:
        try:
            if puerto.in_waiting:
                mensaje = puerto.readline().decode("ascii", errors="replace").strip()
                print("<< ", mensaje)
        except Exception as err:
            print("Error en la lectura:",err)
            break

# Parametros de comunicacion
puerto_com = "COM6"
baudios = 9600

# Incialiacion de la comunicacion
try:
    puerto_serial = serial.Serial(puerto_com, baudios, timeout=1)
    print("Conexion exitosa en", puerto_com, "a", baudios, "baudios!")
except Exception as err:
    print("Error al abrir el puerto:", err)
    raise SystemExit

# Incializacion del hilo de comunicacion
hilo_lectura = threading.Thread(target=leer_serial, args=(puerto_serial,), daemon=True)
hilo_lectura.start()

# Ciclo para la escritura
try:
    while True:
        comando = input("Ingresa un comando o escribe 'exit' para salir: ")
        if comando.lower() == "exit":
            print("Cerrando comnunicacion...")
            break
        puerto_serial.write((comando + "\n").encode("ascii"))
except KeyboardInterrupt:
    print("nterrupción detectada. Cerrando comunicacion...")
finally:
    puerto_serial.close()
    
    




