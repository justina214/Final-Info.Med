Para subir los pacientes utilizamos este codigo 

```python
import pandas as pd
from datetime import datetime

from Scripts.patient import create_patient_resource
from Scripts.location import create_location_resource
from Scripts.Encounter import create_encounter_resource
from Scripts.Observation import create_observation_resource
from Scripts.condition import create_condition_resource
from Scripts.base import send_resource_to_hapi_fhir

# Utilidad para fechas
def convertir_fecha(fecha_str):
    try:
        return datetime.strptime(fecha_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except:
        return None

# Cargar bases
df_pacientes = pd.read_csv("C:/Users/justi/Downloads/Base de datos - Pacientes..csv")
df_casos = pd.read_csv("C:/Users/justi/Downloads/Base de datos - Casos.csv")
df_establecimientos = pd.read_csv("C:/Users/justi/Downloads/Base de datos - Establecimientos.csv")

# Limpiar columnas
df_pacientes.columns = df_pacientes.columns.str.strip()
df_casos.columns = df_casos.columns.str.strip()
df_establecimientos.columns = df_establecimientos.columns.str.strip()

#  Cargar establecimientos
establecimientos_ids = {}
for _, row in df_establecimientos.dropna(subset=["establecimiento_nombre"]).iterrows():
    est_id = row["establecimiento_id"]
    nombre = row["establecimiento_nombre"]
    comuna = row["establecimiento_comuna"]
    loc = create_location_resource(nombre, comuna)
    loc_id = send_resource_to_hapi_fhir(loc, "Location")
    if loc_id:
        establecimientos_ids[est_id] = loc_id
        print(f"Location '{nombre}' subida como ID {loc_id}")
    else:
        print(f" Error al subir Location {nombre}")

# Subir pacientes y vincular todos sus datos
for _, pac in df_pacientes.iterrows():
    documento = str(pac["DNI_V_pasaporte"])
    nombre_completo = pac["nombre_completo"].strip()
    given = nombre_completo.split(" ")[0]
    family = " ".join(nombre_completo.split(" ")[1:]) if " " in nombre_completo else None

    patient = create_patient_resource(
        family_name=family,
        given_name=given,
        birth_date=convertir_fecha(pac["fecha_nacimiento"]),
        gender="male" if pac["sexo"].strip().upper() == "M" else "female",
        phone=pac["numero_cell"] if pd.notna(pac["numero_cell"]) else None,
        identifier=documento
    )

    patient_id = send_resource_to_hapi_fhir(patient, "Patient")
    if not patient_id:
        print(f" Error al subir Patient {given}")
        continue
    print(f"Patient {given} subido con ID {patient_id}")

    # Buscar casos del paciente
    casos_paciente = df_casos[df_casos["ID_pacientes"] == pac["ID_pacientes"]]
    for _, caso in casos_paciente.iterrows():
        est_id = caso["Establecimiento_id"]
        location_id = establecimientos_ids.get(est_id)

        # Encuentro
        fecha_consulta = convertir_fecha(caso["Fecha_consulta"])
        encounter = create_encounter_resource(patient_id, location_id, fecha_consulta)
        encounter_id = send_resource_to_hapi_fhir(encounter, "Encounter")

        # Observación
        sintomas = caso["sintomas"] if pd.notna(caso["sintomas"]) else "No especificado"
        observation = create_observation_resource(patient_id, sintomas)
        observation_id = send_resource_to_hapi_fhir(observation, "Observation")

        # Condición
        enfermedad = caso["Enfermedad"]
        clasificacion = caso["Clasificacion"]
        fecha_sintoma = convertir_fecha(caso["Fecha_sintoma"])
        condition = create_condition_resource(patient_id, enfermedad, fecha_sintoma, clasificacion)
        condition_id = send_resource_to_hapi_fhir(condition, "Condition")

        print(f"Datos relacionados al paciente {patient_id}:")
        print(f"   Encounter: {encounter_id or 'error'}")
        print(f"   Observation: {observation_id or 'error'}")
        print(f"   Condition: {condition_id or 'error'}")
```

Este ajuste en workflow permite que se generen los pacientes con sus respectivos atributos a partir de los 3 archivos .csv que conforman la base de datos

workflow.py lee bases de datos en .csv y por cada paciente, construye y sube 5 recursos FHIR conectados entre sí:

| Recurso FHIR  | Qué representa                     | Fuente CSV                             | Relación clave                      |
| ------------- | ---------------------------------- | -------------------------------------- | ----------------------------------- |
| `Patient`     | Datos personales del paciente      | `Base de datos - Pacientes..csv`       | ID\_pacientes                       |
| `Location`    | Establecimiento donde fue atendido | `Base de datos - Establecimientos.csv` | establecimiento\_id                 |
| `Encounter`   | Episodio de atención médica        | `Base de datos - Casos.csv`            | ID\_pacientes + establecimiento\_id |
| `Observation` | Síntomas reportados                | `Base de datos - Casos.csv`            | ID\_pacientes                       |
| `Condition`   | Diagnóstico confirmado/sospechoso  | `Base de datos - Casos.csv`            | ID\_pacientes                       |


## Funcionamiento del flujo

### Carga y limpieza de datos
Se abren los 3 archivos `.csv` y se limpian los nombres de columnas (`strip()`)

### Carga de Location

Se recorren todos los establecimientos, cada uno se sube como `Location` a FHIR y se guarda un mapa: `establecimiento_id → location_id_fhir`

### 3. **Carga de Patient**

* Se recorre cada fila de pacientes.
* Se crea un recurso `Patient` con:

  * Nombre
  * Género
  * Fecha de nacimiento
  * Documento
* Se guarda un mapa: `ID_pacientes → patient_id_fhir`


### 4. **Por cada paciente:**

Se buscan sus registros en `Casos.csv` y por cada uno se:

#### `Encounter`

* Se crea un `Encounter` con:

  * Referencia al `Patient`
  * Fecha de consulta
  * Ubicación (`Location`) del establecimiento
  * Clase ambulatoria (`AMB`)
  * Estado `finished`

####  `Observation`

* Se crea un `Observation` con:

  * Código LOINC genérico de síntomas (`75325-1`)
  * Texto libre de síntomas desde el CSV


#### `Condition`

* Se crea un `Condition` con:

  * Diagnóstico (mapeado a código SNOMED)
  * Clasificación (confirmed/suspect)
  * Fecha de síntomas
  * Relación al paciente

## ¿Cómo se relacionan?

* Todos los recursos usan referencias como:

  * `"Patient/48264990"`
  * `"Location/48264980"`
* Así se construye una historia clínica **coherente y vinculada** en FHIR.

##  ¿Qué lograste con esto?

* Tenés una simulación de historia clínica distribuida, realista y estandarizada.
* Usaste terminologías oficiales: **SNOMED** y **LOINC**
* Cada paciente tiene asociado:

  * Quién lo atendió (`Location`)
  * Cuándo fue (`Encounter`)
  * Qué síntomas tenía (`Observation`)
  * Qué diagnóstico recibió (`Condition`)


