import os
import json
import copy

from typing import Literal, List

from fhirclient import client
from fhirclient.models.encounter import Encounter
from fhirclient.models.patient import Patient
from fhirclient.models.condition import Condition
from fhirclient.models.allergyintolerance import AllergyIntolerance
from fhirclient.models.medicationrequest import MedicationRequest
from fhirclient.models.observation import Observation
from fhirclient.models.procedure import Procedure
from fhirclient.models.careplan import CarePlan


with open("/content/fhir_resource_templates.json", 'r') as file:
  templates = json.load(file)


settings = {
    'app_id': 'retrieve_hospitalized_patients',
    'api_base': os.getenv("FHIR_SERVER_URL")
}

smart = client.FHIRClient(settings=settings)


def create_patient(names: str, last_name: str, gender: Literal["female", "male"], bod: str):
  data = copy.deepcopy(templates["patient"])
  data.update({
      "name": [{
          "use": "official",
          "family": last_name,
          "given": names.split()}],
      "gender": gender,
      "birthDate": bod})
  
  patient = Patient(data).create(smart.server)

  # Test

  patient = Patient.read(patient["id"], smart.server)

  # Print patient details
  print(f"Patient ID: {patient.id}")
  print(f"Patient Name: {smart.human_name(patient.name[0])}")
  print(f"Patient Birth Date: {patient.birthDate.isostring}")

  return patient


def create_intolerance(type: Literal["intolerance_lactose"], patient_id: str, recorded_date: str):
  data = copy.deepcopy(templates[type])
  data.update({"patient": {"reference": f"Patient/{patient_id}"},
               "recordedDate": recorded_date
               })
  
  intolerance = AllergyIntolerance(data).create(smart.server)

  # Test
  intolerance = AllergyIntolerance.read(intolerance["id"], smart.server)

  # Print details
  print(f"Intolerance ID: {intolerance.id}")
  print(f"Recorded date: {intolerance.recordedDate.as_json()}")
  print(f"Description: {intolerance.reaction[0].substance.text}")

  return intolerance


def create_allergy(type: Literal["alergy_penicillin"], patient_id: str, recorded_date: str):
  data = copy.deepcopy(templates[type])
  data.update({"patient": {"reference": f"Patient/{patient_id}"},
               "recordedDate": recorded_date
               })
  
  allergy = AllergyIntolerance(data).create(smart.server)

  # Test
  allergy = AllergyIntolerance.read(allergy["id"], smart.server)

  # Print details
  print(f"Allergy ID: {allergy.id}")
  print(f"Recorded date: {allergy.recordedDate.as_json()}")
  print(f"Description: {allergy.reaction[0].substance.text}")

  return allergy

def create_medication(
    type: Literal["medication_metformin_500mg_tablet",
                  "medication_morphin_2mg_injection",
                  "medication_ibuprofen_400mg_tablet",
                  "medication_lisinopril_10mg_tablet",
                  "medication_aspirin_81mg_tablet",
                  "medication_ceftriaxone_2g_iv",
                  "medication_metronidazole_500mg_iv",
                  "medication_morphin_3mg_iv"],
    patient_id: str,
    status:str,
    authored_on:str,
    encounter_id: str = None,
    condition_ids: List = None):
  data = copy.deepcopy(templates[type])
  data.update({"subject": {"reference": f"Patient/{patient_id}"},
               "status": status,
               "authoredOn": authored_on
               })
  data.update({"encounter": {"reference": f"Encounter/{encounter_id}"}} if encounter_id else {})
  data.update({"supportingInformation": [{"reference": f"Condition/{c_id}"} for c_id in condition_ids]} if condition_ids else {})

  medication = MedicationRequest(data).create(smart.server)

  # Test
  medication = MedicationRequest.read(medication["id"], smart.server)

  # Print details
  print(f"Medication ID: {medication.id}")
  print(f"Medicament: {medication.medicationCodeableConcept.text}")
  print(f"Status: {medication.status}")
  print(f"Authored on: {medication.authoredOn.as_json()}")

  return medication


def create_condition(
    type: Literal["condition_type_2_diabetes",
                  "condition_acute_cholecystitis",
                  "condition_hypertension",
                  "condition_heart_attack"],
    patient_id: str,
    on_set_date_time:str,
    notes: List = None):
    data = copy.deepcopy(templates[type])
    data.update({"subject": {"reference": f"Patient/{patient_id}"},
                 "onsetDateTime": on_set_date_time,
                 "note": [{"text": note} for note in notes]
                 })

    condition = Condition(data).create(smart.server)

    # Test
    condition = Condition.read(condition["id"], smart.server)

    # Print details
    print(f"Condition ID: {condition.id}")
    print(f"Condition: {condition.code.text}")
    print(f"On set date: {condition.onsetDateTime.as_json()}")

    return condition


def create_encounter(
    type: Literal["encounter_acute_cholecystitis",
                  "encounter_hypertension",
                  "encounter_heart_attack"],
    patient_id: str,
    status: Literal["in-progress", "finished"],
    start: str,
    end: str = None,
    condition_ids: List = None):
  data = copy.deepcopy(templates[type])
  data.update({"reasonReference": [{"reference": f"Condition/{c_id}"} for c_id in condition_ids]}
              if condition_ids else {})
  data.update({"subject": {"reference": f"Patient/{patient_id}"},
      "status": status,
      "period": {"start": start, "end": end},
      })

  encounter = Encounter(data).create(smart.server)

  # Test
  encounter = Encounter.read(encounter["id"], smart.server)

  # Print details
  print(f"Encounter ID: {encounter.id}")
  print(f"Status: {encounter.status}")
  print(f"Period: {encounter.period.as_json()}")
  print(f"Reason: {encounter.reasonCode[0].text}")

  return encounter


def create_observation(
    type: Literal["observation_exam_abdominal_pain",
                  "observation_imagen_abdominal_ultrasound",
                  "observation_laboratory_white_blood_cell_count",
                  "observation_laboratory_hemoglobin_a1c",
                  "observation_troponin_I_level",
                  "observation_vitals_heart_rate"
                  "observation_vitals_oxygen_saturation",
                  "observation_vitals_blood_glucose"
                  ],
    patient_id: str,
    effective_date_time: str,
    encounter_id: str = None,
    value_quantity: float = None,
    notes: List = None
    ):
  data = copy.deepcopy(templates[type])
  
  data.update({"subject": {"reference": f"Patient/{patient_id}"},
               "effectiveDateTime": effective_date_time})
  data.update({"note": [{"text": note} for note in notes]} if notes else {})
  data.update({"encounter": {"reference": f"Encounter/{encounter_id}"}} if encounter_id else {})

  if value_quantity:
      data["valueQuantity"] = {"value": value_quantity}
  observation = Observation(data).create(smart.server)

  # Test
  observation = Observation.read(observation["id"], smart.server)

  # Print details
  print(f"Observation ID: {observation.id}")
  print(f"Effective date: {observation.effectiveDateTime.as_json()}")
  print(f"Observation: {observation.code.text}")
  return observation


def create_overnight_note(
    patient_id: str,
    effective_date_time: str,
    summary: str,
    encounter_id: str = None,
    notes: List = None
    ):
  data = copy.deepcopy(templates["observation_overnight_nursing_notes"])
  
  data.update({"subject": {"reference": f"Patient/{patient_id}"},
               "effectiveDateTime": effective_date_time,
               "valueString": summary
               })
  data.update({"encounter": {"reference": f"Encounter/{encounter_id}"}} if encounter_id else {})
  data.update({"note": [{"text": note} for note in notes]} if notes else {})
  observation = Observation(data).create(smart.server)

  # Test
  observation = Observation.read(observation["id"], smart.server)

  # Print details
  print(f"Observation ID: {observation.id}")
  print(f"Effective date: {observation.effectiveDateTime.as_json()}")
  print(f"Observation: {observation.code.text}")

  return observation


def create_blood_pressure_observation(
    patient_id: str,
    effective_date_time: str,
    systolic: float,
    diastolic: float,
    encounter_id: str = None,
    notes: List = None
    ):
  data = copy.deepcopy(templates["observation_vitals_blood_pressure"])
  
  data.update({"subject": {"reference": f"Patient/{patient_id}"},
               "effectiveDateTime": effective_date_time
               })
  data.update({"encounter": {"reference": f"Encounter/{encounter_id}"}} if encounter_id else {})
  data.update({"note": [{"text": note} for note in notes]} if notes else {})
  
  data["component"][0]["valueQuantity"]["value"] = systolic
  data["component"][1]["valueQuantity"]["value"] = diastolic
  
  observation = Observation(data).create(smart.server)
  
  # Test
  observation = Observation.read(observation["id"], smart.server)

  # Print details
  print(f"Observation ID: {observation.id}")
  print(f"Effective date: {observation.effectiveDateTime.as_json()}")
  print(f"Observation: {observation.code.text}")

  return observation


def create_procedure(
                  
    type: Literal["procedure_cardiac_catheterization",
                  "procedure_laparoscopic_removal_of_gallbladder"],
    patient_id: str,
    start: str,
    end: str,
    outcome: str,
    encounter_id: str = None,
    condition_ids: List = None):
    data = copy.deepcopy(templates[type])
    data.update({"subject": {"reference": f"Patient/{patient_id}"},
                 "performedPeriod": {"start": start, "end": end},
                 "outcome": {"text": outcome}
                 })
    data.update({"encounter": {"reference": f"Encounter/{encounter_id}"}} if encounter_id else {})
    data.update({"reasonReference": [{"reference": f"Condition/{c_id}"} for c_id in condition_ids]}
                if condition_ids else {})

    procedure = Procedure(data).create(smart.server)

    # Test
    procedure = Procedure.read(procedure["id"], smart.server)

    # Print details
    print(f"Procedure ID: {procedure.id}")
    print(f"Performed date: {procedure.performedPeriod.as_json()}")
    print(f"Procedure: {procedure.code.text}")

    return procedure


def ceate_care_plan(
    patient_id: str,
    title: str,
    description: str,
    start: str,
    end: str = None,
    encounter_id: str = None,
    condition_ids: List = None):
    data = copy.deepcopy(templates["care_plan"])
    
    data.update({"subject": {"reference": f"Patient/{patient_id}"},
                 "title": title,
                 "description": description,
                 "period": {"start": start, "end": end}
                 })
    data.update({"supportingInfo": [{"reference": f"Condition/{c_id}"} for c_id in condition_ids]}
                if condition_ids else {})
    data.update({"encounter": {"reference": f"Encounter/{encounter_id}"}} if encounter_id else {})

    care_plan = CarePlan(data).create(smart.server)

    # Test
    care_plan = CarePlan.read(care_plan["id"], smart.server)

    # Print details
    print(f"Care plan ID: {care_plan.id}")
    print(f"Period: {care_plan.period.as_json()}")

    return care_plan
