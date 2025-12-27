import uuid
import locale

def format_currency(amount, currency="XAF"):
    """
    Formatte un montant en devise locale (XAF par défaut).
    """
    try:
        # Essayer de formater avec des espaces comme séparateurs de milliers
        formatted = "{:,.0f}".format(float(amount)).replace(",", " ")
        return f"{formatted} {currency}"
    except (ValueError, TypeError):
        return f"0 {currency}"

def generate_reference_code(prefix="REF"):
    """
    Génère un code de référence unique avec un préfixe.
    Exemple: PRE-1A2B3C4D
    """
    unique_id = str(uuid.uuid4()).split('-')[0].upper()
    return f"{prefix}-{unique_id}"

def get_client_ip(request):
    """
    Récupère l'adresse IP du client depuis la requête.
    Gère les cas derrière un proxy (X-Forwarded-For).
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
