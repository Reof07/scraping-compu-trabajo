import time
import random

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

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
        
        # Abrir perfil en una nueva pestaña
        driver.execute_script("window.open(arguments[0]);", candidate_details_link)
        driver.switch_to.window(driver.window_handles[-1]) 

        # Esperar que cargue la sección principal de información
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.mtB.table.small"))
        )

        # Diccionario para almacenar los detalles del candidato
        candidate_details = {}

        # # Mapeo de campos y selectores
        # fields = {
        #     "email": "li:nth-child(1) span.w100",
        #     "id_number": "li:nth-child(2) span.w100",
        #     "mobile_phone": "li.sub_box:nth-child(3) span.w100.pl10",
        #     "whatsapp": "li.sub_box:nth-child(4) a",
        #     "landline_phone": "li.sub_box:nth-child(5) span.w100",
        #     "location": "li:nth-child(6) span.w100",
        #     "age": "li:nth-child(7) span.w100",
        #     "marital_status": "li:nth-child(8) span.w100",
        #     "employment_status": "li:nth-child(9) span.w100",
        #     "driving_license": "li:nth-child(10) span.w100",
        #     "vehicle": "li:nth-child(11) span.w100",
        #     "availability_to_travel": "li:nth-child(12) span.w100",
        #     "availability_to_move": "li:nth-child(13) span.w100",
        #     "net_monthly_salary": "li:nth-child(14) span.w100",
        #     "cv_link": "a.js_download_file.icon_tooltip",
        #     "candidate_id": candidate_id
        # }
        
            # Mapeo de campos y selectores
        fields = {
            "email": "ul.mtB.table.small li:nth-child(1) span.w100",  # Email
            "id_number": "ul.mtB.table.small li:nth-child(2) span.w100",  # Identificación
            "mobile_phone": "ul.mtB.table.small li.sub_box:nth-child(3) span.w100.pl10",  # Teléfono móvil
            "whatsapp": "ul.mtB.table.small li.sub_box:nth-child(4) a",  # WhatsApp
            "landline_phone": "ul.mtB.table.small li.sub_box:nth-child(5) span.w100",  # Teléfono fijo (si existe)
            "location": "ul.mtB.table.small li:nth-child(5) span.w100",  # Ubicación
            "age": "ul.mtB.table.small li:nth-child(6) span.w100",  # Edad
            "marital_status": "ul.mtB.table.small li:nth-child(7) span.w100",  # Estado civil
            "employment_status": "ul.mtB.table.small li:nth-child(8) span.w100",  # Estado de empleo
            "driving_license": "ul.mtB.table.small li:nth-child(9) span.w100",  # Carnet de conducir
            "vehicle": "ul.mtB.table.small li:nth-child(10) span.w100",  # Vehículo propio
            "availability_to_travel": "ul.mtB.table.small li:nth-child(11) span.w100",  # Disponibilidad para viajar
            "availability_to_move": "ul.mtB.table.small li:nth-child(12) span.w100",  # Disponibilidad para cambio de residencia
            "net_monthly_salary": "ul.mtB.table.small li:nth-child(13) span.w100",  # Salario neto mensual
            "cv_link": "ul.mtB.table.small a.js_download_file",  # Enlace al CV
        }   

        # Iterar sobre los campos y extraer información
        # for field, selector in fields.items():
        #     try:
        #         # Para WhatsApp, obtenemos el enlace en lugar del texto
        #         if field == "whatsapp":
        #             candidate_details[field] = driver.find_element(By.CSS_SELECTOR, selector).get_attribute("href")
        #         # Para el enlace del CV, obtenemos el atributo 'href'
        #         elif field == "cv_link":
        #             candidate_details[field] = driver.find_element(By.CSS_SELECTOR, selector).get_attribute("href")
        #         else:
        #             candidate_details[field] = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
        #     except NoSuchElementException:
        #         # Si no se encuentra el elemento, asignar un valor por defecto
        #         candidate_details[field] = f"{field.replace('_', ' ').capitalize()} no encontrado"
        #     except Exception as e:
        #         # Captura de cualquier otro tipo de error
        #         candidate_details[field] = f"Error al obtener {field}: {str(e)}"
            
        
            # Iterar sobre los campos y extraer información
        for field, selector in fields.items():
            try:
                # Para WhatsApp y CV link, obtenemos el atributo 'href'
                if field == "whatsapp" or field == "cv_link":
                    candidate_details[field] = driver.find_element(By.CSS_SELECTOR, selector).get_attribute("href")
                else:
                    candidate_details[field] = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
            except NoSuchElementException:
                candidate_details[field] = f"{field.replace('_', ' ').capitalize()} no encontrado"
            except TimeoutException:
                candidate_details[field] = f"{field.replace('_', ' ').capitalize()} no disponible (timeout)"
            except Exception as e:
                candidate_details[field] = f"Error al extraer {field}: {str(e)}"    
            
        # Cerrar la pestaña y volver a la original
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        print(f"candidate_details: {candidate_details}")
        # Agregar el candidate_id como 'uuid_candidate'
        candidate_details['uuid_candidate'] = candidate_id
        return candidate_details
    
    except Exception as e:
        print(f"Error al extraer detalles del candidato: {e}")
        # Asegurar regresar a la pestaña original incluso si hay error
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        return {}
