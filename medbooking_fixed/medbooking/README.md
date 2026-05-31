# MedBooking — Système de Gestion de Rendez-vous Médicaux
**Smart Medical Appointment Management System**

Projet PFA — Farouk Bououd & Ismail El Aribi

---

## Installation rapide / Quick Setup

```bash
# 1. Installer les dépendances
pip install django

# 2. Appliquer les migrations
python manage.py migrate

# 3. Créer les données de test
python seed_data.py

# 4. Lancer le serveur
python manage.py runserver
```

Ouvrir http://127.0.0.1:8000 dans votre navigateur.

---

## Comptes de test / Test Accounts

| Rôle | Username | Mot de passe |
|------|----------|--------------|
| Admin | admin | admin123 |
| Médecin (Cardiologue) | dr.dupont | doctor123 |
| Médecin (Pédiatre) | dr.benali | doctor123 |
| Médecin (Neurologue) | dr.martin | doctor123 |
| Patient | patient1 | patient123 |

---

## Structure du projet / Project Structure

```
medbooking/
├── accounts/          # Utilisateurs, Auth, Dashboard
├── doctors/           # Profils médecins, Disponibilités, Avis
├── appointments/      # Rendez-vous, Notifications, Historique
├── templates/         # Templates HTML (Bootstrap 5)
├── static/css/        # Styles CSS personnalisés
├── seed_data.py       # Script de données de test
└── manage.py
```

## Fonctionnalités / Features

### Patient
- Inscription / connexion
- Recherche de médecins (par nom, spécialité, ville, online)
- Réservation de rendez-vous avec créneaux dynamiques
- Annulation avec notification email
- Historique médical
- Avis et notes (après consultation)
- Notifications

### Médecin
- Profil professionnel
- Gestion des disponibilités (jours + horaires + durée de slot)
- Vue des rendez-vous
- Notes de consultation
- Changement de statut des rendez-vous

### Admin
- Dashboard avec statistiques
- Panel d'administration Django complet
- Gestion utilisateurs / médecins / rendez-vous
- Graphiques (Chart.js)

## Technologies utilisées

- **Backend**: Python Django 4.x
- **Frontend**: HTML5 + Bootstrap 5 + Font Awesome 6
- **Base de données**: SQLite
- **Email**: Console backend (dev) / SMTP (prod)
- **Charts**: Chart.js

## Langues / Languages
Interface bilingue Français / English (Django i18n)
