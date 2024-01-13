import os
import re
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
try:
    import folium
except:
    !pip install folium

# Nota: Pour utiliser ce script : placer ce script dans un répertoire. Créer à côté de ce fichier, un répertoire nommé a_traiter. Placer un ou plusieurs fichiers .fit dans le répertoire a_traiter. Lancer le script.

# Fonctions
# Chmod all files in a repository
def chmod_all_files(repertoire):
    try:
        os.system(f"chmod 644 {repertoire}/*")
    except:
        print("[!] Error : cannot change right policy for a file [!]")
        print(f"Concerned file: {repertoire}/{fichier}")
        os.system(f"echo 'Current policy: '; ls -l {repertoire}/{fichier}")
        os.system("New policy wished: 644 (rw-r--r--)\n")
        
def analyse(fichier_nom, fichier_date):
    # Lecture du fichier fit
    f = open(f"resultats/{fichier_nom}_{fichier_date}/{fichier_nom}.json", "r")
    contenu_brut = f.readlines()
    f.close()
    # Nettoyage des données
    x = []
    for ligne in contenu_brut:
        ligne = ligne.replace("\t", "")
        ligne = ligne.replace('"', '')
        x.append(ligne.replace("\n", ""))

    # Parsing des données lues
    timestamp_raw = []
    temperatures_raw = []
    speed_raw = []
    latitude_raw = []
    longitude_raw = []
    altitude_raw = []
    distance_raw = []

    timestamp_odd = 0
    for num_ligne in range(len(x)):
        if (x[num_ligne] == "name: timestamp,"):
            try:
                if (x[num_ligne + 1][0:7] == "value: " and (timestamp_odd % 2 != 1)):
                    date_tmp = x[num_ligne + 1][7:-7]
                    heure = date_tmp[-8:]
                    année = date_tmp[0:4]
                    jour = date_tmp[5:7]
                    mois = date_tmp[8:10]
                    timestamp_raw.append(f"{jour}/{mois}/{année}-{heure}")
                else:
                    pass
            except:
                pass
            timestamp_odd += 1
        elif (x[num_ligne] == "name: temperature,"):
            try:
                if (x[num_ligne + 1][0:7] == "value: "):
                    tmp_temp = x[num_ligne + 1][7:].replace(",", "")
                    try:
                        temperatures_raw.append(int(tmp_temp))
                    except:
                        temperatures_raw.append(tmp_temp)
                else:
                    pass
            except:
                pass
        elif (x[num_ligne] == "name: speed,"):
            try:
                if (x[num_ligne + 1][0:7] == "value: "):
                    try:
                        speed_tmp = x[num_ligne + 1][7:].replace(",", "")
                        speed_raw.append(float(speed_tmp))
                    except:
                        pass
                else:
                    pass
            except:
                pass
        elif (x[num_ligne] == "name: position_lat,"):
            try:
                if (x[num_ligne + 1][0:7] == "value: "):
                    try:
                        lat_tmp = x[num_ligne + 1][7:-1]
                        latitude_raw.append(float(lat_tmp))
                    except:
                        pass
                else:
                    pass
            except:
                pass
        elif (x[num_ligne] == "name: position_long,"):
            try:
                if (x[num_ligne + 1][0:7] == "value: "):
                    try:
                        long_tmp = x[num_ligne + 1][7:-1]
                        longitude_raw.append(float(long_tmp))
                    except:
                        pass
                else:
                    pass
            except:
                pass
        elif (x[num_ligne] == "name: altitude,"):
            try:
                if (x[num_ligne + 1][0:7] == "value: "):
                    try:
                        altitude_tmp = x[num_ligne + 1][7:-1]
                        altitude_raw.append(float(altitude_tmp))
                    except:
                        pass
                else:
                    pass
            except:
                pass
        elif (x[num_ligne] == "name: distance,"):
            try:
                if (x[num_ligne + 1][0:7] == "value: "):
                    try:
                        distance_tmp = x[num_ligne + 1][7:-1]
                        distance_raw.append(float(distance_tmp))
                    except:
                        pass
                    else:
                        pass
            except:
                pass
        else:
            pass

    # Fonctions de post exploitation des données parsées
    def ecart_dates_minutes(mini, maxi):
        maxi = maxi[-8:]
        mini = mini[-8:]
        maxi_h = float(maxi[0:2]) * 60
        mini_h = float(mini[0:2]) * 60
        maxi_m = float(maxi[3:5])
        mini_m = float(mini[3:5])
        maxi_s = float(maxi[6:8]) / 60
        mini_s = float(mini[6:8]) / 60
        maxi_agrégation = maxi_h + maxi_m + maxi_s
        mini_agrégation = mini_h + mini_m + mini_s
        durée = abs(maxi_agrégation - mini_agrégation)
        return round(durée, 2)  # Convertir en hh/mm/ss

    def max_value(x):
        try:
            maxi = x[0]
        except:
            maxi = 0
        for i in x:
            if (i > maxi):
                maxi = i
            else:
                pass
        return maxi
    
    def min_value(x):
        try:
            mini = x[0]
        except:
            mini = 100000
        for i in x:
            if (i < mini):
                mini = i
            else:
                pass
        return mini

    # Calcul de valeurs clées en utilisant les fonctions de calculs
    durée_minutes = ecart_dates_minutes(timestamp_raw[0], timestamp_raw[len(timestamp_raw) - 1])
    heure_min = timestamp_raw[0]
    heure_max = timestamp_raw[len(timestamp_raw) - 1]
    durée_heures = durée_minutes / 60
    distance_totale_km = round(distance_raw[len(distance_raw) - 1], 2)
    distance_totale_m = round(distance_totale_km * 1000, 2)
    vitesse_moyenne = distance_totale_km / (durée_minutes / 60)
    vitesse_max = max_value(speed_raw)
    altitude_max = round(max_value(altitude_raw), 2)
    altitude_min = round(min_value(altitude_raw), 2)
    temperature_moyenne = round(np.mean(temperatures_raw), 2)
    temperature_min = min_value(temperatures_raw)
    temperature_max = max_value(temperatures_raw)
    total_ascention_tmp = abs(altitude_max - altitude_min)
    total_ascention = round(total_ascention_tmp, 2)

    # Création de la carte avec Folium
    carte = folium.Map(location=[49.032316511710704, 2.3412509868576286], zoom_start=12)
    folium.Marker(location=[latitude_raw[0], longitude_raw[0]], icon=folium.Icon(color="green")).add_to(carte)
    for i in range(1, len(latitude_raw)-2):
        folium.Marker(location=[latitude_raw[i], longitude_raw[i]], icon=folium.Icon(color="blue")).add_to(carte)
    folium.Marker(location=[latitude_raw[len(latitude_raw)-1], longitude_raw[len(longitude_raw)-1]], icon=folium.Icon(color="red")).add_to(carte)
    carte.save(f"resultats/{fichier_nom}_{fichier_date}/{fichier_nom}_map.html")
    
    # Affichage de statistiques lors de l'exécution du code
    print(f"Vitesse moyenne: {round(vitesse_moyenne, 2)}km/h")
    print(f"Vitesse max: {vitesse_max}km/h")
    print(f"Altitude moyenne: km/h")
    print(f"Altitude min: {altitude_min}m")
    print(f"Altitude max: {altitude_max}m")
    print(f"Température moyenne: {temperature_moyenne}")
    print(f"Température min: {temperature_min}")
    print(f"Température max: {temperature_max}")
    print(f"Total ascention: {total_ascention}")
    print(f"Distance: {distance_totale_m}m")
    print(f"Distance: {distance_totale_km}km")
    print(f"Durée: {durée_minutes}min")
    print(f"Heure début: {heure_min}")
    print(f"Heure fin: {heure_max}")

    # Enregistrement du résultat de l'exécution du programme
    f = open(f"resultats/{fichier_nom}_{fichier_date}/{fichier_nom}_resultat_analyse.txt", "a")
    f.write("Heure de départ;Heure d'arrivée;Durée;Distance parcourue (m);Distance parcourue (km);Vitesse moyenne;Vitesse max;Lieu arrivée;Lieu Départ;Altitude min;Altitude max;Température min;Température max;Température moyenne\n")
    f.write(f"{heure_min};{heure_max};{durée_minutes};{distance_totale_m};{distance_totale_km};{vitesse_moyenne};{vitesse_max};Lieu inconnu;lieu inconnu;{altitude_min};{altitude_max};{temperature_min};{temperature_max};{temperature_moyenne}\n")
    f.close()
    
    # Création d'un CSV avec toutes les données du trajet
    f = open(f"resultats/{fichier_nom}_{fichier_date}/{fichier_nom}_dataframe.csv", "a")
    f.write("Indice;Heure;Distance;Vitesse;Température;Altitude;Latitude;Longitude\n")
    for i in range(0, len(altitude_raw)):
        f.write(f"{i};")
        try:
            f.write(f"{timestamp_raw[i]};")
        except:
            f.write(f"NaN;")
        try:
            f.write(f"{distance_raw[i]};")
        except:
            f.write(f"NaN;")
        try:
            f.write(f"{speed_raw[i]};")
        except:
            f.write(f"NaN;")
        try:
            f.write(f"{temperatures_raw[i]};")
        except:
            f.write(f"NaN;")
        try:
            f.write(f"{altitude_raw[i]};")
        except:
            f.write(f"NaN;")
        try:
            f.write(f"{latitude_raw[i]};")
        except:
            f.write(f"NaN;")
        try:
            f.write(f"{longitude_raw[i]}\n")
        except:
            f.write(f"NaN\n")
    f.close()

        
def treatment(fichier, date_actuelle):
    # Gestion des emplacements de fichiers
    payload_nom_fichier = fichier[10:-4]
    os.system(f"mkdir resultats/{payload_nom_fichier}_{date_actuelle}")
    
    try:
        os.system(f"fitjson --pretty -o resultats/{payload_nom_fichier}_{date_actuelle}/{payload_nom_fichier}.json a_traiter/{payload_nom_fichier}.fit")
        print(f"[+] Le fichier {payload_nom_fichier} a bien été décodé du format fit !")
        analyse(payload_nom_fichier, date_actuelle)

    except:
        print(f"[!] Erreur lors du décodage du fichier {payload_nom_fichier} !")    

        
# Code principal
# On fournis les bons droits aux fichiers à traiter pour pouvoir les travailler
chmod_all_files("a_traiter")

# On crée ensuite un annuaire des fichiers qui sont à traiter
os.system(f"ls a_traiter/????????????.fit > .fichiers.log")
# On lit ensuite cet annuaire pour le récupérer sous forme de liste exploitable
f = open(".fichiers.log", "r")
contenu_brut = f.readlines()
f.close()
os.system("rm .fichiers.log")
noms_fichiers = []
# Nettoyage des noms de fichiers
for i in contenu_brut:
    if(len(i) > 4):
        noms_fichiers.append(i.replace("\n", ""))
    else:
        pass

# Définition d'un timestamp qui servira à lancer plusieurs exécutions sur un même fichier sans que ce soit bloquant
now = datetime.now()
date_now = now.strftime("%Y%m%d_%H%M%S")

# Création du répertoire de sortie si besoin
if (os.path.exists("resultats") == False):
    print(f"[+] Le répertoire <resultats> va être créé !")
    os.system("mkdir resultats")
else:
    pass

# Lancement du traitement des fichiers
for i in noms_fichiers:
    print(f"[+] Traitement du fichier {i}")
    treatment(i, date_now)
    print("---\n")
    
