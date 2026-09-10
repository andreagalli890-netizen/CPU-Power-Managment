import subprocess
import tkinter as tk
from tkinter import messagebox
import os
import re

def get_current_cpu_max():
    """ Legge l'impostazione attuale dal sistema """
    try:
        # Esegue il comando per leggere (query) le impostazioni di risparmio energia
        result = subprocess.run(
            ["powercfg", "-q", "SCHEME_CURRENT", "SUB_PROCESSOR", "PROCTHROTTLEMAX"],
            capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
        )
        # Analizza l'output riga per riga
        for line in result.stdout.splitlines():
            # Cerca la riga della corrente alternata, valida sia per Windows in ITA (CA) che ENG (AC)
            if ("AC" in line or "CA" in line) and "0x" in line:
                # Trova e converte il valore esadecimale in intero
                hex_val = re.search(r'0x[0-9a-fA-F]+', line).group()
                return int(hex_val, 16)
    except Exception:
        pass
    return 100  # Ritorna 100% come sicurezza in caso di errore di lettura

def aggiorna_testo_cpu():
    """ Aggiorna la label grafica con l'ultimo livello impostato """
    livello = get_current_cpu_max()
    lbl_current_cpu.config(text=f"Current CPU level: {livello}%")

# Creazione dell'interfaccia grafica
root = tk.Tk()
root.title("CPU power control")
root.geometry("325x265")
root.resizable(False, False)

# Leggiamo subito il livello iniziale per impostare le variabili
livello_iniziale = get_current_cpu_max()

# --- Variabile condivisa tra Slider e Casella di Testo ---
var_slider = tk.IntVar(value=livello_iniziale)
var_testo = tk.StringVar(value=str(livello_iniziale))

def on_slider_change(val):
    """ Quando muovi lo slider, aggiorna la casella di testo """
    var_testo.set(val)

def on_testo_change(*args):
    """ Quando scrivi nella casella, aggiorna lo slider SOLO se il numero ha senso """
    try:
        val = int(var_testo.get())
        # Se stai scrivendo 7, non fa nulla. Se scrivi 75, sposta lo slider!
        if 10 <= val <= 100:
            var_slider.set(val)
    except ValueError:
        pass # Ignora se la casella è vuota o ha lettere mentre l'utente digita

# Colleghiamo la funzione di controllo alla casella di testo
var_testo.trace_add("write", on_testo_change)

#contenitore per i due elementi centrali
frame_bot = tk.Frame(root)
frame_bot.pack(fill=tk.X, padx=20, pady=15)

# Etichetta di istruzioni
lbl_info = tk.Label(frame_bot, text="Max CPU level:", font=("Arial", 11))
lbl_info.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))

# Slider grafico
slider = tk.Scale(frame_bot, from_=50, to=100, orient=tk.HORIZONTAL, length=220, font=("Arial", 11), tickinterval=90, variable=var_slider, command=on_slider_change)
slider.pack(side=tk.RIGHT)

# Contenitore per l'input manuale
frame_input = tk.Frame(root)
frame_input.pack(pady=(0, 10))

lbl_input = tk.Label(frame_input, text="enter the exact value (%):", font=("Arial", 10))
lbl_input.pack(side=tk.LEFT)


entry_input = tk.Entry(frame_input, textvariable=var_testo, width=5, font=("Arial", 10, "bold"), justify="center")
entry_input.pack(side=tk.LEFT, padx=5)

def set_cpu_max(percentage):
    """ Modifica lo stato massimo del processore per il piano di alimentazione corrente. """
    try:
        subprocess.run(["powercfg", "-setacvalueindex", "SCHEME_CURRENT", "SUB_PROCESSOR", "PROCTHROTTLEMAX", str(percentage)], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(["powercfg", "-setdcvalueindex", "SCHEME_CURRENT", "SUB_PROCESSOR", "PROCTHROTTLEMAX", str(percentage)], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(["powercfg", "-setactive", "SCHEME_CURRENT"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        aggiorna_testo_cpu() # Aggiorna il testo sulla GUI
        messagebox.showinfo("Operation completed", f"Max CPU level set to {percentage}%")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Unable to modify settings. You may need to run the script as Administrator.")

def applica_limite():
    """ Legge il valore dello slider e lo applica al sistema """
    percentuale = int(var_testo.get())
        
        # Correzione automatica se scrivi numeri fuori limite e premi "Applica"
    if percentuale < 50: percentuale = 50
    if percentuale > 100: percentuale = 100
        
    var_slider.set(percentuale)
    var_testo.set(str(percentuale))
    try:
        subprocess.run(["powercfg", "-setacvalueindex", "SCHEME_CURRENT", "SUB_PROCESSOR", "PROCTHROTTLEMAX", str(percentuale)], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(["powercfg", "-setdcvalueindex", "SCHEME_CURRENT", "SUB_PROCESSOR", "PROCTHROTTLEMAX", str(percentuale)], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(["powercfg", "-setactive", "SCHEME_CURRENT"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        aggiorna_testo_cpu() # Aggiorna il testo sulla GUI
        messagebox.showinfo("Success", f"Max CPU level set to {percentuale}%.")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Unable to modify settings. You may need to run the script as Administrator.")

strong = 100
script_path = r"C:\Users\Andrea\Programs\CPU_PowerManagement\cpu_power.py"
conda_activate = r"C:\Users\Andrea\miniconda3\Scripts\activate.bat"
nome_ambiente = "base"

def mode_max():
    # Ripristina la CPU al 100% per carichi pesanti
    set_cpu_max(strong)

nome_file_base = os.path.basename(script_path).replace('.py', '')
cartella_corrente = os.path.dirname(script_path)
dist_path = os.path.join(cartella_corrente, 'dist', f"{nome_file_base}.exe")

def open_script():
    """ Apre il file .py con l'editor predefinito (es. VS Code) """
    try:
        if os.path.exists(script_path):
            os.startfile(script_path)
        else:
            messagebox.showerror("Error", "Unable to find the file.")
    except Exception as e:
        messagebox.showerror("Error", f"Unable to open the file:\n{e}")

# Contenitore per i due elementi centrali
frame_bot = tk.Frame(root)
frame_bot.pack(fill=tk.X, padx=20, pady=15)

# Pulsante per applicare (ora inserito fisicamente dentro frame_bot)
btn_applica = tk.Button(frame_bot, text="✅ Apply", command=applica_limite, bg="lightgreen", font=("Arial", 11, "bold"))
btn_applica.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))

# Livello attuale della CPU (inizializzato all'avvio)
livello_iniziale = get_current_cpu_max()
lbl_current_cpu = tk.Label(frame_bot, text=f"Current CPU level: {livello_iniziale}%", font=("Arial", 11, "bold"), fg="blue")
lbl_current_cpu.pack(side=tk.RIGHT)

# Separatore visivo
tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=20, pady=5)

# Contenitore per i due pulsanti inferiori
frame_bottom = tk.Frame(root)
frame_bottom.pack(fill=tk.X, padx=20, pady=5)

# Pulsante per massima potenza
btn_max = tk.Button(frame_bottom, text=f"Max Power ({strong}%)", command=mode_max, bg="lightcoral", font=("Arial", 15))
btn_max.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

# Pulsantino quadrato per aprire il codice
btn_open = tk.Button(frame_bottom, text="📝", command=open_script, bg="#f0f0f0", font=("Arial", 15), width=3)
btn_open.pack(side=tk.RIGHT)

# Sincronizza lo slider col valore attuale di sistema all'apertura del programma
slider.set(livello_iniziale)

root.mainloop()