from fastapi import FastAPI
from fastapi.responses import JSONResponse 
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json
from fastapi import Path, HTTPException, Query
app = FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description="The unique ID of the patient", example="P001")]
    name: Annotated[str, Field(..., description="The name of the patient", example="John Doe")]
    city: Annotated[str, Field(..., description="The city of the patient", example="New York")]
    age: Annotated[int, Field(..., gt=0,lt=120, description="The age of the patient", example=30)]
    gender: Annotated[Literal["Male", "Female", "male", "female"], Field(..., description="The gender of the patient", example="Male")]
    height: Annotated[float, Field(..., gt=0, description="The height of the patient in cm", example=175.5)]
    weight: Annotated[float, Field(..., gt=0, description="The weight of the patient in kg", example=70.0)]
    #bmi: Annotated[float, Field(..., gt=0, description="The BMI of the patient", example=22.8)]
    
    @computed_field
    @property
    def bmi(self) -> float:
        if self.height > 0 and self.weight > 0:
            return self.weight / ((self.height / 100) ** 2)
        return 0.0
    
    @computed_field 
    @property
    def verdict(self) -> str:
        bmi_value = self.bmi
        if bmi_value < 18.5:
            return "Underweight"
        elif 18.5 <= bmi_value < 24.9:
            return "Normal weight"
        elif 25 <= bmi_value < 29.9:
            return "Overweight"
        else:
            return "Obesity"

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(None, description="The name of the patient", example="John Doe")]
    city: Annotated[Optional[str], Field(None, description="The city of the patient", example="New York")]
    age: Annotated[Optional[int], Field(None, gt=0,lt=120, description="The age of the patient", example=30)]
    gender: Annotated[Optional[Literal["Male", "Female", "male", "female"]], Field(None, description="The gender of the patient", example="Male")]
    height: Annotated[Optional[float], Field(None, gt=0, description="The height of the patient in cm", example=175.5)]
    weight: Annotated[Optional[float], Field(None, gt=0, description="The weight of the patient in kg", example=70.0)]

    #bmi: Annotated[Optional[float], Field(None, gt=0, description="The BMI of the patient", example=22.8)]

def load_data():
    with open("paitients.json", "r") as f:
        data = json.load(f)
        return data
    
def save_data(data):
    with open("paitients.json", "w") as f:
        json.dump(data, f)

@app.get("/")
def hello():
    return {"message": "Patient Management  System API"}

@app.get("/about")
def about():
    return {"message": "A fully functional Paitient Management System API built with FastAPI."}

@app.get("/view")
def get_patients():
    return load_data()

@app.get("/patient/{patient_id}")
def get_patient(patient_id: str= Path(..., description="The ID of the patient to retrieve", example="P00X")):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    #return {"message": "Patient not found."}
    raise HTTPException(status_code=404, detail="Patient not found.")

@app.get("/sort")
def sort_patients(sort_by: str = Query(..., description="The field to sort patients by height, weight and BMI", example="name"), order: str = Query("asc", description="The order to sort patients by (asc or desc)", example="asc")):
    data = load_data()
    valid_fields = ["height", "weight", "bmi"]
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort field. Valid fields are: {', '.join(valid_fields)}")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order. Valid orders are: asc, desc")
    
    sort_order= True if order == "desc" else False
    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse= sort_order)
    return sorted_data

@app.post('/create')
def create_patient(patient: Patient):
    
    #load existing data
    data = load_data()
    
    #check if patient already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists.")
    
    #new patient data
    data[patient.id] = patient.model_dump(exclude=['id'])
    
    #save updated data
    save_data(data)
    
    return JSONResponse(status_code=201, content={"message": "Patient created successfully.", "patient": data[patient.id]})

@app.put("/update/{patient_id}")

def update_patient(patient_id: str, patient_update: PatientUpdate):
    
    data= load_data()
    
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found.")
    
    existing_patient_info = data[patient_id]
    
    patient_update_dict = patient_update.model_dump(exclude_unset=True) #will return only the fields that are provided in the request body
    
    for key, value in patient_update_dict.items():
        existing_patient_info[key] = value
    
    #existing_patient_info['bmi'] -> pydantic object
    existing_patient_info['id'] = patient_id
    existing_patient_info.pop('bmi', None)
    existing_patient_info.pop('verdict', None)
    try:
        # Re-validate through the Patient model (this recalculates bmi & verdict)
        patient_pydantic_obj = Patient(**existing_patient_info)
    except Exception as e:
        # THIS will show you the real error in the response instead of a generic 500
        raise HTTPException(status_code=400, detail=f"Validation failed: {str(e)}")
    existing_patient_info = patient_pydantic_obj.model_dump(exclude={'id'})
    
    
    data[patient_id] = existing_patient_info
    
    save_data(data)
    
    return JSONResponse(status_code=200, content={"message": "Patient updated successfully.", "patient": data[patient_id]})

@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: str):
    data = load_data()
    
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found.")
    
    deleted_patient = data.pop(patient_id)
    
    save_data(data)
    
    return JSONResponse(status_code=200, content={"message": "Patient deleted successfully.", "patient": deleted_patient})