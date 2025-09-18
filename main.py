import tls_client
from printColor import printRed, printVerde, printHora, printAzul, printMagenta, printYellow
from WebhookOk import notification_viagogo
from seleniumbase import SB
import time
import csv
import threading


def headers_get():
    return {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "es-419,es;q=0.9",
        "dnt": "1",
        "priority": "u=0, i",
        "sec-ch-ua": '"Chromium";v="139", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    }


def headers_post(urlEvento: str):
    return {
        'accept': '*/*',
        'accept-language': 'es-419,es;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://www.viagogo.com',
        'priority': 'u=1, i',
        'referer': urlEvento,
        'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="130", "Chromium";v="139"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    }

# Abrimos el evento con seleniumBase para obtener las cookies necesarias para el antibot
def challenge_handler(event_url_challenge: str, tls_session_challenge: tls_client.Session):
    
    with SB(uc=True, headless=True) as sb:

        printAzul('Obteniendo cookies con SeleniumBase...')
        sb.uc_open(event_url_challenge)
        sb.wait_for_ready_state_complete(timeout=30)

        cookies_selenium = sb.get_cookies()

        for c in cookies_selenium:
            name = c.get("name")
            value = c.get("value", "")
            domain = c.get("domain") or None
            path = c.get("path", "/")
            if name is None:
                continue
            if c.get("expiry") is not None:
                try:
                    import time as _time
                    if int(c["expiry"]) < int(_time.time()):
                        continue
                except Exception:
                    pass
            tls_session_challenge.cookies.set(name, value, domain=domain, path=path)

    # Volvemos a hacer la petición con las cookies requeridas
    headers = headers_get()

    response = tls_session_challenge.get(
        event_url_challenge,
        headers=headers,
    )

    return response.text


def fetch_prices(tls_session: tls_client.Session, event_url: str, page_visit_id: str, category_id: str):
    
    headers = headers_post(event_url)

    params = {
        'categoryId': f'{category_id}',
        'IsDirectFromPaidSearch': 'false',
    }

    json_data = {
        'ShowAllTickets': True,
        'HideDuplicateTicketsV2': False,
        'Quantity': int(event_url.split('quantity=')[1]),
        'IsInitialQuantityChange': False,
        'PageVisitId': page_visit_id,
        'PageSize': 20,
        'CurrentPage': 1,
        'SortBy': 'RECOMMENDED',
        'SortDirection': 1,
        'Sections': '',
        'Rows': '',
        'Seats': '',
        'SeatTypes': '',
        'TicketClasses': '',
        'ListingNotes': '',
        'PriceRange': '0,100',
        'InstantDelivery': False,
        'EstimatedFees': False,
        'BetterValueTickets': True,
        'PriceOption': '',
        'HasFlexiblePricing': False,
        'ExcludeSoldListings': False,
        'RemoveObstructedView': False,
        'NewListingsOnly': False,
        'PriceDropListingsOnly': False,
        'ConciergeTickets': False,
        'EventId': event_url.split('E-')[1].split('?')[0],
        'CategoryId': category_id,
        'ShowBestSellingSections': False,
        'ShowAmazingSections': False,
        'Favorites': False,
    }

    response = tls_session.post(
        'https://www.viagogo.com/Browse/VenueMap/GetMapAvailabilityAndPrices',
        params=params,
        headers=headers,
        json=json_data,
    )

    return response


def fetch_event_page(tls_session: tls_client.Session, event_url: str):

    headers = headers_get()

    response = tls_session.get(
        event_url,
        headers=headers,
    )

    if response.status_code == 302:
        printRed(f'Error al obtener la página, verifique que la url es correcta: {event_url}')
        raise RuntimeError(response.status_code)

    elif response.status_code == 202:
        return challenge_handler(event_url_challenge=event_url, tls_session_challenge=tls_session)
    
    else:
        return response.text



def main(urlEvento, precioMaximo, discordWebhook):

    default_delay = 8  # Tiempo de espera por defecto entre peticiones
    banned = False
    banned_sleep_time = 40  # Tiempo de espera si somos baneados

    session = tls_client.Session()

    response_text = fetch_event_page(tls_session=session, event_url=urlEvento)

    pageVisitId = response_text.split('"pageVisitId":"')[1].split('",')[0]
    categoryId = response_text.split('"categoryId":')[1].split(',')[0]
    titulo = response_text.split('title>')[1].split('<')[0]

    printAzul(f'\n Comenzando a monitorizar {titulo}')

    while True:
        try:

            response = fetch_prices(tls_session=session,event_url=urlEvento, page_visit_id=pageVisitId, category_id=categoryId)

            if response.status_code != 200:
                printRed('Error al obtener la página del producto')
                print(response.status_code)
                banned = True
                time.sleep(banned_sleep_time)

                default_delay += 1 # Vamos aumentando para hallar el default_delay perfecto donde no banee

            if banned == False:

                data = response.json()
                section_data = data.get("sectionPopupData", {})

                # Le añado un precio por defecto muy alto por si no hay entradas disponibles
                precio = min(
                    (item.get("rawMinPrice", float("inf")) for item in section_data.values()),
                    default=100000000
                )
                
                if precio < precioMaximo:

                    headers = headers_get()

                    response = session.get(
                        urlEvento,
                        headers=headers,
                    )

                    # Dependiendo de la seguridad implementada el primer listing puede ser inválido
                    primerListingValido = response.text.split('items"')[1].split('"id":')[1].split(',')[0].strip()[0]

                    if primerListingValido == '-':
                        listingValido = 2
                    else:
                        listingValido = 1

                    listingId = response.text.split('items"')[1].split('"id":')[listingValido].split(',')[0]
                    eventId = response.text.split('items"')[1].split('"id":')[listingValido].split('"eventId":')[1].split(',')[0]
                    ticketQuantity = response.text.split('items"')[1].split('"id":')[listingValido].split('"availableTickets":')[1].split(',')[0]
                    urlcheckout = f'https://www.viagogo.com/secure/buy/Initialise?ListingID={listingId}&EventID={eventId}&quantity={ticketQuantity}'
                    section = response.text.split('items"')[1].split('"id":')[listingValido].split('"section":"')[1].split('",')[0]
                    row = response.text.split('items"')[1].split('"id":')[listingValido].split('"row":"')[1].split('",')[0]
                    seat = response.text.split('items"')[1].split('"id":')[listingValido].split('"seat":"')[1].split('",')[0]
                    infoSeat = f'SEC: {section}, ROW: {row}, SEAT: {seat}, QTY: {ticketQuantity}'
                    imagen = 'https://media.stubhubstatic.com/stubhub-v2-catalog' + response.text.split('stubhub-v2-catalog')[1].split('" />')[0]

                    notification_viagogo(
                        webhook_url=discordWebhook,
                        event_url=urlEvento,
                        event_name=titulo,
                        seat_info=infoSeat,
                        image_url=imagen,
                        price=str(precio),
                        checkout_url=urlcheckout
                    )
                    
                    printVerde(f'Entradas encontradas! {urlEvento}')
                    time.sleep(20)
                    
                else:
                    printHora(f'No se encontraron entradas por debajo de {precioMaximo}€ para {titulo}')
                    time.sleep(default_delay) # Tiempo de espera entre peticiones para evitar rate limit

        except Exception as e:
            print("Error en la solicitud:", e)
            time.sleep(180) # Si da error haciendo la peticion le metemos un tiempo de espera


def leer_csv_y_ejecutar_threads(archivo_csv):
    hilos = []

    with open(archivo_csv, mode='r', newline='') as file:
        lector = csv.DictReader(file)

        for fila in lector:
            enlace = fila['enlace']
            precio = int(fila['precioMax'])
            webhook = fila['discordWebhook']
            hilo = threading.Thread(target=main, args=(enlace, precio, webhook))
            hilos.append(hilo)
            hilo.start()
            time.sleep(2) # Asi hacemos que no arranquen todas las peticiones al mismo tiempo


leer_csv_y_ejecutar_threads('data.csv')
