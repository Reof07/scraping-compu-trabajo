from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
import time
import random
import asyncio
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

from ...core.logger_config import logger
from ..candidate_service import create_candidate

def get_candidate_info(article):
    """Extra the information of a candidate from an article."""
    try:
        name = article.find_element(By.CSS_SELECTOR, "a.js-o-link.nom .w75_ms").text.strip()
    except Exception:
        name = "Nombre no encontrado"

    try:
        applied_date = article.find_element(By.CSS_SELECTOR, "li.aplicado").text.strip()
    except Exception:
        applied_date = "Fecha no encontrada"

    try:
        age = article.find_element(By.CSS_SELECTOR, "li.edad").text.strip()
    except Exception:
        age = "Edad no encontrada"

    try:
        studies = article.find_element(By.CSS_SELECTOR, "li.estudios").text.strip()
    except Exception:
        studies = "Estudios no encontrados"

    try:
        adequacy = article.find_element(By.CSS_SELECTOR, "li.adecuacion p.fs_24").text.strip()
    except Exception:
        adequacy = "Adecuación no encontrada"

    try:
        profile_link = article.find_element(By.CSS_SELECTOR, "a.js-o-link.nom").get_attribute("href")
    except Exception:
        profile_link = "Enlace no encontrado"

    # Devolver los datos extraídos del candidato
    return {
        "name": name,
        "applied_date": applied_date,
        "age": age,
        "studies": studies,
        "adequacy": adequacy,
        "profile_link": profile_link
    }

def go_to_next_page(driver):
    """Try to click on the 'Next' button to load the next page."""
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "a.b_next")
        # Verificar si el botón "Siguiente" está habilitado (sin la clase "sel")
        if "sel" not in next_button.get_attribute("class"):
            next_button.click()  # Hacer clic en "Siguiente"
            print("Cargando la siguiente página...")
            time.sleep(random.uniform(3, 5))
            return True  # Se cargó la siguiente página
        else:
            print("Última página alcanzada.")
            return False  # No hay más páginas
    except Exception as e:
        print(f"Error al intentar hacer clic en 'Siguiente': {e}")
        return False  # Error al intentar hacer clic, detener el bucle

# def extract_candidate_info(db, driver, offer_id, applicants_link):
#     """Extrae la información de los candidatos navegando por las páginas de inscritos."""
#     candidates_info = []

#     # Navegar al enlace de los inscritos
#     driver.get(applicants_link)
#     time.sleep(random.uniform(3, 5))
#     print(f"Abriendo el enlace de inscritos: {applicants_link}")

#     while True:
#         try:
#             # Esperar a que los artículos de candidatos carguen
#             WebDriverWait(driver, 10).until(
#                 EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.rowuser"))
#             )

#             # Extraer la información de los candidatos en la página actual
#             articles = driver.find_elements(By.CSS_SELECTOR, "article.rowuser")

#             for article in articles:
#                 candidate_info = get_candidate_info(article)
#                 candidates_info.append(candidate_info)
#                 logger.info(f"Candidato extraido: {candidate_info}")
#                 create_candidate(db, offer_id, candidate_info)
#                 time.sleep(random.uniform(2, 3))
                
#             # Intentar cargar la siguiente página
#             if not go_to_next_page(driver):
#                 break  # Si no se puede cargar la siguiente página, terminar el bucle

#             time.sleep(random.uniform(5, 10))
            
#             retry_count = 0  # Reiniciar el contador de reintentos si todo va bien
        
#         except (WebDriverException, TimeoutException) as e:
#             retry_count += 1
#             print(f"Error al cargar la página: {e}. Intentando nuevamente ({retry_count}/3)...")

#             # Si hay 3 fallos consecutivos, esperar más tiempo antes de reintentar
#             if retry_count >= 3:
#                 print("Demasiados fallos consecutivos. Esperando más tiempo antes de intentar nuevamente.")
#                 time.sleep(random.uniform(20, 30))  # Pausa más larga antes de reintentar
#                 retry_count = 0  # Reiniciar el contador de reintentos

#             else:
#                 # Reintentar la carga de la página después de una pausa corta
#                 time.sleep(random.uniform(3, 5))  # Pausa entre 3 y 5 segundos entre reintentos

#     return candidates_info

######################################################################################new###########
def extract_candidate_info(db, driver, offer_id, applicants_link):
    """Extrae la información de los candidatos navegando por las páginas de inscritos."""
    candidates_info = []

    # Navegar al enlace de los inscritos
    driver.get(applicants_link)
    time.sleep(random.uniform(3, 5))
    print(f"Abriendo el enlace de inscritos: {applicants_link}")

    while True:
        try:
            # Esperar a que los artículos de candidatos carguen
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.rowuser"))
            )

            # Extraer los artículos de la página actual
            articles = driver.find_elements(By.CSS_SELECTOR, "article.rowuser")

            # Usar ThreadPoolExecutor para procesar los artículos en paralelo
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_article = {executor.submit(get_candidate_info, article): article for article in articles}

                # Esperar que todas las tareas se completen y procesar los resultados
                for future in concurrent.futures.as_completed(future_to_article):
                    candidate_info = future.result()
                    candidates_info.append(candidate_info)
                    logger.info(f"Candidato extraído: {candidate_info}")
                    
                    # Guardar en la base de datos (puedes hacerlo asincrónicamente si tu DB lo soporta)
                    create_candidate(db, offer_id, candidate_info)
                    time.sleep(random.uniform(2, 3))

            # Intentar cargar la siguiente página
            if not go_to_next_page(driver):
                break  # Si no se puede cargar la siguiente página, terminar el bucle

            time.sleep(random.uniform(5, 10))
        
        except (WebDriverException, TimeoutException) as e:
            retry_count += 1
            print(f"Error al cargar la página: {e}. Intentando nuevamente ({retry_count}/3)...")

            # Si hay 3 fallos consecutivos, esperar más tiempo antes de reintentar
            if retry_count >= 3:
                print("Demasiados fallos consecutivos. Esperando más tiempo antes de intentar nuevamente.")
                time.sleep(random.uniform(20, 30))  # Pausa más larga antes de reintentar
                retry_count = 0  # Reiniciar el contador de reintentos

            else:
                # Reintentar la carga de la página después de una pausa corta
                time.sleep(random.uniform(3, 5))  # Pausa entre 3 y 5 segundos entre reintentos

    return candidates_info

def check_offer_status(offer, status):
    """Verifica si la oferta está vencida."""
    try:
        if status == "Vencida":
            return True
        else:
            return False
    except Exception:
        return False

def extract_candidates_from_offers(db, driver, offers_data, user_id):
    """Extrae los candidatos de las ofertas extraídas."""
    print("Extrayendo candidatos de las ofertas...")
    candidates_from_offers = []
    for offer in offers_data:
        try:
            applicants_link = offer["applicants_link"]
            
            #SI LA OFERTA ESTA VENCIDA, HACER UN CHECK DE LA OFERTA.
            if check_offer_status(offer, offer["status"]):
                logger.info("Verificando si la oferta está vencida...")                
                print(f"Abriendo el enlace de inscritos: {applicants_link}")
                driver.get(applicants_link)
                print("Cargando la página de inscritos...")
                time.sleep(random.uniform(3, 5))

                try:
                    element = driver.find_element(By.XPATH, "//h3[text()='Su oferta de empleo ha vencido']")
                    texto_encontrado = element.text
                    print(texto_encontrado)
                    logger.info("La oferta está vencida. por lo tanto, no se extraen candidatos.")
                except Exception as e:
                    print(f"No se encontró el elemento: {e}")
                
            else:
                logger.info(f"La oferta {offer['applicants_link']} no está vencida. Extrayendo candidatos...")
                time.sleep(random.uniform(3, 5))
                logger.info("Cargando la página de inscritos...")
                extract_candidate_info(db, driver, offer["offer_id"], applicants_link)
        

        except Exception as e:
            print(f"Error al extraer candidatos de la oferta: {e}")
            # print(f"Traceback: {traceback.format_exc()}")
