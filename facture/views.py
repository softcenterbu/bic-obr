from django.http import HttpResponse
from django.template import loader
from .models import AssFactureObr

# ---------------------------------------
class Facture:
    def __init__(self):
        self.invoice_number = ""
        self.invoice_date = ""
        self.invoice_type = ""
        self.tp_type = ""
        self.tp_name = ""
        self.tp_TIN = ""
        self.tp_trade_number = ""
        self.tp_postal_number = ""
        self.tp_phone_number = ""
        self.tp_address_province = ""
        self.tp_address_commune = ""
        self.tp_address_quartier = ""
        self.tp_address_avenue = ""
        self.tp_address_number = ""
        self.vat_taxpayer = ""
        self.ct_taxpayer = ""
        self.tl_taxpayer = ""
        self.tp_fiscal_center = ""
        self.tp_activity_sector = ""
        self.tp_legal_form = ""
        self.payment_type = ""
        self.invoice_currency  = ""
        self.customer_name = ""
        self.customer_TIN = ""
        self.customer_address = ""
        self.vat_customer_payer = ""
        self.cancelled_invoice_ref = ""
        self.invoice_ref = ""
        self.invoice_signature = ""
        self.invoice_signature_date = ""

# ---------------------------------------
class Details:
    def __init__(self):
        self.item_designation = ""
        self.item_quantity = ""
        self.item_price = ""
        self.item_ct = ""
        self.item_tl = ""
        self.item_price_nvat = ""
        self.vat = ""
        self.item_price_wvat = ""
        self.item_total_amount = ""

# ---------------------------------------
def LoadFactureFromStringList(lst):
    """
    Load facture and details from string list
    """
    if not lst:
        return None, None
    
    # 1 - Load invoice data from first list
    obj_str_facture = lst[0].facture.split(';')
    facture = Facture(
        invoice_number = obj_str_facture[0].strip(),
        invoice_date = obj_str_facture[1].strip(),
        invoice_type = obj_str_facture[2].strip(),
        tp_type = obj_str_facture[3].strip(),
        tp_name = obj_str_facture[4].strip(),
        tp_TIN = obj_str_facture[5].strip(),
        tp_trade_number = obj_str_facture[6].strip(),
        tp_postal_number = obj_str_facture[7].strip(),
        tp_phone_number = obj_str_facture[8].strip(),
        tp_address_province = obj_str_facture[9].strip(),
        tp_address_commune = obj_str_facture[10].strip(),
        tp_address_quartier = obj_str_facture[11].strip(),
        tp_address_avenue = obj_str_facture[12].strip(),
        tp_address_number = obj_str_facture[13].strip(),
        vat_taxpayer = obj_str_facture[14].strip(),
        ct_taxpayer = obj_str_facture[15].strip(),
        tl_taxpayer = obj_str_facture[16].strip(),
        tp_fiscal_center = obj_str_facture[17].strip(),
        tp_activity_sector = obj_str_facture[18].strip(),
        tp_legal_form = obj_str_facture[19].strip(),
        payment_type = obj_str_facture[20].strip(),
        invoice_currency  = obj_str_facture[21].strip(),
        customer_name = obj_str_facture[22].strip(),
        customer_TIN = obj_str_facture[23].strip(),
        customer_address = obj_str_facture[24].strip(),
        vat_customer_payer = obj_str_facture[25].strip(),
        cancelled_invoice_ref = obj_str_facture[26].strip(),
        invoice_ref = obj_str_facture[27].strip(),
        invoice_signature = obj_str_facture[28].strip(),
        invoice_signature_date = obj_str_facture[29].strip(),
    )

    facture_details = []
    for obj in lst:
        obj_str_item = obj.details.split(';')
        details = Details(
            item_designation = obj_str_item[0].strip(),
            item_quantity = obj_str_item[1].strip(),
            item_price = obj_str_item[2].strip(),
            item_ct = obj_str_item[3].strip(),
            item_tl = obj_str_item[4].strip(),
            item_price_nvat = obj_str_item[5].strip(),
            vat = obj_str_item[6].strip(),
            item_price_wvat = obj_str_item[7].strip(),
            item_total_amount = obj_str_item[8].strip()
        )
        facture_details.append(details)



    return facture, facture_details

# ---------------------------------------
def afficher_facture(request, reference):
    """
    Lire et Afficher la facture
    """
    # Liste des details de facture
    lst = AssFactureObr.object.filter(reference=reference)

    facture, facture_details = LoadFactureFromStringList(lst)

    context = {
		'reference': reference,
        'facture': facture,
        'facture_details': facture_details
	}
    html_template = loader.get_template('envoyer_facture.html')
    return HttpResponse(html_template.render(context, request))

# ---------------------------------------
def envoyer_facture(request, reference):
    """
    Envouyer la facture à l'obr
    Appeler le end-point (API) de l'obr
    """
    pass

    # 1 Envoyer la facture

    # 2 Update facture