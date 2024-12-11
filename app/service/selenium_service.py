import time
import random

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle

from ..core.logger_config import logger
from ..core.selenium import driver
from .scraping_service.job_candidates import extract_candidate_info
from .scraping_service.details_candidate import extract_candidate_details
from .offer_service import create_offer
from .candidate_service import create_candidate


async def get_candidate_info(data, db):
    """Get the information of the candidates from the offer."""
    # candidate_info_list = []
    for applicant in data:
        candidate_info = await extract_candidate_info(driver, applicant['applicants_link'])
        for candidate in candidate_info:
            print(f"Candidate: {candidate}")
            await create_candidate(db, applicant['offer_id'], candidate)
        # candidate_info_list.append(candidate_info)
    
    return candidate_info

async def get_candidates_details(driver, data):
    """Get the information of the candidates from the candidate info."""
    candidates_details_list = []
    for applicant in data:
        details = await extract_candidate_details(driver, applicant['applicants_link'])
        candidates_details_list.append(details)
    
    return candidates_details_list

def load_cookies(driver):
    """Load cookies from a file if they exist."""
    try:
        cookies = pickle.load(open("cookies.pkl", "rb"))
        domain = "empresa.co.computrabajo.com"
        if domain in driver.current_url:
            for cookie in cookies:
                driver.add_cookie(cookie)
            logger.info("Cookies cargadas exitosamente.")
        else:
            logger.info(f"No se pueden cargar cookies en el dominio actual: {driver.current_url}")
    except FileNotFoundError:
        logger.error("No se encontraron cookies guardadas. Realizando login manual.")
        

# Función para guardar cookies
def save_cookies(driver):
    """Save the current cookies in a file."""
    try:
        cookies = driver.get_cookies()
        pickle.dump(cookies, open("cookies.pkl", "wb"))
        logger.info("Cookies guardadas exitosamente.")
    except Exception as e:
        logger.error(f"Error al guardar cookies: {e}")
        
        
# Función para realizar login
async def doing_login(driver, username, password):
    """Perform login with the provided credentials."""
    try:
        logger.info("Accediendo a la página de login...")
        driver.get("https://empresa.co.computrabajo.com/Login")
        # time.sleep(3)  # Esperar para evitar bloqueos
        
        # Esperar hasta que los campos de usuario y contraseña sean visibles
        wait = WebDriverWait(driver, 10)
        usuario = wait.until(EC.visibility_of_element_located((By.NAME, 'UserName')))
        contraseña = wait.until(EC.visibility_of_element_located((By.NAME, 'Password')))

        logger.info("Ingresando credenciales...")
        # usuario = driver.find_element(By.NAME, 'UserName')
        # contraseña = driver.find_element(By.NAME, 'Password')
        usuario.send_keys(username)
        contraseña.send_keys(password)
        time.sleep(1)

        logger.info("Haciendo clic en el botón de login...")
        login_button = driver.find_element(By.CSS_SELECTOR, "input[value='Entrar']")
        login_button.click()
        # time.sleep(5)  # Esperar para evitar problemas con el redireccionamiento

        WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))

        if "Login" not in driver.current_url:
            logger.info("Login exitoso. URL actual:", driver.current_url)
            save_cookies(driver)
        else:
            logger.error("Login fallido. URL actual:", driver.current_url)
            
    except Exception as e:
            logger.error(f"Error al realizar login: {e}")
            # Si el login falla, intentar de nuevo con los cookies guardados
            load_cookies(driver)
            if "Login" in driver.current_url:
                logger.info("Reintentando login...")
                await doing_login(driver, username, password)

                
        
# Función para acceder a la página de ofertas y extraer información
async def extract_all_offers(db, driver, url, user_id):
    """Extrae todas las ofertas laborales desde la página."""
    driver.get(url)
    print(f"Página inicial: {driver.current_url}")

    offers_data = []
    while True:
        # Esperar que los artículos se carguen
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.aClick"))
        )

        # Seleccionar todos los artículos de la página actual
        articles = driver.find_elements(By.CSS_SELECTOR, "article.aClick")

        # Extraer los datos de los artículos
        for article in articles:
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

            # Extraer el ID de la oferta desde el input checkbox
            try:
                checkbox_input = article.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                offer["offer_id"] = checkbox_input.get_attribute("id").split("chk_")[1]
            except Exception:
                offer["offer_id"] = "ID no encontrado"

            #save in database
            await create_offer(db, user_id, offer)
            
            time.sleep(random.uniform(1, 2)) 
            
            offers_data.append(offer)

        # Intentar avanzar a la siguiente página
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.b_next")
            next_button.click()
            WebDriverWait(driver, 10).until(EC.staleness_of(articles[0]))
            
            time.sleep(random.uniform(3, 5))
        except Exception:
            print("No se encontró el botón 'Siguiente', terminando la extracción.")
            break

    return offers_data


async def print_offers(offers_data):
    """Imprime las ofertas extraídas."""
    print("\nOfertas extraídas:")
    for offer in offers_data:
        print(
            f"Título: {offer['title']}\n"
            f"Ubicación: {offer['location']}\n"
            f"Fecha de actualización: {offer['date_updated']}\n"
            f"Vistas: {offer['views']}\n"
            f"Fecha de caducidad: {offer['expiration_date']}\n"
            f"Inscritos: {offer['applicants']}\n"
            f"Enlace a inscritos: {offer['applicants_link']}\n"
            f"ID de la oferta: {offer['offer_id']}\n"
            "--------------------------------------------"
        )


async def flujo_principal(db, email: str, password: str, user_id):
    """Take control of the entire process."""
    try:
        logger.info("Iniciando flujo principal...")
        driver.get("https://empresa.co.computrabajo.com/Login")
        time.sleep(3)  # Esta espera puede mantenerse para la carga inicial

        await doing_login(driver, email, password)

        # Si el login es exitoso, proceder con la extracción de ofertas
        url_offers = "https://empresa.co.computrabajo.com/Company/Offers"
        offers_data = await extract_all_offers(db, driver, url_offers, user_id)
        candidate_info = await get_candidate_info(offers_data, db)
        # candidates_details = await get_candidates_details(driver, candidate_info)
        await print_offers(offers_data)

    except Exception as e:
        logger.error(f"Error en el flujo principal: {e}")
    finally:
        logger.info("Cerrando navegador...")
        driver.quit()