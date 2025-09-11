# Utiliser une image Python officielle
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers du projet dans le conteneur
COPY . /app

# Installer les dépendances si requirements.txt existe
RUN pip install --no-cache-dir -r requirements.txt || true

# Commande de lancement (à adapter selon ton projet)
CMD ["python", "main.py"]
