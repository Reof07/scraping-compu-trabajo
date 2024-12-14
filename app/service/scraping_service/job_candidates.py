import time
import re

from selenium.common.exceptions import WebDriverException, TimeoutException

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..candidate_service import _save_candidates_batch

from ...utils.utils import extract_offer_id


async def extract_candidate_info(driver):
    """ Get the information of the candidates from the page. """
    candidates_info = []

    # Esperar a que los artículos de candidatos carguen
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.rowuser"))
    )

    # Extraer la información de los candidatos en la página actual
    articles = driver.find_elements(By.CSS_SELECTOR, "article.rowuser")

    for article in articles:
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

        # Obtener el enlace del perfil
        try:
            profile_link = article.find_element(By.CSS_SELECTOR, "a.js-o-link.nom").get_attribute("href")
        except Exception:
            profile_link = "Enlace no encontrado"

        # Extraer el ID del candidato del link (valor del parámetro 'ims')
        candidate_id = None
        if profile_link != "Enlace no encontrado":
            match = re.search(r'ims=([A-F0-9]+)', profile_link)
            if match:
                candidate_id = match.group(1)


        # Guardar la información del candidato
        candidate = {
            "name": name,
            "applied_date": applied_date,
            "age": age,
            "studies": studies,
            "adequacy": adequacy,
            "profile_link": profile_link,
            "candidate_id": candidate_id  
        }
        print(candidate)
        candidates_info.append(candidate)

    return candidates_info


async def extract_candidatos(driver, offer_id, batch_size=50):
    """ function to extract candidates from the website """
    info_candidate = {}  
    all_candidates = []  # Lista de todos los candidatos procesados
    batch = []  # Lote actual
    
    
    print('Procesando la extracción...')
    print(driver.current_url)
    
    all_candidates = []

    # Extraer la información de los candidatos
    candidates_info = await extract_candidate_info(driver)
    print(f"Cantidad de candidatos encontrados: {len(candidates_info)}")

    if len(candidates_info) == 0:
        print("No se encontraron candidatos.")
        return  # Termina la función si no hay candidatos
    
    # Procesar los candidatos extraídos
    for candidate in candidates_info:
        try:
            # Procesar datos del candidato
            candidate_data = {
                'name': candidate.get('name', 'N/A'),
                'application_date': candidate.get('applied_date', 'N/A'),
                'age': candidate.get('age', 'N/A'),
                'education_level': candidate.get('studies', 'N/A'),
                'suitability': candidate.get('adequacy', 'N/A'),
                'details_link': candidate.get('profile_link', 'N/A'),
                'uuid_candidate': candidate.get('candidate_id', 'N/A'),
                'uuid_offer': offer_id
            }
            batch.append(candidate_data)
            all_candidates.append(candidate_data)

            # Guardar en la base de datos si alcanzamos el tamaño del lote
            if len(batch) >= batch_size:
                _save_candidates_batch(batch)
                batch.clear()

        except Exception as e:
            print(f"Error procesando el candidato: {e}")

    # Guardar los candidatos restantes en el lote
    if batch:
        _save_candidates_batch(batch)

    print('Fin de la extracción')
    return all_candidates

async def process_pagination(driver, wait, url):
    """
    function to process pagination on the website and extract candidates.

    Args:
        driver: Instance of Selenium WebDriver.
        wait: WebDriverWait configurado con un tiempo de espera.
        wait: WebDriverWaitset up with a wait time.
        url: URL to start the navigation.
    """
    try:
        driver.get(url)
        print(f"Página inicial: {driver.current_url}")
        current_url = driver.current_url
        offer_id = extract_offer_id(current_url)
        print(f"ID de la oferta: {offer_id}")
        current_page = 1

        while True:
            try:
                # Espera y detecta la barra de paginación
                pager = wait.until(EC.presence_of_element_located((By.ID, "pager_Pager_PageSelected")))
                pages = pager.find_elements(By.TAG_NAME, "a")

                # Detecta la página actual
                current_page_element = None
                for page in pages:
                    if "sel" in page.get_attribute("class"):
                        current_page_element = page
                        current_page = int(page.text.strip())
                        print(f"Estás en la página: {current_page}")
                        break

                if not current_page_element:
                    print("No se detectó la página actual.")
                    break

                # Llama a la función de extracción
                candidates = await extract_candidatos(driver, offer_id)

                time.sleep(3)

                # Busca el botón "Siguiente" y verifica si está habilitado
                next_button = pager.find_element(By.CLASS_NAME, "b_next")
                if "disabled" in next_button.get_attribute("class"):
                    print("Botón 'Siguiente' deshabilitado. Fin del paginado.")
                    break

                # Haz clic en "Siguiente" para avanzar
                print(f"Pasando a la página: {current_page + 1}")
                next_button.click()

                # Espera a que el DOM se actualice
                wait.until(EC.staleness_of(pager))

            except Exception as e:
                print(f"Error en el ciclo principal: {e}")
                break

    finally:
        driver.quit()
