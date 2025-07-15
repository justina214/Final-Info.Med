from fhir.resources.encounter import Encounter
from fhir.resources.period import Period
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding

def create_encounter_resource(patient_id, location_id, fecha_consulta):
    # Clase requerida (ambulatoria)
    encounter_class = Coding()
    encounter_class.system = "http://terminology.hl7.org/CodeSystem/v3-ActCode"
    encounter_class.code = "AMB"  # AMB = Ambulatory
    encounter_class.display = "Ambulatory"

    # Crear Encounter con status y class definidos
    encounter = Encounter(
        status="finished",
        class_fhir=encounter_class  # Usar class_fhir porque 'class' es palabra reservada
    )

    # Paciente
    encounter.subject = {"reference": f"Patient/{patient_id}"}

    # Periodo de atención
    if fecha_consulta:
        encounter.period = Period()
        encounter.period.start = fecha_consulta

    # Establecimiento
    if location_id:
        encounter.location = [{
            "location": {"reference": f"Location/{location_id}"}
        }]

    return encounter
