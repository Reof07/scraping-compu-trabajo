import asyncio
import time
import random
import traceback

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle

from ..core.logger_config import logger
from ..core.selenium import driver
from .scraping_service.job_candidates import extract_candidates_from_offers
from .scraping_service.details_candidate import extract_candidate_details
from .offer_service import create_offer
from .scraping_service.offer import extract_all_offers
from .candidate_service import create_candidate


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
        
        # Esperar hasta que los campos de usuario y contraseña sean visibles
        wait = WebDriverWait(driver, 10)
        usuario = wait.until(EC.visibility_of_element_located((By.NAME, 'UserName')))
        contraseña = wait.until(EC.visibility_of_element_located((By.NAME, 'Password')))

        logger.info("Ingresando credenciales...")
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
            f"Estatus: {offer['status']}\n"
            "--------------------------------------------"
        )


async def flujo_principal(db, email: str, password: str, user_id):
    """Take control of the entire process."""
    try:
        logger.info("Iniciando flujo principal...")
        driver.get("https://empresa.co.computrabajo.com/Login")
        time.sleep(3)

        await doing_login(driver, email, password)

        url_offers = "https://empresa.co.computrabajo.com/Company/Offers"
        offers_data = await extract_all_offers(db, driver, url_offers, user_id)
        cadidates_from_offers = extract_candidates_from_offers(db, driver, offers_data, user_id)
        print(f"Candidatos extraídos: {cadidates_from_offers}")
        # await print_offers(offers_data)

    except Exception as e:
        error_message = f"Error en el flujo principal: {str(e)}"
        logger.error(error_message)
        logger.error(f"Traceback: {traceback.format_exc()}")  # Esto loguea el traceback completo
    finally:
        logger.info("Cerrando navegador...")
        driver.quit()