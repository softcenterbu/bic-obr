from django.http import HttpResponse
from django.template import loader
from .models import AssTransfertPNB
import json
import requests
from requests.structures import CaseInsensitiveDict

# ---------------------------------------
class Object:
    """
    Dynamic object for (Assurance and Items)
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
                    "email": self.username,
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
def LoadAndSaveAssuranceFromStringList(lst):
    """
    Load assurance  from string list (MSSQL)
    """
    if not lst:
        return None

    # 2 - Load assurance data from first list
    obj_str_assurance = lst[0].assurance.split(';') # MSSQL.table.assurance culumn

    assurance = Object()
    assurance.NUMERO_PLAQUE = obj_str_assurance[0].strip()
    assurance.NUMERO_ASSURANCE = obj_str_assurance[1].strip()
    assurance.DATE_DEBUT = obj_str_assurance[2].strip()
    assurance.PLACES_ASSURES = obj_str_assurance[3].strip()
    assurance.TYPE_ASSURANCE = obj_str_assurance[4].strip()
    assurance.NOM_PROPRIETAIRE = obj_str_assurance[5].strip()
    assurance.DATE_INSERTION = obj_str_assurance[5].strip()

    # Convert assurance obect into json format
    assurance_json = json.loads(assurance.toJSON())

    # Save assurance to json file
    with open('settings_pnb.json', 'r') as file:
        settings = json.load(file)
        jsonFile = open('{}{}.json'.format(settings['assurance_directory'], assurance.NUMERO_PLAQUE), "w")
        jsonFile.write(json.dumps(assurance_json))
        jsonFile.close()

    return assurance

# ---------------------------------------
def load_assurance_json_file_by_reference(reference):
    """
    Load assurance from json file by reference (referece is the name of object)
    """
    assurance = None
    with open('setting.json', 'r') as file:
        settings = json.load(file)
        with open('{}{}.json'.format(settings['assurance_directory'], reference), 'r') as file:
            assurance = json.load(file)

    return assurance

# ---------------------------------------
def load_assurance(request, reference):
    """
    Lire et Afficher la assurance
    """
    # Liste des details de assurance
    assurance = None
    error = False
    message = "Merci de lire attentivement les commentaires."

    try:
        lst = AssTransfertPNB.objects.filter(reference=reference)
        assurance, assurance_items = LoadAndSaveAssuranceFromStringList(lst)
    except:
        try:
            assurance, assurance_items = load_assurance_json_file_by_reference(reference)
        except:
            message = "assurance non trouvé ou Format incorrect. Veuillez vérifier le format 'json' de l'OBR"
            error = True

    context = {
		'reference': reference,
        'assurance': assurance,
        'sent': False,
        'message': message,
        'error': error
	}

    html_template = loader.get_template('assurance.html')
    return HttpResponse(html_template.render(context, request))

# ---------------------------------------
def check_assurance(assurance_signature):
    """
    Check if assurance exists
    Protocol http de la méthode: POST
    URL: http://app.mediabox.bi:2522/psr/assurances?numero_assurance=
    En-tête
    Authorization:Bearer xxx
    Corps de la requête
    {
        "assurance_signature":"xxx"
    }
    Champs obligatoires
    assurance_signature
    """
    auth = None

    try:
        # Load json settings  
        with open('setting.json', 'r') as file:
            settings = json.load(file)
            if settings:
                auth = AuthenticationEBMS(settings['username'], settings['password'], settings['url_api_login'])

        # Connect to endpoint 
        auth.connect()

        # Send assurance (add assurance)
        url = settings['url_api_get_assurance']
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["Authorization"] = "Bearer {}".format(auth.token)
        response = requests.post(
            url, 
            data=json.dumps(
                {"assurance_signature": assurance_signature}
            ),
            headers=headers
        )
        if (response.status_code == 200):
            return True
    except:
        pass
    
    return False

# ---------------------------------------
def send_assurance(request, reference):
    """
    Send assurance via API
    """
    auth = None
    success = False
    warning = False

    # Load assurance json file
    assurance, assurance_items = load_assurance_json_file_by_reference(reference)

    # Check if assurance exists
    if not check_assurance(assurance['assurance_signature']):
        try:
            with open('setting.json', 'r') as file:
                settings = json.load(file)
                if settings:
                    auth = AuthenticationEBMS(settings['username'], settings['password'], settings['url_api_login'])
        
            # Connect to endpoint 
            auth.connect()

            # Load json assurance in '/temps'
            with open('{}{}.json'.format(settings['assurance_directory'], reference), 'r') as json_file_assurance:
                assurance_to_send = json.load(json_file_assurance)
            
            # Send assurance (add assurance)
            url = settings['url_api_add_assurance']
            headers = CaseInsensitiveDict()
            headers["Accept"] = "application/json"
            headers["Authorization"] = "Bearer {}".format(auth.token)
            response = requests.post(
                url, 
                data=json.dumps(assurance_to_send),
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
        message = "Cette assurance a été déjà envoyée à la PNB"
        warning = True

    context = {
		'reference': reference,
        'assurance': assurance,
        'success': success,
        'message': message,
        'sent': True,
        'warning': warning
	}

    html_template = loader.get_template('assurance.html')
    return HttpResponse(html_template.render(context, request))
