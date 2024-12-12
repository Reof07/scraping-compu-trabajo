# # import time
# # import random

# # from selenium.webdriver.common.by import By
# # from selenium.webdriver.support.ui import WebDriverWait
# # from selenium.webdriver.support import expected_conditions as EC

# # def get_field_value(driver, selector, field_name):
# #     """Extrae el valor de un campo específico en la página del candidato."""
# #     try:
# #         # Para WhatsApp y CV, obtener los atributos 'href' en lugar del texto
# #         if field_name in ["whatsapp", "cv_link"]:
# #             return driver.find_element(By.CSS_SELECTOR, selector).get_attribute("href")
# #         else:
# #             return driver.find_element(By.CSS_SELECTOR, selector).text.strip()
# #     except Exception:
# #         return f"{field_name.replace('_', ' ').capitalize()} no encontrado"

# # def extract_candidate_details(driver, candidate_details_link):
# #     """
# #     Extrae detalles del candidato desde un enlace usando Selenium.

# #     :param driver: Instancia activa de Selenium WebDriver.
# #     :param candidate_details_link: URL con los detalles del candidato.
# #     :return: Diccionario con los detalles extraídos.
# #     """
# #     # Navegar al enlace de los detalles del candidato
# #     driver.get(candidate_details_link)
# #     print(f"Abriendo el enlace del candidato: {candidate_details_link}")
# #     time.sleep(random.uniform(5, 10))
# #     # Esperar que cargue la sección principal de información
# #     WebDriverWait(driver, 10).until(
# #         EC.presence_of_element_located((By.CSS_SELECTOR, "ul.mtB.table.small"))
# #     )

# #     # Diccionario para almacenar los detalles del candidato
# #     candidate_details = {}

# #     # Mapeo de campos y selectores
# #     fields = {
# #         "email": "li:nth-child(1) span.w100",
# #         "id_number": "li:nth-child(2) span.w100",
# #         "mobile_phone": "li.sub_box:nth-child(3) span.w100.pl10",
# #         "whatsapp": "li.sub_box:nth-child(4) a",
# #         "landline_phone": "li.sub_box:nth-child(5) span.w100",
# #         "location": "li:nth-child(6) span.w100",
# #         "age": "li:nth-child(7) span.w100",
# #         "marital_status": "li:nth-child(8) span.w100",
# #         "employment_status": "li:nth-child(9) span.w100",
# #         "driving_license": "li:nth-child(10) span.w100",
# #         "vehicle": "li:nth-child(11) span.w100",
# #         "availability_to_travel": "li:nth-child(12) span.w100",
# #         "availability_to_move": "li:nth-child(13) span.w100",
# #         "net_monthly_salary": "li:nth-child(14) span.w100",
# #         "cv_link": "a.js_download_file.icon_tooltip"
# #     }

# #     # Iterar sobre los campos y extraer información
# #     for field, selector in fields.items():
# #         candidate_details[field] = get_field_value(driver, selector, field)

# #     return candidate_details


# import time
# import random
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# def get_field_value(driver, selector, field_name):
#     """Extrae el valor de un campo específico en la página del candidato."""
#     try:
#         # Para WhatsApp y CV, obtener los atributos 'href' en lugar del texto
#         if field_name in ["whatsapp", "cv_link"]:
#             return driver.find_element(By.CSS_SELECTOR, selector).get_attribute("href")
#         else:
#             return driver.find_element(By.CSS_SELECTOR, selector).text.strip()
#     except Exception:
#         return f"{field_name.replace('_', ' ').capitalize()} no encontrado"

# def extract_candidate_details(driver, candidate_details_link):
#     """
#     Extrae detalles del candidato desde un enlace usando Selenium.

#     :param driver: Instancia activa de Selenium WebDriver.
#     :param candidate_details_link: URL con los detalles del candidato.
#     :return: Diccionario con los detalles extraídos.
#     """
#     # Navegar al enlace de los detalles del candidato
#     driver.get(candidate_details_link)
#     print(f"Abriendo el enlace de detalles del candidato: {candidate_details_link}")
#     time.sleep(random.uniform(5, 10))
    
#     # Esperar que cargue la sección principal de información
#     WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, "ul.mtB.table.small"))
#     )

#     # Mapeo de campos y selectores
#     fields = {
#         "email": "li:nth-child(1) span.w100",
#         "id_number": "li:nth-child(2) span.w100",
#         "mobile_phone": "li.sub_box:nth-child(3) span.w100.pl10",
#         "whatsapp": "li.sub_box:nth-child(4) a",
#         "landline_phone": "li.sub_box:nth-child(5) span.w100",
#         "location": "li:nth-child(6) span.w100",
#         "age": "li:nth-child(7) span.w100",
#         "marital_status": "li:nth-child(8) span.w100",
#         "employment_status": "li:nth-child(9) span.w100",
#         "driving_license": "li:nth-child(10) span.w100",
#         "vehicle": "li:nth-child(11) span.w100",
#         "availability_to_travel": "li:nth-child(12) span.w100",
#         "availability_to_move": "li:nth-child(13) span.w100",
#         "net_monthly_salary": "li:nth-child(14) span.w100",
#         "cv_link": "a.js_download_file.icon_tooltip"
#     }

#     # Extraer los detalles del candidato utilizando el mapeo de campos
#     candidate_details = {
#         field: get_field_value(driver, selector, field)
#         for field, selector in fields.items()
#     }

#     return candidate_details

import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_field_value(driver, selector, field_name):
    """Extrae el valor de un campo específico en la página del candidato."""
    try:
        # Para WhatsApp y CV, obtener los atributos 'href' en lugar del texto
        if field_name in ["whatsapp", "cv_link"]:
            value = driver.find_element(By.CSS_SELECTOR, selector).get_attribute("href")
        else:
            value = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
        
        print(f"Campo '{field_name}': {value}")  # Imprimir el valor extraído para cada campo
        return value
    except Exception as e:
        print(f"Error al extraer el campo '{field_name}': {str(e)}")  # Imprimir el error si ocurre
        return f"{field_name.replace('_', ' ').capitalize()} no encontrado"

def extract_candidate_details(driver, candidate_details_link, id_candidate):
    """
    Extrae detalles del candidato desde un enlace usando Selenium.

    :param driver: Instancia activa de Selenium WebDriver.
    :param candidate_details_link: URL con los detalles del candidato.
    :return: Diccionario con los detalles extraídos.
    """
    print(f"Abriendo el enlace de detalles del candidato: {candidate_details_link}")
    
    # Navegar al enlace de los detalles del candidato
    driver.get(candidate_details_link)
    time.sleep(random.uniform(5, 10))  # Pausa para simular comportamiento humano
    
    # Esperar que cargue la sección principal de información
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ul.mtB.table.small"))
    )
    print("Página cargada, comenzando a extraer detalles...")

    # Mapeo de campos y selectores
    fields = {
        "email": "li:nth-child(1) span.w100",
        "id_number": "li:nth-child(2) span.w100",
        "mobile_phone": "li.sub_box:nth-child(3) span.w100.pl10",
        "whatsapp": "li.sub_box:nth-child(4) a",
        "landline_phone": "li.sub_box:nth-child(5) span.w100",
        "location": "li:nth-child(6) span.w100",
        "age": "li:nth-child(7) span.w100",
        "marital_status": "li:nth-child(8) span.w100",
        "employment_status": "li:nth-child(9) span.w100",
        "driving_license": "li:nth-child(10) span.w100",
        "vehicle": "li:nth-child(11) span.w100",
        "availability_to_travel": "li:nth-child(12) span.w100",
        "availability_to_move": "li:nth-child(13) span.w100",
        "net_monthly_salary": "li:nth-child(14) span.w100",
        #"cv_link": "a.js_download_file.icon_tooltip"
    }

    # Extraer los detalles del candidato utilizando el mapeo de campos
    candidate_details = {}
    
    for field, selector in fields.items():
        print(f"Extrayendo el valor para el campo: {field}")
        candidate_details[field] = get_field_value(driver, selector, field)

    print("Detalles extraídos exitosamente:")
    print(candidate_details)  # Imprimir todo el diccionario de detalles del candidato

    return candidate_details

