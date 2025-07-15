from fhir.resources.condition import Condition
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding

def create_condition_resource(patient_id, enfermedad, fecha, clasificacion):
    # Diccionario de SNOMED
    snomed_map = {
        "COVID-19": "840539006",
        "Dengue": "16541001",
        "Bronquiolitis": "10509002",
        "Gripe": "6142004",
        "Neumonía": "233604007",
        "Gastroenteritis": "235595009"
    }

    # Crear el recurso de condición con todos los campos obligatorios de una
    condition = Condition(
        subject={"reference": f"Patient/{patient_id}"},
        code=CodeableConcept(
            coding=[
                Coding(
                    system="http://snomed.info/sct",
                    code=snomed_map.get(enfermedad, "000000"),
                    display=enfermedad
                )
            ]
        ),
        verificationStatus=CodeableConcept(
            coding=[
                Coding(
                    system="http://terminology.hl7.org/CodeSystem/condition-ver-status",
                    code=clasificacion.lower(),
                    display=clasificacion.capitalize()
                )
            ]
        ),
        onsetDateTime=fecha if fecha else None
    )

    return condition
