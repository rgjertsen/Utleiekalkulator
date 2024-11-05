# Utleiekalkulator

Utleiekalkulator er et Python-basert program som hjelper deg med å beregne økonomiske aspekter ved utleie av bolig. Programmet gir deg innsikt i blant annet gjeld, egenkapital, terminbeløp, lånerenter, avdrag, skatt og cashflow. I tillegg kan du visualisere utviklingen av gjeld, boligverdi og egenkapital over en periode på 10 år gjennom interaktive grafer.

## Funksjoner

- **Beregninger:**

  - Gjeld og egenkapital basert på boligverdi og belåningsgrad.
  - Terminbeløp, lånerenter og avdrag over en 30-årsperiode.
  - Skatteberegninger inkludert fratrekk for møblert utleie.
  - Estimert inntekt før avdrag, årsinntekt og cashflow.

- **Interaktiv grafisk fremstilling:**

  - Visualiser utviklingen av gjeld, boligverdi og egenkapital over 10 år.
  - Interaktive verktøytips som viser detaljerte verdier når du holder musepekeren over punktene.
  - Mulighet til å velge hvilke grafer du vil se (alle, gjeld, boligverdi eller egenkapital).

- **Brukervennlig grensesnitt:**

  - Grafisk brukergrensesnitt bygget med Tkinter.
  - Lagre og laste inn data automatisk ved oppstart og avslutning.
  - Intuitive inndatafelter med validering og feilhåndtering.

## Installasjon

1. **Klon repoet eller last ned koden:**

   ```bash
   git clone https://github.com/ditt-brukernavn/utleiekalkulator.git
   cd utleiekalkulator
   ```

2. **Installer nødvendige avhengigheter:**

   Sørg for at du har Python 3 installert på systemet ditt.

   ```bash
   pip install matplotlib mplcursors pillow
   ```

   *Merk:* `tkinter` er vanligvis inkludert i standard Python-distribusjoner på Windows og macOS. På Linux kan det hende du må installere det manuelt.

3. **Kjør programmet:**

   ```bash
   python utleiekalkulator.py
   ```


## Bruk

1. **Inndata:**

   - \**Nødvendige felter (merket med ***):**

     - **Boligverdi (kr)**\*
     - **Lånerente (%)**\*
     - **Belåningsgrad (%)**\*

   - **Valgfrie felter:**

     - **Boligprisvekst (%)**
     - **Leieinntekter (kr)**
     - **Fellesutgifter/forsikring (kr)**
     - **Internett (kr)**
     - **Kommunale avgifter per år (kr)**
     - **Møblert** (avkrysningsboks)

2. **Utfør beregning:**

   - Klikk på **"Beregn"**-knappen etter å ha fylt inn ønskede felter.
   - Resultatene vises under "Resultater" og "Ekstra Beregninger".

3. **Visualiser grafer:**

   - Klikk på grafikonet øverst til høyre for å åpne grafen.
   - Velg ønsket graf under grafen (Alle, Gjeld, Boligverdi, Egenkapital).
   - Hold musepekeren over punktene for å se detaljerte verdier.
   - Klikk på grafikonet igjen for å lukke grafen.

4. **Nullstill data:**

   - Klikk på **"Nullstill"**-knappen for å tømme alle felter og resultater.

## Avhengigheter

- Python 3.x
- Tkinter
- Matplotlib
- Mplcursors
- Pillow

## Filstruktur

- **utleiekalkulator.py:** Hovedprogramfilen.
- **graph.ico:** Ikon for grafknappen.
- **icon.ico:** Ikon som brukes i programmet for bedre brukeropplevelse.

## Feilhåndtering

- Programmet validerer inndata og vil vise feilmeldinger hvis:
  - Nødvendige felter ikke er fylt ut.
  - Inndata er utenfor tillatt område.
  - Ugyldige tall eller tegn er oppgitt.

## Bidrag

Bidrag er velkomne! Vennligst opprett en branch av repoet, gjør endringene dine, og opprett en pull request.

## AI-assistanse

Dette prosjektet er utviklet med hjelp av GitHub Copilot, ChatGPT og Claude Sonnet.
