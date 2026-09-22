from abc import ABC, abstractmethod

class Boton(ABC):
    @abstractmethod 
    def renderizar(self):
        pass

class Menu(ABC):
    @abstractmethod
    def renderizar(self):
        pass

class Checkbox(ABC):
    @abstractmethod
    def renderizar(self):
        pass

class BotonWindows(Boton):
    def renderizar(self):
        print("Boton estilo windows...")

class BotonMac(Boton):
    def renderizar(self):
        print("Boton esilo mac...")    

class MenuWindows(Menu):
    def renderizar(self):
        print("Menu estilo windows...")

class MenuMac(Menu):
    def renderizar(self):
        print("Menu estilo mac...")

class CheckboxWindows(Checkbox):
    def renderizar(self):
        print("Checkbox estilo windows...")

class CheckboxMac(Checkbox):
    def renderizar(self):
        print("Checkbox estilo mac...")

class UIFactoryABC(ABC):
    @abstractmethod
    def crear_boton(self):
        pass

    @abstractmethod
    def crear_menu(self):
        pass

    @abstractmethod
    def crear_checkbox(self):
        pass

class WindowsFactory(UIFactoryABC):
    def crear_boton(self):
        return BotonWindows()
    def crear_menu(self):
        return MenuWindows()
    def crear_checkbox(self):
        return CheckboxWindows()

class MacFactory(UIFactoryABC):
    def crear_boton(self):
        return BotonMac()
    def crear_menu(self):
        return MenuMac()
    def crear_checkbox(self):
        return CheckboxMac()

def crear_UI(factory: UIFactoryABC):
    boton = factory.crear_boton()
    menu = factory.crear_menu()
    checkbox = factory.crear_checkbox()

    boton.renderizar()
    menu.renderizar()
    checkbox.renderizar()
    
def main():
    sistema = 'Mac'

    if sistema == 'Windows':
        factory = WindowsFactory()
    elif sistema == 'Mac':
        factory = MacFactory()

    crear_UI(factory)

main()