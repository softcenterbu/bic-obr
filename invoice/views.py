from distutils.log import warn
from logging import warning
from django.http import HttpResponse
from django.template import loader
from .models import AssFactureObr
import json
import requests
from requests.structures import CaseInsensitiveDict

# ---------------------------------------
class Object:
    """
    Dynamic object for (Facture and Items)
    """
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

# ---------------------------------------
class AuthenticationEBMS:
    """
    EBMS authentication
    """
    _token = None
    _connected = False
    _password = False
    
    def __init__(self, username, password, url):
        self.username = username
        self._password = password
        self.url = url
    
    def connect(self):
        response = requests.post(
            self.url, 
            data=json.dumps(
                {
                    "username": self.username,
                    "password": self._password
                }
            ),
            headers={"Content-Type": "application/json"},
        )

        if (response.status_code == 200):
            self._token = response.json()['result']['token']
            self._connected = True
        else:
            self._token = None
            self._connected = False
        
        return self._connected

    @property
    def token(self):
        return self._token
    
    @property
    def is_connected(self):
        return self._connected

# ---------------------------------------
def LoadAndSaveFactureFromStringList(lst):
    """
    Load invoice and details from string list (MSSQL)
    """
    if not lst:
        return None, None

    # 1 - Load invoice details data from list items
    invoice_items = []
    for obj in lst:
        # 
        obj_str_item = obj.details.split(';') # MSSQL.table.details column

        item = Object()
        item.item_designation = obj_str_item[0].strip()
        item.item_quantity = obj_str_item[1].strip()
        item.item_price = obj_str_item[2].strip()
        item.item_ct = obj_str_item[3].strip()
        item.item_tl = obj_str_item[4].strip()
        item.item_price_nvat = obj_str_item[5].strip()
        item.vat = obj_str_item[6].strip()
        item.item_price_wvat = obj_str_item[7].strip()
        item.item_total_amount = obj_str_item[8].strip()

        # collect items
        invoice_items.append(item)

    # 2 - Load invoice data from first list
    obj_str_invoice = lst[0].invoice.split(';') # MSSQL.table.invoice culumn

    invoice = Object()
    invoice.invoice_number = obj_str_invoice[0].strip()
    invoice.invoice_date = obj_str_invoice[1].strip()
    invoice.invoice_type = obj_str_invoice[2].strip()
    invoice.tp_type = obj_str_invoice[3].strip()
    invoice.tp_name = obj_str_invoice[4].strip()
    invoice.tp_TIN = obj_str_invoice[5].strip()
    invoice.tp_trade_number = obj_str_invoice[6].strip()
    invoice.tp_postal_number = obj_str_invoice[7].strip()
    invoice.tp_phone_number = obj_str_invoice[8].strip()
    invoice.tp_address_province = obj_str_invoice[9].strip()
    invoice.tp_address_commune = obj_str_invoice[10].strip()
    invoice.tp_address_quartier = obj_str_invoice[11].strip()
    invoice.tp_address_avenue = obj_str_invoice[12].strip()
    invoice.tp_address_number = obj_str_invoice[13].strip()
    invoice.vat_taxpayer = obj_str_invoice[14].strip()
    invoice.ct_taxpayer = obj_str_invoice[15].strip()
    invoice.tl_taxpayer = obj_str_invoice[16].strip()
    invoice.tp_fiscal_center = obj_str_invoice[17].strip()
    invoice.tp_activity_sector = obj_str_invoice[18].strip()
    invoice.tp_legal_form = obj_str_invoice[19].strip()
    invoice.payment_type = obj_str_invoice[20].strip()
    invoice.invoice_currency  = obj_str_invoice[21].strip()
    invoice.customer_name = obj_str_invoice[22].strip()
    invoice.customer_TIN = obj_str_invoice[23].strip()
    invoice.customer_address = obj_str_invoice[24].strip()
    invoice.vat_customer_payer = obj_str_invoice[25].strip()
    invoice.cancelled_invoice_ref = obj_str_invoice[26].strip()
    invoice.invoice_ref = obj_str_invoice[27].strip()
    invoice.invoice_signature = obj_str_invoice[28].strip()
    invoice.invoice_signature_date = obj_str_invoice[29].strip()
    invoice.invoice_items = invoice_items

    # Convert invoice obect into json foramt
    invoice_json = json.loads(invoice.toJSON())

    # Save Facture/Details to json file
    with open('obr_settings.json', 'r') as file:
        settings = json.load(file)
        jsonFile = open('{}{}.json'.format(settings['invoice_directory'], invoice.invoice_number), "w")
        jsonFile.write(json.dumps(invoice_json))
        jsonFile.close()

    return invoice, invoice_items

# ---------------------------------------
def load_invoice_json_file_by_reference(reference):
    """
    Load invoice from json file by reference (referece is the name of object)
    """
    invoice = None
    with open('obr_settings.json', 'r') as file:
        settings = json.load(file)
        with open('{}{}.json'.format(settings['invoice_directory'], reference), 'r') as file:
            invoice = json.load(file)

    return invoice, invoice['invoice_items']

# ---------------------------------------
def load_invoice(request, reference):
    """
    Lire et Afficher la invoice
    """
    # Liste des details de invoice
    invoice = None
    invoice_items = None
    message = None

    try:
        lst = AssFactureObr.objects.filter(reference=reference)
        invoice, invoice_items = LoadAndSaveFactureFromStringList(lst)
    except:
        try:
            invoice, invoice_items = load_invoice_json_file_by_reference(reference)
        except:
            message = "Facture non trouvé."

    context = {
		'reference': reference,
        'invoice': invoice,
        'invoice_items': invoice_items,
        'sent': False,
        'message': message
	}

    html_template = loader.get_template('invoice.html')
    return HttpResponse(html_template.render(context, request))

# ---------------------------------------
def check_invoice(invoice_signature):
    """
    Check if invoice exists
    Protocol http de la méthode: POST
    URL: http://41.79.226.28:8345/ebms_api/getInvoice/
    En-tête
    Authorization:Bearer xxx
    Corps de la requête
    {
        "invoice_signature":"xxx"
    }
    Champs obligatoires
    invoice_signature
    """
    auth = None

    try:
        # Load json settings  
        with open('obr_settings.json', 'r') as file:
            settings = json.load(file)
            if settings:
                auth = AuthenticationEBMS(settings['username'], settings['password'], settings['url_api_login'])

        # Connect to endpoint 
        auth.connect()

        # Send invoice (add invoice)
        url = settings['url_api_get_invoice']
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["Authorization"] = "Bearer {}".format(auth.token)
        response = requests.post(
            url, 
            data=json.dumps(
                {"invoice_signature": invoice_signature}
            ),
            headers=headers
        )
        if (response.status_code == 200):
            return True
    except:
        pass
    
    return False

# ---------------------------------------
def send_invoice(request, reference):
    """
    Send invoice via API
    """
    auth = None
    success = False
    warning = False

    # Load invoice json file
    invoice, invoice_items = load_invoice_json_file_by_reference(reference)

    # Check if invoice exists
    if check_invoice(invoice['invoice_signature']):
        try:
            with open('obr_settings.json', 'r') as file:
                settings = json.load(file)
                if settings:
                    auth = AuthenticationEBMS(settings['username'], settings['password'], settings['url_api_login'])
        
            # Connect to endpoint 
            auth.connect()

            # Load json invoice in '/temps'
            with open('{}{}.json'.format(settings['invoice_directory'], reference), 'r') as json_file_invoice:
                invoice_to_send = json.load(json_file_invoice)
            
            # Send invoice (add invoice)
            url = settings['url_api_add_invoice']
            headers = CaseInsensitiveDict()
            headers["Accept"] = "application/json"
            headers["Authorization"] = "Bearer {}".format(auth.token)
            response = requests.post(
                url, 
                data=json.dumps(invoice_to_send),
                headers=headers
            )
            message = json.loads(response.text)['msg']
            
            if (response.status_code == 200):
                success = True
        except Exception as e:
            try:
                message = str(e.args[0].reason).split(">:")[1]
            except:
                message = str(e)
    else:
        message = "Cette facture a été déjà envoyée à l'OBR"
        warning = True

    context = {
		'reference': reference,
        'invoice': invoice,
        'invoice_items': invoice_items,
        'success': success,
        'message': message,
        'sent': True,
        'warning': warning
	}

    html_template = loader.get_template('invoice.html')
    return HttpResponse(html_template.render(context, request))
