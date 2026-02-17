import ipaddress
import socket
import time
import uuid
from hundirFlota import *

PUERTO = 4000
ID = str(uuid.uuid4())
NOMBRE = "BUJARRILLA"


def obtener_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


def calcular_broadcast():
    return str(ipaddress.IPv4Network(obtener_ip() + "/24", strict=False).broadcast_address)


def buscar_partida():
    dir_broadcast = calcular_broadcast()
    mi_ip = obtener_ip()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", PUERTO))
    sock.settimeout(1.0)

    estado = "ESPERANDO"
    soy_host = False
    oponente = None

    print(f"Mi IP: {mi_ip}")
    print("Buscando partida...")

    while estado == "ESPERANDO":
        mensaje = f"DESCUBRIR;{ID};{NOMBRE}"
        sock.sendto(mensaje.encode(), (dir_broadcast, PUERTO))

        try:
            data, addr = sock.recvfrom(1024)
            ip_oponente, _ = addr
            modo, id_oponente, nombre_oponente = data.decode().split(";")

            if modo == "DESCUBRIR":
                if id_oponente != ID and ID < id_oponente:
                    print(f"Aceptando a {nombre_oponente} ({ip_oponente})")

                    sock.sendto(
                        f"ACEPTADO;{ID};{NOMBRE}".encode(),
                        addr
                    )

                    oponente = (ip_oponente, nombre_oponente)
                    soy_host = True
                    estado = "JUGANDO"
                else:
                    print("Esperando respuesta...")

            elif modo == "ACEPTADO":
                print(f"{nombre_oponente} me ha aceptado")

                oponente = (ip_oponente, nombre_oponente)
                soy_host = False
                estado = "JUGANDO"

        except socket.timeout:
            pass

        if estado == "ESPERANDO":
            time.sleep(1)

    sock.close()
    return oponente[0], soy_host, oponente[1]


def abrir_servidor():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((obtener_ip(), PUERTO))
    s.listen(1)
    print("Esperando conexión TCP...")
    conn, addr = s.accept()
    print("HOST Conectado con", addr)
    return conn


def conectar_cliente(ip_rival):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            s.connect((ip_rival, PUERTO))
            print("Cliente Conectado al host")
            return s
        except:
            time.sleep(1)


def recibir_mensaje(sock):
    try:
        datos = sock.recv(1024)
        if not datos:
            return None
        return datos.decode().strip()
    except:
        return None


def imprimir_tablero_ataques(tablero_ataques, dimension=8):
    """
    Imprime el tablero de seguimiento de ataques al rival.
    Muestra: ~ = no atacado, o = agua, X = tocado/hundido.
    Columnas = letras (A-H), Filas = números (1-8).
    """
    print("\n  TABLERO DE ATAQUES AL RIVAL:")
    print("    ", end="")
    for letra in "ABCDEFGH"[:dimension]:
        print(letra, end=" ")
    print()

    for idx, fila in enumerate(tablero_ataques):
        print(f"  {idx + 1} ", end="")
        for celda in fila:
            print(celda, end=" ")
        print()
    print()

    time.sleep(2)


def registrar_ataque_en_tablero(tablero_ataques, columna_letra, fila_num_usuario, resultado):
    """
    Registra el resultado de un ataque en el tablero de seguimiento.
    - columna_letra: letra 'a'-'h' (columna).
    - fila_num_usuario: número 1-8 (fila).
    - resultado: 'AGUA', 'TOCADO', 'HUNDIDO', etc.
    """
    diccionario_letras = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    col_idx = diccionario_letras[columna_letra.lower()]
    fila_idx = fila_num_usuario - 1  # Conversión 1-8 → 0-7

    if resultado in ("TOCADO", "HUNDIDO"):
        tablero_ataques[fila_idx][col_idx] = "X"
    elif resultado == "AGUA":
        tablero_ataques[fila_idx][col_idx] = "o"


if __name__ == "__main__":
    resultado = buscar_partida()

    if resultado:
        ip_rival, soy_host, nombre_rival = resultado
        print(f"\nPARTIDA ENCONTRADA contra {nombre_rival}")

        canal_juego = None
        es_mi_turno = False

        if soy_host:
            print("ROL: HOST")
            canal_juego = abrir_servidor()
            es_mi_turno = True
        else:
            print("ROL: CLIENTE")
            time.sleep(1)
            canal_juego = conectar_cliente(ip_rival)
            es_mi_turno = False

        mi_tablero = Tablero(8)
        flota = [
            Barco(5, "Portaaviones"), Barco(4, "Acorazado"),
            Barco(3, "Crucero"), Barco(3, "Submarino"), Barco(2, "Destructor")
        ]
        for b in flota:
            mi_tablero.agregar_barco(b)

        # Tablero de seguimiento de ataques al rival (8x8 vacío)
        tablero_ataques = [["~"] * 8 for _ in range(8)]

        partida_activa = True

        while partida_activa:
            time.sleep(1.5)

            print("\n" + "=" * 20)
            print("ESTADO DE TU FLOTA:")
            mi_tablero.imprimir(ocultar_barcos=False)
            print("=" * 20 + "\n")

            if es_mi_turno:
                print(f"\n--- TU TURNO DE ATACAR A {nombre_rival} ---")

                coord_ia = mi_tablero.atacar()
                letra = coord_ia[0].upper()
                fila = coord_ia[1]
                disparo = f"{letra}{fila}"

                try:
                    canal_juego.sendall(disparo.encode())
                    print(f"[RED] Enviando disparo automático: {disparo}")

                    respuesta = recibir_mensaje(canal_juego)

                    if respuesta is None:
                        print("El rival se ha desconectado.")
                        partida_activa = False
                        break

                    print(f"Resultado: {respuesta}")

                    mi_tablero.registrar_resultado(respuesta)

                    # Registrar el ataque en el tablero de seguimiento
                    registrar_ataque_en_tablero(tablero_ataques, letra, fila, respuesta)

                    # Mostrar el tablero de ataques al rival
                    imprimir_tablero_ataques(tablero_ataques)

                    if "VICTORIA" in respuesta:
                        print("\n" + "*" * 40)
                        print("¡VICTORIA! HAS HUNDIDO LA FLOTA RIVAL.")
                        print("*" * 40)
                        partida_activa = False

                    elif "TOCADO" in respuesta or "HUNDIDO" in respuesta:
                        es_mi_turno = True
                    else:
                        es_mi_turno = False

                except Exception as e:
                    print(f"Error de conexión: {e}")
                    partida_activa = False

            else:
                print(f"\n--- TURNO DE {nombre_rival} ---")
                print("Esperando disparo...")

                try:
                    disparo_recibido = recibir_mensaje(canal_juego)

                    if disparo_recibido is None:
                        print("El rival se ha desconectado.")
                        partida_activa = False
                        break

                    print(f"Rival dispara a: {disparo_recibido}")

                    letra_r = disparo_recibido[0].lower()
                    fila_r = int(disparo_recibido[1:])

                    resultado_impacto = mi_tablero.recibir_ataque(letra_r, fila_r)
                    print(f"Impacto en mi tablero: {resultado_impacto}")

                    # Cuando he perdido los barcos
                    if not mi_tablero.quedan_barcos_vivos():
                        resultado_impacto = "VICTORIA"  # Le digo al otro que ganó
                        canal_juego.sendall(resultado_impacto.encode())

                        print("\n" + "!" * 40)
                        print("¡DERROTA! HAN HUNDIDO TU FLOTA.")
                        print("!" * 40)

                        # Pausa para que el mensaje llegue
                        time.sleep(3)
                        partida_activa = False

                    else:
                        canal_juego.sendall(resultado_impacto.encode())

                        if "TOCADO" in resultado_impacto or "HUNDIDO" in resultado_impacto:
                            es_mi_turno = False
                        else:
                            es_mi_turno = True

                except Exception as e:
                    print(f"Error de conexión: {e}")
                    partida_activa = False

        print("Cerrando conexión...")
        try:
            canal_juego.close()
        except:
            pass