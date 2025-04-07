class Helper:
    @staticmethod
    def afficher_menu():
        """Affiche le menu principal"""
        print("\n" + "="*50)
        print("MENU PRINCIPAL")
        print("="*50)
        print("1. Afficher les informations")
        print("2. Rechercher une information par numéro")
        print("3. Afficher les cinq premiers")
        print("4. Ajouter une information")
        print("5. Modifier une information invalide")
        print("0. Quitter")
        print("="*50)
    
    @staticmethod
    def afficher_statistiques(service):
        """Affiche les statistiques des données"""
        print(f"\nNombre de lignes valides: {len(service.lignes_valides)}")
        print(f"Nombre de lignes invalides: {len(service.lignes_invalides)}")
        
        # Affichage des exemples de lignes invalides
        print("\nExemple de lignes invalides avec leurs erreurs:")
        for ligne in service.lignes_invalides[:10]:  # Afficher les 10 premières lignes invalides
            print(f"\nLigne: {ligne['Numero']} - {ligne['Nom']} {ligne.get('Prénom', ligne.get('Prenom', ''))}")
            print(f"Erreurs: {ligne['erreurs']}")