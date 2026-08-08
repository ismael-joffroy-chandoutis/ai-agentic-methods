#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Passe de fusion des constats d'un controle documentaire.

Sans elle, un controle automatise rend une decharge de constats que personne ne
lit. Mesure sur un cas reel : 118 constats bruts donnent 84 constats consolides,
et 69 en donnent 46. C'est l'equivalent machine du « je vous ai mis en gras les
points les plus critiques » d'un instructeur.

Entree  : des fichiers markdown de constats bruts, un par domaine de controle,
          chaque constat introduit par un identifiant « domaine-VERSION-NN ».
Sortie  : un rapport consolide, dedoublonne, hierarchise, regroupe par piece du
          dossier, avec une synthese d'avis en tete.

Cinq etapes :
  1. normalisation   : parsing des constats en tableau structure ;
  2. dedoublonnage   : regroupement par classe de defaut ;
  3. hierarchisation : bloquant > a corriger > vigilance, puis par impact ;
  4. neutralisation  : retrait des noms de tiers, table EXTERNE ;
  5. rendu           : synthese d'avis puis sections par piece.

Deux choix de conception a garder :

  - la fusion est DETERMINISTE. Le rapprochement de libelles proches par un
    modele est une option, desactivee par defaut, pour que la meme entree donne
    toujours la meme sortie et que le resultat soit rejouable gratuitement.
  - la table de neutralisation est un fichier separe, jamais en dur dans le code.
    C'est ce qui permet de publier l'outil sans publier les noms.

Format de constat reconnu (les deux variantes) :

    ### recevabilite-V1-03 — Notice de securite absente du dossier
    - **Severite** : bloquant
    - **Piece(s) concernee(s)** : dossier de securite
    - **Constat** : aucune piece ecrite du dossier de securite n'est fournie.
    - **Correction attendue** : produire la notice de securite signee.
    - **References** : <article applicable>

Usage :
    merge_findings.py --entree <repertoire> [--version V1|OLD|all]
                      [--neutralisation table.yaml] [--format md|json]
                      [--sortie rapport.md]

Licence : MIT (voir LICENSE-CODE).
"""
import argparse
import json
import os
import re
import sys
import unicodedata
from collections import OrderedDict

# --------------------------------------------------------------------------
# Etape 1 — normalisation
# --------------------------------------------------------------------------

RE_DEBUT_CONSTAT = re.compile(
    r"^(?:#{2,4}\s+|\*\*)"
    r"(?P<id>(?P<domaine>[a-zà-ÿ]+(?:-[a-zà-ÿ]+)*)-(?P<version>[A-Z0-9]+)-(?P<num>\d+))"
    r"\s*(?:—|–|-)\s*(?P<reste>.*)$",
    re.MULTILINE,
)

SEVERITES = OrderedDict([
    ("bloquant", 3),
    ("à corriger", 2),
    ("vigilance", 1),
    ("conforme", 0),
])

MOTIFS_SEVERITE = [
    ("bloquant", re.compile(r"bloquant", re.I)),
    ("à corriger", re.compile(r"[àa]\s+corriger", re.I)),
    ("vigilance", re.compile(r"vigilance", re.I)),
    ("conforme", re.compile(r"(?<!non )(?<!in)conforme", re.I)),
]

# Les libelles de champ tolerent les formes « Piece(s) concernee(s) » et
# « Pieces concernees » : un parseur qui ne les accepte pas rend un rapport
# silencieusement vide de ses pieces, ce qui casse le rangement final.
CHAMPS = {
    "severite": r"S[ée]v[ée]rit[ée]",
    "piece": r"Pi[èe]ce\(?s?\)?(?:\s+concern[ée]e\(?s?\)?)?",
    "constat": r"Constat",
    "correction": r"Correction\s+attendue",
    "references": r"R[ée]f[ée]rences?",
}


def sansaccent(s):
    return "".join(c for c in unicodedata.normalize("NFD", s or "")
                   if unicodedata.category(c) != "Mn").lower()


def normaliser(s):
    return re.sub(r"\s+", " ", sansaccent(s)).strip()


def champ(bloc, motif):
    """Recupere un champ ecrit en item de liste, sur une ou plusieurs lignes."""
    m = re.search(r"^[-*]?\s*\**\s*%s\s*\**\s*:\s*(?P<val>.+?)"
                  r"(?=\n\s*[-*]\s*\**\s*[A-ZÀ-Ý]|\n\s*\n|\Z)" % motif,
                  bloc, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    if not m:
        # Variante au fil du texte : « Piece : X. Constat... »
        m = re.search(r"%s\s*:\s*(?P<val>[^.\n]+)" % motif, bloc, re.IGNORECASE)
    return re.sub(r"\s+", " ", m.group("val")).strip(" .;") if m else ""


def severite_de(bloc, declaree):
    source = declaree or bloc
    for nom, motif in MOTIFS_SEVERITE:
        if motif.search(source):
            return nom
    return "vigilance"


def lire_constats(chemin):
    """Parse un fichier de constats en liste de dictionnaires structures."""
    texte = open(chemin, encoding="utf-8").read()
    debuts = list(RE_DEBUT_CONSTAT.finditer(texte))
    constats = []
    for i, m in enumerate(debuts):
        fin = debuts[i + 1].start() if i + 1 < len(debuts) else len(texte)
        bloc = texte[m.end():fin]
        titre = re.sub(r"\**\s*$", "", m.group("reste")).strip()
        declaree = champ(bloc, CHAMPS["severite"])
        constats.append({
            "id": m.group("id"),
            "domaine": m.group("domaine"),
            "version": m.group("version"),
            "titre": titre,
            "severite": severite_de(bloc, declaree),
            "piece": champ(bloc, CHAMPS["piece"]) or "non precisee",
            "constat": champ(bloc, CHAMPS["constat"]) or titre,
            "correction": champ(bloc, CHAMPS["correction"]),
            "references": champ(bloc, CHAMPS["references"]),
            "fichier": os.path.basename(chemin),
        })
    return constats


# --------------------------------------------------------------------------
# Etape 2 — dedoublonnage
# --------------------------------------------------------------------------

def classe_de_defaut(c):
    """Cle de regroupement : deux domaines qui voient le meme defaut fusionnent.

    Volontairement grossiere et deterministe : piece concernee + noyau du titre
    reduit a ses mots signifiants. A defaut de recouvrement, le constat garde sa
    classe propre et n'est pas fusionne.
    """
    mots = [w for w in re.findall(r"[a-zà-ÿ]{4,}", normaliser(c["titre"]))
            if w not in ("dans", "avec", "pour", "sans", "cette", "leur", "plus",
                         "aucun", "aucune", "entre", "selon", "toute", "tous")]
    noyau = " ".join(sorted(set(mots))[:6])
    return "%s|%s|%s" % (c["version"], normaliser(c["piece"]), noyau or c["id"])


def fusionner(constats):
    """Regroupe par classe de defaut. Un groupe = un constat consolide."""
    groupes = OrderedDict()
    for c in constats:
        groupes.setdefault(classe_de_defaut(c), []).append(c)

    consolides = []
    for cle, membres in groupes.items():
        pire = max(membres, key=lambda c: SEVERITES.get(c["severite"], 0))
        corrections, refs, pieces = [], [], []
        for m in membres:
            for val, acc in ((m["correction"], corrections),
                             (m["references"], refs),
                             (m["piece"], pieces)):
                if val and normaliser(val) not in [normaliser(x) for x in acc]:
                    acc.append(val)
        consolides.append({
            "classe": cle,
            "titre": pire["titre"],
            "severite": pire["severite"],
            "version": pire["version"],
            "pieces": pieces,
            "constat": pire["constat"],
            "corrections": corrections,
            "references": refs,
            "sources": [m["id"] for m in membres],
            "domaines": sorted({m["domaine"] for m in membres}),
        })
    return consolides


# --------------------------------------------------------------------------
# Etape 3 — hierarchisation
# --------------------------------------------------------------------------

def hierarchiser(consolides):
    """Bloquant > a corriger > vigilance ; a severite egale, par impact.

    L'impact est approxime par le nombre de domaines de controle qui ont vu le
    defaut : un defaut vu par trois domaines pese plus qu'un defaut isole.
    """
    return sorted(consolides,
                  key=lambda c: (-SEVERITES.get(c["severite"], 0),
                                 -len(c["domaines"]),
                                 normaliser(c["titre"])))


# --------------------------------------------------------------------------
# Etape 4 — neutralisation nominative
# --------------------------------------------------------------------------

def charger_neutralisation(chemin):
    """Table EXTERNE : [{motif: "...", remplacement: "..."}]. Jamais en dur.

    Deux sections : `noms` (substitutions nominatives) et `lissages`
    (corrections de lecture appliquees apres les substitutions).
    """
    if not chemin:
        return []
    import yaml
    table = yaml.safe_load(open(chemin, encoding="utf-8")) or {}
    regles = []
    for section in ("noms", "lissages"):
        for e in table.get(section, []):
            regles.append((re.compile(e["motif"]), e["remplacement"]))
    return regles


def neutraliser(texte, regles):
    for motif, remplacement in regles:
        texte = motif.sub(remplacement, texte)
    return texte


# --------------------------------------------------------------------------
# Etape 5 — rendu
# --------------------------------------------------------------------------

def synthese(consolides):
    n_bloq = sum(1 for c in consolides if c["severite"] == "bloquant")
    n_corr = sum(1 for c in consolides if c["severite"] == "à corriger")
    n_vig = sum(1 for c in consolides if c["severite"] == "vigilance")
    if n_bloq:
        avis = ("**Dépôt possible après reprise des %d constats bloquants ci-dessous**, "
                "chacun renvoyant à la pièce concernée et à la référence applicable." % n_bloq)
    elif n_corr:
        avis = "**Dépôt possible après reprise des %d constats ci-dessous.**" % n_corr
    else:
        avis = "**Aucun constat bloquant ni à corriger.**"
    return avis, (n_bloq, n_corr, n_vig)


def rendre_md(consolides, n_bruts, n_domaines, regles):
    avis, (n_bloq, n_corr, n_vig) = synthese(consolides)
    out = ["# Contrôle documentaire : avis consolidé", ""]
    out += ["## Avis", "", avis, "",
            "Périmètre : %d constats bruts issus de %d domaines de contrôle, "
            "consolidés en %d constats. Bloquants : %d · à corriger : %d · "
            "vigilance : %d." % (n_bruts, n_domaines, len(consolides),
                                 n_bloq, n_corr, n_vig), ""]

    # Rangement par piece, dans l'ordre ou les constats les ont citees.
    par_piece = OrderedDict()
    for c in consolides:
        par_piece.setdefault(c["pieces"][0] if c["pieces"] else "non précisée",
                             []).append(c)

    for piece, membres in par_piece.items():
        out += ["## %s" % neutraliser(piece, regles), ""]
        for c in membres:
            out.append("### %s — %s (%s)"
                       % (c["severite"].capitalize(),
                          neutraliser(c["titre"], regles),
                          ", ".join(c["sources"])))
            out.append("")
            out.append(neutraliser(c["constat"], regles))
            out.append("")
            for corr in c["corrections"]:
                out.append("- **Correction attendue** : %s" % neutraliser(corr, regles))
            if c["references"]:
                out.append("- **Références** : %s"
                           % neutraliser(" · ".join(c["references"]), regles))
            out.append("")

    out += ["## Traçabilité", "",
            "Chaque constat consolidé porte entre parenthèses les identifiants "
            "des constats bruts dont il est issu : la liste brute reste "
            "consultable telle quelle, constat par constat.", ""]
    return "\n".join(out)


# --------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--entree", required=True,
                   help="repertoire contenant les fichiers de constats bruts")
    p.add_argument("--motif-fichier", default=r"^controle-.*\.md$",
                   help="motif des fichiers de constats a lire")
    p.add_argument("--version", default="all",
                   help="ne traiter qu'une version de dossier, ou 'all'")
    p.add_argument("--neutralisation", default="",
                   help="table externe de substitutions nominatives (YAML)")
    p.add_argument("--format", choices=("md", "json"), default="md")
    p.add_argument("--sortie", default="")
    a = p.parse_args()

    if not os.path.isdir(a.entree):
        print("repertoire d'entree introuvable : %s" % a.entree, file=sys.stderr)
        return 2

    motif = re.compile(a.motif_fichier)
    bruts = []
    for f in sorted(os.listdir(a.entree)):
        if motif.match(f):
            bruts += lire_constats(os.path.join(a.entree, f))
    if a.version != "all":
        bruts = [c for c in bruts if c["version"].upper() == a.version.upper()]
    if not bruts:
        print("aucun constat lu : verifier --motif-fichier et le format des constats",
              file=sys.stderr)
        return 2

    regles = charger_neutralisation(a.neutralisation)
    consolides = hierarchiser(fusionner(bruts))
    n_domaines = len({c["domaine"] for c in bruts})

    if a.format == "json":
        rendu = json.dumps({"n_bruts": len(bruts), "n_domaines": n_domaines,
                            "constats": consolides}, ensure_ascii=False, indent=2)
    else:
        rendu = rendre_md(consolides, len(bruts), n_domaines, regles)

    if a.sortie:
        with open(a.sortie, "w", encoding="utf-8") as fh:
            fh.write(rendu + "\n")
        print("%d constats bruts -> %d consolides, ecrit dans %s"
              % (len(bruts), len(consolides), a.sortie))
    else:
        print(rendu)
    return 0


if __name__ == "__main__":
    sys.exit(main())
