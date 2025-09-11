from datetime import datetime
from colorama import Fore, Style, init

init()


def printVerde(imprimir):
    hora_actual = datetime.now()
    hora_actual_str = hora_actual.strftime("%H:%M:%S")
    print(f"{Fore.GREEN}[{hora_actual_str}] {imprimir}{Style.RESET_ALL}")


def printYellow(imprimir):
    hora_actual = datetime.now()
    hora_actual_str = hora_actual.strftime("%H:%M:%S")
    print(f"{Fore.YELLOW}[{hora_actual_str}] {imprimir}{Style.RESET_ALL}")


def printHora(imprimir):
    hora_actual = datetime.now()
    hora_actual_str = hora_actual.strftime("%H:%M:%S")
    print(f"[{hora_actual_str}] {imprimir}")


def printRed(imprimir):
    hora_actual = datetime.now()
    hora_actual_str = hora_actual.strftime("%H:%M:%S")
    print(f"{Fore.RED}[{hora_actual_str}] {imprimir}{Style.RESET_ALL}")


def printMagenta(imprimir):
    hora_actual = datetime.now()
    hora_actual_str = hora_actual.strftime("%H:%M:%S")
    # Combinación de colores rojo y azul para crear un tono de morado
    print(f"{Fore.MAGENTA}[{hora_actual_str}] {imprimir}{Style.RESET_ALL}")


def printAzulN(imprimir):
    hora_actual = datetime.now()
    hora_actual_str = hora_actual.strftime("%H:%M:%S")
    # Combinación de colores rojo y azul para crear un tono de morado
    print(f"{Fore.RED + Style.BRIGHT}{Fore.BLUE +Style.BRIGHT}[{hora_actual_str}] {imprimir}{Style.RESET_ALL}")


def printAzul(imprimir):
    hora_actual = datetime.now()
    hora_actual_str = hora_actual.strftime("%H:%M:%S")
    # Combinación de colores rojo y azul para crear un tono de morado
    print(f"{Fore.LIGHTRED_EX}{Fore.LIGHTBLUE_EX}[{hora_actual_str}] {imprimir}{Style.RESET_ALL}")