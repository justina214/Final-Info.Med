Para subir los pacientes utilizamos este codigo 

```python
import pandas as pd
from datetime import datetime
from Scripts.patient import create_patient_resource
from Scripts.base import send_resource_to_hapi_fhir

# Ruta al archivo CSV
csv_path = "C:/Users/justi/Downloads/Base de datos - Pacientes..csv"

def convertir_fecha(fecha_str):
    try:
        return datetime.strptime(fecha_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except:
        return None

# base de datos
df = pd.read_csv(csv_path)
df.columns = df.columns.str.strip()  # Limpiar espacios en encabezados

# Iterar por cada paciente
for _, row in df.iterrows():
    nombre_completo = row["nombre_completo"].strip()
    if " " in nombre_completo:
        given_name = nombre_completo.split(" ")[0]
        family_name = " ".join(nombre_completo.split(" ")[1:])
    else:
        given_name = nombre_completo
        family_name = None

    patient = create_patient_resource(
        family_name=family_name,
        given_name=given_name,
        birth_date=convertir_fecha(row["fecha_nacimiento"]),
        gender="male" if row["sexo"].strip().upper() == "M" else "female",
        phone=row["numero_cell"] if pd.notna(row["numero_cell"]) else None,
        identifier=str(row["DNI_V_pasaporte"])
    )

    patient_id = send_resource_to_hapi_fhir(patient, "Patient")

    if patient_id:
        print(f"Paciente {given_name} {family_name or ''} subido con ID: {patient_id}")
    else:
        print(f"Error al subir paciente {given_name} {family_name or ''}")
```

Este ajuste en workflow permite que se generen los pacientes a partir de un .csv
