from urllib.parse import urlparse, parse_qs

def extract_offer_id(url):
    """
    Extrae el ID de la oferta (parámetro 'oi') de una URL.

    Args:
        url (str): URL de la cual extraer el ID de la oferta.

    Returns:
        str: El ID de la oferta si está presente, de lo contrario None.
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get('oi', [None])[0]