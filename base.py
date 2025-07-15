import requests
from patient import create_patient_resource


# Enviar el recurso FHIR al servidor HAPI FHIR
def send_resource_to_hapi_fhir(resource,resource_type):
    url = f"http://hapi.fhir.org/baseR4/{resource_type}"
    headers = {"Content-Type": "application/fhir+json"}
    resource_json = resource.json()

    response = requests.post(url, headers=headers, data=resource_json)

    if response.status_code == 201:
        print("Recurso creado exitosamente")
        
        # Devolver el ID del recurso creado
        return response.json()['id']
    else:
        print(f"Error al crear el recurso: {response.status_code}")
        print(response.json())
        return None

# Buscar el recurso por ID 
def get_resource_from_hapi_fhir(resource_id, resource_type):
    url = f"http://hapi.fhir.org/baseR4/{resource_type}/{resource_id}"
    response = requests.get(url, headers={"Accept": "application/fhir+json"})

    if response.status_code == 200:
        resource = response.json()
        print(resource)
    else:
        print(f"Error al obtener el recurso: {response.status_code}")
        print(response.json())

# Con esta funcion podemos buscar por el identifier que en este caso es el documento 
def search_patient_by_document(identifier_value):
    url = f"https://hapi.fhir.org/baseR4/Patient?identifier={identifier_value}"
    response = requests.get(url, headers={"Accept": "application/fhir+json"})

    if response.status_code == 200:
        data = response.json()
        entries = data.get("entry", [])
        if entries:
            print(f"Se encontraron {len(entries)} paciente(s) con documento {identifier_value}:")
            for entry in entries:
                patient = entry["resource"]
                pid = patient.get("id", "ID no disponible")
                name = patient.get("name", [{}])[0]
                full_name = f"{' '.join(name.get('given', []))} {name.get('family', '')}"
                print(f"- ID: {pid}, Nombre: {full_name}")
        else:
            print(f"No se encontró ningún paciente con documento {identifier_value}")
    else:
        print(f"Error al buscar paciente: {response.status_code}")