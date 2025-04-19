# gestion_etudiants.py
import pandas as pd
import re
from datetime import datetime
from entite.etudiant import Etudiant

class GestionEtudiants:
    def __init__(self):
        self.etudiants = []
        self.etudiants_valides = []
        self.etudiants_invalides = []
    
    def charger_donnees_csv(self, chemin_fichier):
        """Charge les données depuis un fichier CSV"""
        try:
            df = pd.read_csv(chemin_fichier)
            for _, row in df.iterrows():
                etudiant = self._creer_etudiant_depuis_ligne(row)
                self.etudiants.append(etudiant)
            return True
        except Exception as e:
            print(f"Erreur lors du chargement des données: {str(e)}")
            return False
    
    def _creer_etudiant_depuis_ligne(self, row):
        """Crée un objet étudiant à partir d'une ligne du DataFrame"""
        notes = self._parser_notes(row['Note']) if 'Note' in row else {}
        
        etudiant = Etudiant(
            code=row.get('CODE'),
            numero=row.get('Numero'),
            nom=row.get('Nom'),
            prenom=row.get('Prenom'),
            date_naissance=row.get('Date de naissance'),
            classe=row.get('Classe'),
            notes=notes
        )
        
        # Calculer la moyenne générale
        etudiant.calculer_moyenne_generale()
        
        return etudiant
    
    def _parser_notes(self, notes_str):
        """Parse la chaîne de notes en structure de données"""
        notes_dict = {}
        matieres = notes_str.split('#')
        
        for matiere in matieres:
            matiere = matiere.strip()
            if not matiere:
                continue
                
            match = re.match(r'(\w+)\[(.*?)\]', matiere)
            if match:
                nom_matiere = match.group(1)
                valeurs = match.group(2)
                
                # Séparer les notes de devoirs et d'examen
                if ':' in valeurs:
                    devoirs, examen = valeurs.split(':')
                    notes_devoirs = [float(n) for n in devoirs.split('|')]
                    note_examen = float(examen)
                    
                    notes_dict[nom_matiere] = {
                        "notes_devoirs": notes_devoirs,
                        "note_examen": note_examen
                    }
        
        return notes_dict
    
    def valider_donnees(self):
        """Valide les données des étudiants"""
        self.etudiants_valides = []
        self.etudiants_invalides = []
        
        for etudiant in self.etudiants:
            if self._est_etudiant_valide(etudiant):
                self.etudiants_valides.append(etudiant)
            else:
                self.etudiants_invalides.append(etudiant)
    
    def _est_etudiant_valide(self, etudiant):
        """Vérifie si les données d'un étudiant sont valides"""
        # Vérification des champs obligatoires
        if not (etudiant.code and etudiant.numero and etudiant.nom and etudiant.prenom):
            return False
            
        # Vérification du format de date
        try:
            if etudiant.date_naissance:
                datetime.strptime(etudiant.date_naissance, '%d/%m/%y')
        except ValueError:
            return False
            
        # Vérification que chaque matière a au moins une note
        if not etudiant.notes:
            return False
            
        return True
    
    def rechercher_par_nom(self, nom):
        """Recherche des étudiants par nom"""
        resultats = []
        for etudiant in self.etudiants_valides:
            if etudiant.nom.lower() == nom.lower():
                resultats.append(etudiant)
        return resultats
    
    def trier_par_moyenne(self, ordre="descendant"):
        """Trie les étudiants par moyenne générale"""
        return sorted(
            self.etudiants_valides, 
            key=lambda e: e.moyenne_generale or 0, 
            reverse=(ordre.lower() == "descendant")
        )
    
    def trier_par_nom(self, ordre="ascendant"):
        """Trie les étudiants par nom"""
        return sorted(
            self.etudiants_valides, 
            key=lambda e: e.nom.lower(), 
            reverse=(ordre.lower() == "descendant")
        )
    
    def rechercher_par_classe(self, classe):
        """Recherche des étudiants par classe"""
        resultats = []
        for etudiant in self.etudiants_valides:
            if etudiant.classe and etudiant.classe.lower() == classe.lower():
                resultats.append(etudiant)
        return resultats
    
    def obtenir_statistiques(self):
        """Obtient des statistiques sur les données"""
        return {
            "total": len(self.etudiants),
            "valides": len(self.etudiants_valides),
            "invalides": len(self.etudiants_invalides)
        }