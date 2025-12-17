import sys

import os

import datetime

import tkinter as tk

from tkinter import filedialog
 
# Vérification de pandas

try:

    import pandas as pd

except ImportError:

    print("ERREUR : La librairie 'pandas' n'est pas installée.")

    input("Appuyez sur Entrée pour quitter...")

    sys.exit()
 
def select_file_manually():

    """Ouvre une fenêtre pour choisir le fichier CSV"""

    print("Ouverture de la fenêtre de sélection de fichier...")

    # Création d'une fenêtre racine invisible

    root = tk.Tk()

    root.withdraw() 

    # Ouvre l'explorateur de fichiers

    file_path = filedialog.askopenfilename(

        title="Sélectionnez votre fichier Excel/CSV 'Bird Strike'",

        filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")]

    )

    return file_path
 
def load_data(filepath):

    if not filepath:

        return None
 
    try:

        print(f"Lecture du fichier : {os.path.basename(filepath)}...")

        df = pd.read_csv(filepath)

        # Nettoyage et conversion

        df['INCIDENT_DATE'] = pd.to_datetime(df['INCIDENT_DATE'])

        # On essaie de convertir l'heure proprement

        df['HOUR'] = pd.to_numeric(df['TIME'].astype(str).str[:2], errors='coerce')

        print(" -> Données chargées avec succès !")

        return df

    except Exception as e:

        print(f"\n[ERREUR] Impossible de lire le fichier : {e}")

        return None
 
def analyze_risk(df, input_date):

    target_month = input_date.month

    month_name = input_date.strftime("%B")

    # Filtre sur le mois

    monthly_data = df[df['INCIDENT_MONTH'] == target_month]

    if monthly_data.empty:

        print(f"\nPas de données historiques pour le mois de {month_name}.")

        return
 
    total_incidents = len(monthly_data)

    # Fonction helper pour les stats

    def get_top_stat(column):

        if column not in df.columns: return "Inconnu", 0

        stats = monthly_data[column].value_counts(normalize=True)

        if stats.empty: return "Inconnu", 0

        return stats.index[0], stats.values[0] * 100
 
    # Calculs statistiques

    top_sky, sky_prob = get_top_stat('SKY')

    top_tod, tod_prob = get_top_stat('TIME_OF_DAY')

    top_ac, ac_prob = get_top_stat('AIRCRAFT')

    top_phase, phase_prob = get_top_stat('PHASE_OF_FLIGHT')

    species_stats = monthly_data['SPECIES'].value_counts(normalize=True)

    top_species = species_stats.index[0] if not species_stats.empty else "Inconnu"
 
    # Génération du rapport en anglais (comme demandé)

    print("\n" + "="*60)

    print(f"ANALYSIS REPORT FOR: {input_date.strftime('%Y-%m-%d')}")

    print(f"Context: {month_name} (based on {total_incidents} historical records)")

    print("="*60)

    print(f"\n1. METEOROLOGY (SKY)")

    print(f"   Most likely condition: '{top_sky}'")

    print(f"   (Probability: {sky_prob:.1f}%)")

    print(f"\n2. TIME & SCHEDULE")

    print(f"   Highest Risk Period: {top_tod} ({tod_prob:.1f}% chance).")

    print(f"\n3. AIRCRAFT & PHASE")

    print(f"   Phase of flight: {top_phase} ({phase_prob:.1f}%).")

    print(f"   Aircraft most at risk: {top_ac}.")

    print(f"\n4. WILDLIFE IDENTIFICATION")

    print(f"   Primary Species Threat: {top_species}")

    print("="*60 + "\n")
 
def main():
    print("\n********************************************************")

    print("      BIRD STRIKE PREDICTION AI      ")

    print("********************************************************")

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # ÉTAPE 1 : DÉTECTER OU CHOISIR LE FICHIER
    default_candidates = [
        "Bird strike Miami CSV.csv",
        "Bird strike Miami.xlsx - Feuil1.csv",
    ]

    csv_path = None
    for filename in default_candidates:
        candidate = os.path.join(script_dir, filename)
        if os.path.isfile(candidate):
            csv_path = candidate
            break

    if csv_path:
        print(f"Fichier détecté automatiquement : {os.path.basename(csv_path)}")
    else:
        print("Veuillez sélectionner le fichier de données (.csv) dans la fenêtre qui s'ouvre.")
        csv_path = select_file_manually()
        if not csv_path:
            print("Aucun fichier sélectionné. Fermeture du programme.")
            input("Appuyez sur Entrée...")
            return
 
    # ÉTAPE 2 : CHARGER

    df = load_data(csv_path)

    if df is None:
        # Si le fichier auto-détecté est illisible, on tente une sélection manuelle
        print("Erreur de chargement. Veuillez sélectionner manuellement un autre fichier.")
        csv_path = select_file_manually()
        if not csv_path:
            input("Erreur de chargement. Appuyez sur Entrée...")
            return

        df = load_data(csv_path)
        if df is None:
            input("Erreur de chargement. Appuyez sur Entrée...")
            return
 
    # ÉTAPE 3 : INTERACTION

    print("\nINSTRUCTIONS: Enter a date (YYYY-MM-DD) to see the prediction.")

    print("Type 'exit' to quit.")

    while True:

        user_input = input("\n>> Enter date (YYYY-MM-DD): ").strip()

        if user_input.lower() == 'exit':

            break

        try:

            date_obj = datetime.datetime.strptime(user_input, "%Y-%m-%d")

            analyze_risk(df, date_obj)

        except ValueError:

            print("Format invalide ! Utilisez YYYY-MM-DD (ex: 2025-08-14)")

        except Exception as e:

            print(f"Erreur: {e}")
 
if __name__ == "__main__":

    main()