# Gestion des Étudiants

Ce projet est une application de gestion d'étudiants qui permet de gérer, rechercher, trier, et générer des rapports sur les données des étudiants.

## Prérequis

- Python 3.8+
- MongoDB
- Redis
- Les bibliothèques Python requises:
  - pandas
  - pymongo
  - redis
  - fpdf
  - matplotlib

## Installation des dépendances

```bash
# Installation des bibliothèques Python nécessaires
pip install pandas pymongo redis fpdf matplotlib
```

## Configuration des bases de données

### MongoDB

1. Assurez-vous que MongoDB est installé sur votre système ou que vous avez accès à une instance MongoDB
2. La chaîne de connexion est définie dans le fichier `main.py`: `mongodb+srv://palaye:passer123@cluster0.qcestsk.mongodb.net/`
3. La base de données utilisée est `gestion-etudiant`

### Redis

1. Installation de Redis (si ce n'est pas déjà fait):
   - Sur Ubuntu/Debian:
     ```bash
     sudo apt install redis-server
     ```
   - Sur macOS avec Homebrew:
     ```bash
     brew install redis
     ```

2. Démarrer le serveur Redis:
   ```bash
   redis-server
   ```

3. Pour vérifier que Redis fonctionne correctement:
   ```bash
   redis-cli ping
   ```
   La réponse devrait être `PONG`.

## Exécution de l'application

1. Assurez-vous que les deux bases de données sont en cours d'exécution
2. Placez-vous dans le répertoire du projet:
   ```bash
   cd chemin/vers/ECOLE221/PYTHON/GestionElevesPOO
   ```
3. Exécutez l'application:
   ```bash
   python main.py
   ```

## Fonctionnalités principales

1. **Authentification**:
   - Identifiants par défaut: 
     - Utilisateur: `admin`
     - Mot de passe: `admin123`
   - Trois tentatives de connexion maximum

2. **Menu principal**:
   - Recherche et tri des étudiants
   - Gestion des données (Import/Export)
   - Rapports et moyennes
   - Administration (pour les utilisateurs avec droits admin)

3. **Recherche et tri**:
   - Recherche par nom
   - Recherche par classe
   - Tri par nom (ascendant/descendant)
   - Tri par moyenne (ascendant/descendant)

4. **Gestion des données**:
   - Export CSV/JSON
   - Import CSV/JSON
   - Sauvegarde dans Redis pour accélérer les chargements futurs

5. **Rapports**:
   - Afficher les moyennes par étudiant
   - Générer un rapport PDF pour un étudiant
   - Générer un rapport PDF pour une classe

6. **Administration**:
   - Gestion des utilisateurs (ajout, listage)
   - Vider le cache Redis

## Commandes Redis utiles

Pour inspecter les données Redis utilisées par l'application:

```bash
# Lancer le client Redis
redis-cli

# Voir toutes les clés dans la base de données
KEYS *

# Examiner une valeur spécifique
GET nom_de_la_cle

# Pour les structures plus complexes (comme les listes)
LRANGE nom_de_la_liste 0 -1

# Pour les hachages (dictionnaires)
HGETALL nom_du_hash

# Pour supprimer une clé
DEL nom_de_la_cle

# Pour vider la base de données
FLUSHDB

# Quitter le client Redis
EXIT
```

## Dépannage

- Si vous rencontrez des problèmes de connexion à MongoDB, vérifiez que votre chaîne de connexion est correcte
- Si Redis n'est pas disponible, l'application fonctionnera sans cache
- En cas d'erreur d'importation de module (`ModuleNotFoundError`), assurez-vous d'avoir installé toutes les dépendances