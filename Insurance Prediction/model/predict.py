import pickle
import pandas as pd
# import the ml model
with open('model/model.pkl', 'rb') as f:
    model = pickle.load(f)

MODEL_VERSION = "1.0.0"

class_labels =model.classes_.tolist()

def predict_output(user_input: dict):
    input_df = pd.DataFrame([user_input])

    prediction = model.predict(input_df)[0]
    
    probabilities = model.predict_proba(input_df)[0]
    confidence=max(probabilities)

    return {
        "predicted_category": prediction,
        "probabilities": dict(zip(class_labels, probabilities)),
        "confidence": confidence
    }