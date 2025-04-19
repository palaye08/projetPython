# export_import.py
import pandas as pd
import json
import csv
import os
from etudiant import Etudiant

class ExportImport:
    def __init__(self, gestion_etudiants):
        self.gestion_etudiants = gestion_etudiants
    
    def exporter_csv(self, chemin_fichier):
        """Exporte les données des étudiants au format CSV"""
        try:
            # Préparer les données
            donnees = []
            for etudiant in self.gestion_etudiants.etudiants_valides:
                notes_str = self._formater_notes_pour_export(etudiant.notes)
                
                donnees.append({
                    "CODE": etudiant.code,
                    "Numero": etudiant.numero,
                    "Nom": etudiant.nom,
                    "Prenom": etudiant.prenom,
                    "Date de naissance": etudiant.date_naissance,
                    "Classe": etudiant.classe,
                    "Note": notes_str,
                    "Moyenne Generale": etudiant.moyenne_generale
                })
            
            # Créer et enregistrer le DataFrame
            df = pd.DataFrame(donnees)
            df.to_csv(chemin_fichier, index=False)
            return True, f"Données exportées avec succès vers {chemin_fichier}"
            
        except Exception as e:
            return False, f"Erreur lors de l'exportation: {str(e)}"
    
    def exporter_json(self, chemin_fichier):
        """Exporte les données des étudiants au format JSON"""
        try:
            # Préparer les données
            donnees = []
            for etudiant in self.gestion_etudiants.etudiants_valides:
                donnees.append(etudiant.to_dict())
            
            # Enregistrer en JSON
            with open(chemin_fichier, 'w') as f:
                json.dump(donnees, f, indent=4)
                
            return True, f"Données exportées avec succès vers {chemin_fichier}"
            
        except Exception as e:
            return False, f"Erreur lors de l'exportation: {str(e)}"
    
    def importer_csv(self, chemin_fichier):
        """Importe les données des étudiants depuis un fichier CSV"""
        try:
            # Réinitialiser les données actuelles
            self.gestion_etudiants.etudiants = []
            
            # Charger le nouveau fichier
            resultat = self.gestion_etudiants.charger_donnees_csv(chemin_fichier)
            
            if resultat:
                # Valider les données importées
                self.gestion_etudiants.valider_donnees()
                return True, f"Données importées avec succès depuis {chemin_fichier}"
            else:
                return False, "Erreur lors de l'importation des données"
                
        except Exception as e:
            return False, f"Erreur lors de l'importation: {str(e)}"
    
    def importer_json(self, chemin_fichier):
        """Importe les données des étudiants depuis un fichier JSON"""
        try:
            # Réinitialiser les données actuelles
            self.gestion_etudiants.etudiants = []
            
            # Charger le fichier JSON
            with open(chemin_fichier, 'r') as f:
                donnees = json.load(f)
            
            # Convertir en objets Etudiant
            for donnee in donnees:
                etudiant = Etudiant.from_dict(donnee)
                self.gestion_etudiants.etudiants.append(etudiant)
            
            # Valider les données
            self.gestion_etudiants.valider_donnees()
            
            return True, f"Données importées avec succès depuis {chemin_fichier}"
            
        except Exception as e:
            return False, f"Erreur lors de l'importation: {str(e)}"
    
    def _formater_notes_pour_export(self, notes):
        """Formate les notes pour l'exportation CSV"""
        notes_str = []
        for matiere, details in notes.items():
            notes_devoirs_str = "|".join(str(note) for note in details["notes_devoirs"])
            note_str = f"{matiere}[{notes_devoirs_str}:{details['note_examen']}]"
            notes_str.append(note_str)
        
        return " #".join(notes_str)