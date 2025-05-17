# Utilise une version stable (3.13 est encore en bêta début 2025 !)
FROM python:3.12-slim

# Définir une variable d'environnement pour désactiver l'écriture de .pyc
ENV PYTHONDONTWRITEBYTECODE 1
# Activer le mode "non bufferisé" (logs visibles immédiatement)
ENV PYTHONUNBUFFERED 1

# Définir le dossier de travail
WORKDIR /app

# Installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code
COPY . .

# Exposer le port Flask
EXPOSE 5000

# Commande par défaut pour démarrer l'application
CMD ["python3", "run.py"]
