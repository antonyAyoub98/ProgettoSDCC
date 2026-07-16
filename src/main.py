from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage
import os


DIR_PRINCIPALE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_MODEL_PATH = os.path.join(DIR_PRINCIPALE, "model_trained.joblib")

BUCKET_NAME="sdcc-model-store"

#credenziali firebase
cred_path = os.path.join(DIR_PRINCIPALE, "config","firebase_credentials.json")
try:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client(database_id="db-progetto-sdcc")
    print("Connessione a Firebase Firestore stabilita con successo.")
except Exception as e:
    print(f"Attenzione: Impossibile connettersi a Firebase. Errore: {e}")
    db = None

def download_model_from_bucket():
    try:
        client = storage.Client.from_service_account_json(cred_path)
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob("model_trained.joblib")
        blob.download_to_filename(LOCAL_MODEL_PATH)
        print("Modello scaricato dal Bucket con successo")        
    except Exception as e:
        print(f"Errore durante il download del modello dal bucket: {e}")

if not os.path.exists(LOCAL_MODEL_PATH):
    download_model_from_bucket()


try:
    print("Tentativo di caricamento modello...")
    pkg = joblib.load(LOCAL_MODEL_PATH)
    model = pkg["model"]
    scaler = pkg["scaler"]
    print("Modello e scaler caricati con successo.")

except Exception as e:
    print(f"Errore durante il caricamento del modello: {e}")
    model = None
    scaler = None

print("Classi conosciute dal modello:", model.classes_)
app = FastAPI(
    title="Room Occupancy API",
    description="API per predire l'occupazione di una stanza basata su sensori ambientali.")

#i sensori previsti dal dataset Room Occupancy Estimation
class RoomSensors(BaseModel):
    Temperature: float
    Light: float
    Sound: float
    CO2: float

# 4. ENDPOINT DI PREDIZIONE (Flusso principale)
@app.post("/predict")
def predict_occupancy(data: RoomSensors):
    if model is None:
        raise HTTPException(status_code=500, detail="Il modello ML non è caricato correttamente.")

    # Converti i dati JSON ricevuti in un DataFrame per Scikit-learn
    input_df = pd.DataFrame([data.model_dump()])

    input_scaled = scaler.transform(input_df)
    
    # Effettua la predizione (0 o 1)
    prediction = model.predict(input_scaled)[0]
    
    # Prepara il documento da salvare su Firestore
    record = {
        "sensori": data.model_dump(),
        "occupazione_predetta": int(prediction),
        "timestamp": firestore.SERVER_TIMESTAMP # Inserisce l'orario automatico di GCP
    }
    
    # Salva nello storico di Firestore (creerà una collezione chiamata 'predictions')
    try:
        db.collection("predictions").add(record)
    except Exception as e:
        print(f"Errore nel salvataggio su Firestore: {e}")
    
    # Restituisce il risultato all'utente
    return {
        "prediction": int(prediction),
        "status": "success",
        "message": "Predizione effettuata e salvata nello storico."
    }

@app.get("/")
def read_root():
    return {"message": "API di funzione. Vai su /docs per l'interfaccia interattiva."}