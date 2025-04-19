import redis

class RedisConnexion:
    def __init__(self, host="localhost", port=6379, db=0, password=None):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.client = None
    
    def connect(self):
        try:
            # Connexion à Redis
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True  # Pour convertir les réponses binaires en chaînes de caractères
            )
            
            # Vérifier la connexion avec un ping
            if self.client.ping():
                print(f"Connexion réussie à Redis sur {self.host}:{self.port}")
                return self.client
            else:
                print("Échec du ping Redis")
                return None
        except Exception as e:
            print(f"Erreur de connexion à Redis: {e}")
            return None
    
    def test_connexion(self):
        """Teste la connexion en effectuant quelques opérations simples."""
        try:
            if not self.client:
                print("Client Redis non initialisé. Appelez connect() d'abord.")
                return False
                
            # Définir une valeur de test
            self.client.set("test_key", "test_value")
            
            # Récupérer la valeur
            value = self.client.get("test_key")
            
            # Vérifier
            if value == "test_value":
                print("Test Redis réussi: opérations set/get fonctionnent correctement.")
                # Supprimer la clé de test
                self.client.delete("test_key")
                return True
            else:
                print(f"Test Redis échoué: valeur obtenue '{value}' ne correspond pas à 'test_value'")
                return False
        except Exception as e:
            print(f"Erreur lors du test Redis: {e}")
            return False
    
    def fermer_connexion(self):
        """Ferme la connexion Redis."""
        if self.client:
            self.client.close()
            print("Connexion Redis fermée")