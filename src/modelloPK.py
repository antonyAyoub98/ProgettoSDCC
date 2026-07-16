import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier

def create_dummy_model():
    print("Inizializzazione dei dati fittizi...")
    
    # 1. Creiamo dei dati di test (X) con le 5 feature esatte richieste dall'API:
    # [Temperature, Humidity, Light, CO2, HumidityRatio]
    X_dummy = np.array([
        [20.0, 30.0, 0.0, 400.0, 0.003],    # Esempio 1: Stanza buia e fredda -> Vuota (0)
        [24.5, 45.0, 450.0, 850.0, 0.005],  # Esempio 2: Stanza calda, luminosa e con tanta CO2 -> Occupata (1)
        [19.5, 28.0, 0.0, 410.0, 0.002],    # Esempio 3: Stanza vuota
        [25.0, 50.0, 500.0, 950.0, 0.006]   # Esempio 4: Stanza occupata
    ])
    
    # 2. Assegniamo le etichette (y) corrispondenti: 0 = Vuota, 1 = Occupata
    y_dummy = np.array([0, 1, 0, 1])

    print("Addestramento del Random Forest in corso...")
    # 3. Creiamo un modello Random Forest base (con 10 alberi per fare in fretta)
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_dummy, y_dummy)

    # 4. Salviamo il modello in un file .pkl nella cartella principale
    # Assumiamo che questo script venga eseguito dalla cartella principale del progetto
    # o dalla cartella scripts/ (il file verrà salvato dove esegui il comando)
    model_path = "../model.pkl" # Salva nella directory superiore se eseguito dentro src/ o scripts/
    
    try:
        with open(model_path, "wb") as file:
            pickle.dump(model, file)
        print(f"✅ Successo! Il file '{model_path}' è stato generato e salvato.")
        print("Ora puoi avviare la tua API FastAPI per testarlo!")
    except Exception as e:
        # Fallback: salva nella cartella corrente se i percorsi non combaciano
        with open("model.pkl", "wb") as file:
            pickle.dump(model, file)
        print(f"✅ Successo! Il file 'model.pkl' è stato salvato nella cartella corrente.")

if __name__ == "__main__":
    create_dummy_model()