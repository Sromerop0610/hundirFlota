import random


class Barco:
    def __init__(self, tamanio, nombre="Barco"):
        self.tamanio = tamanio
        self.nombre = nombre
        self.posiciones = []
        self.vidas = tamanio

    def __str__(self):
        return f"Barco: {self.nombre} - Tamaño: {self.tamanio} - Posiciones: {self.posiciones}"

    def __repr__(self):
        # Esto le dice a Python: "Cuando estés en una lista, usa lo mismo que en __str__"
        return self.__str__()


class Tablero:
    def __init__(self, dimension=8):
        self.dimension = dimension
        self.cuadricula = [["~"] * dimension for _ in range(dimension)]
        self.barcos = []
        self.ataques = []

    def agregar_barco(self, barco):
        barco_puesto = False

        while not barco_puesto:
            orientaciones = ["V", "H"]
            orientacion = random.choice(orientaciones)

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
                if orientacion == "H":
                    f, c = fila, columna + i
                else:
                    f, c = fila + i, columna

                coordenadas_posibles.append((f, c))

                # Si la casilla NO es agua, ya no es válido
                for i_f in range(f - 1, f + 2):
                    for i_c in range(c - 1, c + 2):

                        # A. Comprobamos si la casilla vecina está DENTRO del tablero
                        if 0 <= i_f < len(self.cuadricula) and 0 <= i_c < len(self.cuadricula):

                            # B. Si está dentro, miramos si NO es agua
                            if self.cuadricula[i_f][i_c] != "~":
                                es_valido = False

            if es_valido:
                for f, c in coordenadas_posibles:
                    self.cuadricula[f][c] = barco.nombre[0]

                barco.posiciones = coordenadas_posibles

                self.barcos.append(barco)

                barco_puesto = True

    def imprimir(self):
        for fila in self.cuadricula:
            print(fila)



def main():
    tablero_juego = Tablero(dimension=8)

    flota = [
        Barco(5, "Portaaviones"),
        Barco(4, "Acorazado"),
        Barco(3, "Crucero"),
        Barco(3, "Submarino"),
        Barco(2, "Destructor")
    ]

    for barco in flota:
        tablero_juego.agregar_barco(barco)

    tablero_juego.imprimir()

    print(tablero_juego.barcos)


if __name__ == '__main__':
    main()