from urllib.parse import urlparse, parse_qs

def extract_offer_id(url):
    """
    Extract the offer ID (parameter 'oi') from a URL.

    Args:
        url (str): URL from which to extract the offer ID.

    Returns:
        str: The offer ID if present, otherwise None.
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get('oi', [None])[0]