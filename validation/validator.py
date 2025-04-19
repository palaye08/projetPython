import re
from datetime import datetime

class Validator:
    @staticmethod
    def est_numero_valide(numero):
        if not isinstance(numero, str):
            return False
        return len(numero) == 7 and bool(re.match(r'^[A-Z0-9]{7}$', str(numero)))
    
    @staticmethod
    def est_nom_valide(nom):
        if not isinstance(nom, str):
            return False
        return bool(re.match(r'^[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\- ]+$', nom))
    
    @staticmethod
    def est_prenom_valide(prenom):
        if not isinstance(prenom, str):
            return False
        return bool(re.match(r'^[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\- ]+$', prenom))
    
    @staticmethod
    def formater_date(date):
        try:
            if isinstance(date, str):
                # Gérer le format avec année à 2 chiffres
                if re.match(r'^\d{2}/\d{2}/\d{2}$', date):
                    date_obj = datetime.strptime(date, '%d/%m/%y')
                    return date_obj.strftime('%d/%m/%Y')
                formats = ['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%d.%m.%Y']
                for fmt in formats:
                    try:
                        date_obj = datetime.strptime(date, fmt)
                        return date_obj.strftime('%d/%m/%Y')
                    except:
                        continue
            elif isinstance(date, datetime):
                return date.strftime('%d/%m/%Y')
            return None
        except:
            return None
    
    @staticmethod
    def est_date_valide(date):
        return Validator.formater_date(date) is not None
    
    @staticmethod
    def formater_classe(classe):
        if not isinstance(classe, str):
            return None
        classe = classe.lower().replace(" ", "").replace("iem", "em")
        match = re.match(r'^([3-6])(em)([ab])$', classe)
        if match:
            niveau, em, lettre = match.groups()
            return f"{niveau}{em}{lettre.upper()}"
        return None
    
    @staticmethod
    def est_classe_valide(classe):
        return Validator.formater_classe(classe) is not None
    
    @staticmethod
    def est_note_valide(note):
        if not isinstance(note, str):
            return False
        matieres = note.split('#')
        # Pattern modifié pour accepter les notes avec | et :
        pattern = r'^[A-Za-z]+\[[\d\|\.:]+\]$'
        return all(re.match(pattern, matiere.strip()) for matiere in matieres)
    
    @staticmethod
    def valider_ligne(ligne):
        """Valide une ligne de données et retourne les erreurs trouvées"""
        erreurs = []
        if not Validator.est_numero_valide(ligne.get('Numero', '')):
            erreurs.append('Numero invalide')
        if not Validator.est_nom_valide(ligne.get('Nom', '')):
            erreurs.append('Nom invalide')
        # Vérifier les deux variantes possibles pour le prénom
        prenom = ligne.get('Prenom', ligne.get('Prénom', ''))
        if not Validator.est_prenom_valide(prenom):
            erreurs.append('Prenom invalide')
        # Vérifier la date de naissance
        date = ligne.get('Date de naissance', ligne.get('Date', ''))
        if not Validator.est_date_valide(date):
            erreurs.append('Date invalide')
        if not Validator.est_classe_valide(ligne.get('Classe', '')):
            erreurs.append('Classe invalide')
        if not Validator.est_note_valide(ligne.get('Note', '')):
            erreurs.append('Notes invalides')
        return erreurs