# Logo Placeholders

Ce dossier contient des logos placeholder pour hyb8nate.

## Fichiers disponibles

- `logo-512.svg` - Logo 512x512px (icône principale, haute résolution)
- `logo-256.svg` - Logo 256x256px (icône moyenne résolution)
- `logo-128.svg` - Logo 128x128px (icône basse résolution)
- `logo-64.svg` - Logo 64x64px (très petite icône)
- `../favicon.svg` - Favicon du site (dans /public)
- `../logo.svg` - Logo principal (dans /public)

## Comment remplacer les logos

1. **Préparez vos logos** dans les dimensions suivantes:
   - 512x512px
   - 256x256px
   - 128x128px
   - 64x64px
   - Un favicon de 64x64px ou 32x32px

2. **Remplacez les fichiers** en conservant les mêmes noms:
   ```bash
   # Remplacer les logos dans le dossier logos/
   cp votre-logo-512.png frontend/public/logos/logo-512.svg
   cp votre-logo-256.png frontend/public/logos/logo-256.svg
   cp votre-logo-128.png frontend/public/logos/logo-128.svg
   cp votre-logo-64.png frontend/public/logos/logo-64.svg

   # Remplacer le favicon
   cp votre-favicon.png frontend/public/favicon.svg

   # Remplacer le logo principal
   cp votre-logo-principal.png frontend/public/logo.svg
   ```

3. **Formats supportés**:
   - SVG (recommandé, vectoriel, sans perte de qualité)
   - PNG (avec transparence)
   - ICO (pour le favicon)
   - JPG (non recommandé car pas de transparence)

## Notes

- Les fichiers SVG sont préférables car ils sont vectoriels et s'adaptent à toutes les tailles
- Si vous utilisez des PNG, assurez-vous qu'ils ont un fond transparent
- Les noms de fichiers doivent correspondre exactement à ceux listés ci-dessus
- Après remplacement, rechargez votre navigateur (Ctrl+F5 ou Cmd+Shift+R) pour voir les changements
