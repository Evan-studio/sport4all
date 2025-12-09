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
import csv
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Dossiers à exclure lors de la détection des langues
EXCLUDED_DIRS = {
    'APPLI:SCRIPT aliexpress', 'scripts', 'config', 'images', 'page_html', 
    'upload_cloudflare', 'sauv', 'CSV', '__pycache__', '.git', 'node_modules',
    'upload youtube'
}

# Noms de langues
LANGUAGE_NAMES = {
    'en': 'Anglais',
    'fr': 'Français',
    'de': 'Allemand',
    'es': 'Espagnol',
    'pt': 'Portugais',
    'it': 'Italien',
    'nl': 'Néerlandais',
    'ru': 'Russe',
    'pl': 'Polonais',
}

def detect_languages():
    """Détecte automatiquement toutes les langues disponibles."""
    languages = []
    
    # Ajouter le dossier principal (en) s'il existe
    root_index = BASE_DIR / 'index.html'
    root_translations = BASE_DIR / 'translations.csv'
    root_generate_script = BASE_DIR / 'generate_all_en.py'
    
    if root_index.exists() and root_translations.exists():
        languages.append({
            'code': 'en',
            'name': LANGUAGE_NAMES.get('en', 'Anglais'),
            'generate_script': root_generate_script,
            'update_script': BASE_DIR / 'scripts' / 'generate' / 'update_domain_urls.py',
            'dir': BASE_DIR
        })
    
    # Détecter les dossiers de langue
    for item in BASE_DIR.iterdir():
        if (item.is_dir() and 
            not item.name.startswith('.') and 
            item.name not in EXCLUDED_DIRS and
            (item / 'index.html').exists() and 
            (item / 'translations.csv').exists()):
            
            lang_code = item.name.lower()
            generate_script = item / 'scripts' / f'generate_all_{lang_code}.py'
            update_script = item / 'scripts' / 'generate' / 'update_domain_urls.py'
            
            languages.append({
                'code': lang_code,
                'name': LANGUAGE_NAMES.get(lang_code, lang_code.upper()),
                'generate_script': generate_script,
                'update_script': update_script,
                'dir': item
            })
    
    return sorted(languages, key=lambda x: (x['code'] != 'en', x['code']))

def load_domain_from_translations(translations_path: Path):
    """Lit translations.csv et renvoie la première valeur non vide pour site.domain."""
    if not translations_path.exists():
        return None
    try:
        with translations_path.open(newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('key', '').strip() == 'site.domain':
                    # Chercher la première colonne non vide (hors key/description)
                    for k, v in row.items():
                        if k in ('key', 'description'):
                            continue
                        if v and v.strip():
                            return v.strip()
                    break
    except Exception as e:
        print(f"  ⚠️  Impossible de lire {translations_path}: {e}")
    return None

def update_robots_sitemap(domain: str, lang_code: str, robots_path: Path):
    """Met à jour (ou ajoute) la ligne Sitemap dans robots.txt pour la langue donnée."""
    domain = domain.rstrip('/')
    sitemap_url = f"{domain}/sitemap.xml" if lang_code == 'en' else f"{domain}/{lang_code}/sitemap.xml"
    sitemap_line = f"Sitemap: {sitemap_url}"

    if not robots_path.exists():
        return False

    try:
        content = robots_path.read_text(encoding='utf-8')
        # Remplacer la ligne Sitemap existante ou l'ajouter en bas si absente
        if re.search(r'^Sitemap: .*', content, flags=re.MULTILINE):
            content_new = re.sub(r'^Sitemap: .*', sitemap_line, content, flags=re.MULTILINE)
        else:
            if not content.endswith('\n'):
                content += '\n'
            content_new = content + sitemap_line + '\n'

        if content_new != content:
            robots_path.write_text(content_new, encoding='utf-8')
        return True
    except Exception as e:
        print(f"  ⚠️  Impossible de mettre à jour {robots_path}: {e}")
        return False

def update_all_robots_sitemaps(languages):
    """Met à jour robots.txt pour la racine et chaque langue avec le bon sitemap."""
    updated = 0
    for lang in languages:
        lang_code = lang['code']
        lang_dir = lang['dir']
        translations_path = lang_dir / 'translations.csv'
        robots_path = lang_dir / 'robots.txt'

        domain = load_domain_from_translations(translations_path)
        if not domain:
            # Fallback sur le domaine de la racine si non trouvé
            root_domain = load_domain_from_translations(BASE_DIR / 'translations.csv')
            domain = root_domain or 'https://bafang-shop.com'

        if update_robots_sitemap(domain, lang_code, robots_path):
            updated += 1
    if updated:
        print(f"  ✅ robots.txt mis à jour ({updated} fichier(s))")
    else:
        print("  ⚠️  Aucun robots.txt mis à jour")

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
    
    # Détecter automatiquement les langues
    languages = detect_languages()
    
    if not languages:
        print("❌ Aucune langue détectée")
        print("   Assurez-vous que le dossier principal ou les dossiers de langue")
        print("   contiennent index.html et translations.csv")
        sys.exit(1)
    
    print(f"✅ {len(languages)} langue(s) détectée(s):")
    for lang in languages:
        print(f"   - {lang['name']} ({lang['code']})")
    print()
    
    success_count = 0
    total_count = len(languages)
    
    for lang in languages:
        print(f"\n{'=' * 70}")
        print(f"🌐 {lang['name'].upper()} ({lang['code']})")
        print(f"{'=' * 70}")
        
        # Vérifier si les scripts existent
        if not lang['generate_script'].exists():
            print(f"  ⚠️  Script de génération non trouvé: {lang['generate_script']}")
            print(f"     Créez d'abord cette langue avec: python3 create_language_site.py")
            continue
        
        if not lang['update_script'].exists():
            print(f"  ⚠️  Script de mise à jour des domaines non trouvé: {lang['update_script']}")
            print(f"     Créez d'abord cette langue avec: python3 create_language_site.py")
            continue
        
        # Étape 1: Génération
        if not run_script(lang['generate_script'], lang['name'], "Génération"):
            print(f"  ⚠️  Échec de la génération pour {lang['name']}")
            continue
        
        # Étape 2: Mise à jour des domaines
        if not run_script(lang['update_script'], lang['name'], "Mise à jour des domaines"):
            print(f"  ⚠️  Échec de la mise à jour des domaines pour {lang['name']}")
            continue
        
        success_count += 1

    # Mettre à jour robots.txt (Sitemap) avec les bons domaines
    print("\n📄 Mise à jour des robots.txt (Sitemap)...")
    update_all_robots_sitemaps(languages)
    
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

