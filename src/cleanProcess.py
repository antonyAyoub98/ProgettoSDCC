import functions_framework
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from google.cloud import storage
import io
import logging

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)


bucketPulito="sdcc-clean-data"

@functions_framework.cloud_event
def preprocess(cloudEvent):
    data= cloudEvent.data
    bucketN=data["bucket"]
    fileN=data["name"]
    
    logger.info(f"File ricevuto:{fileN} dal bucket {bucketN}")
    
    #verifica che sia file csv
    if not fileN.endswith(".csv"):
        logger.info("file non CSV")
        return
    
    client = storage.Client()
    bucket_raw=client.bucket(bucketN)
    blob=bucket_raw.blob(fileN)
    content=blob.download_as_text(encoding="utf-8")
    df=pd.read_csv(io.StringIO(content))
    
    logger.info(f"Dataset uploaded: {df.shape[0]} righe, {df.shape[1]} colonne")
    
    #rimozione duplicati
    lenIn=len(df)
    df.drop_duplicates(inplace=True)
    logger.info(f"Duplicates Removed: {lenIn - len(df)}")
    
    
    #gestione Null in ogni colonna
    nColonne=df.select_dtypes(include=["number"]).columns.to_list() #seleziona le colonne dei sensori
    logger.info(f"Colonne numeriche trovate: {nColonne}")
    
    for col in nColonne:
        null=df[col].isnull().sum()
        if null>0:
            mediana=df[col].median()
            df[col].fillna(mediana,inplace=True)
            logger.info(f"Nella colonna {col} ci sono {null} valori nulli riempiti con la mediana {mediana:.2f}")
        else:
            logger.info(f"Nella colonna {col} NON ci sono valori nulli")
            
    
    #MinMax Normalization
    
    colTarget="Room_Occupancy_Count"
    colonneTest=[]
    for col in nColonne:
        if col != colTarget:
            colonneTest.append(col)
    scaler=MinMaxScaler()
    df[colonneTest]=scaler.fit_transform(df[colonneTest])
    logger.info(f"Normalizzazione applicata su {len(colonneTest)} colonne: {colonneTest}")
    
    csvOut=df.to_csv(index=False)

    output=f"file_pulito_{fileN}"

    bucket_pulito=client.bucket(bucketPulito)
    blob_pulito=bucket_pulito.blob(output)
    blob_pulito.upload_from_string(csvOut, content_type="text/csv")
    
    logger.info(f"Il file pulito e' stato salvato in gs://{bucketPulito}/{output}")
    logger.info("Preprocessing completato")

