class ComportamientoVuelo():
    def volar(self):
        raise NotImplementedError

class VuelaConAlas(ComportamientoVuelo):
    def volar(self):
        return "Volando con alas."

class NoVuela(ComportamientoVuelo):
    def volar(self):
        print("No puedo volar.")
        return "No puedo volar."

class  ComportamientoGraznar:
    def graznar(self):
        raise NotImplementedError

class GraznarNormal(ComportamientoGraznar):
    def graznar(self):
        print("Cuac.")

class GraznidoDeGoma(ComportamientoGraznar):
    def graznar(self):
        print("Chirrido de goma.")

class Pato: 
    def __init__(self, comportamiento_vuelo, comportamiento_graznar):
        self.comportamiento_vuelo = comportamiento_vuelo
        self.comportamiento_graznar = comportamiento_graznar

    def nadar(self):
        print("Nadando.")

    def graznar(self):
        self.comportamiento_graznar.graznar()

    def volar(self):
        return self.comportamiento_vuelo.volar()

class PatoSalvaje(Pato):
    def __init__(self):
        vuela_alas = VuelaConAlas()
        graznar_normal = GraznarNormal()
        super().__init__(vuela_alas, graznar_normal)


class PatoDeGoma(Pato):
    def __init__(self):
        no_vuela = NoVuela()
        graznido_goma = GraznidoDeGoma()
        super().__init__(no_vuela, graznido_goma)

if __name__ == "__main__":
    salvaje = PatoSalvaje()
    salvaje.nadar()
    salvaje.graznar()  
    salvaje.volar() 

    print()

    goma = PatoDeGoma()
    goma.nadar()
    goma.graznar()
    goma.volar()  