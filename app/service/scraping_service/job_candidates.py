import time
import re

from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..candidate_service import _save_candidates_batch
from ..candidate_service import save_candidate_details_batch

from ...utils.utils import extract_offer_id
from .details_candidate import extract_candidate_details
from ...core.logger_config import logger


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

        try:
            profile_link = article.find_element(By.CSS_SELECTOR, "a.js-o-link.nom").get_attribute("href")
        except Exception:
            profile_link = "Enlace no encontrado"

        candidate_id = None
        if profile_link != "Enlace no encontrado":
            match = re.search(r'ims=([A-F0-9]+)', profile_link)
            if match:
                candidate_id = match.group(1)

        candidate = {
            "name": name,
            "applied_date": applied_date,
            "age": age,
            "studies": studies,
            "adequacy": adequacy,
            "profile_link": profile_link,
            "candidate_id": candidate_id  
        }
        candidates_info.append(candidate)

    return candidates_info


async def extract_candidatos(driver, offer_id, url, wait, batch_size=50):
    """ function to extract candidates from the website """
    info_candidate = {}  
    all_candidates = []  
    batch = [] 
    
    
    logger.info('Procesando la extracción...')
    logger.info(driver.current_url)
    
    all_candidates = []

    candidates_info = await extract_candidate_info(driver)
    logger.info(f"Cantidad de candidatos encontrados: {len(candidates_info)}")

    if len(candidates_info) == 0:
        logger.info("No se encontraron candidatos.")
        return 
    
    
    for candidate in candidates_info:
        try:
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
                    
            if len(batch) >= batch_size:
                await _save_candidates_batch(batch)
                batch.clear()

        except Exception as e:
            logger.info(f"Error procesando el candidato: {e}")

    if batch:
        await _save_candidates_batch(batch)

    logger.info('Fin de la extracción')
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
        logger.info(f"Página inicial: {driver.current_url}")
        
        if driver.current_url == "https://empresa.co.computrabajo.com/Account/Used" or driver.current_url == "https://empresa.co.computrabajo.com/Login?ReturnUrl=%2fCompany":
            logger.info("No es posible acceder a la página...")
            return

        current_url = driver.current_url
        offer_id = extract_offer_id(current_url)
        current_page = 1

        while True:
            try:
                pager = wait.until(EC.presence_of_element_located((By.ID, "pager_Pager_PageSelected")))
                pages = pager.find_elements(By.TAG_NAME, "a")

                # Detecta la página actual
                current_page_element = None
                for page in pages:
                    if "sel" in page.get_attribute("class"):
                        current_page_element = page
                        current_page = int(page.text.strip())
                        logger.info(f"Estás en la página: {current_page}")
                        break

                if not current_page_element:
                    logger.info("No se detectó la página actual.")
                    break

                candidates = await extract_candidatos(driver, offer_id, url,wait)
                
                logger.info(f"numero de candidatos: {len(candidates)}")
                
                logger.info(f"procesados la extracción de detalles  de: {len(candidates)} candidatos.")
                
                details_list =[]
                for candidate in candidates:
                    details = await extract_candidate_details(driver, candidate['details_link'], candidate['uuid_candidate'])
                    details_list.append(details)
                                        
                    
                await save_candidate_details_batch(details_list) ## saque esto del for
                details_list.clear()
                
                time.sleep(5)
                
                try:
                    # Busca el botón "Siguiente" y verifica si está habilitado
                    next_button = pager.find_element(By.CLASS_NAME, "b_next")

                
                except TimeoutException:
                    print("No se encontró el botón 'Siguiente' después del tiempo de espera.")
                    return None
                except NoSuchElementException:
                    print("No se encontró el botón 'Siguiente'.")
                    return None

                # Haz clic en "Siguiente" para avanzar
                logger.info(f"Pasando a la página: {current_page + 1}")
                next_button.click()

                # Espera a que el DOM se actualice
                wait.until(EC.staleness_of(pager))

            except Exception as e:
                logger.error(f"Error en el ciclo principal: {e}")
                break

    finally:
        logger.info(f"Finalizando extracción de candidatos para la oferta: {url}")

