# ISTANTANEA_DB_S7 - Siemens PLC S7 DB Snapshot & Backup Tool

**ISTANTANEA_DB_S7** è un'applicazione Windows portable, leggera e intuitiva, progettata per facilitare il backup, il ripristino, il monitoraggio in tempo reale e il confronto dei Data Block (DB) dei PLC Siemens della famiglia **S7-300** e **S7-400**. 

L'interfaccia grafica richiama lo stile classico del celebre **Siemens SIMATIC Manager Step 7**, combinando un'estetica retro con funzionalità diagnostiche moderne.

---

## 🚀 Caratteristiche Principali

1. **Scansione Nodi Accessibili (Accessible Nodes):**
   - Rilevamento automatico degli adattatori di rete locali e delle sotto-reti associate.
   - Scansione rapida multi-thread sulla porta TCP 102 (ISO-on-TCP).
   - Identificazione automatica del tipo di CPU, numero seriale e nome stazione tramite query diagnostiche SZL.
   
2. **Backup Snapshot dei Data Block (DB) e tolleranza all'errore:**
   - Connessione istantanea (sotto il secondo) grazie al caricamento dei DB asincrono e non bloccante.
   - Scansione automatica in background della memoria PLC (fino a 65535 DB) all'avvio del collegamento qualora la CPU non supporti l'elenco nativo (come le famiglie S7-400), mantenendo l'interfaccia interattiva e reattiva fin dal primo istante.
   - Scansione manuale di un intervallo personalizzato di DB (con default predefinito `1` a `65535`) con un pool parallelo ottimizzato a 6 thread che evita qualsiasi sovraccarico della CP del PLC.
   - Elenco dinamico di tutti i DB rilevati sul PLC con le rispettive dimensioni reali in byte.
   - Selezione selettiva (tramite checkbox) o totale dei DB da salvare.
   - **Tolleranza all'errore:** Se un DB configurato o presente nel simbolico restituisce un errore di lettura a causa di blocchi protetti o indirizzi inesistenti, la procedura di backup non si interrompe. Il DB viene loggato, l'operazione prosegue completando il backup dei restanti blocchi e un popup finale di avviso elenca in dettaglio le anomalie riscontrate.
   - Salvataggio dello snapshot in formato `.s7d` (JSON) o in formato **Excel (.xlsx)** multischeda avanzato.

3. **Salvataggio dello Snapshot in Excel (.xlsx) con struttura a Fogli di Lavoro per DB:**
   - **Foglio Overview:** Un foglio iniziale contenente i metadati di connessione (IP PLC, Data/Ora, Simulazione) e la lista complessiva di tutte le DB rilevate con descrizione simbolica.
   - **Un Foglio per DB:** Ogni blocco viene esportato in un foglio dedicato (es. `DB 10`). I dati non sono in esadecimale grezzo ma visualizzati come variabili individuali (Nome, Tipo Dato, Offset, Valore Live tradotto in tipo nativo di Excel: float, intero, bool) imitando il visualizzatore dell'applicazione.
   - **Editing ed Importazione:** L'utente può aprire il foglio Excel, modificare i valori all'interno delle celle e caricare direttamente l'Excel in ISTANTANEA_DB_S7 per effettuare ripristini nel PLC o confronti. L'applicazione ricostruisce automaticamente sia il bytearray grezzo che la struttura delle variabili dal foglio Excel!

4. **Ripristino Snapshot (Restore):**
   - Caricamento di file snapshot sia `.xlsx` multischeda che `.s7d` / `.json` tradizionali.
   - Selezione dei singoli DB da ripristinare e riscrittura dei byte direttamente nella memoria del PLC.
   - Ripristino automatico e caricamento immediato dei layout delle variabili custom direttamente dal file Excel.

5. **Importazione Simbolico PLC (STEP 7 .asc):**
   - Possibilità di importare direttamente la tabella dei simboli esportata da Siemens SIMATIC Manager STEP 7 in formato ASCII (`.asc`, `.seq`, `.sdf`, `.csv`, `.txt`).
   - Parser automatico con gestione intelligente degli spazi e delle tabulazioni (conserva i simboli che contengono spazi singoli) e fallback di codifica ANSI/Latin-1 per evitare caratteri errati.
   - Sostituzione automatica della descrizione generica nella tabella dei blocchi con i nomi simbolici e commenti reali (es: `CDZ-01_INV`).
   - Mantenimento ed esportazione delle descrizioni simboliche all'interno degli snapshot.

6. **Report Comparativo Avanzato (Confronto Live su entrambi i lati):**
   - Confronto dettagliato tra due file di snapshot differenti o tra uno snapshot e i valori in esecuzione sul PLC Live.
   - **Confronto Live Duale:** Sia la Sorgente A che la Sorgente B supportano il pulsante **"Usa PLC Live"** per consentire confronti incrociati completi e in tempo reale.
   - Evidenziazione cromatica immediata di ogni byte o variabile modificata.
   - Esportazione del report delle differenze in formato **CSV** e in formato **Excel (.xlsx)** con layout professionale a colori (stile Siemens Teal).

7. **Editor Mappa DB e Monitor Live:**
   - Possibilità di definire una struttura di mapping delle variabili per ciascun DB (assegnando nomi simbolici, tipi di dato e offset).
   - Generazione automatica di variabili organizzate in blocchi **WORD a passi di 2** (`DBW0`, `DBW2`, `DBW4` ecc.) per i DB non ancora mappati, con offset formattati secondo lo standard Simatic Manager (`byte.bit`, es. `0.0`, `2.0`, `4.0`...).
   - Tipi di dato S7 supportati: `BOOL`, `BYTE`, `CHAR`, `INT`, `WORD`, `DINT`, `DWORD`, `REAL` (Float 32), `STRING` (Siemens string standard).
   - Importazione ed esportazione delle mappe in formato `.json`.
   - Monitoraggio ciclico in tempo reale (polling a 200ms, 500ms, 1s, 2s).
   - Modifica e scrittura di singole variabili in tempo reale sul PLC.

8. **Cartella Tabelle di Variabili (Watch Tables) e Notazione S7 Inglese (I, Q, M, DB):**
   - Cartella **"Tabelle di variabili"** integrata nell'albero di progetto a sinistra (sotto il nodo PLC).
   - Creazione, rinominazione, eliminazione e duplicazione di tabelle di variabili personalizzate dal menu contestuale del tasto destro.
   - Notazione **inglese S7** per tutti gli indirizzi PLC:
     - **Ingressi (Input):** `I` (es. `I0.0`, `IB0`, `IW0`, `ID0`)
     - **Uscite (Output):** `Q` (es. `Q0.0`, `QB0`, `QW0`, `QD0`)
     - **Merker:** `M` (es. `M0.0`, `MB0`, `MW0`, `MD0`)
     - **Data Block:** `DB` (es. `DB1.DBX0.0`, `DB1.DBD0`)
   - Riconoscimento ed auto-predizione del tipo di dato alla digitazione dell'indirizzo.
   - Monitoraggio live in tempo reale con intervallo di aggiornamento personalizzabile (200ms, 500ms, 1s, 2s).
   - Scrittura singola o cumulativa delle variabili sul PLC.
   - **Importazione ed Esportazione in formato Excel (.xlsx):** salvataggio ed importazione diretta delle tabelle di variabili in file `.xlsx` (con supporto anche per `.json`).
   - Persistenza automatica delle tabelle di variabili nel file `config.json`.

9. **Ridimensionamento Interattivo Colonne su Tutte le Tabelle:**
   - Tutte le tabelle dell'applicazione (`blocks_table`, visualizzatore DB, tabella di variabili, confronto snapshot, dialog nodi accessibili) consentono di regolare liberamente la larghezza di ciascuna colonna trascinando le intestazioni.

10. **Simulatore Integrato:**
    - L'applicazione include un PLC virtuale interno. Spuntando la casella **"Simula"** sulla barra degli strumenti, è possibile testare tutte le funzionalità dell'app (scansione, backup, ripristino, monitor live con valori fluttuanti e report comparativi) anche senza essere fisicamente collegati a un PLC reale!

---

## 🛠️ Requisiti e Configurazione del PLC

- **Porta di Comunicazione:** Il PC deve poter raggiungere il PLC tramite la porta **TCP 102**. Assicurarsi che le regole del firewall consentano il traffico su questa porta.
- **Parametri di default:**
  - S7-300: Rack `0`, Slot `2`.
  - S7-400: Rack `0`, Slot `3` (o slot definiti in configurazione hardware).
- **PLCs S7-1200 / S7-1500 (Supporto Compatibilità):**
  L'applicazione può connettersi anche ai PLC più recenti (utilizzando Rack `0`, Slot `1`), purché nella configurazione hardware di TIA Portal siano attive le seguenti opzioni:
  1. Nelle proprietà della CPU, in *Protection & Security > Connection mechanisms*, deve essere abilitata la spunta su **"Permit access with PUT/GET communication from remote partner"**.
  2. I Data Block (DB) da leggere/scrivere devono avere la proprietà **"Optimized Block Access"** disabilitata (Accesso Standard).

---

## 💻 Come Eseguire e Compilare

Il progetto è strutturato per essere eseguito direttamente dal codice sorgente o compilato in un unico file eseguibile `.exe` indipendente (portable).

### Struttura del Progetto
```
ISTANTANEA_DB_S7/
├── src/
│   ├── main.py                 # File di avvio principale
│   ├── plc_comm.py             # Driver di comunicazione (wrapper python-snap7 + simulatore)
│   ├── utils.py                # Scanner di rete, parser e packager di tipi S7
│   ├── ui/
│   │   ├── main_window.py      # Finestra principale (Simatic Manager style)
│   │   ├── nodes_dialog.py     # Dialog di scansione nodi accessibili
│   │   ├── db_viewer.py        # Widget monitor live e mappatura variabili
│   │   ├── compare_window.py   # Finestra comparativa e generazione report Excel/CSV
│   │   ├── watch_table_viewer.py # Gestione e monitoraggio Tabelle di Variabili (Watch Tables)
│   │   ├── icons.py            # Generatore dinamico di icone vettoriali
│   │   └── styles.py           # Fogli di stile QSS del tema retro Siemens
│   └── __init__.py
├── tests/
│   └── test_plc.py             # Unit test automatizzati della logica di comunicazione
├── requirements.txt            # Dipendenze Python
├── run.bat                     # Script per avvio rapido da sorgente (crea venv ed esegue)
├── build.bat                   # Script per compilare l'eseguibile portable .exe
└── README.md
```

### 1. Avvio da sorgente (Developer Mode)
Fai doppio clic sul file **`run.bat`** (oppure esegui in PowerShell/CMD `run.bat`).
Questo script si occuperà automaticamente di:
- Verificare la presenza di Python 3.
- Creare un ambiente virtuale locale (`venv`).
- Aggiornare pip e installare le dipendenze (`PyQt6`, `python-snap7`, `openpyxl`, `pyinstaller`).
- Avviare l'applicazione.

### 2. Generazione dell'applicazione Portable (.exe)
Fai doppio clic sul file **`build.bat`**.
Lo script utilizzerà `PyInstaller` per impacchettare l'interprete Python, le librerie grafiche e i driver in un **singolo file eseguibile autonomo**:
- Il file compilato sarà salvato nella cartella **`dist/ISTANTANEA_DB_S7.exe`**.
- Questo file è **completamente portable**: può essere copiato su una chiavetta USB e avviato su qualsiasi computer Windows senza necessità di installare Python o altre dipendenze!

---

## 🧪 Test di Integrità e Validazione
Il progetto include una suite di unit test per convalidare la logica di calcolo degli offset, la codifica dei tipi Siemens e la comunicazione simulata. 

Per eseguire i test unitari:
```bash
.\venv\Scripts\python -m unittest tests/test_plc.py
```

---

## 🎨 Grafica e Design
L'applicazione imita fedelmente il design classico di Simatic Manager:
- Campi Rack e Slot implementati come ComboBox a scorrimento che garantiscono perfetta visibilità e clickability in qualsiasi risoluzione dello schermo e sia con Windows Light Mode che Dark Mode.
- Albero del progetto sulla sinistra con icone dedicate per Progetto, PLC e Data Block (disegnate dinamicamente per garantire massima risoluzione e portabilità).
- Barra dei menu e strumenti classica.
- Colori coordinati con il brand Siemens (Teal/Petrolio `#009999` e grigio industriale `#f0f0f0`).