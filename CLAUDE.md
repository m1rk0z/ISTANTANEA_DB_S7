# CLAUDE.md - Development Guide

This file contains instructions for building, running, testing, and understanding the architecture of **IstanteS7**.

## 🛠️ Common Commands

### Running the Application (Source Mode)
* Windows (CMD/PowerShell): `run.bat`
* Manual virtual environment startup:
  ```powershell
  .\venv\Scripts\activate
  python src/main.py
  ```

### Building the Portable Executable
* Windows: `build.bat` (automatically kills running instances and compiles using PyInstaller)
* Manual PyInstaller command:
  ```powershell
  .\venv\Scripts\pyinstaller --onefile --noconsole --clean --name="IstanteS7" --paths=src src/main.py
  ```
  The output binary will be located in `dist/IstanteS7.exe`.

### Running Tests
* Run unit tests:
  ```powershell
  .\venv\Scripts\python -m unittest tests/test_plc.py
  ```

---

## 📁 Project Architecture & Layout

* `src/main.py`: App entry point. Sets path bindings (`_MEIPASS`) and launches the GUI.
* `src/plc_comm.py`: Communication logic wrapper around `python-snap7` (includes a virtual mock PLC simulator).
* `src/utils.py`: Encoders/decoders for Siemens S7 types (`parse_s7_data`, `pack_s7_data`) and multi-threaded network node scanner.
* `src/ui/main_window.py`: Main Siemens retro QSS interface. Coordinates project tree navigation, profile book, backups, restores, and symbols imports.
* `src/ui/db_viewer.py`: Real-time variable monitor tab and layout editor.
* `src/ui/compare_window.py`: Side-by-side snapshot comparison view (supports live comparison inputs and exports color-coded Excel/CSV).
* `src/ui/styles.py`: QSS dark/light branding stylesheet.
* `src/ui/icons.py`: Dynamically generated SVG icons.

---

## ⚙️ Key Development Conventions & Specifications

### 1. Excel Snapshots (.xlsx)
* Saved with an **Overview** sheet (metadata + list of DBs) and dedicated **DB X** sheets.
* Each DB sheet contains metadata on row 2, table headers on row 4, and structured variables on rows 5+ (`Nome Variabile`, `Tipo Dato`, `Offset (Byte.Bit)`, `Valore`).
* Values are stored with native Excel formats (floats, ints, booleans) for ease of manual editing.
* Read/load procedures parse the worksheets, rebuild byte buffers using `pack_s7_data`, and restore variable layout configurations into `self.dbs_structures`.

### 2. STEP 7 Symbols Import (.asc)
* Parses Simatic Manager Symbol exports delimited by tabs or spaces.
* Uses regex `re.split(r'\s{2,}', content)` to prevent splitting symbol names containing single spaces.
* Implements a fallback reader attempting `utf-8` decoding first, falling back to `latin-1`/`cp1252` (ANSI) to prevent Unicode failures.

### 3. Fault Tolerance
* Individual DB reads during backup or online comparison are wrapped in `try-except` blocks. Failing to read a specific DB does not halt the operation; the block is logged as skipped, and a summary warning list is shown to the user upon completion.
* PyInstaller compiles must be preceded by `taskkill /F /IM IstanteS7.exe` to release file locks on target binaries.
