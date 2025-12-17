import sys
import datetime
 
# Bloc pour vérifier si pandas est installé
try:
    import pandas as pd
except ImportError:
    print("ERREUR CRITIQUE : La librairie 'pandas' n'est pas installée.")
    print("Veuillez ouvrir PowerShell et taper : pip install pandas openpyxl")
    input("\nAppuyez sur Entrée pour fermer...")
    sys.exit()
 
def load_data(filepath):
    try:
        # Tentative de chargement
        print(f"Chargement du fichier '{filepath}' en cours...")
        df = pd.read_csv(filepath)
        # Nettoyage et conversion des dates
        df['INCIDENT_DATE'] = pd.to_datetime(df['INCIDENT_DATE'])
        # Extraction de l'heure
        df['HOUR'] = pd.to_numeric(df['TIME'].astype(str).str[:2], errors='coerce')
        print("Fichier chargé avec succès !")
        return df
    except FileNotFoundError:
        print(f"\n[ERREUR] Le fichier '{filepath}' est introuvable.")
        print("Assurez-vous que le fichier CSV est bien dans le MEME dossier que ce script python.")
        return None
    except Exception as e:
        print(f"\n[ERREUR] Une erreur inattendue est survenue : {e}")
        return None
 
def analyze_risk(df, input_date):
    target_month = input_date.month
    month_name = input_date.strftime("%B")
    # Filtrer par mois
    monthly_data = df[df['INCIDENT_MONTH'] == target_month]
    if monthly_data.empty:
        print(f"\nNo historical data found for {month_name}. Cannot predict.")
        return
 
    total_incidents = len(monthly_data)
    # Calcul des stats (Météo, Heure, Avion, Espèce)
    def get_top_stat(column):
        if column not in df.columns: return "Unknown", 0
        stats = monthly_data[column].value_counts(normalize=True)
        if stats.empty: return "Unknown", 0
        return stats.index[0], stats.values[0] * 100
 
    top_sky, sky_prob = get_top_stat('SKY')
    top_tod, tod_prob = get_top_stat('TIME_OF_DAY')
    top_ac, ac_prob = get_top_stat('AIRCRAFT')
    top_phase, phase_prob = get_top_stat('PHASE_OF_FLIGHT')
    # Espèce (top 1)
    species_stats = monthly_data['SPECIES'].value_counts(normalize=True)
    top_species = species_stats.index[0] if not species_stats.empty else "Unknown"
 
    # Affichage du rapport
    print("\n" + "="*60)
    print(f"ANALYSIS REPORT FOR: {input_date.strftime('%Y-%m-%d')}")
    print(f"Context: {month_name} (based on {total_incidents} historical records)")
    print("="*60)
    print(f"\n1. METEOROLOGY (SKY)")
    print(f"   The data suggests that '{top_sky}' is the most common condition")
    print(f"   during strikes in this month ({sky_prob:.1f}% risk factor).")
    print(f"\n2. TIME & SCHEDULE")
    print(f"   Highest Risk Period: {top_tod} ({tod_prob:.1f}% of incidents).")
    print(f"\n3. AIRCRAFT & PHASE")
    print(f"   Be extra vigilant during: {top_phase} ({phase_prob:.1f}%).")
    print(f"   Most impacted aircraft type: {top_ac}.")
    print(f"\n4. WILDLIFE IDENTIFICATION")
    print(f"   Primary Species Threat: {top_species}")
    print("="*60 + "\n")
 
def main():
    # Nom exact du fichier
    FILE_NAME = 'Bird strike Miami CSV'
    df = load_data(FILE_NAME)
    if df is None:
        # On met une pause ici pour que l'utilisateur voie l'erreur
        input("\nAppuyez sur Entrée pour quitter le programme...")
        return
 
    print("\n********************************************************")
    print("      BIRD STRIKE PREDICTION AI (READY)      ")
    print("********************************************************")
    print("INSTRUCTIONS: Enter a date (YYYY-MM-DD) to generate a report.")
    print("Type 'exit' to quit.")
    while True:
        user_input = input("\n>> Enter date (YYYY-MM-DD): ").strip()
        if user_input.lower() == 'exit':
            break
        try:
            date_obj = datetime.datetime.strptime(user_input, "%Y-%m-%d")
            analyze_risk(df, date_obj)
        except ValueError:
            print("Format Error! Please use YYYY-MM-DD (ex: 2024-05-12)")
        except Exception as e:
            print(f"Error during analysis: {e}")
 
if __name__ == "__main__":
    main()