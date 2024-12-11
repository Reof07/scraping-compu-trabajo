import asyncio
import time
import random
import traceback

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from ..offer_service import create_offer
from ...core.logger_config import logger

async def process_offer(db, article, user_id):
    """Procesa una sola oferta de trabajo de un artículo."""
    offer = {}

    try:
        title_element = article.find_element(By.CLASS_NAME, "test_offername")
        offer["title"] = title_element.text.strip()
    except Exception:
        try:
            title_element = article.find_element(By.CSS_SELECTOR, "span.fs18.lh1")
            offer["title"] = title_element.text.strip()
        except Exception:
            offer["title"] = "Título no encontrado"

    try:
        offer["location"] = article.find_element(By.CSS_SELECTOR, "p.mt5").text.strip()
    except Exception:
        offer["location"] = "Ubicación no encontrada"

    try:
        offer["date_updated"] = article.find_element(By.CSS_SELECTOR, "p.fc_aux.fs12").text.strip()
    except Exception:
        offer["date_updated"] = "Fecha no encontrada"

    try:
        views_text = article.find_element(By.CSS_SELECTOR, "div.fc_aux.fwB.mt5").text
        offer["views"] = views_text.split()[0] if views_text else "0"
    except Exception:
        offer["views"] = "0"

    try:
        offer["expiration_date"] = article.find_element(By.CSS_SELECTOR, "div.tc_fx").text.strip()
    except Exception:
        offer["expiration_date"] = "Fecha no encontrada"

    try:
        applicants_element = article.find_element(By.CSS_SELECTOR, "a.dB.fwB.fs20.hide_m")
        offer["applicants"] = applicants_element.text.strip()
        offer["applicants_link"] = applicants_element.get_attribute("href")
    except Exception:
        offer["applicants"] = "0"
        offer["applicants_link"] = "Enlace no encontrado"

    try:
        offer_link = article.find_element(By.CSS_SELECTOR, "a.fn.fs18.test_offername")
        offer["offer_id"] = offer_link.get_attribute("href").split('oi=')[1]
    except Exception:
        offer["offer_id"] = "ID no encontrado"

    try:
        checkbox_input = article.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
        offer["offer_id"] = checkbox_input.get_attribute("id").split("chk_")[1]
    except Exception:
        offer["offer_id"] = "ID no encontrado"

    # Guardar la oferta en la base de datos asincrónicamente
    await create_offer(db, user_id, offer)

    # Introducimos un pequeño delay aleatorio para simular comportamiento humano
    await asyncio.sleep(random.uniform(1, 2))

    return offer

async def go_to_next_page(driver):
    """Manejo de paginación de la oferta (ir a la siguiente página)."""
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "a.b_next")
        next_button.click()
        WebDriverWait(driver, 10).until(EC.staleness_of(next_button))  # Asegura que la página anterior se haya cargado completamente
        await asyncio.sleep(random.uniform(3, 5))  # Usamos asyncio.sleep para permitir que se ejecute sin bloquear
        return True
    except Exception:
        return False

async def extract_all_offers(db, driver, url, user_id, batch_size=10):
    """Extrae todas las ofertas laborales desde la página procesándolas en lotes."""
    try:
        driver.get(url)
        print(f"Página inicial: {driver.current_url}")
        offers_data = []
        all_articles = []  # Lista para almacenar todos los artículos de la página

        while True:
            try:
                # Esperar que los artículos se carguen de manera más eficiente
                WebDriverWait(driver, 60).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.aClick"))
                )
            except TimeoutException:
                logger.error(f"Timeout esperando artículos en la URL: {driver.current_url}")
                break  # Salir del loop si ocurre un timeout

            # Seleccionar todos los artículos de la página actual
            articles = driver.find_elements(By.CSS_SELECTOR, "article.aClick")
            if not articles:
                logger.warning("No se encontraron artículos en esta página.")
                break  # Si no se encontraron artículos, salir del loop

            all_articles.extend(articles)  # Añadimos los artículos a la lista global

            while len(all_articles) >= batch_size:
                batch = all_articles[:batch_size]  # Creamos el lote
                all_articles = all_articles[batch_size:]  # Eliminamos el lote procesado

                tasks = [asyncio.create_task(process_offer(db, article, user_id)) for article in batch]
                batch_results = await asyncio.gather(*tasks)
                # Filtrar valores None (en caso de error durante el procesamiento)
                batch_results = [result for result in batch_results if result is not None]
                offers_data.extend(batch_results)  # Añadimos los resultados del lote a la lista final

            # Intentar avanzar a la siguiente página
            if not await go_to_next_page(driver):
                print("No se encontró el botón 'Siguiente', terminando la extracción.")
                break

            # Añadir una pequeña pausa para evitar demasiadas solicitudes rápidas al servidor
            time.sleep(random.uniform(3, 5))

        # Procesar los artículos restantes si hay alguno pendiente
        if all_articles:
            tasks = [asyncio.create_task(process_offer(db, article, user_id)) for article in all_articles]
            batch_results = await asyncio.gather(*tasks)
            # Filtrar valores None (en caso de error durante el procesamiento)
            batch_results = [result for result in batch_results if result is not None]
            offers_data.extend(batch_results)

        return offers_data

    except Exception as e:
        logger.error(f"Error en extract_all_offers: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise 