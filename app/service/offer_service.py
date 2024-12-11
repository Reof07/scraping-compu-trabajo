from sqlalchemy.orm import Session
from datetime import datetime


from ..db.models.offer import Offer
from ..db.models.user import User


async def create_offer(db: Session, user_id: int, offer_data: dict):
    """
    Función para crear una oferta de trabajo.
    
    Args:
        db: Sesión de la base de datos.
        user_id: ID del usuario (reclutador) que está creando la oferta.
        offer_data: Datos de la oferta en forma de diccionario.
        
    Returns:
        Offer: Instancia de la oferta creada.
    """

     # Verificar si la oferta ya existe
    existing_offer = db.query(Offer).filter(Offer.offer_id == offer_data["offer_id"]).first()
    
    if existing_offer:
        # Si la oferta existe, actualiza los datos
        existing_offer.title = offer_data["title"]
        existing_offer.location = offer_data["location"]
        existing_offer.last_update = offer_data["date_updated"]
        existing_offer.views = offer_data["views"]
        existing_offer.expiration_date = offer_data["expiration_date"]
        existing_offer.applicants_count = offer_data["applicants"]
        existing_offer.applicants_link = offer_data["applicants_link"]
        existing_offer.updated_at = datetime.now()  # Actualizamos la fecha de actualización
        db.commit()
        db.refresh(existing_offer)
        return existing_offer
    else:
        # Si la oferta no existe, crea una nueva
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
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(offer)
        db.commit()
        db.refresh(offer)
        return offer
    

    # offer = Offer(
    #     offer_id=offer_data["offer_id"],
    #     title=offer_data["title"],
    #     location=offer_data["location"],
    #     last_update=offer_data["date_updated"],
    #     views=offer_data["views"],
    #     expiration_date=offer_data["expiration_date"],
    #     applicants_count=offer_data["applicants"],
    #     applicants_link=offer_data["applicants_link"],
    #     user_id=user_id,
    #     created_at=datetime.now(),
    #     updated_at=datetime.now()
    # )
    
    # db.add(offer)
    # db.commit()
    # db.refresh(offer)
    # return offer
