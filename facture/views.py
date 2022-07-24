from datetime import date
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from .models import AssFactureObr

class Facture:
    def __init__(self):
        reference = None
        date = None
        client = None
        montant = 0

class Details:
    def __init__(self):
        code = None
        nom = None
        quantite = 0.0
        unite = None
        montant = 0.0
        

def afficher_facture(request, reference):
    """
    Lire et Afficher la facture
    """
    # # Liste des details de facture
    # lst = AssFactureObr.object.filter(reference=reference)

    # # info de la facture
    # obj = lst[0].details.split(';')
    # facture = Facture(
    #     reference = obj[0],
    #     date = obj[1],
    #     client = obj[2],
    #     montant = obj[3]
    # )

    # details = []
    # for obj in lst:
    #     details
    #     det = obj.details.split(';')
    #     details

    

    context = {
		'reference': reference
	}
    html_template = loader.get_template('envoyer_facture.html')
    return HttpResponse(html_template.render(context, request))


def envoyer_facture(request, reference):
    """
    Envouyer la facture à l'obr
    Appeler le end-point (API) de l'obr
    """
    pass

    # 1 Envoyer la facture

    # 2 Update facture