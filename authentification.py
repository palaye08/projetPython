# authentification.py
import hashlib
import json
import os

class Authentification:
    def __init__(self, fichier_utilisateurs="utilisateurs.json"):
        self.fichier_utilisateurs = fichier_utilisateurs
        self.utilisateur_courant = None
        self.utilisateurs = self._charger_utilisateurs()
    
    def _charger_utilisateurs(self):
        """Charge les utilisateurs depuis le fichier JSON"""
        if os.path.exists(self.fichier_utilisateurs):
            try:
                with open(self.fichier_utilisateurs, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erreur lors du chargement des utilisateurs: {str(e)}")
                return {}
        return {}
    
    def _sauvegarder_utilisateurs(self):
        """Sauvegarde les utilisateurs dans le fichier JSON"""
        try:
            with open(self.fichier_utilisateurs, 'w') as f:
                json.dump(self.utilisateurs, f, indent=4)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des utilisateurs: {str(e)}")
            return False
    
    def _hasher_mot_de_passe(self, mot_de_passe):
        """Hashe le mot de passe pour le sécuriser"""
        return hashlib.sha256(mot_de_passe.encode()).hexdigest()
    
    def ajouter_utilisateur(self, username, mot_de_passe, role="user"):
        """Ajoute un nouvel utilisateur"""
        if username in self.utilisateurs:
            return False, "Nom d'utilisateur déjà existant."
            
        self.utilisateurs[username] = {
            "mot_de_passe": self._hasher_mot_de_passe(mot_de_passe),
            "role": role
        }
        
        return self._sauvegarder_utilisateurs(), "Utilisateur ajouté avec succès."
    
    def authentifier(self, username, mot_de_passe):
        """Authentifie un utilisateur"""
        if username not in self.utilisateurs:
            return False, "Nom d'utilisateur inexistant."
            
        if self.utilisateurs[username]["mot_de_passe"] != self._hasher_mot_de_passe(mot_de_passe):
            return False, "Mot de passe incorrect."
            
        self.utilisateur_courant = {
            "username": username,
            "role": self.utilisateurs[username]["role"]
        }
        
        return True, "Authentification réussie."
    
    def deconnecter(self):
        """Déconnecte l'utilisateur courant"""
        self.utilisateur_courant = None
        return True, "Déconnexion réussie."
    
    def est_authentifie(self):
        """Vérifie si un utilisateur est authentifié"""
        return self.utilisateur_courant is not None
    
    def a_permission(self, permission_requise):
        """Vérifie si l'utilisateur courant a une permission spécifique"""
        if not self.est_authentifie():
            return False
            
        # Définir les permissions par rôle
        permissions = {
            "admin": ["lire", "ecrire", "supprimer", "exporter", "importer"],
            "teacher": ["lire", "ecrire"],
            "user": ["lire"]
        }
        
        role = self.utilisateur_courant["role"]
        if role in permissions:
            return permission_requise in permissions[role]
            
        return False