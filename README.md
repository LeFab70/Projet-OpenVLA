# openVLA

**Programmeur :** Fabrice Kouonang  
**Date :** 14 mai 2026

---

## Intro stage

Développement d’un démonstrateur OpenVLA pour robot collaboratif UR et vision 2D ou 3D ZIVID

## Objectifs

Le projet visera en particulier à répondre à la question suivante : quels sont les ingrédients de la « sauce OpenVLA » et en quoi cette approche diffère-t-elle des méthodes robotiques plus traditionnelles ? Le stage permettra donc de combiner veille technologique, expérimentation pratique, intégration robotique et vulgarisation technique.

## Principales responsabilités

- Étudier l’architecture générale d’OpenVLA et en produire une description technique claire et structurée.
- Identifier les différentes composantes de la pipeline : perception, inférence, génération d’actions et exécution robotique.
- Comparer l’approche OpenVLA aux approches robotiques traditionnelles, notamment en ce qui concerne la programmation de tâches, la perception, la planification et le contrôle.
- Mettre en place un démonstrateur expérimental utilisant un robot collaboratif UR et une caméra Zivid.
- Réaliser l’intégration logicielle et matérielle nécessaire au fonctionnement du démonstrateur.
- Effectuer des essais, analyser les résultats obtenus et documenter les limites, défis et opportunités de l’approche.
- Produire une documentation technique et une synthèse vulgarisée destinée à l’équipe de CCNB-INNOV.
- Présenter les résultats du stage sous forme de démonstration et de présentation technique.

---

## Jour 02 — Robot UR (tracé lettre A)

**Date :** 14 mai 2026

Premier programme URScript sur le bras collaboratif : tracé géométrique de la lettre **A** avec déplacement linéaire (`movel`), approche sécurisée et paramètres de vitesse/accélération.

- Script : `scripts/ur/URscriptLetterA.script` — fonction `trace_A(n)` pour tracer 1 à 4 lettres (décalage automatique sur Y).
- Script : `scripts/ur/traceAOnce.script` — un seul A, sans boucle.
- Script : `scripts/ur/returnToCenter.script` — retour position centre table.
- Rapport : `OpenVLA_day02_trace_A.docx` — objectifs, code de référence et notes de sécurité.

## Jour 03 — API Zivid (MR130)

**Date :** 14 mai 2026

Prise en main de l’API Zivid : connexion à la caméra **Zivid 2+ MR130** et envoi d’une commande d’acquisition 2D/3D (`capture_2d_3d`).

- Rapport : `OpenVLA_day03_zivid_api.docx` — prérequis SDK, étapes API Python, exemple d’acquisition, lien vers OpenVLA.

**Fichiers du dépôt**

| Fichier | Description |
|---------|-------------|
| `OpenVLA_prise_en_main.docx` | Prise en main OpenVLA (architecture, flux de données) |
| `OpenVLA_day02_trace_A.docx` | Journal jour 02 — intégration UR |
| `OpenVLA_day03_zivid_api.docx` | Journal jour 03 — API Zivid MR130 |
| `scripts/ur/URscriptLetterA.script` | Programme UR — tracé du A (boucle) |
| `scripts/ur/traceAOnce.script` | Programme UR — tracé d’un seul A |
| `scripts/ur/returnToCenter.script` | Programme UR — retour au centre |
