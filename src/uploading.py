from google.cloud import storage


fileADD = r"/home/antayo98/ProgettoSDCC/data/Occupancy_Estimation.csv"


client= storage.Client()
bucket= client.bucket("raw-clean-data")
blob= bucket.blob("Occupancy_Estimation.csv")
blob.upload_from_filename(fileADD)
print(f"File caricato su GCS dentro il bucket {bucket}— il trigger si avvierà automaticamente!")

