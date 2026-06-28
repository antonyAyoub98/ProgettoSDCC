import functions_framework
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from google.cloud import storage
import joblib
import io
import logging

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

colTarget="Room_Occupancy_Count"

bucketTraining="sdcc-model-store"

@functions_framework.cloud_event
def training_model(cloudEvent):
    data= cloudEvent.data
    bucketN=data["bucket"]
    fileN=data["name"]
    
    
    logger.info(f"File pulito ricevuto:{fileN} dal bucket {bucketN}")
    
    #verifica che sia file csv
    if not fileN.endswith(".csv"):
        logger.info("file non CSV")
        return
    
    client = storage.Client()
    bucket_raw=client.bucket(bucketN)
    blob=bucket_raw.blob(fileN)
    content=blob.download_as_text(encoding="utf-8")
    df=pd.read_csv(io.StringIO(content))

    X=df.drop(columns=[colTarget])

    y=df[colTarget]

    
    
    logger.info(f"Tabella X (sensori) ha {X.shape[1]} colonne")
    logger.info(f"Tabella y (target) ha {len(y)} righe")

    #applico il classifier

    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42, test_size=0.2)

    rf=RandomForestClassifier(n_estimators=100, max_depth=10, min_samples_split=5, random_state=42)
    rf.fit(X_train, y_train)
    score=rf.score(X_test, y_test)
    logger.info(f"Score del modello: {score}")
    y_pred=rf.predict(X_test)
    logger.info(f"Classificazione del modello: {classification_report(y_test, y_pred)}")


    #salvataggio del modello

    path_model="/tmp/occupancy_model.joblib"

    joblib.dump(rf, path_model)

    model_filename="occupancy_model.joblib"

    bucket_model=client.bucket(bucketTraining)
    blob_model=bucket_model.blob(model_filename)
    blob_model.upload_from_filename(path_model)
    logger.info(f"Modello salvato in gs://{bucketTraining}/{model_filename}")