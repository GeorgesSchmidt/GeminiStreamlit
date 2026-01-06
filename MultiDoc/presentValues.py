import pandas as pd
import matplotlib.pyplot as plt
import os
import math

def tracer_courbes_evolution_reelle(csv_path):
    try:
        # 1. Chargement et nettoyage
        df = pd.read_csv(csv_path, on_bad_lines='skip')
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        df['Valeur'] = pd.to_numeric(df['Valeur'].astype(str).str.replace(',', '.'), errors='coerce')
        
        # Suppression des lignes incomplètes
        df = df.dropna(subset=['Date', 'Valeur']).sort_values('Date')

        # 2. Filtrage : on ne garde que les paramètres ayant AU MOINS 2 points
        counts = df['Paramètre'].value_counts()
        parametres_valides = counts[counts >= 2].index.tolist()
        
        nb_params = len(parametres_valides)
        if nb_params == 0:
            print("Aucun paramètre ne possède assez de points (min. 2) pour tracer une courbe.")
            return

        print(f"📊 {nb_params} paramètres avec évolution trouvés. Génération des graphiques...")

        # 3. Configuration de la pagination (8 par page)
        params_par_page = 8
        nb_pages = math.ceil(nb_params / params_par_page)

        for page in range(nb_pages):
            plt.figure(figsize=(15, 20))
            
            start_idx = page * params_par_page
            end_idx = start_idx + params_par_page
            params_page = parametres_valides[start_idx:end_idx]

            for i, nom in enumerate(params_page, 1):
                plt.subplot(4, 2, i)
                
                # Extraction des données pour ce paramètre
                data_sub = df[df['Paramètre'] == nom]
                
                # Tracé de la courbe
                plt.plot(data_sub['Date'], data_sub['Valeur'], marker='o', color='#2ecc71', linewidth=2, markersize=8)
                plt.fill_between(data_sub['Date'], data_sub['Valeur'], color='#2ecc71', alpha=0.1)
                
                plt.title(f"Évolution : {nom}", fontsize=12, fontweight='bold')
                plt.grid(True, linestyle='--', alpha=0.5)
                plt.xticks(rotation=30, fontsize=8)
                
                # Gestion de l'unité
                unite = data_sub['Unité'].iloc[0] if 'Unité' in data_sub.columns else ""
                plt.ylabel(unite, fontsize=9)

            plt.tight_layout(pad=4.0)
            
            # Sauvegarde
            output_path = f"Resultats/bilan_evolution_page_{page + 1}.png"
            plt.savefig(output_path)
            print(f"✅ Page {page + 1} créée (Paramètres avec historique).")
            
        plt.show()

    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    tracer_courbes_evolution_reelle("Resultats/courbes_analyses.csv")