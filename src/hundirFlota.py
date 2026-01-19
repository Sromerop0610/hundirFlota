import random


class Barco:
    def __init__(self, tamanio):
        self.tamanio = tamanio
        self.posiciones = []


def colocar_barco(tablero, barco):
    true = True
    while true:
        orientacion = ["V", "H"]
        orientacion_elegida = random.choice(orientacion)

        maximo = 7 - barco.tamanio

        if orientacion_elegida == "H":
            fila = random.randint(0, 7)
            columna = random.randint(0, maximo)
        else:
            fila = random.randint(0, maximo)
            columna = random.randint(0, 7)

        posiciones = []

        for i in range(barco.tamanio):
            if orientacion_elegida == "H":
                f = fila
                c = columna + i
            else:
                f = fila + i
                c = columna

            if f >= 8 or c >= 8:
                true = False
            else:
                if tablero[f][c] != "~":
                    true = False

            posiciones.append((f, c))

        if len(posiciones) == barco.tamanio:
            for f, c in posiciones:
                tablero[f][c] = "B"
            barco.posiciones = posiciones
            return

def tocado_hundido(tablero, barco, posicion_ataque):



    posicion_ataque[0]




def main():
    tablero = [["~"] * 8 for _ in range(8)]

    crucero = Barco(4)

    colocar_barco(tablero, crucero)


    for fila in tablero:
        print(fila)

if __name__ == '__main__':
    main()

""" portaaviones =
    acorazado = 
    crucero = 
    submarino = 
    destructor = """
