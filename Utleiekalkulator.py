import tkinter as tk
from tkinter import messagebox
import json
import os
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import sys

# Funksjon for å runde til nærmeste multiplum
def mround(value, base):
    return base * round(value / base)

graph_visible = False  # Holder styr på om grafen er synlig

# Få sti til AppData\Roaming
appdata_dir = Path(os.getenv('APPDATA'))

# Opprett en undermappe for programdataene dine
program_data_dir = appdata_dir / 'Utleiekalkulator'

# Opprett katalogen hvis den ikke finnes
program_data_dir.mkdir(exist_ok=True)

# Full sti til datafilen
data_file = program_data_dir / 'lagrede_data.json'

def beregn():
    global avdrag  # Legg til hvis 'avdrag' brukes i andre funksjoner
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
        months_to_subtract = 1 if var_11_mnd.get() else 0
        årsinntekt_diff = (inntekt_før_avdrag * 12) - (leieinntekter * months_to_subtract)
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
        "beregn_med_11_mnd": var_11_mnd.get(),
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
            var_11_mnd.set(data.get("beregn_med_11_mnd", False))

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
    sys.exit()  # Sørg for at programmet avslutter

def nullstill():
    global graph_visible
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

    # Skjul grafen hvis den er synlig
    if graph_visible:
        vis_grafer()  # Dette vil skjule grafen

def vis_grafer():
    global graph_visible, graph_option
    if graph_visible:
        # Skjul grafen
        for widget in graph_frame.winfo_children():
            widget.destroy()
        graph_frame.pack_forget()
        # Tilbakestill vindusstørrelsen
        vindu.geometry("500x900")  # Original størrelse
        graph_visible = False
    else:
        # Sjekk at nødvendig data er tilgjengelig
        if lbl_gjeld.cget("text") == "Gjeld: " or lbl_avdrag.cget("text") == "Avdrag: ":
            messagebox.showerror("Feil", "Du må utføre beregningen før du kan vise grafen.")
            return

        # Vis grafen
        # Rydd opp i graph_frame
        for widget in graph_frame.winfo_children():
            widget.destroy()

        try:
            # Opprett canvas for grafen
            global canvas, fig, ax
            fig, ax = plt.subplots(figsize=(6, 4))
            canvas = FigureCanvasTkAgg(fig, master=graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10)

            # Opprett en ramme for radioknappene under grafen
            options_frame = tk.Frame(graph_frame)
            options_frame.pack(pady=5)

            # Initialiser graph_option variabel
            graph_option = tk.StringVar(value="Alle")  # Standardverdi
            graph_option.trace('w', oppdater_graf)

            # Opprett label og radioknapper i options_frame
            lbl_graph_option = tk.Label(options_frame, text="Velg graf:", font=('Arial', 12, 'bold'))
            lbl_graph_option.pack()

            options = ["Alle", "Gjeld", "Boligverdi", "Egenkapital"]
            for option in options:
                rb = tk.Radiobutton(options_frame, text=option, variable=graph_option, value=option)
                rb.pack(side='left', padx=5)


            # Kall funksjonen for å tegne grafen første gang
            oppdater_graf()

            # Pakk graph_frame for å vise grafen
            graph_frame.pack(side='left', fill='both', expand=True)

            # Utvid vinduet for å gi plass til grafen
            vindu.geometry("1000x900")  # Øk bredden

            graph_visible = True
        except Exception as e:
            messagebox.showerror("Feil", f"Kunne ikke generere grafen: {e}")

def oppdater_graf(*args):
    global fig, ax, canvas
    try:
        valgt_graf = graph_option.get()

        # Beregn utvikling over tid
        år = list(range(1, 11))  # År 1 til 10
        boligverdier = []
        gjeldsverdier = []
        egenkapitalverdier = []

        # Initialverdier
        boligverdi = float(entry_boligverdi.get())
        gjeld_text = lbl_gjeld.cget("text").split(":")[1].strip().replace(" kr", "").replace(",", "")
        gjeld = float(gjeld_text)
        avdrag_text = lbl_avdrag.cget("text").split(":")[1].strip().replace(" kr", "").replace(",", "")
        avdrag = float(avdrag_text)
        avdrag_per_år = avdrag * 12
        boligprisvekst = float(entry_boligprisvekst.get() or 0) / 100  # Konverter til desimaltall

        for _ in år:
            # Oppdater boligverdi med boligprisvekst
            boligverdi = boligverdi * (1 + boligprisvekst)
            boligverdier.append(boligverdi)

            # Oppdater gjeld
            gjeld = gjeld - avdrag_per_år
            gjeld = mround(gjeld, 100)

            # Unngå negativ gjeld
            if gjeld < 0:
                gjeld = 0

            gjeldsverdier.append(gjeld)

            # Beregn egenkapital
            egenkapital = boligverdi - gjeld
            egenkapitalverdier.append(egenkapital)

        # Tøm tidligere plott
        ax.clear()

        # Plot data basert på valgt graf
        if valgt_graf == "Gjeld":
            ax.plot(år, gjeldsverdier, label='Gjeld', marker='o')
            ax.set_title('Gjeld over 10 år')
            ax.set_ylabel('Gjeld (kr)')
        elif valgt_graf == "Boligverdi":
            ax.plot(år, boligverdier, label='Boligverdi', marker='o')
            ax.set_title('Boligverdi over 10 år')
            ax.set_ylabel('Boligverdi (kr)')
        elif valgt_graf == "Egenkapital":
            ax.plot(år, egenkapitalverdier, label='Egenkapital', marker='o')
            ax.set_title('Egenkapital over 10 år')
            ax.set_ylabel('Egenkapital (kr)')
        else:
            # Standard: Vis alle
            ax.plot(år, boligverdier, label='Boligverdi', marker='o')
            ax.plot(år, gjeldsverdier, label='Gjeld', marker='o')
            ax.plot(år, egenkapitalverdier, label='Egenkapital', marker='o')
            ax.set_title('Utvikling over 10 år')
            ax.set_ylabel('Beløp (kr)')

        ax.set_xlabel('År')
        ax.legend()
        fig.tight_layout()

        # Oppdater canvas
        canvas.draw()
    except Exception as e:
        messagebox.showerror("Feil", f"Kunne ikke oppdatere grafen: {e}")

def opprett_graf_knapp():
    try:
        # Last inn grafikonet
        graf_icon = Image.open("graph.ico")
        graf_icon = graf_icon.resize((30, 30), Image.LANCZOS)
        graf_photo = ImageTk.PhotoImage(graf_icon)

        # Opprett knappen
        btn_graf = tk.Button(vindu, image=graf_photo, command=vis_grafer, borderwidth=0)
        btn_graf.image = graf_photo  # Hold referansen
        btn_graf.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)  # Plasserer knappen øverst til høyre
    except Exception as e:
        # Hvis ikon ikke kan lastes, bruk en tekstknapp
        btn_graf = tk.Button(vindu, text="Vis graf", command=vis_grafer)
        btn_graf.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)

# Opprett hovedvinduet
vindu = tk.Tk()
vindu.title("Utleiekalkulator")
vindu.geometry("500x900")  # Justert vindustørrelse

# Koble Return-tasten til beregningsfunksjonen
vindu.bind('<Return>', lambda event: beregn())

# Initialiser var_møblert og var_11_mnd
var_møblert = tk.BooleanVar()
var_11_mnd = tk.BooleanVar()

# Innholdsramme
content_frame = tk.Frame(vindu)
content_frame.pack(fill='both', expand=True)

# Hovedramme for inndata og resultater
main_frame = tk.Frame(content_frame)
main_frame.pack(side='left', fill='both', expand=True, pady=10)

# Ramme for grafen (starter tom)
graph_frame = tk.Frame(content_frame)
# Vi pakker denne rammen når grafen vises

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

# Initialiser var_møblert og var_11_mnd
var_møblert = tk.BooleanVar()
var_11_mnd = tk.BooleanVar()

# Ramme for avhukingsbokser
checkbox_frame = tk.Frame(input_frame)
checkbox_frame.pack(pady=(5, 0))

# Avhukingsboks for "Møblert"
chk_møblert = tk.Checkbutton(checkbox_frame, text="Møblert", variable=var_møblert)
chk_møblert.pack(side='left')

# Avhukingsboks for "Beregn med 11 måneder"
chk_11_mnd = tk.Checkbutton(checkbox_frame, text="Beregn med 11 måneders leieinntekt", variable=var_11_mnd)
chk_11_mnd.pack(side='left', padx=10)

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
button_frame = tk.Frame(main_frame)
button_frame.pack(pady=30)

# Beregningsknapp
btn_beregn = tk.Button(button_frame, text="Beregn", command=beregn)
btn_beregn.pack(side=tk.LEFT, padx=10)

# Nullstill-knapp
btn_nullstill = tk.Button(button_frame, text="Nullstill", command=nullstill)
btn_nullstill.pack(side=tk.LEFT, padx=10)

# Etikett for å vise resultatet
lbl_resultat = tk.Label(main_frame, text="Resultat: ")
lbl_resultat.pack()

# Last inn data ved oppstart
laste_inn_data()

# Koble ved_avslutning-funksjonen til lukkingen av vinduet
vindu.protocol("WM_DELETE_WINDOW", ved_avslutning)

# Opprett grafknappen
opprett_graf_knapp()

# Start hovedløkken
vindu.mainloop()
