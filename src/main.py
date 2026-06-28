from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import numpy as np
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

# 1. INIZIALIZZAZIONE FASTAPI E FIREBASE
app = FastAPI(
    title="Room Occupancy API",
    description="API di inferenza per il progetto di Sistemi Distribuiti",
    version="1.0.0"
)

# Inizializza Firebase Admin SDK
# NOTA: Assicurati di scaricare il file JSON dalla console Firebase e metterlo nella cartella config/
# In ambiente di produzione (sulla VM), assicurati che il percorso sia corretto.
cred_path = os.getenv("FIREBASE_CRED_PATH", "../config/firebase_credentials.json")
try:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Connessione a Firebase Firestore stabilita con successo.")
except Exception as e:
    print(f"Attenzione: Impossibile connettersi a Firebase. Errore: {e}")
    db = None

# 2. CARICAMENTO DEL MODELLO (Eseguito una sola volta all'avvio)
# In un'architettura cloud reale, qui potresti inserire il codice per 
# scaricare prima il file .pkl dal bucket di Google Cloud Storage.
model_path = os.getenv("MODEL_PATH", "../model.pkl")
try:
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    print("Modello Random Forest caricato in memoria con successo.")
except FileNotFoundError:
    print("Attenzione: File model.pkl non trovato. Assicurati che esista prima di fare predizioni.")
    model = None

# 3. DEFINIZIONE DELLO SCHEMA DATI (Pydantic)
# Questi sono i sensori previsti dal dataset Room Occupancy Estimation.
# FastAPI userà questa classe per bloccare automaticamente dati formattati male.
class RoomSensors(BaseModel):
    Temperature: float
    Humidity: float
    Light: float
    CO2: float
    HumidityRatio: float

# 4. ENDPOINT DI PREDIZIONE (Flusso principale)
@app.post("/predict")
async def predict_occupancy(data: RoomSensors):
    if model is None:
        raise HTTPException(status_code=500, detail="Modello non caricato nel server.")
    
    try:
        # A. Preparazione dati per Scikit-Learn
        # Il modello si aspetta un array numpy 2D (una riga, tante colonne)
        input_data = np.array([[
            data.Temperature, 
            data.Humidity, 
            data.Light, 
            data.CO2, 
            data.HumidityRatio
        ]])
        
        # B. Inferenza: Calcolo del Random Forest (Majority Voting)
        pred = model.predict(input_data)[0]
        
        # Calcolo opzionale della probabilità (percentuale di alberi d'accordo)
        try:
            probabilities = model.predict_proba(input_data)[0]
            confidence = round(max(probabilities) * 100, 2)
        except AttributeError:
            confidence = None # Nel caso il modello non supporti predict_proba
            
        # C. Registrazione (Log) su Firebase Firestore
        risultato_testuale = "Occupata" if pred == 1 else "Vuota"
        
        if db is not None:
            log_doc = {
                "timestamp": datetime.utcnow().isoformat(),
                "sensori": data.model_dump(),
                "predizione_valore": int(pred),
                "predizione_testo": risultato_testuale,
                "confidenza_modello": confidence
            }
            # Salva il documento in una collezione chiamata "storico_predizioni"
            db.collection("storico_predizioni").add(log_doc)
            
        # D. Risposta al Client (restituita come JSON)
        return {
            "status": "success",
            "prediction": int(pred),
            "label": risultato_testuale,
            "confidence": f"{confidence}%" if confidence else "N/A"
        }
        
    except Exception as e:
        # Se qualcosa va storto durante l'inferenza, restituisci un errore 500
        raise HTTPException(status_code=500, detail=f"Errore durante l'inferenza: {str(e)}")

# Endpoint di test per verificare che l'API sia accesa
@app.get("/")
def read_root():
    return {"message": "API di Inferenza attiva. Vai su /docs per l'interfaccia interattiva."}