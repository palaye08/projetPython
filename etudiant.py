# etudiant.py
class Etudiant:
    def __init__(self, code=None, numero=None, nom=None, prenom=None, date_naissance=None, classe=None, notes=None):
        self.code = code
        self.numero = numero
        self.nom = nom
        self.prenom = prenom
        self.date_naissance = date_naissance
        self.classe = classe
        self.notes = notes if notes else {}
        self.moyenne_generale = None
    
    def calculer_moyenne_matiere(self, matiere):
        """Calcule la moyenne d'une matière spécifique"""
        if matiere not in self.notes:
            return 0
            
        notes_matiere = self.notes[matiere]
        if not notes_matiere:
            return 0
            
        somme = sum(notes_matiere["notes_devoirs"]) + notes_matiere["note_examen"]
        diviseur = len(notes_matiere["notes_devoirs"]) + 1
        return round(somme / diviseur, 2)
    
    def calculer_moyenne_generale(self):
        """Calcule la moyenne générale de l'étudiant"""
        if not self.notes:
            return 0
            
        somme_moyennes = 0
        for matiere in self.notes:
            somme_moyennes += self.calculer_moyenne_matiere(matiere)
            
        self.moyenne_generale = round(somme_moyennes / len(self.notes), 2)
        return self.moyenne_generale
    
    def to_dict(self):
        """Convertit l'objet étudiant en dictionnaire pour la sauvegarde"""
        return {
            "code": self.code,
            "numero": self.numero,
            "nom": self.nom,
            "prenom": self.prenom,
            "date_naissance": self.date_naissance,
            "classe": self.classe,
            "notes": self.notes,
            "moyenne_generale": self.moyenne_generale
        }
    
    @staticmethod
    def from_dict(data):
        """Crée un objet étudiant à partir d'un dictionnaire"""
        etudiant = Etudiant(
            code=data.get("code"),
            numero=data.get("numero"),
            nom=data.get("nom"),
            prenom=data.get("prenom"),
            date_naissance=data.get("date_naissance"),
            classe=data.get("classe"),
            notes=data.get("notes")
        )
        etudiant.moyenne_generale = data.get("moyenne_generale")
        return etudiant