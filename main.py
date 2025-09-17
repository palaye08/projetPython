import os
import pandas as pd
from flask import Flask, jsonify, request, render_template_string
from validation.validator import Validator
from service import Service
from helper import Helper
from connexion.db_connexion import DbConnexion
from connexion.redis_connexion import RedisConnexion
from gestion_etudiants import GestionEtudiants
from auth.authentification import Authentification
from cache_redis import CacheRedis
from export_import import ExportImport
from rapport_pdf import RapportPDF
from entite.etudiant import Etudiant

# Initialisation de Flask
app = Flask(__name__)

# Template HTML simple
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Gestion des Étudiants</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .info { background-color: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        .endpoints { background-color: #f8f9fa; padding: 20px; border-radius: 5px; }
        .endpoint { margin: 10px 0; padding: 5px; background-color: white; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎓 Gestion des Étudiants - API</h1>
        <div class="status {{ status_class }}">
            <strong>Status:</strong> {{ status_message }}
        </div>
        
        <div class="endpoints">
            <h2>Endpoints disponibles:</h2>
            <div class="endpoint"><strong>GET /</strong> - Cette page d'accueil</div>
            <div class="endpoint"><strong>GET /health</strong> - Vérification de l'état de l'application</div>
            <div class="endpoint"><strong>GET /api/students</strong> - Liste de tous les étudiants</div>
            <div class="endpoint"><strong>GET /api/students/stats</strong> - Statistiques des étudiants</div>
            <div class="endpoint"><strong>GET /api/students/search?nom=XXX</strong> - Recherche par nom</div>
            <div class="endpoint"><strong>GET /api/test-db</strong> - Test de connexion MongoDB</div>
            <div class="endpoint"><strong>GET /api/test-redis</strong> - Test de connexion Redis</div>
        </div>
        
        <div class="info">
            <p><strong>Note:</strong> Cette application est maintenant accessible via une API REST.</p>
            <p>Vous pouvez utiliser ces endpoints pour interagir avec le système de gestion des étudiants.</p>
        </div>
    </div>
</body>
</html>
"""

# Instance globale de l'application
application_instance = None

class WebApplication:
    def __init__(self):
        self.service = Service()
        self.helper = Helper()
        self.gestion_etudiants = GestionEtudiants()
        self.authentification = Authentification()
        self.redis_client = None
        self.cache = None
        self.export_import = None
        self.rapport_pdf = None
        self.initialized = False
        
    def initialiser_redis(self, host="localhost", port=6379, password=None, db=0):
        """Initialise la connexion Redis et le cache"""
        try:
            redis_conn = RedisConnexion(host=host, port=port, password=password, db=db)
            self.redis_client = redis_conn.connect()
            
            if self.redis_client:
                self.cache = CacheRedis(self.redis_client)
                return True
        except Exception as e:
            print(f"Erreur Redis: {e}")
        return False
    
    def initialiser_services(self):
        """Initialise les services dépendants"""
        try:
            if self.gestion_etudiants:
                self.export_import = ExportImport(self.gestion_etudiants)
                self.rapport_pdf = RapportPDF(self.gestion_etudiants)
            return True
        except Exception as e:
            print(f"Erreur initialisation services: {e}")
            return False
    
    def charger_donnees_exemple(self):
        """Charge des données d'exemple si pas de fichier CSV"""
        try:
            # Créer quelques étudiants d'exemple
            etudiants_exemple = [
                {"code": "E001", "numero": "001", "nom": "Diop", "prenom": "Amadou", "classe": "L3", "moyenne": 15.5},
                {"code": "E002", "numero": "002", "nom": "Fall", "prenom": "Fatou", "classe": "L3", "moyenne": 17.2},
                {"code": "E003", "numero": "003", "nom": "Sall", "prenom": "Omar", "classe": "L2", "moyenne": 13.8}
            ]
            
            # Créer des objets Etudiant
            for data in etudiants_exemple:
                etudiant = Etudiant(
                    code=data["code"],
                    numero=data["numero"],
                    nom=data["nom"],
                    prenom=data["prenom"],
                    classe=data["classe"]
                )
                etudiant.moyenne_generale = data["moyenne"]
                self.gestion_etudiants.etudiants.append(etudiant)
            
            return True
        except Exception as e:
            print(f"Erreur chargement données exemple: {e}")
            return False
    
    def initialiser(self):
        """Initialise l'application complète"""
        if self.initialized:
            return True
            
        try:
            # Initialiser les services
            self.initialiser_services()
            
            # Tentative d'initialisation de Redis (optionnel)
            try:
                self.initialiser_redis()
            except:
                pass  # Redis optionnel
            
            # Charger des données d'exemple
            self.charger_donnees_exemple()
            
            self.initialized = True
            return True
            
        except Exception as e:
            print(f"Erreur initialisation: {e}")
            return False

def get_app_instance():
    """Récupère l'instance de l'application"""
    global application_instance
    if application_instance is None:
        application_instance = WebApplication()
        application_instance.initialiser()
    return application_instance

# Routes Flask
@app.route('/')
def home():
    """Page d'accueil"""
    app_instance = get_app_instance()
    
    if app_instance.initialized:
        status_class = "success"
        status_message = "✅ Application initialisée avec succès"
    else:
        status_class = "error"
        status_message = "❌ Erreur lors de l'initialisation"
    
    return render_template_string(HTML_TEMPLATE, 
                                status_class=status_class,
                                status_message=status_message)

@app.route('/health')
def health():
    """Endpoint de santé"""
    app_instance = get_app_instance()
    
    health_data = {
        "status": "healthy" if app_instance.initialized else "unhealthy",
        "services": {
            "gestion_etudiants": app_instance.gestion_etudiants is not None,
            "redis_cache": app_instance.cache is not None,
            "export_import": app_instance.export_import is not None,
            "rapport_pdf": app_instance.rapport_pdf is not None
        },
        "data": {
            "nombre_etudiants": len(app_instance.gestion_etudiants.etudiants) if app_instance.gestion_etudiants else 0
        }
    }
    
    return jsonify(health_data)

@app.route('/api/students')
def get_students():
    """Récupère tous les étudiants"""
    app_instance = get_app_instance()
    
    if not app_instance.initialized:
        return jsonify({"error": "Application non initialisée"}), 500
    
    try:
        etudiants_data = []
        for etudiant in app_instance.gestion_etudiants.etudiants:
            etudiants_data.append({
                "code": etudiant.code,
                "numero": etudiant.numero,
                "nom": etudiant.nom,
                "prenom": etudiant.prenom,
                "classe": etudiant.classe,
                "moyenne": getattr(etudiant, 'moyenne_generale', 'N/A')
            })
        
        return jsonify({
            "success": True,
            "count": len(etudiants_data),
            "students": etudiants_data
        })
        
    except Exception as e:
        return jsonify({"error": f"Erreur: {str(e)}"}), 500

@app.route('/api/students/stats')
def get_stats():
    """Récupère les statistiques des étudiants"""
    app_instance = get_app_instance()
    
    if not app_instance.initialized:
        return jsonify({"error": "Application non initialisée"}), 500
    
    try:
        stats = app_instance.gestion_etudiants.obtenir_statistiques()
        return jsonify({
            "success": True,
            "statistics": stats
        })
    except Exception as e:
        return jsonify({"error": f"Erreur: {str(e)}"}), 500

@app.route('/api/students/search')
def search_students():
    """Recherche des étudiants par nom"""
    app_instance = get_app_instance()
    nom = request.args.get('nom', '')
    
    if not nom:
        return jsonify({"error": "Paramètre 'nom' requis"}), 400
    
    if not app_instance.initialized:
        return jsonify({"error": "Application non initialisée"}), 500
    
    try:
        resultats = app_instance.gestion_etudiants.rechercher_par_nom(nom)
        
        etudiants_data = []
        for etudiant in resultats:
            etudiants_data.append({
                "code": etudiant.code,
                "numero": etudiant.numero,
                "nom": etudiant.nom,
                "prenom": etudiant.prenom,
                "classe": etudiant.classe,
                "moyenne": getattr(etudiant, 'moyenne_generale', 'N/A')
            })
        
        return jsonify({
            "success": True,
            "query": nom,
            "count": len(etudiants_data),
            "results": etudiants_data
        })
        
    except Exception as e:
        return jsonify({"error": f"Erreur: {str(e)}"}), 500

@app.route('/api/test-db')
def test_db():
    """Test de connexion MongoDB"""
    try:
        conn_string = os.environ.get('MONGODB_URI', 'mongodb+srv://palaye:passer123@cluster0.qcestsk.mongodb.net/')
        connexion = DbConnexion(connection_string=conn_string, db_name="gestion-etudiant")
        db = connexion.toConnecte()
        
        if db is not None:
            # Test simple
            test_collection = db["test"]
            test_doc = {"test": "connexion", "timestamp": str(pd.Timestamp.now())}
            test_collection.insert_one(test_doc)
            connexion.fermer_connexion()
            
            return jsonify({
                "success": True,
                "message": "Connexion MongoDB réussie",
                "database": "gestion-etudiant"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Échec de connexion MongoDB"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur MongoDB: {str(e)}"
        }), 500

@app.route('/api/test-redis')
def test_redis():
    """Test de connexion Redis"""
    try:
        redis_host = os.environ.get('REDIS_URL', 'localhost')
        redis_conn = RedisConnexion(host=redis_host, port=6379, db=0)
        redis_client = redis_conn.connect()
        
        if redis_client:
            # Test simple
            redis_client.set("test_key", "test_value")
            value = redis_client.get("test_key")
            redis_conn.fermer_connexion()
            
            return jsonify({
                "success": True,
                "message": "Connexion Redis réussie",
                "test_value": value.decode('utf-8') if value else None
            })
        else:
            return jsonify({
                "success": False,
                "message": "Échec de connexion Redis"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur Redis: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Configuration pour le déploiement
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Initialiser l'application
    get_app_instance()
    
    print(f"🚀 Démarrage de l'application sur le port {port}")
    print(f"🌐 Mode debug: {debug}")
    
    # Lancer l'application
    app.run(host='0.0.0.0', port=port, debug=debug)