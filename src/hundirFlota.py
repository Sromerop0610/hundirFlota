import random


class Barco:
    def __init__(self, tamanio, nombre="Barco"):
        self.tamanio = tamanio
        self.nombre = nombre
        self.posiciones = []
        self.tocados = 0


class Tablero:
    def __init__(self, dimension=8):
        self.dimension = dimension
        self.grid = [["~"] * dimension for _ in range(dimension)]
        self.barcos = []

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
            coords_tentativas = []

            for i in range(barco.tamanio):
                if orientacion == "H":
                    f, c = fila, columna + i
                else:
                    f, c = fila + i, columna

                coords_tentativas.append((f, c))

                # Si la casilla NO es agua, ya no es válido
                if self.grid[f][c] != "~":
                    es_valido = False

            if es_valido:
                for f, c in coords_tentativas:
                    self.grid[f][c] = barco.nombre[0]

                barco.posiciones = coords_tentativas

                self.barcos.append(barco)

                barco_puesto = True

    def imprimir(self):
        for fila in self.grid:
            print(fila)



def main():
    mi_tablero = Tablero(dimension=8)

    flota = [
        Barco(5, "Portaaviones"),
        Barco(4, "Acorazado"),
        Barco(3, "Crucero"),
        Barco(3, "Submarino"),
        Barco(2, "Destructor")
    ]

    for nave in flota:
        mi_tablero.agregar_barco(nave)

    mi_tablero.imprimir()

    print(f"\nEl Portaaviones quedó en: {flota[0].posiciones}")


if __name__ == '__main__':
    main()