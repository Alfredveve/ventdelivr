# VentDelivr 🚀

**VentDelivr** est une plateforme complète de vente et de livraison développée avec Django. Elle connecte les marchands, les clients et les services de livraison dans un écosystème unifié.

## 📋 Table des Matières

- [Fonctionnalités](#-fonctionnalités)
- [Architecture du Projet](#-architecture-du-projet)
- [Stack Technique](#-stack-technique)
- [Installation et Configuration](#-installation-et-configuration)
- [Utilisation](#-utilisation)
- [Contribution](#-contribution)

## ✨ Fonctionnalités

- **Authentification & Utilisateurs** : Gestion sécurisée des comptes utilisateurs, clients et administrateurs.
- **Marchands (`merchants`)** : Gestion des profils vendeurs, boutiques et tableaux de bord.
- **Catalogue (`catalog`)** : Gestion des produits, catégories, stocks et prix.
- **Commandes (`orders`)** : Cycle de vie complet des commandes, du panier au paiement.
- **Livraison (`delivery`)** : Suivi des livraisons et gestion logistique.
- **Finance (`finance`)** : Gestion des portefeuilles, transactions et paiements.
- **Interface Moderne** : Design réactif et esthétique utilisant TailwindCSS.

## 🏗 Architecture du Projet

Le projet est structuré de manière modulaire autour de plusieurs applications Django :

| Application | Description |
|-------------|-------------|
| `core` | Fonctionnalités de base, templates globaux et utilitaires. |
| `users` | Modèles d'utilisateurs personnalisés et authentification. |
| `merchants` | Logique métier liée aux vendeurs. |
| `catalog` | Données produits et inventaire. |
| `orders` | Traitement des commandes. |
| `delivery` | Gestion des expéditions. |
| `finance` | Logique financière et comptable. |

## 🛠 Stack Technique

- **Backend** : Django (Python)
- **Base de Données** : SQLite (Dev) / PostgreSQL (Prod - Recommandé)
- **Frontend** : HTML5, TailwindCSS, JavaScript
- **Admin Interface** : Jazzmin
- **Déploiement** : Compatible WSGI/ASGI

## 🚀 Installation et Configuration

Suivez ces étapes pour lancer le projet localement :

### 1. Cloner le dépôt

```bash
git clone https://github.com/Alfredveve/ventdelivr.git
cd ventdelivr
```

### 2. Créer un environnement virtuel

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
# Si vous n'avez pas de fichier requirements.txt, installez Django et les dépendances manuellement :
# pip install django python-dotenv django-jazzmin
```

### 4. Configurer les variables d'environnement

Créez un fichier `.env` à la racine du projet (basé sur `.env.example` s'il existe) :

```env
DEBUG=True
SECRET_KEY=votre_clé_secrète_ici
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Appliquer les migrations

```bash
python manage.py migrate
```

### 6. Créer un super-utilisateur (Admin)

```bash
python manage.py createsuperuser
```

### 7. Lancer le serveur de développement

```bash
python manage.py runserver
```

Accédez au site via [http://127.0.0.1:8000](http://127.0.0.1:8000).

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour proposer des changements :

1. Forkez le projet.
2. Créez une branche (`git checkout -b feature/NouvelleFeature`).
3. Committez vos changements (`git commit -m 'Ajout de NouvelleFeature'`).
4. Pushez vers la branche (`git push origin feature/NouvelleFeature`).
5. Ouvrez une Pull Request.
