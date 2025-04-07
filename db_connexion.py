# Créez un fichier nommé db_connexion.py
import pymongo
from pymongo import MongoClient

class DbConnexion:
    def __init__(self, connection_string=None, db_name="gestion-etudiant"):
        self.connection_string = connection_string
        self.db_name = db_name
        self.client = None
        self.db = None
    
    def toConnecte(self):
        try:
            # Connexion à MongoDB Atlas avec la chaîne de connexion
            self.client = MongoClient(self.connection_string)
            # Créer/accéder à la base de données "gestion-etudiant"
            self.db = self.client[self.db_name]
            print(f"Connexion réussie à la base de données '{self.db_name}'")
            return self.db
        except Exception as e:
            print(f"Erreur de connexion à MongoDB: {e}")
            return None
    
    def fermer_connexion(self):
        if self.client:
            self.client.close()
            print("Connexion fermée")