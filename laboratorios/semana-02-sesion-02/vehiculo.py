#Vehiculo -> mueva -> mover()

#Auto -> mueve por carretera
#Bote -> mueve por agua
#Avion -> mueve por aire

class mover():
    def mover(self):
        raise NotImplementedError

class mueveporcarretera(mover):
    def mover(self):
        return "Conduciendo por carretera."

class mueveporagua(mover):
    def mover(self):
        return "Navegando por agua."

class mueveporaire(mover):
    def mover(self):
        return "Volando por el aire."

class  vehiculo: 
    def __init__(self, mover):
        self.mover = mover

    def moverse(self):
        return self.mover.mover()

class auto(vehiculo):
    def __init__(self):
        mueve_carretera = mueveporcarretera()
        super().__init__(mueve_carretera)

class bote(vehiculo):
    def __init__(self):
        mueve_agua = mueveporagua()
        super().__init__(mueve_agua)

class avion(vehiculo):
    def __init__(self):
        mueve_aire = mueveporaire()
        super().__init__(mueve_aire)

if __name__ == "__main__":
    auto = auto()
    print(auto.moverse())

    bote = bote()
    print(bote.moverse())

    avion = avion()
    print(avion.moverse())    