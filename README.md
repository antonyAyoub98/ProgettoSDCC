# Pipeline Automatizzata di Machine Learning in Ambiente Cloud

**Corso:** Sistemi Distribuiti e Cloud Computing (A.A. 2024/2025)  
**Studente:** Antony Ayoub (Matricola: 263745)

## Panoramica del Progetto
Questo progetto implementa una pipeline automatizzata di Machine Learning sfruttando l'ecosistema serverless (FaaS) e IaaS di Google Cloud Platform (GCP). L'obiettivo del sistema è analizzare il "Room Occupancy Estimation Dataset" per prevedere il numero esatto di occupanti (da 0 a 3 persone) all'interno di un ambiente chiuso, elaborando i dati provenienti da sensori IoT non intrusivi (Temperatura, Luce, Suono, $\text{CO}_2$ e sensori di movimento PIR).

## Architettura del Sistema
L'architettura è event-driven e si articola in 4 step principali:

* **Step 1 (Ingestion e Trigger):** Il caricamento del dataset grezzo (in formato CSV) su un bucket Google Cloud Storage agisce come evento trigger. Attraverso Eventarc, la notifica dell'evento attiva automaticamente la fase successiva senza intervento manuale.
* **Step 2 (Preprocessing Serverless):** Una Cloud Run Function in Python si attiva per leggere i dati dal bucket, pulirli tramite la libreria Pandas (effettuando rimozione di valori nulli e normalizzazione) e salvare il dataset elaborato in un bucket di destinazione isolato.
* **Step 3 (Training Serverless):** Una seconda Cloud Function viene innescata dal salvataggio dei dati puliti per addestrare un modello di classificazione multi-classe (Random Forest) utilizzando Scikit-learn. Il modello addestrato viene serializzato tramite la libreria joblib (in formato `.pkl` o `.joblib`) e salvato nello storage cloud.
* **Step 4 (Inference Engine):** L'inferenza in tempo reale è gestita su una Virtual Machine Ubuntu (Compute Engine). Un'API REST sviluppata in FastAPI carica il modello serializzato. L'applicativo è containerizzato con Docker per garantire riproducibilità ambientale e servito al pubblico tramite Nginx, che funge da Reverse Proxy per isolare l'API dal traffico web diretto.

## Tracciabilità e Frontend
* **Auditing con Firestore:** Ogni inferenza andata a buon fine viene salvata in modo asincrono su un database NoSQL Cloud Firestore. Il documento JSON salvato include i parametri ambientali ricevuti, l'occupazione predetta e un timestamp di sistema.
* **Dashboard Interattiva:** Il sistema integra un'interfaccia frontend moderna realizzata con Bootstrap 5. La dashboard permette di inviare i 4 parametri tramite un form e visualizzare una tabella riassuntiva interrogando l'endpoint dedicato `GET /history` per leggere lo storico delle predizioni.

## Struttura del Repository
* `data/`: Ambiente isolato per i dataset grezzi e puliti (esclusi dal tracciamento Git per sicurezza).
* `src/`: Contiene il codice sorgente Python, inclusi gli script serverless (`clean_data.py`, `train_model.py`) e l'API backend (`main.py`).
* `config/requirements.txt`: Elenca le librerie Python e le versioni esatte necessarie per il progetto (es. Pandas, Scikit-learn, FastAPI).
* `Dockerfile`: File di configurazione per creare l'immagine isolata dell'Inference Engine.
* `.gitignore`: Direttive per escludere file sensibili, set di dati pesanti, il file `firebase_credentials.json` e l'ambiente virtuale locale (`.venv/`).

## Deploy e Avvio (Step 4)
Istruzioni base per avviare il container di inferenza sull'istanza Ubuntu ospitata su Compute Engine:
1.  Clonare o aggiornare il codice sulla Virtual Machine tramite `git pull`.
2.  Costruire l'immagine Docker: `sudo docker build -t room-occupancy-api .`.
3.  Avviare il container mappando la porta d'ascolto (es. 8000 o 8080): `sudo docker run -d --name api_container -p 8080:8080 room-occupancy-api`.
4.  Assicurarsi che il servizio Nginx sia attivo e configuri il `proxy_pass` verso `http://127.0.0.1:8080` (o 8000) per gestire le connessioni esterne.
