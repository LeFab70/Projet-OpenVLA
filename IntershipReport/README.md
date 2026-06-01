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

Structure par jour (identique aux rapports hebdomadaires) : objectif, réalisations, problèmes/solutions, livrables, prochaine étape.
