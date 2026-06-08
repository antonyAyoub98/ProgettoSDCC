from sklearn.preprocessing import StandardScaler
from google.cloud import storage
import pandas as pd
import os

file_room = r"D:\Magistrale\Sistemi distribuiti\room_occupancy_estimation/Occupancy_Estimation.csv"


client= storage.Client()
bucket= client.bucket("ayoub-raw-clean-data")
blob= bucket.blob("Occupancy_Estimation.csv")
blob.upload_from_filename(file_room)
print("File caricato su GCS — il trigger si avvierà automaticamente!")

