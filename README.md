# Competitive Level-Based Foraging - IA & Jeux 2026

Projet universitaire réalisé dans le cadre du cours **IA & Jeux**.  
L’objectif est d’implémenter et de comparer plusieurs stratégies d’agents dans un environnement multi-agents compétitif de collecte de ressources.

## Binôme

- Jalil Keddara
- Kenzi Thiriet

## Présentation du projet

Le projet repose sur une simulation dans laquelle deux équipes de joueurs s’affrontent sur une carte.  
À chaque épisode, les agents doivent choisir des fioles à collecter. Chaque fiole possède ses propres règles de capture selon sa couleur :

- **Jaune** : nécessite au moins un joueur.
- **Rouge** : nécessite au moins deux joueurs de la même équipe.
- **Verte** : nécessite au moins trois joueurs au total.
- **Bleue** : suit une règle spécifique où un joueur seul peut parfois remporter la fiole face à une équipe adverse plus nombreuse.

Le but du projet est de définir plusieurs stratégies de décision, puis de les comparer expérimentalement sur différentes cartes.

## Objectifs

Le projet avait plusieurs objectifs :

- comprendre le moteur de simulation fourni ;
- implémenter le calcul des scores ;
- faire tourner plusieurs épisodes de jeu ;
- définir plusieurs stratégies d’agents ;
- comparer les stratégies sur différentes cartes ;
- analyser les résultats obtenus.

## Stratégies implémentées

Plusieurs stratégies ont été développées et comparées.

### Stratégie uniforme

Stratégie de référence.  
Les agents répartissent leurs choix de manière uniforme entre les fioles disponibles.  
Elle sert de baseline pour mesurer l’intérêt des stratégies plus avancées.

### Stratégie têtue

Stratégie rigide dans laquelle les agents conservent une logique fixe.  
Elle permet d’observer les limites d’un comportement peu adaptatif.

### Stratégie expert

Stratégie heuristique construite à la main.  
Elle utilise des règles simples pour choisir les fioles jugées les plus intéressantes selon la situation.

### Stratégie coordination

Stratégie pensée pour améliorer le comportement collectif.  
Elle cherche à mieux répartir les agents afin d’éviter les redondances inutiles et d’augmenter les chances de collecte.

### Stratégie fictitious play

Stratégie adaptative qui prend en compte le comportement passé de l’adversaire.  
Elle permet aux agents d’anticiper certaines décisions adverses.

### Stratégie regret matching

Stratégie basée sur l’idée de corriger progressivement les mauvais choix.  
Elle ajuste ses décisions à partir des résultats précédents.

## Organisation du code

Le projet est organisé autour de plusieurs fichiers principaux.

### `strategies.py`

Contient les différentes stratégies utilisées par les agents.  
Chaque stratégie correspond à une manière différente de choisir une cible ou une action.

### `engine.py`

Gère le déroulement de la simulation :

- lancement des épisodes ;
- déplacement des agents ;
- interaction entre les équipes ;
- calcul des scores ;
- enchaînement des parties.

### Fichiers `main_*.py`

Les fichiers de lancement permettent de comparer directement deux stratégies entre elles.  
Par exemple :

- `main_coordination_vs_expert.py`
- `main_uniforme_vs_uniforme.py`

Ils servent à configurer les duels, les cartes utilisées et les paramètres d’exécution.

## Cartes utilisées

Les stratégies ont été testées sur plusieurs cartes :

- Mixed
- Yellow
- Red
- Green
- Blue

Tester plusieurs cartes permet d’évaluer la robustesse des stratégies dans différents environnements.

## Protocole expérimental

Pour comparer les stratégies, nous avons lancé plusieurs duels entre elles.  
Chaque duel a été testé sur différentes cartes.

Les simulations ont été exécutées à **1000 fps** afin d’accélérer les expérimentations sans modifier le comportement des agents.

La mesure principale utilisée est le score final obtenu par chaque équipe à la fin des confrontations.

## Résultats principaux

Les résultats montrent que les stratégies simples, comme la stratégie têtue, manquent souvent de robustesse.  
La stratégie uniforme reste une baseline utile et peut parfois obtenir de bons résultats, notamment sur certaines cartes spécifiques.

Les stratégies plus avancées donnent globalement de meilleurs résultats.  
La stratégie coordination montre l’intérêt d’une meilleure répartition collective des agents.  
La stratégie fictitious play se révèle particulièrement forte grâce à sa capacité à exploiter le comportement adverse.  
La stratégie regret matching reste compétitive grâce à son mécanisme d’adaptation progressive.

Un point important observé est le rôle particulier de la carte Blue, qui modifie fortement l’équilibre entre les stratégies.

## Conclusion

Ce projet met en évidence l’importance de l’adaptation et de la coordination dans un environnement multi-agents compétitif.

Les stratégies les plus performantes ne sont pas seulement celles qui utilisent des règles complexes, mais celles qui prennent en compte l’environnement, les autres agents et les résultats passés.

Le projet montre aussi qu’il n’existe pas de stratégie universellement optimale : les performances dépendent fortement du type de carte et des règles associées aux ressources.
