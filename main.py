from fastapi import FastAPI
from pudantic import BaseModel, Field, computed_Field
from typing import Annotated, Literal
import json
from fastapi import Path, HTTPException, Query
app = FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description="The unique ID of the patient", example="P001")]
    name: Annotated[str, Field(..., description="The name of the patient", example="John Doe")]
    city: Annotated[str, Field(..., description="The city of the patient", example="New York")]
    age: Annotated[int, Field(..., gt=0,lt=120, description="The age of the patient", example=30)]
    gender: Annotated[Literal["Male", "Female"], Field(..., description="The gender of the patient", example="Male")]
    height: Annotated[float, Field(..., gt=0, description="The height of the patient in cm", example=175.5)]
    weight: Annotated[float, Field(..., gt=0, description="The weight of the patient in kg", example=70.0)]
    #bmi: Annotated[float, Field(..., gt=0, description="The BMI of the patient", example=22.8)]
    
    @computed_Field
    @property
    def bmi(self) -> float:
        if self.height > 0 and self.weight > 0:
            return self.weight / ((self.height / 100) ** 2)
        return 0.0

def load_data():
    with open("paitients.json", "r") as f:
        data = json.load(f)
        return data

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