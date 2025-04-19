# rapport_pdf.py
from fpdf import FPDF
import os
import matplotlib.pyplot as plt
from datetime import datetime

class RapportPDF:
    def __init__(self, gestion_etudiants):
        self.gestion_etudiants = gestion_etudiants
    
    def generer_rapport_individuel(self, etudiant, chemin_sortie):
        """Génère un rapport PDF pour un étudiant individuel"""
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # En-tête
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(190, 10, "Rapport de l'étudiant", 0, 1, 'C')
            pdf.ln(10)
            
            # Informations de l'étudiant
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(190, 10, "Informations personnelles:", 0, 1)
            
            pdf.set_font('Arial', '', 12)
            pdf.cell(50, 10, "Nom:", 0, 0)
            pdf.cell(140, 10, etudiant.nom, 0, 1)
            
            pdf.cell(50, 10, "Prénom:", 0, 0)
            pdf.cell(140, 10, etudiant.prenom, 0, 1)
            
            pdf.cell(50, 10, "Numéro:", 0, 0)
            pdf.cell(140, 10, etudiant.numero, 0, 1)
            
            pdf.cell(50, 10, "Date de naissance:", 0, 0)
            pdf.cell(140, 10, etudiant.date_naissance, 0, 1)
            
            pdf.cell(50, 10, "Classe:", 0, 0)
            pdf.cell(140, 10, etudiant.classe, 0, 1)
            
            pdf.ln(10)
            
            # Notes par matière
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(190, 10, "Notes par matière:", 0, 1)
            
            pdf.set_font('Arial', '', 12)
            for matiere, details in etudiant.notes.items():
                moyenne_matiere = etudiant.calculer_moyenne_matiere(matiere)
                
                pdf.cell(50, 10, f"{matiere}:", 0, 0)
                pdf.cell(140, 10, f"Devoirs: {', '.join(str(n) for n in details['notes_devoirs'])} - Examen: {details['note_examen']} - Moyenne: {moyenne_matiere}", 0, 1)
            
            pdf.ln(10)
            
            # Moyenne générale
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(50, 10, "Moyenne générale:", 0, 0)
            pdf.cell(140, 10, str(etudiant.moyenne_generale), 0, 1)
            
            # Pied de page
            pdf.set_y(-30)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0, 10, f"Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", 0, 0, 'C')
            
            # Enregistrer le PDF
            pdf.output(chemin_sortie)
            
            return True, f"Rapport généré avec succès: {chemin_sortie}"
            
        except Exception as e:
            return False, f"Erreur lors de la génération du rapport: {str(e)}"
    
    def generer_rapport_classe(self, classe, chemin_sortie):
        """Génère un rapport PDF pour une classe entière"""
        try:
            # Récupérer les étudiants de la classe
            etudiants_classe = self.gestion_etudiants.rechercher_par_classe(classe)
            
            if not etudiants_classe:
                return False, f"Aucun étudiant trouvé dans la classe {classe}"
            
            # Générer un graphique des moyennes
            self._generer_graphique_moyennes(etudiants_classe, "temp_graph.png")
            
            pdf = FPDF()
            pdf.add_page()
            
            # En-tête
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(190, 10, f"Rapport de la classe {classe}", 0, 1, 'C')
            pdf.ln(10)
            
            # Liste des étudiants
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(190, 10, "Liste des étudiants:", 0, 1)
            
            pdf.set_font('Arial', '', 10)
            
            # En-tête du tableau
            pdf.cell(60, 10, "Nom", 1, 0, 'C')
            pdf.cell(60, 10, "Prénom", 1, 0, 'C')
            pdf.cell(70, 10, "Moyenne générale", 1, 1, 'C')
            
            # Données du tableau
            for etudiant in sorted(etudiants_classe, key=lambda e: e.moyenne_generale or 0, reverse=True):
                pdf.cell(60, 10, etudiant.nom, 1, 0)
                pdf.cell(60, 10, etudiant.prenom, 1, 0)
                pdf.cell(70, 10, str(etudiant.moyenne_generale), 1, 1, 'C')
            
            pdf.ln(10)
            
            # Statistiques
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(190, 10, "Statistiques:", 0, 1)
            
            pdf.set_font('Arial', '', 12)
            moyenne_classe = sum(e.moyenne_generale or 0 for e in etudiants_classe) / len(etudiants_classe)
            pdf.cell(90, 10, "Moyenne de la classe:", 0, 0)
            pdf.cell(100, 10, f"{round(moyenne_classe, 2)}", 0, 1)
            
            # Ajouter le graphique
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(190, 10, "Graphique des moyennes:", 0, 1)
            pdf.image("temp_graph.png", x=10, y=None, w=190)
            
            # Supprimer le fichier temporaire
            os.remove("temp_graph.png")
            
            # Pied de page
            pdf.set_y(-30)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0, 10, f"Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", 0, 0, 'C')
            
            # Enregistrer le PDF
            pdf.output(chemin_sortie)
            
            return True, f"Rapport de classe généré avec succès: {chemin_sortie}"
            
        except Exception as e:
            # Nettoyer en cas d'erreur
            if os.path.exists("temp_graph.png"):
                os.remove("temp_graph.png")
                
            return False, f"Erreur lors de la génération du rapport: {str(e)}"
    
    def _generer_graphique_moyennes(self, etudiants, chemin_sortie):
        """Génère un graphique des moyennes des étudiants"""
        # Trier les étudiants par moyenne
        etudiants = sorted(etudiants, key=lambda e: e.moyenne_generale or 0, reverse=True)
        
        # Limiter à 10 étudiants pour la lisibilité
        if len(etudiants) > 10:
            etudiants = etudiants[:10]
        
        noms = [f"{e.nom} {e.prenom}" for e in etudiants]
        moyennes = [e.moyenne_generale or 0 for e in etudiants]
        
        # Créer le graphique
        plt.figure(figsize=(10, 6))
        plt.bar(noms, moyennes, color='skyblue')
        plt.xlabel('Étudiants')
        plt.ylabel('Moyenne générale')
        plt.title('Moyennes générales des étudiants')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Enregistrer le graphique
        plt.savefig(chemin_sortie)
        plt.close()