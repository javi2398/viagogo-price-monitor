import tls_client
from printColor import printRed, printVerde, printHora, printAzul, printMagenta, printYellow
from WebhookOk import notificationOk
import time
import csv
import threading
import time



# Hacemos la petición a la página
def main(urlEvento, precioMaximo):
    while True:
        try:
            s = tls_client.Session()
            baneo = False
            delay = 8

            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'es-419,es;q=0.9',
                'dnt': '1',
                'if-none-match': 'W\\MDBjNGNiMjYtMDkyYS00Y2VhLThiMzEtZTFmYjNiYzEwMzZlfDF8YWU5ZmRmNDFmNGM1ZGE5Y2VkYWRmNWZkNzU3MDI0MTl8NjM4NjUzMTI0MDY=',
                'priority': 'u=0, i',
                'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            }

            response = s.get(
                urlEvento,
                headers=headers,
            )

            if response.status_code == 200:
                printVerde("Página obtenida con éxito")
            else:
                printRed('Error al obtener la página del producto')
                print(response.status_code)
                baneo = True
                time.sleep(20)
                # En un futuro rotaria de proxy

                delay += 1 # Vamos aumentando el delay para hallar el delay perfecto donde no banee

            if baneo == False:
                precio = float(response.text.split('Ir a la página de inicio')[2].split('rawPrice":')[1].split(',')[0])
                titulo = response.text.split('title>')[1].split('<')[0]

                if precio < precioMaximo:

                    listingId = response.text.split('Ir a la página de inicio')[2].split('"id":')[1].split(',')[0]
                    eventId = response.text.split('Ir a la página de inicio')[2].split('"eventId":')[1].split(',')[0]
                    ticketQuantity = response.text.split('Ir a la página de inicio')[2].split('availableTickets":')[1].split(',')[0]
                    urlcheckout = f'https://www.viagogo.com/secure/buy/Initialise?ListingID={listingId}&EventID={eventId}&quantity={ticketQuantity}'

                    section = response.text.split('Ir a la página de inicio')[2].split('section":"')[1].split('"')[0]
                    row = response.text.split('Ir a la página de inicio')[2].split('row":"')[1].split('",')[0]
                    seat = response.text.split('Ir a la página de inicio')[2].split('seat":"')[1].split('",')[0]
                    infoSeat = f'SEC: {section}, ROW: {row}, SEAT: {seat}, QTY: {ticketQuantity}'
                    imagen = 'https://media.stubhubstatic.com/stubhub-v2-catalog' + response.text.split('stubhub-v2-catalog')[1].split('" />')[0]
                    notificationOk(url=urlEvento, eventName=titulo, seatInfo=infoSeat, imgUrl=imagen, price=str(precio), urlCheckout=urlcheckout)
                    printVerde(f'Entradas encontradas! {urlEvento}')
                    time.sleep(20)
                    
                else:
                    printHora(f'No se encontraron entradas por debajo de {precioMaximo}€ para {titulo}')
                    time.sleep(delay) # Tiempo de espera entre peticiones para evitar rate limit

        except Exception as e:
            print("Error en la solicitud:", e)
            time.sleep(180) # Si da error haciendo la peticion le metemos un tiempo de espera


def leer_csv_y_ejecutar_hilos(archivo_csv):
    hilos = []
    with open(archivo_csv, mode='r', newline='') as file:
        lector = csv.DictReader(file)
        for fila in lector:
            enlace = fila['enlace']
            precio = int(fila['precioMax'])
            # Crear un hilo para monitorear cada enlace
            hilo = threading.Thread(target=main, args=(enlace, precio))
            hilos.append(hilo)
            hilo.start()  # Iniciar el hilo
            time.sleep(2) # Asi hacemos que no arranque todas las peticiones al mismo tiempo


leer_csv_y_ejecutar_hilos('datos.csv') # Hay que indicarle el nombre del archivo

#! TESTEAR
# main('https://www.viagogo.com/Concert-Tickets/Country-and-Folk-Music/Taylor-Swift-Tickets/E-152129115?quantity=0', 100)