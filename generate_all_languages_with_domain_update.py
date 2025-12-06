#!/usr/bin/env python3
"""
Script master pour régénérer TOUT le site dans toutes les langues
ET mettre à jour les domaines automatiquement.

Ce script exécute dans l'ordre pour chaque langue :
1. update_index_template.py - Met à jour index.html
2. generate_and_check_menu_footer_pages.py - Génère les pages catégories et légales
3. generate_all_product_pages.py - Génère toutes les pages produits
4. update_domain_urls.py - Met à jour toutes les URLs avec le domaine du CSV

Usage:
    python3 generate_all_languages_with_domain_update.py
"""

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Configuration des langues
LANGUAGES = [
    {
        'code': 'en',
        'name': 'Anglais',
        'generate_script': BASE_DIR / 'generate_all_en.py',
        'update_script': BASE_DIR / 'scripts' / 'generate' / 'update_domain_urls.py',
        'dir': BASE_DIR
    },
    {
        'code': 'fr',
        'name': 'Français',
        'generate_script': BASE_DIR / 'fr' / 'scripts' / 'generate_all_fr.py',
        'update_script': BASE_DIR / 'fr' / 'scripts' / 'generate' / 'update_domain_urls.py',
        'dir': BASE_DIR / 'fr'
    },
    {
        'code': 'de',
        'name': 'Allemand',
        'generate_script': BASE_DIR / 'de' / 'scripts' / 'generate_all_de.py',
        'update_script': BASE_DIR / 'de' / 'scripts' / 'generate' / 'update_domain_urls.py',
        'dir': BASE_DIR / 'de'
    },
    {
        'code': 'es',
        'name': 'Espagnol',
        'generate_script': BASE_DIR / 'es' / 'scripts' / 'generate_all_es.py',
        'update_script': BASE_DIR / 'es' / 'scripts' / 'generate' / 'update_domain_urls.py',
        'dir': BASE_DIR / 'es'
    },
    {
        'code': 'pt',
        'name': 'Portugais',
        'generate_script': BASE_DIR / 'pt' / 'scripts' / 'generate_all_pt.py',
        'update_script': BASE_DIR / 'pt' / 'scripts' / 'generate' / 'update_domain_urls.py',
        'dir': BASE_DIR / 'pt'
    }
]

def run_script(script_path, lang_name, step_name):
    """Exécute un script."""
    if not script_path.exists():
        print(f"  ⚠️  Script non trouvé: {script_path}")
        return False
    
    try:
        print(f"  📄 {step_name}...")
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=script_path.parent,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"  ✅ {step_name} - Terminé")
            return True
        else:
            print(f"  ❌ {step_name} - Erreur:")
            if result.stderr:
                print(result.stderr[:500])  # Limiter l'affichage
            return False
    except Exception as e:
        print(f"  ❌ {step_name} - Exception: {e}")
        return False

def main():
    """Fonction principale."""
    print("=" * 70)
    print("🌍 RÉGÉNÉRATION COMPLÈTE + MISE À JOUR DES DOMAINES")
    print("=" * 70)
    print()
    
    success_count = 0
    total_count = len(LANGUAGES)
    
    for lang in LANGUAGES:
        print(f"\n{'=' * 70}")
        print(f"🌐 {lang['name'].upper()} ({lang['code']})")
        print(f"{'=' * 70}")
        
        # Étape 1: Génération
        if not run_script(lang['generate_script'], lang['name'], "Génération"):
            print(f"  ⚠️  Échec de la génération pour {lang['name']}")
            continue
        
        # Étape 2: Mise à jour des domaines
        if not run_script(lang['update_script'], lang['name'], "Mise à jour des domaines"):
            print(f"  ⚠️  Échec de la mise à jour des domaines pour {lang['name']}")
            continue
        
        success_count += 1
    
    print()
    print("=" * 70)
    print("📊 RÉSUMÉ")
    print("=" * 70)
    print(f"✅ Réussi: {success_count}/{total_count}")
    print(f"❌ Échoué: {total_count - success_count}/{total_count}")
    print()
    
    if success_count == total_count:
        print("🎉 Toutes les langues ont été régénérées avec succès !")
        print()
        print("📝 Prochaines étapes:")
        print("  1. Régénérer les sitemaps: python3 generate_sitemaps.py")
        print("  2. Vérifier les fichiers générés")
        print("  3. Déployer: python3 update_github_auto.py")
    else:
        print("⚠️  Certaines langues ont échoué. Vérifiez les erreurs ci-dessus.")
        sys.exit(1)

if __name__ == '__main__':
    main()

