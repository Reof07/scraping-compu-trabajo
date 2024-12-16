from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from ...core.logger_config import logger

# Función para extraer datos basados en el ícono
async def extract_data_by_icon(driver, icon_class, is_link=False):
    try:
        # Encuentra el ícono específico
        icon = driver.find_element(By.CSS_SELECTOR, f"span.icon.{icon_class}")
        parent = icon.find_element(By.XPATH, "./ancestor::li")  # Buscar el contenedor 'li'
        if is_link:
            link = parent.find_element(By.TAG_NAME, "a")
            return link.get_attribute("href") if link else None
        return parent.find_element(By.CSS_SELECTOR, "span.w100").text.strip()
    except:
        return None 

async def extract_candidate_details(driver, candidate_details_link, candidate_id):
    """
    Extrae detalles del candidato desde un enlace usando Selenium y muestra el progreso.

    :param driver: Instancia activa de Selenium WebDriver.
    :param candidate_details_link: URL con los detalles del candidato.
    :param current_index: Índice actual del enlace procesado en el batch.
    :param total_links: Número total de enlaces en el batch.
    :return: Diccionario con los detalles extraídos.
    """
    try:
        driver.execute_script("window.open(arguments[0]);", candidate_details_link)
        driver.switch_to.window(driver.window_handles[-1])

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.mtB.table.small"))
        )

        candidate_details = {}

        # Mapeo de íconos a campos
        icon_map = {
            "i_email": "email",
            "i_card": "id_number",
            "i_mobile": "mobile_phone",
            "i_whatsapp": "whatsapp",
            "i_flag": "location",
            "i_partner": "marital_status",
            "i_yes": "employment_status",
            "i_no": "driving_license", 
            "i_money": "net_monthly_salary",
        }

        for icon_class, field in icon_map.items():
            try:
                # Buscar el ícono correspondiente
                icon_element = driver.find_element(By.CSS_SELECTOR, f"span.icon.{icon_class}")
                parent = icon_element.find_element(By.XPATH, "./ancestor::li")

                if field == "whatsapp":
                    link = parent.find_element(By.TAG_NAME, "a")
                    candidate_details[field] = link.get_attribute("href") if link else None
                else:
                    candidate_details[field] = parent.find_element(By.CSS_SELECTOR, "span.w100").text.strip()

            except NoSuchElementException:
                candidate_details[field] = f"{field.replace('_', ' ').capitalize()} no encontrado"
            except TimeoutException:
                candidate_details[field] = f"{field.replace('_', ' ').capitalize()} no disponible (timeout)"
            except Exception as e:
                candidate_details[field] = f"Error al extraer {field}: {str(e)}"

        try:
            cv_element = driver.find_element(By.CSS_SELECTOR, "ul.mtB.table.small a.js_download_file")
            candidate_details["cv_link"] = cv_element.get_attribute("href")
        except NoSuchElementException:
            candidate_details["cv_link"] = "CV no encontrado"
        except Exception as e:
            candidate_details["cv_link"] = f"Error al extraer CV: {str(e)}"

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        #logger.info(f"candidate_details: {candidate_details}")
        candidate_details['uuid_candidate'] = candidate_id
        return candidate_details

    except Exception as e:
        logger.error(f"Error al extraer detalles del candidato: {e}")
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        return {}
