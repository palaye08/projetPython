import pandas as pd
from validator import Validator
from service import Service
from helper import Helper
from db_connexion import DbConnexion


class Application:
    def __init__(self):
        self.service = Service()
        self.helper = Helper()
    
    def lire_donnees_csv(self, chemin_fichier='donnees_eleves.csv'):
        """Lit les données depuis un fichier CSV"""
        try:
            df = pd.read_csv(chemin_fichier)
            print("Colonnes dans le fichier:", df.columns.tolist())
            return df
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier: {str(e)}")
            return None
    
    def executer_menu(self):
        """Gestion du menu principal"""
        while True:
            self.helper.afficher_menu()
            choix = input("\nEntrez votre choix (0-5): ")
            
            if choix == "0":
                print("Au revoir!")
                break
            
            elif choix == "1":
                type_info = input("Afficher les informations valides ou invalides? (V/I): ")
                self.service.afficher_informations(
                    "valide" if type_info.upper() == "V" else "invalide"
                )
            
            elif choix == "2":
                numero = input("Entrez le numéro à rechercher: ")
                self.service.rechercher_par_numero(numero)
            
            elif choix == "3":
                type_info = input("Afficher les 5 premiers éléments valides ou invalides? (V/I): ")
                self.service.afficher_cinq_premiers(
                    "valide" if type_info.upper() == "V" else "invalide"
                )
            
            elif choix == "4":
                self.service.ajouter_information()
            
            elif choix == "5":
                self.service.modifier_information_invalide()
            
            else:
                print("Choix invalide. Veuillez réessayer.")
    
    def demarrer(self):
        """Fonction principale pour démarrer l'application"""
        # Lecture des données
        df = self.lire_donnees_csv()
        if df is not None:
            # Validation des données
            self.service.valider_donnees(df)
            
            # Affichage des résultats initiaux
            self.helper.afficher_statistiques(self.service)
            
            # Lancement du menu
            self.executer_menu()

def main():
    app = Application()
    app.demarrer()

# if __name__ == "__main__":
#     main()

if __name__ == "__main__":
    # Votre chaîne de connexion MongoDB Atlas (à remplacer)
    conn_string = "mongodb+srv://palaye:<passer123>@cluster0.qcestsk.mongodb.net/"
    
    # Créer une instance de DbConnexion
    connexion = DbConnexion(connection_string=conn_string, db_name="gestion-etudiant")
    
    # Se connecter à la base de données
    db = connexion.toConnecte()
    
    if db:
        # Créer une collection pour les étudiants
        etudiants = db["etudiants"]
        
        # Insérer un document de test
        etudiant_test = {
            "nom": "Diop",
            "prenom": "Abdoulaye",
            "age": 20,
            "filiere": "Informatique"
        }
        
        resultat = etudiants.insert_one(etudiant_test)
        print(f"Document inséré avec l'ID: {resultat.inserted_id}")
    
    # Fermer la connexion
    connexion.fermer_connexion()

      # Test de connexion Redis
    print("\nTest de connexion à Redis...")
    from redis_connexion import RedisConnexion
    
    # Pour une connexion locale
    redis_conn = RedisConnexion(host="localhost", port=6379, db=0)
    # Pour une connexion distante (par exemple, Redis Cloud)
    # redis_conn = RedisConnexion(host="redis-xxxxx.c123.region.cloud.redislabs.com", 
    #                           port=15630, 
    #                           password="votre_mot_de_passe")
    
    redis_client = redis_conn.connect()
    if redis_client:
        # Tester les opérations Redis
        redis_conn.test_connexion()
        # Fermer la connexion
        redis_conn.fermer_connexion()
    
    # Démarrage de l'application
    print("\nDémarrage de l'application principale...")

    