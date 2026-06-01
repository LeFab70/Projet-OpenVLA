# IntershipReport — Agenda quotidien

| Fichier | Description |
|---------|-------------|
| `agenda_quotidien_Fabrice.docx` | Agenda journalier (Word) — jours 01 à 12 |
| `build_agenda_quotidien.py` | Script de génération du `.docx` |
| `agenda_quotidien_Fabrice.md` | Aperçu Markdown (le document de référence est le Word) |

**Régénérer le Word :**

```bash
pip install python-docx
python IntershipReport/build_agenda_quotidien.py
```

Organisation par **semaine** (objectif hebdo + jours 01–12). Par jour : objectif, réalisations techniques, prochaine étape (pas de sections livrables / problèmes).

Le `.docx` reprend le **logo CCNB-INNOV** et l’**en-tête** du modèle `rapports_hebdomadaires/Semaine_01_14-15_mai_2026.docx` (styles Heading1, ListBullet).
