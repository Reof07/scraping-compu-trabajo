import time
import random
import traceback

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle

from ..core.logger_config import logger
from ..core.selenium import driver
from .scraping_service.job_candidates import process_pagination


async def load_cookies(driver):
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
        

async def save_cookies(driver):
    """Save the current cookies in a file."""
    try:
        cookies = driver.get_cookies()
        pickle.dump(cookies, open("cookies.pkl", "wb"))
        logger.info("Cookies guardadas exitosamente.")
    except Exception as e:
        logger.error(f"Error al guardar cookies: {e}")
        
        
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

        WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))

        if "Login" not in driver.current_url:
            logger.info("Login exitoso. URL actual:", driver.current_url)
            await save_cookies(driver)
        else:
            logger.error("Login fallido. URL actual:", driver.current_url)
            
    except Exception as e:
            logger.error(f"Error al realizar login: {e}")
            # Si el login falla, intentar de nuevo con los cookies guardados
            await load_cookies(driver)
            if "Login" in driver.current_url:
                logger.info("Reintentando login...")
                await doing_login(driver, username, password)

    
async def get_offers(driver, list_offers):
    """Validate the links of the offers."""
    validate_links = []
    
    for offer in list_offers.offers: 
        url = offer.url
        print(f"Abriendo el enlace de la oferta: {url}")
        
        driver.get(url)
        WebDriverWait(driver, 10)
        print(driver.current_url)
        
        print("Verificando si la oferta está vencida...")
        time.sleep(random.uniform(3, 5))  
        try:
            element = driver.find_element(By.XPATH, "//h3[text()='Su oferta de empleo ha vencido']")
            texto_encontrado = element.text
            if texto_encontrado:
                print(texto_encontrado)
                print(f"La oferta {url} está vencida..")
        except Exception:
            print(f"La oferta {url} no está vencida..")
            validate_links.append(url)
    
    return validate_links


async def flujo_principal(db, email: str, password: str, list_offers):
    """Take control of the entire process."""
    try:
        logger.info("Iniciando extracción de candidatos...")    
        
        #doing login
        await doing_login(driver, email, password)
        
        #validate links
        list_offers = await get_offers(driver, list_offers)
        
        wait = WebDriverWait(driver, 10)
        
        for url in list_offers:
            await process_pagination(driver, wait, url)

    except Exception as e:
        error_message = f"Error en el flujo principal: {str(e)}"
        logger.error(error_message)
        logger.error(f"Traceback: {traceback.format_exc()}")
    finally:
        logger.info("Cerrando navegador...")
        driver.quit()