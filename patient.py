from fhir.resources.patient import Patient
from fhir.resources.humanname import HumanName
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.identifier import Identifier  
#Es importante en este renglon agregamos el identifier que va a ser donde ponemos el documento desp

def create_patient_resource(family_name=None, given_name=None, birth_date=None, gender=None, phone=None, identifier=None):
    patient = Patient()
    
    if family_name or given_name:
        name = HumanName()
        if family_name:
            name.family = family_name
        if given_name:
            name.given = [given_name]
        patient.name = [name]

    if birth_date:
        patient.birthDate = birth_date

    if gender:
        patient.gender = gender

    if phone:
        contact = ContactPoint()
        contact.system = "phone"
        contact.value = phone
        contact.use = "mobile"
        patient.telecom = [contact]

    # Agregar documento!!
    if identifier:
        doc = Identifier()
        doc.value = identifier
        patient.identifier = [doc]

    return patient
