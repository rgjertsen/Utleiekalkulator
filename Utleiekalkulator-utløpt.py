import tkinter as tk
from tkinter import messagebox
import json
import os
from pathlib import Path

# Få sti til AppData\Roaming
appdata_dir = Path(os.getenv('APPDATA'))

# Opprett en undermappe for programdataene dine
program_data_dir = appdata_dir / 'Utleiekalkulator'

# Opprett katalogen hvis den ikke finnes
program_data_dir.mkdir(exist_ok=True)

# Full sti til datafilen
data_file = program_data_dir / 'lagrede_data.json'

def beregn():
    try:
        # Hent nødvendige verdier fra inntastingsfeltene
        boligverdi_text = entry_boligverdi.get()
        lånerente_text = entry_lånerente.get()
        belåningsgrad_text = entry_belåningsgrad.get()
        
        # Valider at nødvendige felt er fylt ut
        if not boligverdi_text or not lånerente_text or not belåningsgrad_text:
            lbl_resultat.config(text="Feil: Vennligst fyll ut alle nødvendige felt (*)")
            return
        
        boligverdi = float(boligverdi_text)
        lånerente = float(lånerente_text)
        belåningsgrad = float(belåningsgrad_text)
        
        # Valider verdiene
        if not (200000 <= boligverdi <= 20000000):
            messagebox.showerror("Ugyldig verdi", "Boligverdi må være mellom 200 000 og 20 000 000 kr.")
            return
        if not (0 <= lånerente <= 20):
            messagebox.showerror("Ugyldig verdi", "Lånerente må være mellom 0% og 20%.")
            return
        if not (0 <= belåningsgrad <= 85):
            messagebox.showerror("Ugyldig verdi", "Belåningsgrad må være mellom 0% og 85%.")
            return
        
        # Hent valgfrie verdier, sett til 0 hvis tomme
        boligprisvekst = float(entry_boligprisvekst.get() or 0)
        if not (0 <= boligprisvekst <= 10):
            messagebox.showerror("Ugyldig verdi", "Boligprisvekst må være mellom 0% og 10%.")
            return
        
        leieinntekter = float(entry_leieinntekter.get() or 0)
        fellesutgifter = float(entry_fellesutgifter.get() or 0)
        internett = float(entry_internett.get() or 0)
        kommunale_avgifter = float(entry_kommunale_avgifter.get() or 0)
        møblert = var_møblert.get()  # Dette vil være True eller False
        
        # Sjekk at de resterende verdiene er positive
        for value, name in [(leieinntekter, "Leieinntekter"), (fellesutgifter, "Fellesutgifter/forsikring"),
                            (internett, "Internett"), (kommunale_avgifter, "Kommunale avgifter per år")]:
            if value < 0:
                messagebox.showerror("Ugyldig verdi", f"{name} kan ikke være negativ.")
                return
    
        # Beregning av Gjeld og Egenkapital
        gjeld = boligverdi * (belåningsgrad / 100)
        egenkapital = boligverdi - gjeld

        lbl_gjeld.config(text=f"Gjeld: {gjeld:,.0f} kr")
        lbl_egenkapital.config(text=f"Egenkapital: {egenkapital:,.0f} kr")

        # Beregning av Terminbeløp
        månedlig_rente = (lånerente / 100) / 12
        antall_terminer = 30 * 12  # 30 år * 12 måneder

        # Implementer PMT-funksjonen
        if månedlig_rente != 0:
            terminbeløp = (gjeld * månedlig_rente * (1 + månedlig_rente) ** antall_terminer) / ((1 + månedlig_rente) ** antall_terminer - 1)
        else:
            terminbeløp = gjeld / antall_terminer

        terminbeløp += 50  # Legger til 50 som i formelen

        # Beregning av Lånerenter
        lånerenter = gjeld * månedlig_rente + 50

        # Beregning av Avdrag
        avdrag = terminbeløp - lånerenter

        lbl_terminbelop.config(text=f"Terminbeløp: {terminbeløp:,.0f} kr")
        lbl_lånerenter.config(text=f"Lånerenter: {lånerenter:,.0f} kr")
        lbl_avdrag.config(text=f"Avdrag: {avdrag:,.0f} kr")

        # Beregning av Fratrekk møblert
        if møblert:
            fratrekk_møblert = leieinntekter * 0.15
        else:
            fratrekk_møblert = 0

        lbl_fratrekk_møblert.config(text=f"Fratrekk møblert: {fratrekk_møblert:,.0f} kr")

        # Beregning av Vedlikeholdsutgifter
        vedlikeholdsutgifter = leieinntekter * 0.03

        lbl_vedlikeholdsutgifter.config(text=f"Vedlikeholdsutgifter: {vedlikeholdsutgifter:,.0f} kr")

        # Beregning av Skatt
        skatt = (leieinntekter - fellesutgifter - internett - lånerenter - (kommunale_avgifter / 12) - vedlikeholdsutgifter) * 0.22 - fratrekk_møblert

        lbl_skatt.config(text=f"Skatt: {skatt:,.0f} kr")

        # Beregning av Inntekt før avdrag
        inntekt_før_avdrag = ((leieinntekter - fellesutgifter - internett - (kommunale_avgifter / 12)) - skatt) - lånerenter - vedlikeholdsutgifter
        lbl_inntekt_før_avdrag.config(text=f"Inntekt før avdrag: {inntekt_før_avdrag:,.0f} kr")

        # Beregning av Årsinntekt
        årsinntekt_diff = (inntekt_før_avdrag * 12) - leieinntekter
        if årsinntekt_diff < 0:
            årsinntekt = -round(abs(årsinntekt_diff) / 100) * 100
        else:
            årsinntekt = round(årsinntekt_diff / 100) * 100
        lbl_årsinntekt.config(text=f"Årsinntekt: {årsinntekt:,.0f} kr")

        # Beregning av Cashflow inn/ut
        cashflow = (årsinntekt / 12) - avdrag
        lbl_cashflow.config(text=f"Cashflow inn/ut: {cashflow:,.0f} kr")

        lbl_resultat.config(text="Beregning utført.")

        # Lagre dataene etter beregning
        lagre_data()

    except ValueError:
        lbl_resultat.config(text="Ugyldig input! Vennligst skriv inn gyldige tall.")

def lagre_data():
    data = {
        "boligverdi": entry_boligverdi.get(),
        "lånerente": entry_lånerente.get(),
        "belåningsgrad": entry_belåningsgrad.get(),
        "boligprisvekst": entry_boligprisvekst.get(),
        "leieinntekter": entry_leieinntekter.get(),
        "fellesutgifter": entry_fellesutgifter.get(),
        "internett": entry_internett.get(),
        "kommunale_avgifter": entry_kommunale_avgifter.get(),
        "møblert": var_møblert.get(),
        "resultater": {
            "gjeld": lbl_gjeld.cget("text"),
            "egenkapital": lbl_egenkapital.cget("text"),
            "terminbelop": lbl_terminbelop.cget("text"),
            "lånerenter": lbl_lånerenter.cget("text"),
            "avdrag": lbl_avdrag.cget("text"),
            "fratrekk_møblert": lbl_fratrekk_møblert.cget("text"),
            "skatt": lbl_skatt.cget("text"),
            "vedlikeholdsutgifter": lbl_vedlikeholdsutgifter.cget("text"),
            "inntekt_før_avdrag": lbl_inntekt_før_avdrag.cget("text"),
            "årsinntekt": lbl_årsinntekt.cget("text"),
            "cashflow": lbl_cashflow.cget("text"),
        }
    }
    with open(data_file, "w") as f:
        json.dump(data, f)

def laste_inn_data():
    if data_file.exists():
        with open(data_file, "r") as f:
            data = json.load(f)
            entry_boligverdi.insert(0, data.get("boligverdi", ""))
            entry_lånerente.insert(0, data.get("lånerente", ""))
            entry_belåningsgrad.insert(0, data.get("belåningsgrad", ""))
            entry_boligprisvekst.insert(0, data.get("boligprisvekst", ""))
            entry_leieinntekter.insert(0, data.get("leieinntekter", ""))
            entry_fellesutgifter.insert(0, data.get("fellesutgifter", ""))
            entry_internett.insert(0, data.get("internett", ""))
            entry_kommunale_avgifter.insert(0, data.get("kommunale_avgifter", ""))
            var_møblert.set(data.get("møblert", False))

            # Fyll ut resultater hvis de finnes
            resultater = data.get("resultater", {})
            lbl_gjeld.config(text=resultater.get("gjeld", "Gjeld: "))
            lbl_egenkapital.config(text=resultater.get("egenkapital", "Egenkapital: "))
            lbl_terminbelop.config(text=resultater.get("terminbelop", "Terminbeløp: "))
            lbl_lånerenter.config(text=resultater.get("lånerenter", "Lånerenter: "))
            lbl_avdrag.config(text=resultater.get("avdrag", "Avdrag: "))
            lbl_fratrekk_møblert.config(text=resultater.get("fratrekk_møblert", "Fratrekk møblert: "))
            lbl_skatt.config(text=resultater.get("skatt", "Skatt: "))
            lbl_vedlikeholdsutgifter.config(text=resultater.get("vedlikeholdsutgifter", "Vedlikeholdsutgifter: "))
            lbl_inntekt_før_avdrag.config(text=resultater.get("inntekt_før_avdrag", "Inntekt før avdrag: "))
            lbl_årsinntekt.config(text=resultater.get("årsinntekt", "Årsinntekt: "))
            lbl_cashflow.config(text=resultater.get("cashflow", "Cashflow inn/ut: "))

def ved_avslutning():
    lagre_data()
    vindu.destroy()

def nullstill():
    # Nullstill inndatafeltene
    entry_boligverdi.delete(0, tk.END)
    entry_lånerente.delete(0, tk.END)
    entry_belåningsgrad.delete(0, tk.END)
    entry_boligprisvekst.delete(0, tk.END)
    entry_leieinntekter.delete(0, tk.END)
    entry_fellesutgifter.delete(0, tk.END)
    entry_internett.delete(0, tk.END)
    entry_kommunale_avgifter.delete(0, tk.END)
    var_møblert.set(False)

    # Nullstill resultater
    lbl_gjeld.config(text="Gjeld: ")
    lbl_egenkapital.config(text="Egenkapital: ")
    lbl_terminbelop.config(text="Terminbeløp: ")
    lbl_lånerenter.config(text="Lånerenter: ")
    lbl_avdrag.config(text="Avdrag: ")
    lbl_fratrekk_møblert.config(text="Fratrekk møblert: ")
    lbl_skatt.config(text="Skatt: ")
    lbl_vedlikeholdsutgifter.config(text="Vedlikeholdsutgifter: ")
    lbl_inntekt_før_avdrag.config(text="Inntekt før avdrag: ")
    lbl_årsinntekt.config(text="Årsinntekt: ")
    lbl_cashflow.config(text="Cashflow inn/ut: ")
    lbl_resultat.config(text="Resultat: ")

    # Fjern lagrede data
    if data_file.exists():
        os.remove(data_file)

# Opprett hovedvinduet
vindu = tk.Tk()
vindu.title("Utleiekalkulator")
vindu.geometry("500x900")  # Justert vindustørrelse

# Koble Return-tasten til beregningsfunksjonen
vindu.bind('<Return>', lambda event: beregn())

# Initialiser var_møblert
var_møblert = tk.BooleanVar()

# Hovedramme
main_frame = tk.Frame(vindu)
main_frame.pack(pady=10)

# Inntastingsfelt og etiketter
# Nødvendige inndata
input_frame = tk.Frame(main_frame)
input_frame.pack()

lbl_nødvendig = tk.Label(input_frame, text="Nødvendige inndata (*):", font=('Arial', 12, 'bold'))
lbl_nødvendig.pack()

# Boligverdi (*)
lbl_boligverdi = tk.Label(input_frame, text="Boligverdi (kr) *:")
lbl_boligverdi.pack()
entry_boligverdi = tk.Entry(input_frame)
entry_boligverdi.pack()

# Lånerente (*)
lbl_lånerente = tk.Label(input_frame, text="Lånerente (%) *:")
lbl_lånerente.pack()
entry_lånerente = tk.Entry(input_frame)
entry_lånerente.pack()

# Belåningsgrad (*)
lbl_belåningsgrad = tk.Label(input_frame, text="Belåningsgrad (%) *:")
lbl_belåningsgrad.pack()
entry_belåningsgrad = tk.Entry(input_frame)
entry_belåningsgrad.pack()

# Valgfrie inndata
lbl_valgfri = tk.Label(input_frame, text="Valgfrie inndata:", font=('Arial', 12, 'bold'))
lbl_valgfri.pack(pady=(10,0))

# Boligprisvekst (valgfri)
lbl_boligprisvekst = tk.Label(input_frame, text="Boligprisvekst (%):")
lbl_boligprisvekst.pack()
entry_boligprisvekst = tk.Entry(input_frame)
entry_boligprisvekst.pack()

# Leieinntekter (valgfri)
lbl_leieinntekter = tk.Label(input_frame, text="Leieinntekter (kr):")
lbl_leieinntekter.pack()
entry_leieinntekter = tk.Entry(input_frame)
entry_leieinntekter.pack()

# Fellesutgifter/forsikring (valgfri)
lbl_fellesutgifter = tk.Label(input_frame, text="Fellesutgifter/forsikring (kr):")
lbl_fellesutgifter.pack()
entry_fellesutgifter = tk.Entry(input_frame)
entry_fellesutgifter.pack()

# Internett (valgfri)
lbl_internett = tk.Label(input_frame, text="Internett (kr):")
lbl_internett.pack()
entry_internett = tk.Entry(input_frame)
entry_internett.pack()

# Kommunale avgifter per år (valgfri)
lbl_kommunale_avgifter = tk.Label(input_frame, text="Kommunale avgifter per år (kr):")
lbl_kommunale_avgifter.pack()
entry_kommunale_avgifter = tk.Entry(input_frame)
entry_kommunale_avgifter.pack()

# Avhukingsboks for "Møblert"
chk_møblert = tk.Checkbutton(input_frame, text="Møblert", variable=var_møblert)
chk_møblert.pack()

# Resultater
result_frame = tk.Frame(main_frame)
result_frame.pack(pady=10)

lbl_resultater = tk.Label(result_frame, text="Resultater:", font=('Arial', 12, 'bold'))
lbl_resultater.pack()

# Gjeld og Egenkapital
lbl_gjeld = tk.Label(result_frame, text="Gjeld: ")
lbl_gjeld.pack()
lbl_egenkapital = tk.Label(result_frame, text="Egenkapital: ")
lbl_egenkapital.pack()

# Terminbeløp, Lånerenter og Avdrag
lbl_terminbelop = tk.Label(result_frame, text="Terminbeløp: ")
lbl_terminbelop.pack()
lbl_lånerenter = tk.Label(result_frame, text="Lånerenter: ")
lbl_lånerenter.pack()
lbl_avdrag = tk.Label(result_frame, text="Avdrag: ")
lbl_avdrag.pack()

# Fratrekk møblert
lbl_fratrekk_møblert = tk.Label(result_frame, text="Fratrekk møblert: ")
lbl_fratrekk_møblert.pack()
# Skatt
lbl_skatt = tk.Label(result_frame, text="Skatt: ")
lbl_skatt.pack()
# Vedlikeholdsutgifter
lbl_vedlikeholdsutgifter = tk.Label(result_frame, text="Vedlikeholdsutgifter: ")
lbl_vedlikeholdsutgifter.pack()

# Ny ramme for ekstra beregninger
extra_frame = tk.Frame(main_frame)
extra_frame.pack(pady=10)

lbl_ekstra = tk.Label(extra_frame, text="Ekstra Beregninger:", font=('Arial', 12, 'bold'))
lbl_ekstra.pack()

# Inntekt før avdrag
lbl_inntekt_før_avdrag = tk.Label(extra_frame, text="Inntekt før avdrag: ")
lbl_inntekt_før_avdrag.pack()
# Årsinntekt
lbl_årsinntekt = tk.Label(extra_frame, text="Årsinntekt: ")
lbl_årsinntekt.pack()
# Cashflow inn/ut
lbl_cashflow = tk.Label(extra_frame, text="Cashflow inn/ut: ")
lbl_cashflow.pack()

# Knappene plasseres lenger ned med større margin
button_frame = tk.Frame(vindu)
button_frame.pack(pady=30)

# Beregningsknapp
btn_beregn = tk.Button(button_frame, text="Beregn", command=beregn)
btn_beregn.pack(side=tk.LEFT, padx=10)

# Nullstill-knapp
btn_nullstill = tk.Button(button_frame, text="Nullstill", command=nullstill)
btn_nullstill.pack(side=tk.LEFT, padx=10)

# Etikett for å vise resultatet
lbl_resultat = tk.Label(vindu, text="Resultat: ")
lbl_resultat.pack()

# Last inn data ved oppstart
laste_inn_data()

# Koble ved_avslutning-funksjonen til lukkingen av vinduet
vindu.protocol("WM_DELETE_WINDOW", ved_avslutning)

# Start hovedløkken
vindu.mainloop()
