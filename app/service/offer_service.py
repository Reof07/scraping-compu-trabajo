from sqlalchemy.orm import Session
from datetime import datetime
from ..core.logger_config import logger
from ..db.models.offer import Offer
from ..db.models.user import User


async def create_offer(db: Session, user_id: int, offer_data: dict):
    """Crea o actualiza una oferta en la base de datos."""
    try:
        # Verificar si la oferta ya existe en la base de datos
        existing_offer = db.query(Offer).filter(Offer.offer_id == offer_data["offer_id"]).first()
        if existing_offer:
            # Actualizar los datos de la oferta existente
            existing_offer.title = offer_data["title"]
            existing_offer.location = offer_data["location"]
            existing_offer.last_update = offer_data["date_updated"]
            existing_offer.views = offer_data["views"]
            existing_offer.expiration_date = offer_data["expiration_date"]
            existing_offer.applicants_count = offer_data["applicants"]
            existing_offer.applicants_link = offer_data["applicants_link"]
            existing_offer.status = offer_data["status"]
            existing_offer.updated_at = datetime.now()
            db.commit()
            db.refresh(existing_offer)
            return existing_offer
        else:
            # Crear una nueva oferta si no existe
            offer = Offer(
                offer_id=offer_data["offer_id"],
                title=offer_data["title"],
                location=offer_data["location"],
                last_update=offer_data["date_updated"],
                views=offer_data["views"],
                expiration_date=offer_data["expiration_date"],
                applicants_count=offer_data["applicants"],
                applicants_link=offer_data["applicants_link"],
                user_id=user_id,
                status=offer_data["status"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(offer)
            db.commit()
            db.refresh(offer)
            return offer
    except Exception as e:
        # Log error if something goes wrong during offer creation or update
        logger.error(f"Error al crear o actualizar la oferta: {e}")
        return None
