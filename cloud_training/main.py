import functions_framework
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from google.cloud import storage
import io
import logging

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

bucketPulito="sdcc-clean-data"
output="occupancy_estimation_pulito.csv"
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
    
    colTarget="Room_Occupancy_Count"
    X=df.drop(columns=[colTarget])
    y=df[colTarget]
    