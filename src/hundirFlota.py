import random


class Barco:
    def __init__(self, tamanio, nombre="Barco"):
        self.tamanio = tamanio
        self.nombre = nombre
        self.posiciones = []
        self.vidas = tamanio


class Tablero:
    def __init__(self, dimension=8):
        self.dimension = dimension
        self.cuadricula = [["~"] * dimension for _ in range(dimension)]
        self.barcos = []
        self.ataques_realizados = []

        # Atributos para la IA
        self.cola_objetivos = []
        self.ultimo_ataque_exitoso = None
        self.casillas_descartadas = set()
        self.impactos_barco_actual = []

    def agregar_barco(self, barco):
        barco_puesto = False
        while not barco_puesto:
            orientacion = random.choice(["V", "H"])
            limite = self.dimension - barco.tamanio
            if orientacion == "H":
                fila = random.randint(0, self.dimension - 1)
                columna = random.randint(0, limite)
            else:
                fila = random.randint(0, limite)
                columna = random.randint(0, self.dimension - 1)

            es_valido = True
            coordenadas_posibles = []
            for i in range(barco.tamanio):
                f, c = (fila, columna + i) if orientacion == "H" else (fila + i, columna)
                coordenadas_posibles.append((f, c))
                for i_f in range(f - 1, f + 2):
                    for i_c in range(c - 1, c + 2):
                        if 0 <= i_f < self.dimension and 0 <= i_c < self.dimension:
                            if self.cuadricula[i_f][i_c] != "~":
                                es_valido = False
            if es_valido:
                for f, c in coordenadas_posibles:
                    self.cuadricula[f][c] = barco.nombre[0]
                barco.posiciones = coordenadas_posibles
                self.barcos.append(barco)
                barco_puesto = True

    def recibir_ataque(self, columna_letra, fila_num_usuario):
        """
        Recibe ataque con formato (letra_columna, número_fila).
        - columna_letra: letra 'a'-'h' que indica la columna.
        - fila_num_usuario: número del 1 al 8 que indica la fila.
        Internamente convierte: col_idx = letra->0-7, fila_idx = número - 1.
        """
        diccionario_letras = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
        col_idx = diccionario_letras[columna_letra.lower()]
        fila_idx = fila_num_usuario - 1  # Conversión 1-8 → 0-7

        contenido = self.cuadricula[fila_idx][col_idx]

        if contenido == "X" or contenido == "o":
            return "YA DISPARADO"
        elif contenido == "~":
            self.cuadricula[fila_idx][col_idx] = "o"
            return "AGUA"
        else:
            self.cuadricula[fila_idx][col_idx] = "X"
            for barco in self.barcos:
                if (fila_idx, col_idx) in barco.posiciones:
                    barco.vidas -= 1
                    return "HUNDIDO" if barco.vidas == 0 else "TOCADO"
        return "ERROR"

    def _casilla_valida_para_atacar(self, fila_idx, col_idx):
        """Verifica si una casilla es válida para atacar (usa índices internos 0-7)."""
        if not (0 <= fila_idx < self.dimension and 0 <= col_idx < self.dimension):
            return False
        # Comprobamos en ataques_realizados usando el formato externo [letra, número 1-8]
        letra_c = chr(97 + col_idx)
        fila_usuario = fila_idx + 1  # Conversión 0-7 → 1-8
        if [letra_c, fila_usuario] in self.ataques_realizados:
            return False
        if (fila_idx, col_idx) in self.casillas_descartadas:
            return False
        return True

    def _descartar_adyacentes(self, fila_idx, col_idx):
        """Marca las casillas adyacentes (incluidas diagonales) como descartadas."""
        for df in range(-1, 2):
            for dc in range(-1, 2):
                vf, vc = fila_idx + df, col_idx + dc
                if 0 <= vf < self.dimension and 0 <= vc < self.dimension:
                    self.casillas_descartadas.add((vf, vc))

    def atacar(self):
        """
        Estrategia inteligente con patrón de ajedrez.
        Devuelve [letra_columna, número_fila] con número del 1 al 8.
        """
        diccionario_idx_a_let = {i: chr(97 + i) for i in range(8)}

        fila_idx, col_idx = None, None

        # MODO DESTRUCCIÓN: Atacar objetivos prioritarios
        while self.cola_objetivos and fila_idx is None:
            candidato = self.cola_objetivos.pop(0)
            if self._casilla_valida_para_atacar(candidato[0], candidato[1]):
                fila_idx, col_idx = candidato

        # MODO CAZA: Patrón de ajedrez
        if fila_idx is None:
            casillas_ajedrez = [
                (f, c) for f in range(self.dimension)
                for c in range(self.dimension)
                if (f + c) % 2 == 0 and self._casilla_valida_para_atacar(f, c)
            ]

            if casillas_ajedrez:
                fila_idx, col_idx = random.choice(casillas_ajedrez)
            else:
                # Fallback: cualquier casilla válida restante
                casillas_restantes = [
                    (f, c) for f in range(self.dimension)
                    for c in range(self.dimension)
                    if self._casilla_valida_para_atacar(f, c)
                ]
                if casillas_restantes:
                    fila_idx, col_idx = random.choice(casillas_restantes)

        if fila_idx is not None:
            columna_letra = diccionario_idx_a_let[col_idx]
            fila_usuario = fila_idx + 1  # Conversión 0-7 → 1-8
            intento = [columna_letra, fila_usuario]  # [letra_columna, número_fila 1-8]
            self.ataques_realizados.append(intento)
            self.ultimo_ataque_exitoso = (fila_idx, col_idx)
            return intento

    def registrar_resultado(self, resultado):
        """Actualiza la estrategia según el resultado del último ataque."""
        f, c = self.ultimo_ataque_exitoso

        if resultado == "TOCADO":
            self.impactos_barco_actual.append((f, c))
            diagonales = [(f - 1, c - 1), (f - 1, c + 1), (f + 1, c - 1), (f + 1, c + 1)]
            for vf, vc in diagonales:
                if 0 <= vf < self.dimension and 0 <= vc < self.dimension:
                    self.casillas_descartadas.add((vf, vc))

            vecinos = [(f - 1, c), (f + 1, c), (f, c - 1), (f, c + 1)]
            for vf, vc in vecinos:
                if self._casilla_valida_para_atacar(vf, vc) and (vf, vc) not in self.cola_objetivos:
                    self.cola_objetivos.append((vf, vc))

        elif resultado == "HUNDIDO":
            self.impactos_barco_actual.append((f, c))
            for impacto_f, impacto_c in self.impactos_barco_actual:
                self._descartar_adyacentes(impacto_f, impacto_c)
            self.impactos_barco_actual = []
            self.cola_objetivos = []

        elif resultado == "AGUA":
            self.casillas_descartadas.add((f, c))

    def quedan_barcos_vivos(self):
        return any(barco.vidas > 0 for barco in self.barcos)

    def imprimir(self, ocultar_barcos=False):
        """
        Imprime el tablero con columnas = letras (A-H) y filas = números (1-8).
        """
        # Encabezado: letras de columna A-H
        print("\n    ", end="")
        for letra in "ABCDEFGH"[:self.dimension]:
            print(letra, end=" ")
        print()

        # Filas: números 1-8
        for idx, fila in enumerate(self.cuadricula):
            print(f"  {idx + 1} ", end="")  # Muestra 1-8 en vez de 0-7
            for celda in fila:
                if ocultar_barcos and celda not in ["~", "X", "o"]:
                    print("~", end=" ")
                else:
                    print(celda, end=" ")
            print()
        print()


def main():
    tablero_jugador = Tablero(dimension=8)
    tablero_oponente = Tablero(dimension=8)

    flota_jugador = [
        Barco(5, "Portaaviones"), Barco(4, "Acorazado"),
        Barco(3, "Crucero"), Barco(3, "Submarino"), Barco(2, "Destructor")
    ]
    flota_oponente = [
        Barco(5, "Portaaviones"), Barco(4, "Acorazado"),
        Barco(3, "Crucero"), Barco(3, "Submarino"), Barco(2, "Destructor")
    ]

    for barco in flota_jugador:
        tablero_jugador.agregar_barco(barco)
    for barco in flota_oponente:
        tablero_oponente.agregar_barco(barco)

    print("=" * 50)
    print("         BATALLA NAVAL - IA vs IA")
    print("=" * 50)

    print("\nTU TABLERO (tus barcos):")
    tablero_jugador.imprimir(ocultar_barcos=False)

    print("\nTABLERO ENEMIGO (tus ataques):")
    tablero_oponente.imprimir(ocultar_barcos=True)

    jugar = True
    turno = 1

    while jugar:
        print(f"\n{'='*50}")
        print(f"TURNO {turno}")
        print(f"{'='*50}")

        # TURNO JUGADOR (IA)
        print("\n--- Tu Turno ---")
        columna_letra, fila_num = tablero_jugador.atacar()  # [letra, número 1-8]
        estado = tablero_oponente.recibir_ataque(columna_letra, fila_num)
        print(f"➤ Atacas en ({columna_letra.upper()}, {fila_num}): {estado}")
        tablero_jugador.registrar_resultado(estado)

        if not tablero_oponente.quedan_barcos_vivos():
            print("\n" + "=" * 50)
            print("¡VICTORIA!")
            print("Has hundido toda la flota enemiga")
            print("=" * 50)
            print("\nTABLERO ENEMIGO FINAL:")
            tablero_oponente.imprimir(ocultar_barcos=False)
            jugar = False
            continue

        # TURNO OPONENTE
        print("\n--- Turno del Oponente ---")
        columna_letra, fila_num = tablero_oponente.atacar()  # [letra, número 1-8]
        estado = tablero_jugador.recibir_ataque(columna_letra, fila_num)
        print(f"➤ Enemigo ataca en ({columna_letra.upper()}, {fila_num}): {estado}")
        tablero_oponente.registrar_resultado(estado)

        print("\n TU TABLERO:")
        tablero_jugador.imprimir(ocultar_barcos=False)

        print("\nTABLERO ENEMIGO:")
        tablero_oponente.imprimir(ocultar_barcos=True)

        if not tablero_jugador.quedan_barcos_vivos():
            print("\n" + "=" * 50)
            print("DERROTA")
            print("El enemigo hundió tu flota")
            print("=" * 50)
            jugar = False

        turno += 1


if __name__ == '__main__':
    main()