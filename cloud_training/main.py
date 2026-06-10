import functions_framework
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier 
from google.cloud import storage
import io
import logging
import joblib

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)


MODEL_BUCKET= "sdcc-model-STORAGE"
NOME_MODELLO= "occupany_model.pkl"
COL_TARGET="Room_Occupancy_Count"

@functions_framework.cloud_event
def train_model(cloudEvent):
    data= cloudEvent.data
    bucketN=data["bucket"]
    fileN=data["name"]
    
    logger.info(f"File rilevato nel bucket pulito: {fileN}")
    
    if fileN != "occupancy_estimation_pulito.csv":
        logger.info("File non rilevante per il training. Salto.")
        return
    
    client = storage.Client()
    bucket_raw=client.bucket(bucketN)
    blob=bucket_raw.blob(fileN)
    content=blob.download_as_text(encoding="utf-8")
    df=pd.read_csv(io.StringIO(content))
    
    X=df.drop(columns=[COL_TARGET])
    y=df[COL_TARGET]
    
    #divido il training 80% e 20%
    
    X_train, X_test, y_train, y_test=train_test_split(X, y, test_size=0.2, random_state=42)
    
    logger.info("Inizio addestramento del modello...")
    modello= RandomForestClassifier(n_estimators=100, random_state=42)
    modello.fit(X_train, y_train)
    
    accuracy=modello.score(X_test, y_test)
    logger.info(f"Modello addestrato con successo con Accuratezza del {accuracy*100:.2f}%")
    

    #serializzazione
    
    buffer_modello=io.BytesIO()
    joblib.dump(modello, buffer_modello)
    buffer_modello.seek(0)
    
    bucket_modello=client.bucket(MODEL_BUCKET)
    blob_modello=bucket_modello.blob(NOME_MODELLO)
    blob_modello.upload_from_file(buffer_modello,content_type="application/octet-stream")
    logger.info(f"Modello salvato in gs://{MODEL_BUCKET}/{NOME_MODELLO}")

