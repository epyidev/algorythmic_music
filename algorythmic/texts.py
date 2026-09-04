"""
Tous les textes affichés par l'interface.

Aucune chaîne visible n'est écrite ailleurs : les regrouper ici évite qu'un
libellé traîne au milieu de la logique et rend la relecture immédiate.

@author epyidev
"""

from __future__ import annotations

from .engine.progress import RenderStage

WINDOW_TITLE = "Algorythmic Music"
WINDOW_SUBTITLE = "Générateur de morceau par règles, sans échantillon d'origine"

GROUP_COMPOSITION = "Composition"
GROUP_TEXTURE = "Texture"
GROUP_OUTPUT = "Sortie"
GROUP_PROGRESS = "Rendu"

LABEL_SEED = "Graine"
LABEL_TONIC = "Tonique"
LABEL_MODE = "Mode"
LABEL_TEMPO = "Tempo"
LABEL_STRUCTURE = "Structure"
LABEL_SPECTRAL_TILT = "Basculement spectral"
LABEL_REVERB = "Réverbération"
LABEL_STEREO_WIDTH = "Largeur stéréo"
LABEL_LOOSENESS = "Flou rythmique"
LABEL_OUTPUT_FILE = "Fichier"

BUTTON_RANDOM_SEED = "Tirer"
BUTTON_BROWSE = "Parcourir"
BUTTON_RENDER = "Générer le morceau"
BUTTON_CANCEL = "Annuler"
BUTTON_OPEN_FOLDER = "Ouvrir le dossier"
BUTTON_PLAY = "Écouter"

TEMPO_SUFFIX = " BPM"
PERCENT_SUFFIX = " %"

DIALOG_SAVE_TITLE = "Choisir le fichier de sortie"
DIALOG_SAVE_FILTER = "Fichier audio WAV (*.wav)"

STATUS_IDLE = "Prêt."
STATUS_CANCELLING = "Annulation en cours."
STATUS_CANCELLED = "Rendu annulé."

STAGE_LABELS = {
    RenderStage.PREPARING: "Préparation de la grille",
    RenderStage.LAYERS: "Synthèse des couches",
    RenderStage.EFFECTS: "Chaînes d'effets",
    RenderStage.AUTOMATION: "Automation de mixage",
    RenderStage.REVERB: "Réverbération",
    RenderStage.SPECTRAL_TILT: "Basculement spectral",
    RenderStage.STEREO: "Image stéréo",
    RenderStage.DYNAMICS: "Dynamique de sortie",
    RenderStage.WRITING: "Écriture du fichier",
    RenderStage.DONE: "Terminé",
}

LOG_STARTED = "Rendu lancé, graine {seed}, {tonic} {mode}, {bpm:.1f} BPM."
LOG_STRUCTURE = "Structure {structure}, {sections} sections, {events} accords."
LOG_FINISHED = "Morceau écrit : {path}"
LOG_DURATION = "Durée {minutes:d} min {seconds:02d} s."
LOG_CANCELLED = "Rendu interrompu, aucun fichier écrit."
LOG_FAILED = "Échec du rendu : {reason}"

CLI_DESCRIPTION = "Génère un morceau sans ouvrir l'interface graphique."
CLI_HELP_CLI = "lance le rendu en ligne de commande"
CLI_HELP_SEED = "graine du générateur, la même graine rend le même morceau"
CLI_HELP_OUTPUT = "chemin du fichier WAV à écrire"
CLI_HELP_TONIC = "tonique en numéro MIDI"
CLI_HELP_MODE = "mode de la gamme"
CLI_HELP_TEMPO = "tempo en battements par minute"
CLI_HELP_STRUCTURE = "structure du morceau"
CLI_PROGRESS = "[{percent:3d} %] {stage}"

TAB_COMPOSITION = "Composition"
TAB_INSTRUMENTS = "Instruments"

GROUP_TRANSITIONS = "Enchaînement"
LABEL_HARD_CUT = "Coupes franches"
LABEL_SECTION_BLEND = "Fondu entre sections"
SECONDS_SUFFIX = " s"

LABEL_LAYER = "Couche"
LABEL_LAYER_ENABLED = "Couche active"
LABEL_LAYER_GAIN = "Niveau"
LABEL_TIMBRE = "Timbre"
LABEL_BRIGHTNESS = "Brillance"
LABEL_DETUNE = "Désaccord"
LABEL_ATTACK = "Attaque"
LABEL_CHARACTER = "Caractère"

GROUP_VOICE = "Voix"
GROUP_EFFECTS = "Chaîne d'effets"
BUTTON_ADD_EFFECT = "Ajouter"
BUTTON_REMOVE_EFFECT = "Retirer"
BUTTON_MOVE_UP = "Monter"
BUTTON_MOVE_DOWN = "Descendre"
EFFECTS_EMPTY = "Aucun effet sur cette couche."
DRUMS_WITHOUT_TIMBRE = "Les percussions ont leur propre synthèse, sans timbre à choisir."

BUTTON_PREVIEW = "Préécouter"
BUTTON_PREVIEW_STOP = "Arrêter la préécoute"
STATUS_PREVIEW_RENDERING = "Préparation de la préécoute."
STATUS_PREVIEW_PLAYING = "Préécoute en boucle."
LOG_PREVIEW_READY = "Préécoute prête, {seconds:.1f} s jouées en boucle."
LOG_PREVIEW_STOPPED = "Préécoute arrêtée."
LOG_NO_AUDIO_DEVICE = "Aucune sortie audio disponible sur ce poste."
