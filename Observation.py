from fhir.resources.observation import Observation
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding

def create_observation_resource(patient_id, sintomas_texto):
    observation = Observation(
        status="final",
        code=CodeableConcept(
            coding=[
                Coding(
                    system="http://loinc.org",
                    code="75325-1",
                    display="Síntomas referidos por el paciente"
                )
            ]
        ),
        subject={"reference": f"Patient/{patient_id}"},
        valueString=sintomas_texto
    )

    return observation
