# cache_redis.py
import json
import pickle

class CacheRedis:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.prefix = "gestion_etudiants:"
        self.ttl = 3600  # 1 heure par défaut
    
    def set_ttl(self, ttl):
        """Définit le TTL (Time-To-Live) pour les clés en cache"""
        self.ttl = ttl
    
    def mettre_en_cache(self, cle, valeur):
        """Met une valeur en cache"""
        try:
            # Créer une clé préfixée
            cle_complete = f"{self.prefix}{cle}"
            
            # Si la valeur est complexe, la sérialiser
            if isinstance(valeur, (dict, list, set, tuple)) or hasattr(valeur, "__dict__"):
                valeur_serialisee = pickle.dumps(valeur)
                self.redis.set(cle_complete, valeur_serialisee, ex=self.ttl)
            else:
                self.redis.set(cle_complete, str(valeur), ex=self.ttl)
                
            return True
        except Exception as e:
            print(f"Erreur lors de la mise en cache: {str(e)}")
            return False
    
    def recuperer_du_cache(self, cle):
        """Récupère une valeur du cache"""
        try:
            # Créer une clé préfixée
            cle_complete = f"{self.prefix}{cle}"
            
            # Récupérer du cache
            valeur = self.redis.get(cle_complete)
            
            if valeur is None:
                return None
                
            # Essayer de désérialiser la valeur
            try:
                return pickle.loads(valeur)
            except:
                # Si la désérialisation échoue, retourner la valeur telle quelle
                return valeur.decode('utf-8') if isinstance(valeur, bytes) else valeur
                
        except Exception as e:
            print(f"Erreur lors de la récupération du cache: {str(e)}")
            return None
    
    def supprimer_du_cache(self, cle):
        """Supprime une valeur du cache"""
        try:
            cle_complete = f"{self.prefix}{cle}"
            self.redis.delete(cle_complete)
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression du cache: {str(e)}")
            return False
    
    def vider_cache(self):
        """Vide tout le cache lié à l'application"""
        try:
            for cle in self.redis.keys(f"{self.prefix}*"):
                self.redis.delete(cle)
            return True
        except Exception as e:
            print(f"Erreur lors du vidage du cache: {str(e)}")
            return False