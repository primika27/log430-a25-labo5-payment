"""
Payment controller
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
import numbers
import requests
from commands.write_payment import create_payment, update_status_to_paid
from queries.read_payment import get_payment_by_id
from config import STORE_MANAGER_URL

def get_payment(payment_id):
    return get_payment_by_id(payment_id)

def add_payment(request):
    """ Add payment based on given params """
    payload = request.get_json() or {}
    user_id = payload.get('user_id')
    order_id = payload.get('order_id')
    total_amount = payload.get('total_amount')
    result = create_payment(order_id, user_id, total_amount)
    if isinstance(result, numbers.Number):
        return {"payment_id": result}
    else:
        return {"error": str(result)}
    
def process_payment(payment_id, credit_card_data):
    """ Process payment with given ID, notify store_manager sytem that the order is paid """
    # S'il s'agissait d'une véritable API de paiement, nous enverrions les données de la carte de crédit à un payment gateway (ex. Stripe, Paypal) pour effectuer le paiement. Cela pourrait se trouver dans un microservice distinct.
    _process_credit_card_payment(credit_card_data)

    # Si le paiement est réussi, mettre à jour les statut de la commande
    # Ensuite, faire la mise à jour de la commande dans le Store Manager (en utilisant l'order_id)
    update_result = update_status_to_paid(payment_id)
    print(f"Updated order {update_result['order_id']} to paid={update_result}")

    # Notify Store Manager service to mark the order as paid
    order_id = update_result.get("order_id")
    store_update = None
    if order_id:
        try:
            url = f"{STORE_MANAGER_URL.rstrip('/')}/orders/{order_id}"
            print(f"Notifying Store Manager at {url} to set is_paid=true")
            resp = requests.put(url, json={"is_paid": True}, timeout=5)
            resp.raise_for_status()
            
            try:
                store_update = resp.json()
            except Exception:
                store_update = {"status_code": resp.status_code, "text": resp.text}
        except Exception as e:
            print(f"Failed to notify store manager: {e}")
            store_update = {"error": str(e)}

    result = {
        "order_id": update_result.get("order_id"),
        "payment_id": update_result.get("payment_id"),
        "is_paid": update_result.get("is_paid"),
        "store_update": store_update
    }

    return result
    
def _process_credit_card_payment(payment_data):
    """ Placeholder method for simulated credit card payment """
    print(payment_data.get('cardNumber'))
    print(payment_data.get('cardCode'))
    print(payment_data.get('expirationDate'))