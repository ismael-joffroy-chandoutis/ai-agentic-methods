#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ancrage numerique : tout chiffre cite dans une sortie doit exister dans l'entree.

C'est le controle decisif d'une chaine de production de rapports, et ce n'est pas
un moteur : c'est du code. Il ne depend d'aucun fournisseur, il est deterministe,
et c'est lui qui attrape le chiffre invente.

Il sert aussi de juge dans une comparaison de moteurs : plusieurs moteurs de
familles differentes recoivent la meme entree et les memes consignes, et passent
exactement le meme controle. Sans validateur identique pour tous, des sorties
differentes ne prouvent rien.

Trois controles, cumulables :
  - chiffres non ancres : toute valeur numerique de la sortie absente de l'entree ;
  - vocabulaire proscrit : tournures interdites par les regles metier
    (comparaisons interdites, anglicismes, emojis, formulations bannies) ;
  - schema : presence et type des champs attendus d'une sortie JSON.

Tolerances prevues, parce qu'un chiffre legitime peut ne pas figurer tel quel dans
l'entree : les valeurs calculees (sommes, ecarts, pourcentages) se declarent en
liste blanche, et les petits entiers de langage courant s'ignorent par seuil.

Usage :
    numeric_grounding.py <entree.json|.txt|repertoire> <sortie.json> [--regles r.yaml]
Sortie : rapport lisible, code retour 1 si un controle echoue.

Licence : MIT (voir LICENSE-CODE).
"""
import json
import os
import re
import sys
import unicodedata

NOMBRE = re.compile(r"\d[\d   ]*(?:[.,]\d+)?")
EMOJI = re.compile("[\U0001F000-\U0001FAFF←-⇿☀-➿⬀-⯿]")

# En dessous de ce seuil, un entier est du langage courant (« les trois postes »,
# « en 2026 ») et non une donnee a ancrer.
SEUIL_ENTIER_IGNORE = 12


def normalise(txt):
    """Rend le texte comparable : espaces insecables et apostrophes uniformises."""
    txt = unicodedata.normalize("NFC", txt or "")
    for ch in (" ", " ", " "):
        txt = txt.replace(ch, " ")
    return txt.replace("’", "'")


def nombres(txt):
    """Ensemble des valeurs numeriques citees dans un texte."""
    vals = set()
    for m in NOMBRE.finditer(normalise(txt)):
        brut = m.group(0).strip()
        compact = brut.replace(" ", "").replace(",", ".")
        # Un separateur de milliers laisse un point parasite : « 1.234.567 ».
        if compact.count(".") > 1:
            compact = compact.replace(".", "")
        try:
            vals.add(round(float(compact), 4))
        except ValueError:
            continue
    return vals


def texte_de(chemin):
    """Concatene le texte d'un fichier ou de tous les fichiers d'un repertoire."""
    if os.path.isdir(chemin):
        morceaux = []
        for racine, _, fichiers in os.walk(chemin):
            for f in sorted(fichiers):
                if f.startswith("."):
                    continue
                morceaux.append(texte_de(os.path.join(racine, f)))
        return "\n".join(morceaux)
    try:
        with open(chemin, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def aplatir(obj, sortie=None):
    """Tout le texte d'une structure JSON, cles comprises."""
    sortie = [] if sortie is None else sortie
    if isinstance(obj, dict):
        for k, v in obj.items():
            sortie.append(str(k))
            aplatir(v, sortie)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            aplatir(v, sortie)
    elif obj is not None:
        sortie.append(str(obj))
    return sortie


def charger_sortie(chemin):
    """-> (texte complet, structure ou None)."""
    brut = texte_de(chemin)
    try:
        data = json.loads(brut)
    except (ValueError, TypeError):
        return brut, None
    return "\n".join(aplatir(data)), data


# ------------------------------------------------------------------ controles
def chiffres_non_ancres(texte_sortie, texte_entree, calculees=()):
    """Valeurs de la sortie absentes de l'entree et non declarees calculees."""
    tolerees = set(nombres(" ".join(str(c) for c in calculees)))
    ref = nombres(texte_entree)
    manquants = []
    for v in sorted(nombres(texte_sortie)):
        if v in ref or v in tolerees:
            continue
        if float(v).is_integer() and abs(v) <= SEUIL_ENTIER_IGNORE:
            continue
        manquants.append(v)
    return manquants


def vocabulaire_proscrit(texte_sortie, motifs):
    trouves = []
    bas = normalise(texte_sortie).lower()
    for m in motifs:
        if re.search(m, bas, re.IGNORECASE):
            trouves.append(m)
    if EMOJI.search(texte_sortie):
        trouves.append("emoji")
    return trouves


def schema_manquant(data, champs):
    if data is None:
        return list(champs)
    return [c for c in champs if c not in data]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        print("usage: numeric_grounding.py <entree> <sortie.json> [--regles r.yaml]",
              file=sys.stderr)
        return 2
    regles = {}
    if "--regles" in sys.argv:
        import yaml
        chemin_regles = sys.argv[sys.argv.index("--regles") + 1]
        regles = yaml.safe_load(open(chemin_regles, encoding="utf-8")) or {}
        args = [a for a in args if a != chemin_regles]

    texte_entree = texte_de(args[0])
    texte_sortie, data = charger_sortie(args[1])

    echecs = []

    manquants = chiffres_non_ancres(texte_sortie, texte_entree,
                                    regles.get("valeurs_calculees", []))
    if manquants:
        echecs.append("chiffres non ancres dans l'entree : %s"
                      % ", ".join("%g" % v for v in manquants))
    else:
        print("OK|ancrage numerique|toutes les valeurs citees existent dans l'entree")

    proscrits = vocabulaire_proscrit(texte_sortie, regles.get("motifs_proscrits", []))
    if proscrits:
        echecs.append("vocabulaire proscrit : %s" % ", ".join(proscrits))
    else:
        print("OK|vocabulaire|aucune tournure proscrite")

    champs = regles.get("champs_attendus", [])
    if champs:
        absents = schema_manquant(data, champs)
        if absents:
            echecs.append("champs attendus absents : %s" % ", ".join(absents))
        else:
            print("OK|schema|tous les champs attendus sont presents")

    for e in echecs:
        print("ECHEC|%s" % e)
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
