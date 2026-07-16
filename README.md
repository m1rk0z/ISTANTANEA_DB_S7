# IstanteS7 - Siemens PLC S7 DB Snapshot & Backup Tool

**IstanteS7** è un'applicazione Windows portable, leggera e intuitiva, progettata per facilitare il backup, il ripristino, il monitoraggio in tempo reale e il confronto dei Data Block (DB) dei PLC Siemens della famiglia **S7-300** e **S7-400**. 

L'interfaccia grafica richiama lo stile classico del celebre **Siemens SIMATIC Manager Step 7**, combinando un'estetica retro con funzionalità diagnostiche moderne.

---

## 🚀 Caratteristiche Principali

1. **Scansione Nodi Accessibili (Accessible Nodes):**
   - Rilevamento automatico degli adattatori di rete locali e delle sotto-reti associate.
   - Scansione rapida multi-thread sulla porta TCP 102 (ISO-on-TCP).
   - Identificazione automatica del tipo di CPU, numero seriale e nome stazione tramite query diagnostiche SZL.
   
2. **Backup Snapshot dei Data Block (DB):**
   - Connessione istantanea (sotto il secondo) grazie al caricamento dei DB asincrono e non bloccante.
   - Scansione automatica in background della memoria PLC (fino a 65535 DB) all'avvio del collegamento qualora la CPU non supporti l'elenco nativo (come le famiglie S7-400), mantenendo l'interfaccia interattiva e reattiva fin dal primo istante.
   - Scansione manuale di un intervallo personalizzato di DB (con default predefinito `1` a `65535`) con un pool parallelo ottimizzato a 6 thread che evita qualsiasi sovraccarico della CP del PLC.
   - Elenco dinamico di tutti i DB rilevati sul PLC con le rispettive dimensioni reali in byte.
   - Selezione selettiva (tramite checkbox) o totale dei DB da salvare.
   - Salvataggio dello snapshot in un file compatto in formato `.s7d` (JSON-based, contenente i byte grezzi in formato esadecimale).

3. **Ripristino Snapshot (Restore):**
   - Caricamento di qualsiasi file snapshot precedentemente salvato.
   - Selezione dei singoli DB da ripristinare e riscrittura dei byte direttamente nella memoria del PLC.

4. **Report Comparativo e di Modifica:**
   - Confronto dettagliato tra due file di snapshot differenti o tra uno snapshot e i valori in esecuzione sul PLC Live.
   - Evidenziazione cromatica immediata di ogni byte o variabile modificata.
   - Esportazione del report delle differenze in formato **CSV** e in formato **Excel (.xlsx)** con layout professionale a colori (stile Siemens Teal).

5. **Editor Mappa DB e Monitor Live:**
   - Possibilità di definire una struttura di mapping delle variabili per ciascun DB (assegnando nomi simbolici, tipi di dato e offset).
   - Generazione automatica di variabili organizzate in blocchi **WORD a passi di 2** (`DBW0`, `DBW2`, `DBW4` ecc.) per i DB non ancora mappati, con offset formattati secondo lo standard Simatic Manager (`byte.bit`, es. `0.0`, `2.0`, `4.0`...).
   - Tipi di dato S7 supportati: `BOOL`, `BYTE`, `CHAR`, `INT`, `WORD`, `DINT`, `DWORD`, `REAL` (Float 32), `STRING` (Siemens string standard).
   - Importazione ed esportazione delle mappe in formato `.json`.
   - Monitoraggio ciclico in tempo reale (polling a 200ms, 500ms, 1s, 2s).
   - Modifica e scrittura di singole variabili in tempo reale sul PLC.

6. **Simulatore Integrato:**
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
- Il file compilato sarà salvato nella cartella **`dist/IstanteS7.exe`**.
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