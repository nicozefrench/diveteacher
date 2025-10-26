📚 1. Contenu et Documents
Q1.1: Quels types de documents de plongée allez-vous uploader ?
Manuels de certification PADI, SSI (documentation officielle ssi), FFESSM (MFT et autre pdf et ppt)
Procédures de sécurité et d'urgence > oui
Théorie de la plongée (physique, physiologie) > oui
Guides de planification de plongée > pas pour le moment
Réglementations locales/internationales > oui specialement en France
Autre (précisez) > MFT FFESSM officiel tout niveau, cours niveau 4 (N4), cours MF1 et instructeur (france) , exercice de pratique pour la plongée,  excercices d'entainement en piscine 
Q1.2: Dans quelle(s) langue(s) seront les documents ?
Français et Anglais 
Q1.3: Quelle est la taille moyenne des documents ?
Courts (< 10 pages) 
Longs (50-200 pages) > a determiner si je dois separer les long document en chapitre manageable pour le rag pipe 
Très longs (> 200 pages - manuels complets)  > a determiner si je dois separer les long document en chapitre manageable pour le rag pipe
👥 2. Utilisateurs et Cas d'Usage
Q2.1: Qui utilisera principalement DiveTeacher ?
[ ] Instructeurs de plongée (pour préparer cours) > oui
[ ] Élèves plongeurs (pour réviser)  > oui
[ ] Centres de plongée (référence rapide) > oui 
[ ] Examinateurs (préparation certifications) > non
Q2.2: Quels sont les cas d'usage principaux ?
[ ] "Quelles sont les procédures d'urgence pour un accident de décompression ?"
[ ] "Explique-moi la loi de Dalton en plongée"
[ ] "Quels sont les prérequis pour le niveau Advanced ?"
[ ] "Comment calculer la consommation d'air pour une plongée à 30m ?"
[ ] Autres exemples ?
répondre a toutes les question de facon trés précise sur la base des données ingérée via le pipe rag et graphiti inject dans les db aux utilisteurs avec les référence exactes incluant les schema ou image présentes dans les document d'origines. il y aura plusieurs forfait éléve en formation ou instructeur de plongée 
Q2.3: Besoin d'authentification multi-utilisateurs ?
Démarrage : Un seul utilisateur (vous) > oui
V1 : Multi-utilisateurs avec comptes séparés > oui et payant , a voir comment on inclu stripe paiement plus tard
V1 : Partage de documents entre utilisateurs > non 
V1: interface d'admin pour uploader les document de reference ppt et pdf a etre ingéré par le rag et knowledge graph pipe. on etandra l'interface admin dans les version suivante pour la collection des paiement, la creation et le management des comptes utilisateurs, le monitoring de l'app 
🎨 3. Interface et Expérience Utilisateur
Q3.1: Préférences de branding/design ?
Thème plongée (bleu océan, images sous-marines) > ok
Nom visible : "DiveTeacher" ou autre > diver teacher
Logo / icône spécifique > pour le moment on commence avec le logo "diver teacher" en typo
Q3.2: Fonctionnalités UI prioritaires pour V1 ?
 Upload simple de documents ✅ (déjà dans boilerplate) > oui mais avec une iterface ui pour l'admin qui permet de voir la liste des documents et le statis de l'injection. et aussi ajouter et supprimer des document. attention l'application doit fonctionner en ligne , ui sur vercel et back end et rag sur digotal ocean 
Chat Q&A streaming ✅ (déjà dans boilerplate) > oui en V1 on verra au fur est a mesure pour améliorer
Citations des sources avec numéros de page > non pas de numero de page juste la citation exact sans la source, si image ou schema alors montrer
Export des conversations en PDF > non je vois pas pourquoi juste le fait queles conversaion son "sauvée" poru chaque utilisateur donc il peut naviguer a travers les diverses conversations
Favoris / bookmarks des questions > non pas en V1
Visualisation du graphe de connaissances > uniquement access pour l'admin
Q3.3: Langue de l'interface utilisateur > Anglais et Français 
Bilingue avec switch FR/EN > oui 
🤖 4. LLM et Configuration Technique
Q4.1: Quel LLM voulez-vous utiliser pour V1 > mistral:7b-instruct-q5_K_M
Ollama local (gratuit, privé, mais nécessite machine puissante) ?
Modèle recommandé : llama3:8b ou mistral:7b ? > mistral:7b-instruct-q5_K_M
Claude API (payant, excellent pour contenu éducatif) > option de switch mais on commence par un modele opensource qui tournera sur digotal ocean 
OpenAI GPT-4 (payant, très performant) > pas du touyt 
Q4.2: Contraintes de coûts ?
Budget mensuel cible pour V1 > pas de contrainte pour la V1 l'optimisation se fera plus tard 
Préférence pour solution locale (gratuite) vs API (payante mais meilleure qualité) > y a pas de solution locale c'est une application en-ligne qui fonctionne 100% dans le cloud. on fait le dev en local sur un mac M1 max avec des instance docker. on peut imaginer tourner le modele LLM en local en test car on a 32 gig de ram unifiée 
Q4.3: Hébergement 
Backend (DigitalOcean) :
GPU Droplet - Basic AI/ML
├── GPU: NVIDIA T4 / RTX 3070 (8GB VRAM)
├── RAM: 16-24GB DDR4
├── CPU: 4-6 vCPUs
├── Storage: 100GB SSD
└── Prix: ~$100-150/mois 

GPU Droplet 8GB (RAM 16-24GB)          │
│  Prix: ~$100-150/mois                   │
│                                         │
│  GPU (8GB VRAM):                        │
│  ├── Mistral Q5_K_M: 5.2GB             │
│  └── Buffer: 2.8GB                      │
│                                         │
│  RAM (16GB+):                           │
│  ├── Backend API: 2GB                   │
│  ├── Qdrant: 6-8GB                      │
│  ├── PostgreSQL: 2GB                    │
│  └── OS: 2-4GB       

Frontend (Vercel) : on a deja un compte
📊 5. Données et Graphe de Connaissances
Q5.1: Types d'entités importantes pour la plongée ?
Certifications > toutes SSI et toute FFESSM en v1
Équipement (détendeur, ordinateur, combinaison...) > toute (présente dans les document qui seront ingest dans le rag et le knowledge graph 
Procédures (décompression, remontée d'urgence...)  > toute (présente dans les document qui seront ingest dans le rag et le knowledge graph 
Concepts (azote, narcose, flottabilité...)  > toute (présente dans les document qui seront ingest dans le rag et le knowledge graph 
Organismes:  SSI, FFESSM en V1 PADI en V2
Profondeurs, limites, paliers  > toute (présente dans les document qui seront ingest dans le rag et le knowledge graph . focus particulier sur la france avec plongée loisir max 60 m
[ ] Autres >  > toute (présente dans les document qui seront ingest dans le rag et le knowledge graph 
Q5.2: Relations importantes ?
"Certification A prérequis de Certification B" > oui , meme prérequis pour tel exercice a des prérequis (ex: on ne peut pas se mettre a l'eau si on a pas fait la discociation buco nazale) les documents qui seront demandé pointes deja les prerequis mais il faudra contruire un arbre de prerequis qui sera accessible et modifiable avec le compte admin
"Équipement X utilisé pour Procédure Y" > oui
"Concept A lié à Concept B" > oui
"Profondeur X nécessite Palier Y" > oui
Q5.3: Métadonnées importantes ?
Source SSI vs FFESSM pour la V1 on ajoutera d'autres écoles pour les versions suivantes
Niveau de certification concerné > tous dans les niveau des école donc les documents sont fournis (ex FFESSM du niveau 1 , N1 au MF1 et MF2)
Date/version du document > oui et source (meme si la source n'est pas acessible a l'utilisateur saud via le compte admin qui lui a access a plus d'outils)
Langue > Francais et anglais 
⚡ 6. Priorités pour V1 (MVP)
Q6.1: Quelle est votre deadline pour V1 > peut importe il fauat que cela marche nickel 
1 semaine (MVP minimal) > ok 
2-4 semaines (MVP complet) > ok on verra 
1-2 mois (version plus polieUltimate, plus de features) > ok pn verra 
Q6.2: Features absolument nécessaires pour V1 (ordre de priorité) ?
Upload documents + traitement → Graphe ✅
Q&A avec streaming ✅
Citations avec sources > non citation exacte des extraits sans la source juste l'ecole (SSI / FFESSM)
Interface en français > francais et anglais avec un toggle
Multi-utilisateurs > oui minimum 1 utilisateur et admin pour commencer (attention il faut peut etre supabase pour cela)
Visualisation graphe > pour admin uniquement
Export conversations > non
Autre > all admin fonction dicussed above. pour utilisateur que la partie chat avec recall et navigation a travers les chats passés
Q6.3: Qu'est-ce qui peut attendre la V2 ?
Fonctionnalités "nice to have" mais pas bloquantes > on verra au fur et a mesure
🔒 7. Sécurité et Conformité
Q7.1: Documents confidentiels > non
Matériel propriétaire (manuels sous copyright) > non
Besoin de garantir que données restent privées > oui les docuent d'origine stocké dans le back end et les sources doivent resté privé et uniquement accessible a travers les outils / fonctionanlité disponibles pour le compte admin 
l'app est en ligne c'est un service saas 
Q7.2: Besoin de tracking/audit > besoin de monitoring uniquement (sentry)
Qui a posé quelle question ? > uniquement pour l'admin
Export des logs pour analyse > biensur ,une solution saas monétisée professionnelle
