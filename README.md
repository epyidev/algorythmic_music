<h1 align="center">algorythmic_music</h1>

<p align="center"><b>Générateur de musique algorithmique : un morceau déduit d'un jeu de règles, jamais d'un échantillon.</b></p>

Vieux projet de 2023, écrit en cours d'audiovisuel : analyser un morceau, en extraire les règles (gamme, boucle harmonique, pulsation, couleur spectrale), puis regénérer de la musique à partir de ces règles seules. Ceci en est le remaster récent, avec une interface Qt et un rendu cinquante fois plus rapide.

## Prérequis

Python 3.11 ou plus récent.

```bash
pip install -r requirements.txt
```

## Commandes

```bash
python run.py                                    # ouvre l'interface graphique
python run.py --cli --seed 7 --out morceau.wav   # rendu sans interface
python run.py --cli --help                       # options disponibles
```

Une même graine redonne exactement le même morceau. La structure standard fait 3 min 44 s et se rend en une quinzaine de secondes. Le bouton de préécoute rend un extrait de 10 s et le joue en boucle, pour régler sans attendre le morceau entier.

## Réglages

Onglet Composition : graine, tonique, mode, tempo, structure, basculement spectral, réverbération, largeur stéréo, flou rythmique, longueur des coupes franches et fondu entre sections.

Onglet Instruments, couche par couche : niveau, timbre parmi quatre (additif, modulation de fréquence, impulsion filtrée, corde pincée) avec brillance, désaccord, attaque et caractère, puis une chaîne d'effets cumulables et réordonnables parmi dix.

## Structure

| Chemin | Rôle |
|--------|------|
| `algorythmic/model/` | gamme, accords, structure, grille rythmique |
| `algorythmic/synthesis/voices/` | les quatre timbres |
| `algorythmic/synthesis/effects/` | les dix effets et leur chaînage |
| `algorythmic/synthesis/` | percussions, réverbération, basculement spectral, dynamique |
| `algorythmic/engine/` | grille temporelle, couches, automation, mixage |
| `algorythmic/ui/` | fenêtre Qt, réglages, progression |
| `algorythmic/texts.py` | tous les textes affichés |
