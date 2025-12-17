import sys

import os

import datetime

import tkinter as tk

from tkinter import filedialog
 
# Check for required libraries

try:

    import pandas as pd

    import openpyxl # Necessary for reading Excel files

except ImportError as e:

    print(f"CRITICAL ERROR: Missing library. {e}")

    print("Please run: pip install pandas openpyxl")

    input("Press Enter to exit...")

    sys.exit()
 
def select_file_manually():

    """Opens a window to select the Excel file."""

    print("Opening file selection window...")

    # Create invisible root window

    root = tk.Tk()

    root.withdraw() 

    # Open file explorer filtered for Excel

    file_path = filedialog.askopenfilename(

        title="Select your Bird Strike Excel File",

        filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]

    )

    return file_path
 
def load_data(filepath):

    if not filepath:

        return None
 
    try:

        print(f"Loading file: {os.path.basename(filepath)}...")

        # CHANGED: Now using read_excel instead of read_csv

        df = pd.read_excel(filepath)

        # Standardize column names (optional, but good practice if headers possess spaces)

        df.columns = [c.strip() for c in df.columns]

        # Ensure DATE column is datetime objects

        # Adjust 'INCIDENT_DATE' if your column name is different

        df['INCIDENT_DATE'] = pd.to_datetime(df['INCIDENT_DATE'])

        # Extract hour from TIME column (assuming HH:MM format)

        df['HOUR'] = pd.to_numeric(df['TIME'].astype(str).str[:2], errors='coerce')

        print(" -> Data loaded successfully!")

        return df

    except Exception as e:

        print(f"\n[ERROR] Could not read the Excel file: {e}")

        return None
 
def analyze_risk(df, input_date):

    """

    Analyzes historical data for the specific month of the input_date.

    """

    target_month = input_date.month

    month_name = input_date.strftime("%B")

    # Filter data by month (Seasonal Analysis)

    monthly_data = df[df['INCIDENT_MONTH'] == target_month]

    if monthly_data.empty:

        print(f"\n[!] No historical data found for {month_name}. Cannot generate prediction.")

        return
 
    total_incidents = len(monthly_data)

    # Helper to get top statistic and its percentage

    def get_top_stat(column):

        if column not in df.columns: return "Unknown", 0

        stats = monthly_data[column].value_counts(normalize=True)

        if stats.empty: return "Unknown", 0

        return stats.index[0], stats.values[0] * 100
 
    # Calculate statistics

    top_sky, sky_prob = get_top_stat('SKY')

    top_tod, tod_prob = get_top_stat('TIME_OF_DAY')

    top_ac, ac_prob = get_top_stat('AIRCRAFT')

    top_phase, phase_prob = get_top_stat('PHASE_OF_FLIGHT')

    # Species logic

    species_stats = monthly_data['SPECIES'].value_counts(normalize=True)

    top_species = species_stats.index[0] if not species_stats.empty else "Unknown"
 
    # Generate Report in English

    print("\n" + "="*60)

    print(f"PREDICTION REPORT FOR: {input_date.strftime('%Y-%m-%d')}")

    print(f"Context: {month_name} (Analysis based on {total_incidents} past events)")

    print("="*60)

    print(f"\n1. METEOROLOGY (SKY)")

    print(f"   - Predicted Condition: {top_sky}")

    print(f"   - Confidence: {sky_prob:.1f}%")

    print(f"\n2. TIME & VISIBILITY")

    print(f"   - Time of Day Risk: {top_tod} ({tod_prob:.1f}% probability)")

    print(f"\n3. FLIGHT PARAMETERS")

    print(f"   - High Risk Phase: {top_phase} ({phase_prob:.1f}%)")

    print(f"   - Most Vulnerable Aircraft: {top_ac}")

    print(f"\n4. WILDLIFE THREAT")

    print(f"   - Primary Species: {top_species}")

    print("="*60 + "\n")
 
def main():

    print("\n********************************************************")

    print("      BIRD STRIKE PREDICTION AI (EXCEL VERSION)      ")

    print("********************************************************")

    print("Please select your .xlsx file in the popup window.")

    # 1. Select File

    excel_path = select_file_manually()

    if not excel_path:

        print("No file selected. Exiting system.")

        input("Press Enter to close...")

        return
 
    # 2. Load Data

    df = load_data(excel_path)

    if df is None:

        input("Fatal Error during loading. Press Enter to close...")

        return
 
    # 3. Main Loop

    print("\nSYSTEM READY.")

    print("INSTRUCTIONS: Enter a target date to generate a risk profile.")

    print("The AI will analyze past data for that specific time of year.")

    print("Type 'exit' to quit.")

    while True:

        user_input = input("\n>> Enter date (YYYY-MM-DD): ").strip()

        if user_input.lower() == 'exit':

            print("Shutting down. Goodbye.")

            break

        try:

            date_obj = datetime.datetime.strptime(user_input, "%Y-%m-%d")

            analyze_risk(df, date_obj)

        except ValueError:

            print("Invalid format! Please use YYYY-MM-DD (e.g., 2025-12-25)")

        except Exception as e:

            print(f"An error occurred: {e}")
 
if __name__ == "__main__":

    main()
 