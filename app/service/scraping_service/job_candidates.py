import time
import re

from selenium.common.exceptions import WebDriverException, TimeoutException

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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


async def extract_candidatos(driver):
    """ function to extract candidates from the website """
    info_candidate = {}  
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
            # Extraer detalles de cada candidato
            name = candidate.get('name', 'N/A')
            applied_date = candidate.get('applied_date', 'N/A')
            age = candidate.get('age', 'N/A')
            studies = candidate.get('studies', 'N/A')
            adequacy = candidate.get('adequacy', 'N/A')
            profile_link = candidate.get('profile_link', 'N/A')
            candidate_id = candidate.get('candidate_id', 'N/A')

            info_candidate = {
                'nombre': name,
                'fecha_aplicacion': applied_date,
                'edad': age,
                'nivel_estudios': studies,
                'adecuacion': adequacy,
                'link_detalles': profile_link,
                'candidate_id': candidate_id
            }

            all_candidates.append(info_candidate)
                                
            # Mostrar los detalles del candidato
            print(f"Nombre: {name}")
            print(f"Fecha de aplicación: {applied_date}")
            print(f"Edad: {age}")
            print(f"Nivel de estudios: {studies}")
            print(f"Adecuación: {adequacy}")
            print(f"Link Detalles: {profile_link}")
            print(f"ID del candidato: {candidate_id}")
            # print(f"Detalles del candidato: {combined_candidate_data}")
            print("-----------------------------------")
        
        except Exception as e:
            print(f"Error procesando el candidato: {e}")
    
    print('Fin de la extracción')
    return  all_candidates

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
                candidates = await extract_candidatos(driver)

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
