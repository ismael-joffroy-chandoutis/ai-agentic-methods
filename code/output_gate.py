#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Barriere de sortie : rien n'est declare reussi sans avoir ete ouvert et mesure.

Le defaut que ce controle corrige : un code retour nul sans aucun livrable
produit, double d'un message de controle de mise en page affiche alors qu'il n'y
avait rien a controler. Un code retour ne prouve rien ; seul un fichier ouvert et
mesure vaut reussite.

Controles, dans l'ordre, l'echec du premier arretant la sequence pour ce fichier :
  1. le fichier existe ;
  2. sa taille depasse le plancher configure (un fichier vide ou tronque est un
     echec, pas une reussite) ;
  3. il s'ouvre reellement comme le format attendu ;
  4. il porte au moins le nombre de pages attendu ;
  5. il ne contient aucune trace de fabrication (liste de jetons interdits) ;
  6. il ne contient aucune consigne de production recopiee ;
  7. il passe le controle mecanique des regles de mise en page, s'il est fourni.

A completer par l'ancrage des sources (voir source_anchoring.py) : cette barriere
mesure la forme, pas la veracite d'une attribution.

Configuration attendue (YAML) :

    production:
      taille_min_octets: 40000
      pages_min: 12
      controle_mise_en_page: true
    barriere:
      jetons_interdits: ["<nom d'outil>", "<marqueur de gabarit>"]
      motifs_consigne:  ["\\btodo\\b", "a retirer"]

Usage : output_gate.py <config.yaml> <repertoire_sortie> <fichier1> [fichier2...]
Variable d'environnement optionnelle : LAYOUT_CHECK=<script de mise en page>.
Sortie : lignes « OK|... » et « ECHEC|... », code retour 1 si un controle echoue.

Licence : MIT (voir LICENSE-CODE).
"""
import os
import re
import subprocess
import sys

import yaml

# Defauts prudents. La liste reelle se declare en configuration : elle depend du
# gabarit et de la chaine de production, et elle a vocation a grandir a chaque
# incident constate.
JETONS_INTERDITS_DEFAUT = [
    "prompt", "pipeline", "lorem ipsum",
    "xxx", "a completer", "à compléter", "placeholder",
]
# Consignes de production recopiees dans le document : l'incident qui a motive
# ce controle est arrive deux fois de suite sur le meme livrable.
MOTIFS_CONSIGNE_DEFAUT = [
    r"c'?[ée]tait une consigne", r"consigne pour la mise en forme",
    r"[àa] retirer", r"ne pas int[ée]grer",
    r"\btodo\b", r"\bfixme\b",
]


def texte_du_deck(prs):
    """Tout le texte du document : formes et cellules de tableau."""
    out = []
    for slide in prs.slides:
        for sh in slide.shapes:
            if sh.has_text_frame and sh.text_frame.text:
                out.append(sh.text_frame.text)
            if getattr(sh, "has_table", False) and sh.has_table:
                for row in sh.table.rows:
                    for cell in row.cells:
                        out.append(cell.text)
    return "\n".join(out)


def main():
    if len(sys.argv) < 4:
        print("usage: output_gate.py <config.yaml> <repertoire_sortie> <fichier...>",
              file=sys.stderr)
        return 2
    cfg = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
    outdir = sys.argv[2]
    attendus = sys.argv[3:]
    prod = cfg.get("production", {})
    barr = cfg.get("barriere", {})
    taille_min = int(prod.get("taille_min_octets", 40000))
    pages_min = int(prod.get("pages_min", 12))
    jetons = [j.lower() for j in barr.get("jetons_interdits", JETONS_INTERDITS_DEFAUT)]
    motifs = barr.get("motifs_consigne", MOTIFS_CONSIGNE_DEFAUT)
    echecs = []

    for nom in attendus:
        chemin = nom if os.path.isabs(nom) else os.path.join(outdir, nom)
        base = os.path.basename(chemin)

        if not os.path.isfile(chemin):
            echecs.append("ECHEC|%s|fichier absent" % base)
            continue
        taille = os.path.getsize(chemin)
        if taille < taille_min:
            echecs.append("ECHEC|%s|taille %d octets sous le plancher %d"
                          % (base, taille, taille_min))
            continue
        try:
            from pptx import Presentation
            prs = Presentation(chemin)
            n = len(prs.slides._sldIdLst)
        except Exception as e:                       # noqa: BLE001
            echecs.append("ECHEC|%s|fichier illisible : %s" % (base, e))
            continue
        if n < pages_min:
            echecs.append("ECHEC|%s|%d pages, minimum attendu %d" % (base, n, pages_min))
            continue

        bas = texte_du_deck(prs).lower()
        trouves = [j for j in jetons if j in bas]
        if trouves:
            echecs.append("ECHEC|%s|trace de fabrication dans le document : %s"
                          % (base, ", ".join(trouves)))
            continue
        consignes = [m for m in motifs if re.search(m, bas)]
        if consignes:
            echecs.append("ECHEC|%s|consigne de production recopiee dans le document : %s"
                          % (base, ", ".join(consignes)))
            continue

        print("OK|%s|%d octets, %d pages, aucun jeton interdit" % (base, taille, n))

    if not echecs and prod.get("controle_mise_en_page", True):
        check = os.environ.get("LAYOUT_CHECK", "")
        presents = [n if os.path.isabs(n) else os.path.join(outdir, n) for n in attendus]
        presents = [p for p in presents if os.path.isfile(p)]
        if check and os.path.isfile(check) and presents:
            r = subprocess.run([sys.executable, check] + presents,
                               capture_output=True, text=True)
            if r.returncode != 0:
                echecs.append("ECHEC|mise-en-page|%s" % r.stdout.strip().replace("\n", " · "))
            else:
                print("OK|mise-en-page|regles respectees")
        else:
            # Une degradation propre doit rester bruyante : en production, tracer
            # ce cas comme une anomalie d'exploitation, pas comme un succes.
            echecs.append("ECHEC|mise-en-page|verificateur introuvable, controle non execute")

    for e in echecs:
        print(e)
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
