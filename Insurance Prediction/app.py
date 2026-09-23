from fastapi import FastAPI
from fastapi.responses import JSONResponse
from schema.user_input import UserInput
from model.predict import predict_output, MODEL_VERSION
from schema.prediction_responese import PredictionResponse

app = FastAPI()


@app.get('/')
def home():
    return {"message": "Welcome to the Insurance Premium Category Predictor API"}
@app.get('/health')
def health_check():
    return {"status": "OK",
            "version": MODEL_VERSION
            }

@app.post('/predict', response_model=PredictionResponse)
def predict_premium(data: UserInput):

    input_df = {
        'bmi': data.bmi,
        'age_group': data.age_group,
        'lifestyle_risk': data.lifestyle_risk,
        'city_tier': data.city_tier,
        'income_lpa': data.income_lpa,
        'occupation': data.occupation
    }

    try:
        prediction = predict_output(input_df)
        
    except Exception as e:
        return JSONResponse(status_code=500, content={'error': str(e)})

    return JSONResponse(status_code=200, content={'predicted_category': prediction})



