# main.py
import pandas as pd
from validator import Validator
from service import Service
from helper import Helper
from db_connexion import DbConnexion
from redis_connexion import RedisConnexion
from gestion_etudiants import GestionEtudiants
from authentification import Authentification
from cache_redis import CacheRedis
from export_import import ExportImport
from rapport_pdf import RapportPDF
from etudiant import Etudiant


class Application:
    def __init__(self):
        self.service = Service()
        self.helper = Helper()
        self.gestion_etudiants = GestionEtudiants()
        self.authentification = Authentification()
        self.redis_client = None
        self.cache = None
        self.export_import = None
        self.rapport_pdf = None
    
    def initialiser_redis(self, host="localhost", port=6379, password=None, db=0):
        """Initialise la connexion Redis et le cache"""
        redis_conn = RedisConnexion(host=host, port=port, password=password, db=db)
        self.redis_client = redis_conn.connect()
        
        if self.redis_client:
            self.cache = CacheRedis(self.redis_client)
            return True
        return False
    
    def initialiser_services(self):
        """Initialise les services dépendants"""
        if self.gestion_etudiants:
            self.export_import = ExportImport(self.gestion_etudiants)
            self.rapport_pdf = RapportPDF(self.gestion_etudiants)
    
    def lire_donnees_csv(self, chemin_fichier='donnees_eleves.csv'):
        """Lit les données depuis un fichier CSV"""
        try:
            # Vérifier si les données sont en cache
            if self.cache:
                donnees_cache = self.cache.recuperer_du_cache("donnees_eleves")
                if donnees_cache:
                    print("Données récupérées depuis le cache.")
                    self.gestion_etudiants.etudiants = donnees_cache
                    self.gestion_etudiants.valider_donnees()
                    return True
            
            # Si pas en cache, charger depuis le fichier
            df = pd.read_csv(chemin_fichier)
            print("Colonnes dans le fichier:", df.columns.tolist())
            
            # Charger les données dans la gestion d'étudiants
            resultat = self.gestion_etudiants.charger_donnees_csv(chemin_fichier)
            
            if resultat:
                self.gestion_etudiants.valider_donnees()
                
                # Mettre en cache si possible
                if self.cache:
                    self.cache.mettre_en_cache("donnees_eleves", self.gestion_etudiants.etudiants)
                    
                return True
                
            return False
            
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier: {str(e)}")
            return False
    
    def executer_menu(self):
        """Gestion du menu principal"""
        # Vérifier l'authentification
        if not self._authentifier_utilisateur():
            return
        
        while True:
            self._afficher_menu_principal()
            choix = input("\nEntrez votre choix: ")
            
            if choix == "0":
                print("Au revoir!")
                self.authentification.deconnecter()
                break
            
            elif choix == "1":
                self._menu_recherche_tri()
                
            elif choix == "2":
                self._menu_gestion_donnees()
                
            elif choix == "3":
                self._menu_rapports()
                
            elif choix == "4":
                self._menu_admin()
            
            elif choix == "5":
                type_info = input("Afficher les informations valides ou invalides? (V/I): ")
                self.service.afficher_informations(
                    "valide" if type_info.upper() == "V" else "invalide"
                )
            
            elif choix == "6":
                numero = input("Entrez le numéro à rechercher: ")
                self.service.rechercher_par_numero(numero)
            
            elif choix == "7":
                type_info = input("Afficher les 5 premiers éléments valides ou invalides? (V/I): ")
                self.service.afficher_cinq_premiers(
                    "valide" if type_info.upper() == "V" else "invalide"
                )
            
            elif choix == "8":
                self.service.ajouter_information()
            
            elif choix == "9":
                self.service.modifier_information_invalide()
                
            else:
                print("Choix invalide. Veuillez réessayer.")
    
    def _authentifier_utilisateur(self):
        """Authentifie l'utilisateur"""
        # Vérifier si déjà authentifié
        if self.authentification.est_authentifie():
            return True
        
        print("\n=== Authentification ===")
        
        # Si aucun utilisateur n'existe, créer un administrateur par défaut
        if not self.authentification.utilisateurs:
            print("Aucun utilisateur trouvé. Création d'un compte administrateur...")
            self.authentification.ajouter_utilisateur("admin", "admin123", "admin")
            print("Compte admin créé. Utilisateur: admin, Mot de passe: admin123")
        
        # Authentification
        max_tentatives = 3
        for tentative in range(max_tentatives):
            username = input("Nom d'utilisateur: ")
            mot_de_passe = input("Mot de passe: ")
            
            succes, message = self.authentification.authentifier(username, mot_de_passe)
            print(message)
            
            if succes:
                return True
            
            if tentative < max_tentatives - 1:
                print(f"Tentatives restantes: {max_tentatives - tentative - 1}")
        
        print("Nombre maximum de tentatives atteint. Fermeture de l'application.")
        return False
    
    def _afficher_menu_principal(self):
        """Affiche le menu principal"""
        print("\n=== Menu Principal ===")
        print("1. Recherche et tri des étudiants")
        print("2. Gestion des données (Export/Import)")
        print("3. Rapports et moyennes")
        
        # Afficher l'option admin si l'utilisateur a les droits
        if self.authentification.a_permission("supprimer"):
            print("4. Administration")
        
        # Options originales du menu
        print("5. Afficher les informations (valides/invalides)")
        print("6. Rechercher par numéro")
        print("7. Afficher les 5 premiers éléments")
        print("8. Ajouter une information")
        print("9. Modifier une information invalide")
        print("0. Quitter")
    
    def _menu_recherche_tri(self):
        """Menu de recherche et tri des étudiants"""
        while True:
            print("\n=== Recherche et Tri ===")
            print("1. Rechercher par nom")
            print("2. Rechercher par classe")
            print("3. Trier par nom")
            print("4. Trier par moyenne")
            print("0. Retour au menu principal")
            
            choix = input("\nEntrez votre choix: ")
            
            if choix == "0":
                break
                
            elif choix == "1":
                nom = input("Entrez le nom à rechercher: ")
                resultats = self.gestion_etudiants.rechercher_par_nom(nom)
                self._afficher_resultats(resultats)
                
            elif choix == "2":
                classe = input("Entrez la classe à rechercher: ")
                resultats = self.gestion_etudiants.rechercher_par_classe(classe)
                self._afficher_resultats(resultats)
                
            elif choix == "3":
                ordre = input("Ordre (A)scendant ou (D)escendant? ").upper()
                etudiants_tries = self.gestion_etudiants.trier_par_nom(
                    "descendant" if ordre == "D" else "ascendant"
                )
                self._afficher_resultats(etudiants_tries)
                
            elif choix == "4":
                ordre = input("Ordre (A)scendant ou (D)escendant? ").upper()
                etudiants_tries = self.gestion_etudiants.trier_par_moyenne(
                    "ascendant" if ordre == "A" else "descendant"
                )
                self._afficher_resultats(etudiants_tries)
                
            else:
                print("Choix invalide. Veuillez réessayer.")
    
    def _menu_gestion_donnees(self):
        """Menu de gestion des données"""
        while True:
            print("\n=== Gestion des Données ===")
            print("1. Exporter les données (CSV)")
            print("2. Exporter les données (JSON)")
            print("3. Importer des données (CSV)")
            print("4. Importer des données (JSON)")
            print("0. Retour au menu principal")
            
            choix = input("\nEntrez votre choix: ")
            
            if choix == "0":
                break
                
            elif choix == "1":
                if not self.authentification.a_permission("exporter"):
                    print("Vous n'avez pas les permissions nécessaires.")
                    continue
                    
                chemin = input("Entrez le chemin du fichier d'exportation (CSV): ")
                succes, message = self.export_import.exporter_csv(chemin)
                print(message)
                
            elif choix == "2":
                if not self.authentification.a_permission("exporter"):
                    print("Vous n'avez pas les permissions nécessaires.")
                    continue
                    
                chemin = input("Entrez le chemin du fichier d'exportation (JSON): ")
                succes, message = self.export_import.exporter_json(chemin)
                print(message)
                
            elif choix == "3":
                if not self.authentification.a_permission("importer"):
                    print("Vous n'avez pas les permissions nécessaires.")
                    continue
                    
                chemin = input("Entrez le chemin du fichier d'importation (CSV): ")
                succes, message = self.export_import.importer_csv(chemin)
                print(message)
                
                # Mettre à jour le cache si nécessaire
                if succes and self.cache:
                    self.cache.mettre_en_cache("donnees_eleves", self.gestion_etudiants.etudiants)
                
            elif choix == "4":
                if not self.authentification.a_permission("importer"):
                    print("Vous n'avez pas les permissions nécessaires.")
                    continue
                    
                chemin = input("Entrez le chemin du fichier d'importation (JSON): ")
                succes, message = self.export_import.importer_json(chemin)
                print(message)
                
                # Mettre à jour le cache si nécessaire
                if succes and self.cache:
                    self.cache.mettre_en_cache("donnees_eleves", self.gestion_etudiants.etudiants)
                
            else:
                print("Choix invalide. Veuillez réessayer.")
    
    def _menu_rapports(self):
        """Menu des rapports et calcul des moyennes"""
        while True:
            print("\n=== Rapports et Moyennes ===")
            print("1. Afficher les moyennes par étudiant")
            print("2. Générer un rapport PDF pour un étudiant")
            print("3. Générer un rapport PDF pour une classe")
            print("0. Retour au menu principal")
            
            choix = input("\nEntrez votre choix: ")
            
            if choix == "0":
                break
                
            elif choix == "1":
                # Affichage des moyennes pour tous les étudiants
                etudiants_tries = self.gestion_etudiants.trier_par_moyenne()
                print("\n=== Moyennes Générales ===")
                for i, etudiant in enumerate(etudiants_tries, 1):
                    print(f"{i}. {etudiant.nom} {etudiant.prenom} ({etudiant.classe}): {etudiant.moyenne_generale}")
                
            elif choix == "2":
                # Générer un rapport pour un étudiant spécifique
                nom = input("Entrez le nom de l'étudiant: ")
                resultats = self.gestion_etudiants.rechercher_par_nom(nom)
                
                if not resultats:
                    print(f"Aucun étudiant trouvé avec le nom '{nom}'.")
                    continue
                
                # Si plusieurs étudiants, demander de choisir
                if len(resultats) > 1:
                    print("Plusieurs étudiants trouvés:")
                    for i, etudiant in enumerate(resultats, 1):
                        print(f"{i}. {etudiant.nom} {etudiant.prenom} ({etudiant.classe})")
                    
                    choix_etudiant = input("Choisissez un étudiant (numéro): ")
                    try:
                        index = int(choix_etudiant) - 1
                        if index < 0 or index >= len(resultats):
                            print("Choix invalide.")
                            continue
                            
                        etudiant = resultats[index]
                    except ValueError:
                        print("Entrée invalide.")
                        continue
                else:
                    etudiant = resultats[0]
                
                # Générer le rapport
                chemin = input("Entrez le chemin du fichier PDF à générer: ")
                succes, message = self.rapport_pdf.generer_rapport_individuel(etudiant, chemin)
                print(message)
                
            elif choix == "3":
                # Générer un rapport pour une classe
                classe = input("Entrez la classe: ")
                chemin = input("Entrez le chemin du fichier PDF à générer: ")
                succes, message = self.rapport_pdf.generer_rapport_classe(classe, chemin)
                print(message)
                
            else:
                print("Choix invalide. Veuillez réessayer.")
    
    def _menu_admin(self):
        """Menu d'administration"""
        # Vérifier les permissions
        if not self.authentification.a_permission("supprimer"):
            print("Vous n'avez pas les permissions nécessaires.")
            return
            
        while True:
            print("\n=== Administration ===")
            print("1. Gérer les utilisateurs")
            print("2. Vider le cache Redis")
            print("0. Retour au menu principal")
            
            choix = input("\nEntrez votre choix: ")
            
            if choix == "0":
                break
                
            elif choix == "1":
                self._gerer_utilisateurs()
                
            elif choix == "2":
                if self.cache:
                    succes = self.cache.vider_cache()
                    print("Cache vidé avec succès." if succes else "Erreur lors du vidage du cache.")
                else:
                    print("Le cache Redis n'est pas initialisé.")
                
            else:
                print("Choix invalide. Veuillez réessayer.")
    
    def _gerer_utilisateurs(self):
        """Gestion des utilisateurs"""
        while True:
            print("\n=== Gestion des Utilisateurs ===")
            print("1. Ajouter un utilisateur")
            print("2. Lister les utilisateurs")
            print("0. Retour")
            
            choix = input("\nEntrez votre choix: ")
            
            if choix == "0":
                break
                
            elif choix == "1":
                username = input("Nom d'utilisateur: ")
                mot_de_passe = input("Mot de passe: ")
                
                print("Rôles disponibles:")
                print("1. Administrateur (admin)")
                print("2. Enseignant (teacher)")
                print("3. Utilisateur (user)")
                
                choix_role = input("Choisissez un rôle (1-3): ")
                role = {
                    "1": "admin",
                    "2": "teacher",
                    "3": "user"
                }.get(choix_role, "user")
                
                succes, message = self.authentification.ajouter_utilisateur(username, mot_de_passe, role)
                print(message)
                
            elif choix == "2":
                print("\nListe des utilisateurs:")
                for username, details in self.authentification.utilisateurs.items():
                    print(f"- {username} (Rôle: {details['role']})")
                
            else:
                print("Choix invalide. Veuillez réessayer.")
    
    def _afficher_resultats(self, etudiants):
        """Affiche les résultats de recherche ou de tri"""
        if not etudiants:
            print("Aucun résultat trouvé.")
            return
            
        print(f"\n=== {len(etudiants)} étudiants trouvés ===")
        print("CODE\tNumero\tNom\tPrénom\tClasse\tMoyenne")
        print("-" * 70)
        
        for etudiant in etudiants:
            print(f"{etudiant.code}\t{etudiant.numero}\t{etudiant.nom}\t{etudiant.prenom}\t{etudiant.classe}\t{etudiant.moyenne_generale}")
        
        print("-" * 70)
    
    def demarrer(self):
        """Fonction principale pour démarrer l'application"""
        print("=== Gestion des Étudiants ===")
        
        # Initialiser les services
        self.initialiser_services()
        
        # Tentative d'initialisation de Redis
        try:
            redis_ok = self.initialiser_redis()
            if redis_ok:
                print("Connexion à Redis établie avec succès.")
            else:
                print("Impossible de se connecter à Redis. Le cache sera désactivé.")
        except Exception as e:
            print(f"Erreur lors de l'initialisation de Redis: {str(e)}")
            print("Le cache sera désactivé.")
        
        # Lecture des données
        print("\nChargement des données...")
        self.lire_donnees_csv()
        
        # Affichage des statistiques initiales
        stats = self.gestion_etudiants.obtenir_statistiques()
        print(f"\nStatistiques:")
        print(f"- Total des étudiants: {stats['total']}")
        print(f"- Étudiants valides: {stats['valides']}")
        print(f"- Étudiants invalides: {stats['invalides']}")
        
        # Validation avec la classe Service existante
        df = pd.read_csv('donnees_eleves.csv')
        self.service.valider_donnees(df)
        
        # Affichage des statistiques via Helper existant
        self.helper.afficher_statistiques(self.service)
        
        # Lancement du menu
        self.executer_menu()


def main():
    # Création et démarrage de l'application
    app = Application()
    app.demarrer()


if __name__ == "__main__":
    # Test de connexion MongoDB
    conn_string = "mongodb+srv://palaye:passer123@cluster0.qcestsk.mongodb.net/"
    connexion = DbConnexion(connection_string=conn_string, db_name="gestion-etudiant")
    db = connexion.toConnecte()
    
    if db is not None:
    # code ici
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
    
    # Fermer la connexion MongoDB
    connexion.fermer_connexion()

    # Test de connexion Redis
    print("\nTest de connexion à Redis...")
    from redis_connexion import RedisConnexion
    
    # Pour une connexion locale
    redis_conn = RedisConnexion(host="localhost", port=6379, db=0)
    redis_client = redis_conn.connect()
    
    if redis_client:
        # Tester les opérations Redis
        redis_conn.test_connexion()
        # Fermer la connexion
        redis_conn.fermer_connexion()
    
    # Démarrage de l'application principale
    print("\nDémarrage de l'application principale...")
    main()