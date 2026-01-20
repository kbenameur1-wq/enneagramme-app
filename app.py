import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from fpdf import FPDF
import tempfile
import numpy as np
import io
import os
import sqlite3
import json
import hashlib
import time
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================
st.set_page_config(page_title="Ennéagramme Pro V2", layout="wide", page_icon="🧩")

# ==========================================
# CONSTANTES & DONNÉES PÉDAGOGIQUES (ENRICHIES)
# ==========================================

TYPE_SEQUENCE = [8, 9, 1, 2, 3, 4, 5, 6, 7]

ENNEAGRAM_INFO = {
    1: {
        "nom": "Le Perfectionniste",
        "desc": """Le type 1 est motivé par un désir profond de bien faire les choses, d'améliorer le monde et d'éviter l'erreur. Rationnels et consciencieux, ils possèdent une boussole morale très forte. Ils cherchent constamment à aligner leurs actions sur leurs principes élevés. Cependant, cette quête de perfection s'accompagne souvent d'un "critique intérieur" impitoyable qui juge leurs moindres faits et gestes, ainsi que ceux des autres. Sous stress, ils peuvent devenir rigides, irritables et moralisateurs, ressentant de la colère contenue (ressentiment) face à ce qu'ils perçoivent comme du laxisme chez autrui. Ils ont fondamentalement peur d'être "mauvais", défectueux ou corrompus.""",
        "forces": [
            "Intégrité et éthique irréprochables.",
            "Sens du détail et rigueur organisationnelle.",
            "Fiabilité : ils font ce qu'ils disent.",
            "Désir sincère d'amélioration et de justice."
        ],
        "vigilance": [
            "Critique excessive envers soi-même et les autres.",
            "Difficulté à déléguer (peur que ce soit mal fait).",
            "Ressentiment et colères refoulées.",
            "Rigidité face aux changements de plans."
        ],
        "recommandations": """Pour votre développement, le chemin consiste à passer de la rigidité à la sérénité. Apprenez à accepter que l'imperfection fait partie intégrante de la condition humaine et de la nature.
        
1. **Calmez votre critique intérieur** : Lorsque vous entendez cette voix qui vous juge, notez-la mais ne l'écoutez pas aveuglément. Dites-vous : "Je fais de mon mieux et c'est suffisant."
2. **Pratiquez le lâcher-prise** : Accordez-vous délibérément des moments de "non-productivité". Le plaisir sans but n'est pas un péché, c'est une nécessité pour votre équilibre.
3. **Développez la tolérance** : Essayez de voir les erreurs (les vôtres et celles des autres) comme des opportunités d'apprentissage plutôt que comme des fautes morales. La perfection n'est pas la seule voie vers l'excellence.
4. **Exprimez votre colère** : Au lieu de ravaler votre irritation jusqu'à l'explosion ou l'implosion, apprenez à exprimer vos frustrations au fur et à mesure, de manière constructive."""
    },
    2: {
        "nom": "L'Aidant",
        "desc": """Le type 2 est orienté vers les relations humaines. Chaleureux, empathiques et démonstratifs, ils trouvent leur valeur dans le service aux autres et le sentiment d'être indispensables. Ils sont exceptionnellement doués pour percevoir les besoins émotionnels de leur entourage, souvent avant même que les personnes concernées n'en soient conscientes. Cependant, cette générosité cache souvent une peur profonde de ne pas être aimé pour ce qu'ils sont, mais uniquement pour ce qu'ils donnent. Ils peuvent avoir tendance à négliger leurs propres besoins jusqu'à l'épuisement, et devenir envahissants ou manipulateurs s'ils ne reçoivent pas la reconnaissance qu'ils attendent secrètement.""",
        "forces": [
            "Empathie profonde et intelligence émotionnelle.",
            "Générosité et altruisme naturel.",
            "Capacité à encourager et soutenir les autres.",
            "Adaptabilité relationnelle."
        ],
        "vigilance": [
            "Négligence de ses propres besoins (épuisement).",
            "Orgueil : croire qu'on n'a besoin de l'aide de personne.",
            "Intrusivité : aider sans qu'on le demande.",
            "Attente inconsciente de réciprocité."
        ],
        "recommandations": """Votre croissance passe par la découverte de l'humilité (reconnaître vos propres besoins) et de l'autonomie émotionnelle. Vous n'avez pas besoin d'acheter l'amour par vos services.
        
1. **Écoutez-vous** : Prenez l'habitude de vous demander plusieurs fois par jour : "De quoi ai-je besoin, moi, en ce moment ?". Et donnez-le vous.
2. **Apprenez à dire NON** : Refuser une demande n'est pas un rejet de l'autre, c'est un respect de vos limites. Cela rend votre OUI plus authentique.
3. **Laissez les autres se débrouiller** : Parfois, votre aide empêche les autres de grandir. Faites confiance à leur capacité à résoudre leurs propres problèmes.
4. **Acceptez de recevoir** : Laissez les autres vous aider. C'est un cadeau que vous leur faites en les laissant exprimer leur affection."""
    },
    3: {
        "nom": "Le Compétiteur",
        "desc": """Le type 3 est l'incarnation de l'énergie, de l'efficacité et de la volonté de réussir. Pragmatiques et orientés vers l'action, ils cherchent à atteindre des objectifs ambitieux pour se sentir valables. Ce sont des caméléons sociaux capables de s'adapter à n'importe quel environnement pour y briller. Cependant, ils risquent de confondre leur véritable identité avec leur travail ou leur image sociale. Leur peur fondamentale est l'échec et d'être perçus comme "sans valeur". Sous stress, ils peuvent devenir opportunistes, trompeurs (enjolivant la vérité) et se couper totalement de leurs émotions pour rester performants, risquant le burnout.""",
        "forces": [
            "Efficacité et productivité exceptionnelles.",
            "Optimisme et capacité à motiver les équipes.",
            "Adaptabilité et charisme.",
            "Orientation résultats."
        ],
        "vigilance": [
            "Confusion entre l'être et le faire (travaholisme).",
            "Compétitivité excessive.",
            "Impatience face à l'inefficacité.",
            "Tendance à masquer ses faiblesses."
        ],
        "recommandations": """Votre défi est de retrouver l'authenticité et de comprendre que vous êtes aimé pour qui vous êtes, pas pour ce que vous faites.
        
1. **Ralentissez** : Intégrez des pauses où vous ne faites "rien". C'est souvent là que vos vraies émotions émergent.
2. **Soyez vrai** : Osez montrer vos faiblesses ou vos échecs à des proches. Vous verrez que cela renforce les liens au lieu de les briser.
3. **Définissez votre propre succès** : Vos objectifs sont-ils vraiment les vôtres, ou ceux valorisés par la société/votre entreprise ? Reconnectez-vous à vos valeurs profondes.
4. **Pratiquez la bienveillance** : Envers vous-même en cas d'échec, et envers les autres qui n'ont pas votre rapidité."""
    },
    4: {
        "nom": "L'Individualiste",
        "desc": """Le type 4 est un être sensible, introspectif et en quête de sens. Ils se sentent souvent différents, uniques, voire incompris, comme s'il leur manquait quelque chose que les autres possèdent (le bonheur simple). Ils sont attirés par l'authenticité émotionnelle, la beauté et l'expression de soi. Ils vivent leurs émotions avec une grande intensité. Leur piège est l'envie : ils comparent leur ressenti intérieur complexe avec l'apparence heureuse des autres. Sous stress, ils peuvent sombrer dans la mélancolie, le drame ou se retirer du monde pour protéger leur identité fragile.""",
        "forces": [
            "Grande créativité et sens esthétique.",
            "Capacité à supporter la souffrance et profondeur émotionnelle.",
            "Authenticité et quête de vérité personnelle.",
            "Compassion pour la souffrance d'autrui."
        ],
        "vigilance": [
            "Humeur changeante et instabilité émotionnelle.",
            "Envie et comparaison constante.",
            "Repli sur soi et narcissisme mélancolique.",
            "Dramatisation des situations."
        ],
        "recommandations": """Votre voie d'évolution est l'équanimité émotionnelle. Vous devez apprendre à ne pas vous laisser emporter par chaque vague de sentiment.
        
1. **Discipline et Routine** : Paradoxalement, une structure quotidienne rigoureuse vous aide à ne pas vous noyer dans vos humeurs. Faites votre lit, même si vous êtes triste.
2. **Action plutôt qu'introspection** : Lorsque vous tournez en rond dans vos pensées, agissez. L'action physique coupe court à la rumination mentale.
3. **Appréciez l'ordinaire** : Cherchez la beauté dans le quotidien banal, pas seulement dans l'exceptionnel ou le tragique.
4. **Sortez de vous-même** : Intéressez-vous sincèrement aux autres. Cela vous soulagera du poids de votre propre introspection permanente."""
    },
    5: {
        "nom": "L'Observateur",
        "desc": """Le type 5 est un cérébral qui cherche à comprendre le monde pour s'y sentir en sécurité. Ils accumulent des connaissances, analysent et observent avec détachement. Ils ont un besoin vital d'intimité et protègent farouchement leur temps et leur énergie, qu'ils perçoivent comme des ressources limitées. Ils craignent d'être envahis ou de ne pas être compétents pour faire face à la vie. Sous stress, ils s'isolent physiquement et émotionnellement, devenant cyniques ou intellectuellement arrogants, coupés de leur corps et de leurs sentiments.""",
        "forces": [
            "Esprit analytique et visionnaire.",
            "Objectivité et calme en situation de crise.",
            "Curiosité intellectuelle et expertise.",
            "Indépendance et autonomie."
        ],
        "vigilance": [
            "Isolement social et détachement émotionnel.",
            "Avarice de son temps et de sa présence.",
            "Intellectualisation des sentiments.",
            "Négligence des besoins physiques."
        ],
        "recommandations": """Votre défi est de vous engager dans la vie et de partager ce que vous savez et ce que vous êtes.
        
1. **Reconnectez-vous au corps** : Pratiquez une activité physique régulière (sport, yoga, marche) pour "descendre" de votre tête.
2. **Osez l'intimité** : Forcez-vous doucement à partager vos sentiments, pas seulement vos pensées. Prenez le risque d'être touché émotionnellement.
3. **Participez** : Ne restez pas en périphérie. Votre savoir est utile, mais il ne prend valeur que s'il est partagé et appliqué.
4. **La spontanéité** : Essayez d'agir sans avoir toutes les informations. La vie ne peut pas être entièrement maîtrisée par l'esprit avant d'être vécue."""
    },
    6: {
        "nom": "Le Loyaliste",
        "desc": """Le type 6 est centré sur la sécurité, la loyauté et l'anticipation des risques. Dotés d'une grande imagination, ils envisagent souvent le "pire scénario" pour s'y préparer. Ils sont dévoués à leurs groupes ou à leurs autorités de confiance, mais peuvent aussi être rebelles s'ils doutent de ces autorités. L'anxiété est leur toile de fond. Ils cherchent la certitude et le soutien. Sous stress, ils deviennent soupçonneux, indécis, ou au contraire réactifs et agressifs (contre-phobiques) pour devancer le danger perçu.""",
        "forces": [
            "Loyauté indéfectible et fiabilité.",
            "Esprit d'équipe et solidarité.",
            "Vigilance et capacité à anticiper les problèmes.",
            "Courage (agir malgré la peur)."
        ],
        "vigilance": [
            "Anxiété chronique et doute de soi.",
            "Scénarios catastrophes (paranoïa).",
            "Indécision ou procrastination par peur de l'erreur.",
            "Vision du monde comme un lieu hostile."
        ],
        "recommandations": """Votre chemin est celui de la confiance en soi et du courage intérieur. Vous possédez votre propre guidance.
        
1. **Observez votre peur** : Acceptez votre anxiété sans la laisser diriger vos actions. Demandez-vous : "Est-ce un danger réel ou une projection de mon esprit ?"
2. **Développez l'optimisme** : Pour chaque scénario catastrophe imaginé, forcez-vous à imaginer aussi le scénario où tout se passe bien.
3. **Faites-vous confiance** : Arrêtez de demander l'avis de tout le monde avant de décider. Vous avez les compétences pour juger par vous-même.
4. **Calmez votre esprit** : La méditation ou la respiration sont essentielles pour apaiser votre mental hyperactif."""
    },
    7: {
        "nom": "L'Épicurien",
        "desc": """Le type 7 est un optimiste insatiable, spontané et polyvalent. Ils cherchent à multiplier les expériences excitantes et les options pour éviter à tout prix l'ennui, la frustration ou la souffrance intérieure. Leur esprit papillonne d'une idée à l'autre, planifiant toujours le futur. Ils apportent de la joie et de l'énergie, mais ont du mal à s'engager dans la durée ou à traiter les émotions négatives. Sous stress, ils deviennent impulsifs, dispersés, superficiels et fuient les contraintes.""",
        "forces": [
            "Enthousiasme contagieux et optimisme.",
            "Créativité et rapidité d'esprit.",
            "Curiosité et ouverture à la nouveauté.",
            "Capacité à rebondir après un échec."
        ],
        "vigilance": [
            "Impulsivité et difficulté à finir les tâches.",
            "Fuite des problèmes émotionnels.",
            "Intempérance (excès de nourriture, fêtes, projets...).",
            "Égoïsme inconscient (ma liberté avant tout)."
        ],
        "recommandations": """Votre évolution passe par la sobriété et la capacité à vivre le moment présent, même quand il est désagréable.
        
1. **Restez présent** : Lorsque l'ennui ou une émotion triste survient, ne fuyez pas vers un nouveau projet. Restez avec l'émotion, elle finira par passer.
2. **Finissez ce que vous commencez** : La satisfaction profonde vient de l'accomplissement, pas juste du démarrage. Choisissez moins de projets, mais menez-les au bout.
3. **Écoutez les autres** : Parfois, votre rapidité et votre verbiage empêchent les autres d'exister. Apprenez le silence et l'écoute active.
4. **La qualité sur la quantité** : Appréciez une seule chose en profondeur plutôt que dix en surface (une conversation, un plat, un livre)."""
    },
    8: {
        "nom": "Le Leader",
        "desc": """Le type 8 est une force de la nature : assertif, direct et protecteur. Ils ont un besoin viscéral de contrôler leur environnement et leur destin pour éviter d'être vulnérables ou dominés. Ils respectent la force et le courage, et prennent naturellement le commandement. Ils sont très protecteurs envers "les leurs". Cependant, leur intensité peut intimider. Ils ont tendance à nier leurs propres faiblesses et à voir le monde en noir et blanc (forts vs faibles). Sous stress, ils deviennent agressifs, tyranniques et se coupent de leur cœur.""",
        "forces": [
            "Courage, leadership et prise de décision.",
            "Franchise et honnêteté directe.",
            "Protection des faibles et sens de la justice.",
            "Énergie vitale et capacité d'action."
        ],
        "vigilance": [
            "Colère et agressivité intimidante.",
            "Déni de sa propre vulnérabilité.",
            "Excès (travail, plaisirs, confrontations).",
            "Difficulté à reconnaître ses torts."
        ],
        "recommandations": """Votre grandeur réelle viendra de votre capacité à montrer votre vulnérabilité et à utiliser votre force avec douceur.
        
1. **Acceptez votre fragilité** : Être touché ou triste n'est pas être faible, c'est être humain. Osez baisser la garde avec vos proches.
2. **Modérez votre impact** : Réalisez que votre voix ou votre présence peut être plus intimidante que vous ne le pensez. Parlez moins fort, écoutez plus.
3. **La patience** : Tout le monde n'a pas votre énergie ou votre rapidité de décision. Ne jugez pas la lenteur comme de la faiblesse.
4. **L'innocence** : Retrouvez la part d'enfant en vous qui n'a pas besoin de se battre contre le monde entier. Tout n'est pas un rapport de force."""
    },
    9: {
        "nom": "Le Médiateur",
        "desc": """Le type 9 est le pacificateur, cherchant l'harmonie intérieure et extérieure. Faciles à vivre, rassurants et acceptants, ils ont un don pour comprendre tous les points de vue. Cependant, pour éviter les conflits et les tensions, ils ont tendance à s'effacer, à fusionner avec les désirs des autres et à "s'anesthésier" (par la routine, la nourriture, la TV) pour ne pas ressentir de dérangement. Leur colère est souvent refoulée et se manifeste par de l'entêtement passif ou de la procrastination. Ils ont du mal à dire non et à définir leurs propres priorités.""",
        "forces": [
            "Diplomatie et capacité à apaiser les conflits.",
            "Écoute empathique et non-jugement.",
            "Patience et stabilité.",
            "Vision globale et inclusive."
        ],
        "vigilance": [
            "Procrastination et inertie (résistance au changement).",
            "Difficulté à dire non et à s'affirmer.",
            "Oubli de soi (fusion avec les autres).",
            "Minimisation des problèmes."
        ],
        "recommandations": """Votre défi est de vous réveiller à vous-même et de comprendre que votre présence et votre opinion comptent.
        
1. **Affirmez-vous** : Osez exprimer votre désaccord, même sur des petites choses. Le monde ne s'écroulera pas si vous créez un léger conflit.
2. **Fixez des priorités** : Ne vous laissez pas distraire par le non-essentiel. Faites la tâche la plus importante en premier.
3. **Restez conscient** : Remarquez quand vous passez en "pilote automatique" (narcotisation). Revenez à votre corps et à l'action.
4. **La colère est une énergie** : Ne la voyez pas comme quelque chose de mauvais, mais comme un carburant qui vous indique que vos limites ont été franchies. Utilisez-la pour agir."""
    }
}

CSV_DATA_BACKUP = """No,Question
1,"Je passe pour quelqu’un de coriace et les autres y regardent à deux fois avant de me marcher sur les pieds"
2,"Je sais garder mon calme en situation de conflit. Contrairement à d’autres, cela ne m’émeut pas"
3,"Je sens que j’ai une responsabilité morale à intervenir pour corriger les choses quand les gens font des erreurs"
4,"J’ai tendance à me sacrifier pour les autres et je me sens bien lorsque je leur consacre mon temps et mon énergie"
5,"J’aime que mes efforts soient payants et qu’ils m’apportent succès et reconnaissance"
6,"Je me sens différent des autres, étranger à la façon dont la plupart expriment leurs sentiments"
7,"Je suis une personne indépendante qui tient particulièrement à sa vie privée et à avoir du temps pour elle"
8,"Quand j’ai des décisions importantes à prendre, je demande l’avis des autres, car ce genre de situations m’insécurise"
9,"Je me sens frustré par les règles qui n’ont pas lieu d’être, par les limitations et par le fait de risquer de passer à côté d’opportunités intéressantes"
10,"C’est important pour moi d’éprouver un sentiment d’union avec les autres et d’éviter les conflits"
11,"Je sais comment les choses doivent être faites et je ne tolère pas l’imperfection, à commencer par ce qui me concerne"
12,"Je consacre volontiers mon temps libre à aider les autres et je trouve gratifiant de sentir qu’ils ont besoin de moi"
13,"Je suis attentif à donner une image de gagnant pour ce qui est de ma carrière et de mon style de vie"
14,"Je suis enclin à me plonger dans les fantasmes et les souvenirs, ce qui peut à l’occasion me faire passer pour quelqu’un qui s’apitoie sur son propre sort"
15,"Je fonctionne de façon objective et je résous les problèmes sans en discuter avec les autres"
16,"C’est lorsque je fais ce qu’il faut pour que les relations avec les autres se passent en douceur que je me sens le mieux"
17,"J’aime être toujours partant, avoir un calendrier bien rempli et il est exclu pour moi de ne pas profiter de la vie"
18,"Je fais ce qu’il faut pour atteindre les objectifs fixés, quitte à mettre la pression sur les autres, si besoin"
19,"Je me reproche souvent de ne pas avoir fait aussi bien que je l’aurais dû et j’ai tendance à faire la même critique aux autres"
20,"Je me perçois comme quelqu’un d’affectueux, dépendant sur le plan émotionnel et parfois possessif avec ceux que j’aime"
21,"Je tiens beaucoup à faire bonne impression. C’est important pour atteindre mes objectifs et obtenir la reconnaissance que je souhaite"
22,"Je suis une personne sensible et je mobilise mon imagination et mes sentiments pour résoudre la plupart des problèmes"
23,"Je préfère garder mes pensées pour moi et résoudre les problèmes par ma seule réflexion"
24,"Je suis prudent et je me sens anxieux lorsque je dois prendre d’importantes décisions sans le soutien des autres"
25,"Ca m’est égal d’être excessif ou de faire entorse à certaines règles, si cela peut me permettre de vivre différentes situations excitantes"
26,"J’ai confiance en ma force et en mon courage. Lorsque vient le moment de prendre position je ne fais pas de compromis"
27,"Je suis prêt à faire tout mon possible pour éviter les discussions houleuses ou les conflits"
28,"Je suis un négociateur coriace et comme je sais prendre le contrôle des situations, j’en sors généralement gagnant"
29,"Je suis ambitieux et je me pousse pour réaliser mes objectifs"
30,"Je me lance souvent dans de nouveaux projets ou de nouvelles aventures avant même que ceux qui sont en cours ne soient terminés"
31,"Je suis un être unique et souvent incompris des autres"
32,"Je tiens tellement à vivre de façon tranquille et harmonieuse que j’ai parfois tendance à me voiler la face à propos de problèmes pourtant sérieux"
33,"Je préfère me tenir à l’écart et observer les autres plutôt que de me trouver pris dans des conversations superficielles ou dans leurs problèmes émotionnels"
34,"Je veux tenir une place importante dans la  vie des autres. Savoir qu’ils ont besoin de moi est important pour mon bonheur"
35,"Je fais tout pour être efficace, parfait et au-dessus de toute critique."
36,"Il y a toujours quelque chose qui me préoccupe ou m’inquiète"
37,"Lorsque trop de choix s’offrent à moi, j’ai du mal à rester centré et à ne pas me disperser"
38,"Je vis avec passion et intensité mes sentiments et mes goûts raffinés et hors du commun"
39,"En société, je préfère apprendre des choses sur les autres plutôt que d’en révéler sur moi"
40,"J’appréhende souvent que quelque chose de grave ne m’arrive ou n’arrive à mes proches"
41,"Je m’efforce sans cesse d’être quelqu’un de bon, fiable, efficace et de parole."
42,"Dans ma vie, aimer et être aimé comptent plus que pratiquement tout le reste"
43,"Si mon plan d’action ne marche pas, je change simplement de stratégie et je me donne les moyens de faire ce qu’il faut pour atteindre mon but par une autre voie"
44,"J’ai tellement tendance à voir le côté positif des choses, que je peux parfois passer pour quelqu’un d’irresponsable et coupé de la réalité"
45,"J’ai une forte volonté et je n’hésite pas à faire usage de mon pouvoir pour obtenir ce que je veux ou pour protéger mes proches et mes amis"
46,"Je sais ce qui est bien et j’aimerais que les autres travaillent aussi dur que moi pour parvenir à cet idéal"
47,"Mon souci des autres me donnent envie de les aider par tous les moyens dont je dispose"
48,"J’attache de l’importance à la loyauté et aux avantages que procure l’appartenance à un groupe et ce de façon plus marquée que la plupart des gens"
49,"Je suis compétitif, fort et direct. Je peux être très exigeant avec les autres si c‘est nécessaire"
50,"Je ne comprends pas pourquoi certaines personnes ont tant de mal à voir le bon côté des choses"
51,"Je sais me motiver tout seul et je garde les yeux fixés sur mon objectif jusqu’à ce qu’il soit atteint."
52,"Je suis souvent absorbé dans mon univers intérieur, malheureux ou envieux de ce que les autres ont et qui me manque"
53,"Lorsque quelqu’un me demande ce que je ressens, je ne suis pas à l’aise car je considère que mes sentiments ne regardent que moi"
54,"Je préfère abonder dans le sens des autres si cela peut permettre de créer un climat de bonne entente, dans lequel chacun peut se sentir calme et fonctionner de façon relax"
55,"Quand il s’agit de réfléchir à des projets qui me semblent intéressants, je préfère le faire seul"
56,"Je suis quelqu’un qui « en veut ». J’au le goût d’entreprendre et j’ai suis plus tourné vers la réussite que les autres"
57,"Les notions de bien et de mal sont importantes pour moi. Les gens qui s’en fichent, qui sont négligés ou brouillons, me mettent en colère"
58,"Les autres ne peuvent pas comprendre ce que je ressens vraiment et je me retrouve parfois seul du fait de ma personnalité particulière"
59,"Je suis extrêmement loyal envers les gens et les groupes dont je fais part et j’espère qu’eux aussi le sont à mon égard"
60,"Je suis capable d’utiliser la force pour parvenir à mes fins, surtout si on m’y contraint"
61,"Je suis tourné vers les autres, nourricier et j’ai envie de me sentir proche d’eux"
62,"Je peux parfois être trop complaisant, donner aux autres l’impression de « planer » et de me laisser vivre"
63,"Je sais prendre du bon temps avec les plupart des gens que je fréquente, car c’est une évidence pour moi qu’on a intérêt à profiter au maximum des situations qui se présentent"
64,"Les autres me décrivent comme quelqu’un qui a les pieds sur terre, qui est brusque, solide et bagarreur"
65,"Je me laisse parfois tellement absorber par mes émotions que je remets tout en question et que je me replie sur moi"
66,"Pour me sentir protégé et en sécurité, je veille à ce que les choses se passent bien pour le groupe auquel j’appartiens et j’y apporte toute ma contribution"
67,"Je vais de l’avant, je ne me retourne pas et je me débrouille pour éviter tout ce qui pourrait être de source de souffrance"
68,"La plupart du temps je fais ce qui est facile plutôt que ce qui est important"
69,"Je suis une personne généreuse, qui prend soin des autres et qui se sacrifie pour eux"
70,"Je suis plus excité par l’idée de démarrer des projets que par celle de les mener à bien dans le long terme"
71,"J’ai des opinions tranchées, basées sur l’intégrité et sur des principes qui guident mon jugement et ma moralité"
72,"En général, j’évite d’être trop proche des gens et de m’impliquer avec eux sur le plan personnel"
73,"Les gens qui me connaissent me disent parfois que je devrais prendre davantage soin de mes propres besoins plutôt que de me soucier autant des besoins et des sentiments des autres"
74,"J’ai besoin de stimulation, d’être entouré de nombreux amis et de sources d’excitation. Je ne veux pas passer à côté de toutes les expériences que j’ai à vivre et de tous les projets qui m’enthousiasment"
75,"Je suis un médiateur efficace parce que j’ai une influence apaisante sur les autres"
76,"Lorsque j’effectue un achat, je le fais à partir d’éléments bien réfléchis et sur une base rationnelle, plutôt que par impulsion"
77,"Je me sens courroucé quand les choses ne sont pas faites de la meilleure façon qui soit"
78,"Pour réussir dans la vie, je m’adapte aux autres et j’ajuste mes attitudes, de façon à trouver la meilleure manière d’obtenir d’eux les résultats que je vise"
79,"Ma façon de travailler est très différente de celle de la plupart des gens, car je ne me laisse pas enfermer dans des comportements conventionnels. Je cherche à vivre les situations avec profondeur et authenticité et à leur donner de la classe"
80,"Je suis un individualiste convaincu et j’attache beaucoup d’importance à ma capacité à contrôler l’environnement et à triompher de lui"
81,"Je suis timide et je manque de courage pour me confronter à l’autorité, dans des situations ou bien d’autres semblent y arriver plus facilement que moi"
82,"Les autres m’irritent souvent par leur manque d’éthique et d’intégrité"
83,"J’ai le sentiment que quelque chose manque à ma vie car la plupart des gens me paraissent plus heureux et plus épanouis que je ne le suis"
84,"Je me soucie peu de l’argent et j’ai tendance à en dépenser plus que je ne le devrais, pour me faire plaisir, souvent en achats impulsifs"
85,"Cela me plaît lorsque les gens dépendent vraiment de moi et reconnaissent ma générosité"
86,"Ma capacité à me centrer sur mon projet et à travailler moi-même, sans avoir besoin de directives extérieures, est l’un de mes atouts"
87,"Je suis un « dur à cuire » et un protecteur pour les plus faibles que moi"
88,"J’ai du talent pour initier les projets et motiver les autres"
89,"Parfois je me lance dans trop de choses à la fois et je me retrouve pris dans un tourbillon, une sorte de frénésie qui me rend anxieux"
90,"Mes amis me perçoivent comme quelqu’un de tranquille et serein, plutôt que comme quelqu’un de confrontant ou d’incisif"
91,"Je prends mes responsabilités sociales au sérieux et je me sens la plupart du temps inquiet ou sur mes gardes"
92,"Je suis une personne facile à vivre mais j’ai tendance à avoir peu d’énergie et à me mettre en difficulté en matière de temps et de délais car je reste longtemps indécis quand il s’agit de faire des choix."
93,"J’ai des buts bien précis et j’aime être reconnu quand je réussis brillamment"
94,"Je passe un temps considérable à rechercher l’authenticité – « mon vrai Moi »- et à me comparer aux autres"
95,"Je suis toujours actif et toujours partant, pris par des tâches et des activités multiples"
96,"Je n’ai de cesse de m’améliorer et d’améliorer le monde qui m’entoure"
97,"Certaines personnes me voient comme quelqu’un de distant, non impliqué et peu sociable"
98,"Je sais dire non, je ne plie pas et l’autorité ne m’impressionne pas"
99,"Je pense et j’agis trop en fonction de mon cœur et pas assez en fonction de ma tête"
100,"Je suis une personne idéaliste et efficace, cherchant à améliorer ce qui est en mon pouvoir quand j’en ai l’occasion"
101,"Dans mes relations avec les autres j’ai souvent tendance à ne compter que sur moi et à passer pour quelqu’un qui est brusque ou qui à l’air d’avoir la tête dure, alors que j’ai simplement les pieds sur terre et l’esprit pratique"
102,"Face à un conflit, j’aborde celui-ci sous tous les angles et j’accorde autant d’importance au pour qu’au contre"
103,"Il m’arrive de m’impliquer de façon excessive dans les problèmes des autres et d’avoir tendance à trop m’exposer sur le plan émotionnel"
104,"Lorsque je m’éloigne des autres et du monde extérieur pour approfondir mon univers intérieur, cette recherche finit toujours par me déprimer"
105,"Parce qu’il est extrêmement important pour moi d’atteindre le succès, je m’en donne les moyens et je suis prêt à payer le prix pour cela"
106,"Je ne suis pas très porté sur les organisations – associations, amicales… etc – et je ne cherche pas, pour la plupart d’entre elles, à en faire partie"
107,"Je tiens à vivre dans un environnement matériel confortable et je sais m’offrir de bonnes parties de shopping quand l’envie m’en prend"
108,"J’ai souvent des sentiments contradictoires vis-à-vis des figures d’autorité, ce qui peut se traduire par une attitude ouvertement défensive ou par de l’insécurité"
109,"Lorsque j’ai la conviction que j’ai raison, je tiens à le dire aux autres et à leur montrer comment accomplir leur tâche correctement"
110,"Je suis sensible sur le plan émotionnel et je me sens attiré par l’aspect dramatique et significatif des crises qui jalonnent l’existence"
111,"Lorsque je veux quelque chose je me débrouille pour l’avoir. Je ne vois pas de raisons de manquer ou de passer à côté d’opportunités"
112,"J’aime apporter mon aide aux autres personnes en situation émotionnelle difficile et j’aime que les autres aient besoin de moi"
113,"Je garde mes projets pour moi et je préfère que les autres ne sachent pas ce que je suis en train de faire"
114,"Je préfère de beaucoup être aux commandes et avoir le contrôle qu’être contrôlé par une autre personne et dépendre d’elle"
115,"Exceller dans ce que je fais et être reconnu pour mes succès est très important pour moi"
116,"Je suis parfois soupçonneux quant aux motivations des autres ; je scrute l’environnement pour prévenir un éventuel danger"
117,"Je m’attache à ce qui est familier, la routine me convient et je désire vivre de façon harmonieuse dans un environnement stable"
118,"Je suis plus méfiant que la plupart des gens et je sais mieux qu’eux sentir le danger et détecter les situations menaçantes"
119,"J’ai du mal à me donner des priorités ou à me centrer sur des décisions précises parce que tous les points de vue me semblent intéressants"
120,"Même si je suis déprimé ou sous pression, c’est très important pour moi de donner aux autres l’image d’une personne sûre d’elle"
121,"Je passe de temps à fantasmer et à raviver des sentiments nostalgiques ayant trait à des moments du passé"
122,"J’ai tendance à penser que si « un peu c’est bien, alors beaucoup c’est encore mieux » et du coup à être excessif dans certains domaines"
123,"Je suis critique avec les autres lorsqu’ils sont imprécis, inefficaces, ou qu’ils ne suivent pas la direction attendue"
124,"Je cloisonne mes relations (travail, famille, sport, hobbies…). La plupart des personnes que je rencontre dans ces domaines ne se connaissent pas entre elles"
125,"J’ai du respect pour le courage et la force ainsi que pour la capacité à utiliser son pouvoir lorsqu’il le faut"
126,"Je mes sens obligé d’aider les autres et je donne parfois trop sans être payé de retour"
127,"Les autres me voient comme quelqu’un d’organisé, de précis et peut-être même de rigide et un peu coincé"
128,"Les gens se tournent vers moi pour que je les épaule parce qu’ils savent qu’en cas de coups durs on peut compter sur moi"
129,"Je ne suis pas quelqu’un d’agressif et ma présence est au contraire sécurisante et apaisante pour les autres de par mon flegme et mon sens de la diplomatie"
130,"J’éprouve un grand désir d’apporter de l’assistance aux autres et de tenir une place importante dans leur vie"
131,"Je veux vraiment que l’on me considère comme un être à part, singulier et différent des autres"
132,"Je sais comment projeter le style d’image le plus approprié pour réussir et éviter l’échec"
133,"Les autres ont du mal à savoir ce que je pense et me trouvent distant parce que je ne sollicite ni leur opinion ni leur approbation"
134,"J’aime repousser les limites et aller au devant de nouvelles aventures ; je n’aime pas perdre mon temps à ne rien faire"
135,"je suis souvent félicité par mes supérieurs pour ma bonne organisation et mon respect des règles de l’organisation"
"""

# ==========================================
# BASE DE DONNÉES (SQLite)
# ==========================================

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS results
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, date TEXT, scores TEXT, winner INTEGER)''')
    conn.commit()
    conn.close()

def register_user(username, password):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT id, username FROM users WHERE username=? AND password=?", (username, hashed_pw))
    user = c.fetchone()
    conn.close()
    return user

def save_result(user_id, scores, winner):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    scores_json = json.dumps(scores)
    c.execute("INSERT INTO results (user_id, date, scores, winner) VALUES (?, ?, ?, ?)", 
              (user_id, date_str, scores_json, winner))
    conn.commit()
    conn.close()

def get_user_results(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT date, scores, winner FROM results WHERE user_id=? ORDER BY id DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    results = []
    for row in rows:
        results.append({
            "date": row[0],
            "scores": json.loads(row[1]), # Convert JSON text back to dict (keys are strings now)
            "winner": row[2]
        })
    return results

# ==========================================
# FONCTIONS MÉTIER
# ==========================================

@st.cache_data
def load_data():
    df = None
    if os.path.exists("questions.xlsx"):
        try:
            df = pd.read_excel("questions.xlsx")
        except: pass
    
    if df is None:
        try:
            df = pd.read_csv(io.StringIO(CSV_DATA_BACKUP))
        except: return pd.DataFrame()
            
    if df is not None:
        best_col = None
        max_avg_len = 0
        for col in df.columns:
            try:
                series = df[col].astype(str)
                avg_len = series.apply(len).mean()
                if avg_len > max_avg_len:
                    max_avg_len = avg_len
                    best_col = col
            except: continue
        
        if best_col:
             df = df.rename(columns={best_col: "Question"})
        elif "Question" not in df.columns:
             df = df.rename(columns={df.columns[-1]: "Question"})

        df = df[~df["Question"].astype(str).str.contains("Remplissez les affirmations", case=False, na=False)]
        df = df[~df["Question"].astype(str).str.contains("Toujours vrai", case=False, na=False)]
        df = df.dropna(subset=["Question"]).reset_index(drop=True)
        df["Type"] = [TYPE_SEQUENCE[i % 9] for i in range(len(df))]
        
    return df

def calculate_scores(responses, df_questions):
    scores = {i: 0 for i in range(1, 10)}
    for idx, note in responses.items():
        if idx in df_questions.index:
            t = df_questions.loc[idx, "Type"]
            scores[t] += int(note)
    return scores

def generate_pdf(user_name, scores, winner_type, date_str):
    pdf = FPDF()
    pdf.add_page()
    def txt(s): return s.encode('latin-1', 'replace').decode('latin-1')
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt("Rapport de Profil Ennéagramme"), 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt(f"Nom : {user_name}"), ln=True)
    pdf.cell(0, 10, txt(f"Date : {date_str}"), ln=True)
    pdf.ln(10)
    
    # Détails Profil
    info = ENNEAGRAM_INFO[winner_type]
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, txt(f"Type Dominant : {winner_type} - {info['nom']}"), ln=True)
    pdf.set_text_color(0, 0, 0)
    
    # Description
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, txt("Description :"), ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 6, txt(info["desc"]))
    pdf.ln(5)
    
    # Graphique
    categories = [f"T{i}" for i in range(1, 10)]
    s_vals = [scores.get(str(i), scores.get(i, 0)) for i in range(1, 10)]
    values = s_vals + s_vals[:1]
    angles = [n / float(len(categories)) * 2 * np.pi for n in range(len(categories))]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    plt.xticks(angles[:-1], categories)
    ax.plot(angles, values, color='blue', linewidth=2)
    ax.fill(angles, values, color='blue', alpha=0.1)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        plt.savefig(tmp.name)
        pdf.image(tmp.name, x=50, y=pdf.get_y(), w=110)
    pdf.ln(100)
    
    # Forces
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 100, 0)
    pdf.cell(0, 8, txt("Vos Forces :"), ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=11)
    for f in info["forces"]:
        pdf.cell(5)
        pdf.cell(0, 6, txt(f"- {f}"), ln=True)
    pdf.ln(5)

    # Vigilance
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(150, 50, 0)
    pdf.cell(0, 8, txt("Points de Vigilance :"), ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=11)
    for v in info["vigilance"]:
        pdf.cell(5)
        pdf.cell(0, 6, txt(f"- {v}"), ln=True)
    pdf.ln(5)
    
    # Conseils
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(200, 50, 50)
    pdf.cell(0, 8, txt("Pistes de Développement :"), ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'I', 11)
    pdf.multi_cell(0, 6, txt(info["recommandations"]))
        
    return pdf.output(dest='S').encode('latin-1')

def plot_radar_chart(scores, title="Votre Profil"):
    categories = [f"Type {i}" for i in range(1, 10)]
    # Handle int/str key difference from DB JSON
    r_values = [scores.get(i, scores.get(str(i), 0)) for i in range(1, 10)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=r_values,
        theta=categories,
        fill='toself',
        name=title
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, max(r_values)+5])),
        showlegend=False
    )
    return fig

# ==========================================
# GESTION DES VUES
# ==========================================

def login_page():
    st.subheader("Authentification")
    tab1, tab2 = st.tabs(["Se Connecter", "Créer un Compte"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Identifiant")
            password = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter")
            if submit:
                user = login_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user[0]
                    st.session_state.username = user[1]
                    st.session_state.current_view = 'home'
                    st.rerun()
                else:
                    st.error("Identifiants incorrects.")
                    
    with tab2:
        with st.form("register_form"):
            new_user = st.text_input("Nouvel Identifiant")
            new_pass = st.text_input("Nouveau Mot de passe", type="password")
            submit_reg = st.form_submit_button("S'inscrire")
            if submit_reg:
                if new_user and new_pass:
                    success = register_user(new_user, new_pass)
                    if success:
                        st.success("Compte créé ! Connectez-vous.")
                    else:
                        st.error("Cet identifiant existe déjà.")
                else:
                    st.warning("Remplissez tous les champs.")

def view_home():
    st.markdown(f"# 👋 Bienvenue, {st.session_state.username} !")
    st.markdown("""
    ### Découvrez votre potentiel avec l'Ennéagramme.
    
    Cette application vous permet de :
    - 📝 **Passer le test** complet de 135 questions.
    - 📊 **Visualiser** votre profil sous forme de radar interactif.
    - 📥 **Télécharger** des rapports PDF détaillés.
    - 🕰️ **Suivre votre évolution** et comparer vos résultats dans le temps.
    
    Utilisez le menu latéral pour naviguer.
    """)

def view_test():
    st.markdown("## 📝 Test de Personnalité")
    # Légende mise à jour avec les termes exacts
    st.info("Notation : 0 = Jamais vrai | 1 = Parfois vrai | 2 = Souvent vrai | 3 = Toujours vrai")
    
    df_questions = load_data()
    if df_questions.empty:
        st.error("Impossible de charger les questions.")
        return

    # Dictionnaire de formatage pour les options 0,1,2,3
    score_labels = {
        0: "0 - Jamais vrai",
        1: "1 - Parfois vrai",
        2: "2 - Souvent vrai",
        3: "3 - Toujours vrai"
    }
    
    with st.form("test_form"):
        responses = {}
        # Affichage de toutes les questions
        for idx, row in df_questions.iterrows():
            st.markdown(f"**{idx + 1}. {row['Question']}**")
            
            # Correction UX : Options 0,1,2,3 et format_func
            # Correction Bug : Clé unique (index + hash partiel de la question)
            q_hash = hashlib.md5(row['Question'].encode()).hexdigest()[:6]
            unique_key = f"q_{idx}_{q_hash}"
            
            responses[idx] = st.radio(
                f"Question {idx+1}", 
                options=[0, 1, 2, 3], 
                horizontal=True, 
                index=None, 
                key=unique_key, 
                format_func=lambda x: score_labels[x], 
                label_visibility="collapsed"
            )
            st.write("")
            
        if st.form_submit_button("✅ Calculer et Sauvegarder", type="primary"):
            missed = [k for k, v in responses.items() if v is None]
            if missed:
                st.error(f"Il manque {len(missed)} réponses.")
            else:
                scores = calculate_scores(responses, df_questions)
                winner = max(scores, key=scores.get)
                save_result(st.session_state.user_id, scores, winner)
                st.success("Résultats sauvegardés !")
                st.session_state.current_view = 'results'
                st.rerun()

def view_results():
    results = get_user_results(st.session_state.user_id)
    if not results:
        st.warning("Aucun résultat disponible. Passez le test d'abord.")
        return

    last_res = results[0] # Le plus récent
    scores = last_res['scores']
    winner = last_res['winner']
    info = ENNEAGRAM_INFO[winner]
    
    st.markdown(f"## 📊 Vos Résultats du {last_res['date']}")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.plotly_chart(plot_radar_chart(scores), use_container_width=True)
        
    with col2:
        st.success(f"### Type Dominant : {winner} - {info['nom']}")
        st.write(info['desc'])
        
        st.markdown("#### 💪 Vos Forces")
        for f in info['forces']:
            st.write(f"- {f}")

        st.markdown("#### ⚠️ Points de Vigilance")
        for v in info['vigilance']:
            st.write(f"- {v}")
            
    st.divider()
    st.markdown("### 🚀 Pistes de Développement")
    st.info(info['recommandations'])
            
    pdf_data = generate_pdf(st.session_state.username, scores, winner, last_res['date'])
    st.download_button("📥 Télécharger le Rapport PDF Complet", data=pdf_data, 
                       file_name=f"Rapport_{st.session_state.username}_{last_res['date']}.pdf", mime="application/pdf")

def view_history():
    st.markdown("## 🕰️ Historique & Comparaison")
    results = get_user_results(st.session_state.user_id)
    
    if not results:
        st.info("Pas encore d'historique.")
        return
        
    # 1. Tableau d'historique (Isolation stricte)
    with st.container():
        data = []
        for r in results:
            data.append({"Date": r['date'], "Type Dominant": r['winner'], "Score Max": max(r['scores'].values())})
        
        # Clé statique pour le tableau (pas de besoin de mise à jour dynamique ici)
        st.dataframe(pd.DataFrame(data), use_container_width=True, key="history_data_table_static")
    
    st.divider()
    st.subheader("📈 Comparer des sessions")
    
    # 2. Contrôles (Isolation stricte)
    with st.container():
        options = {r['date']: r for r in results}
        # Clé spécifique pour le multiselect
        selected_dates = st.multiselect(
            "Choisissez jusqu'à 3 dates pour comparer :", 
            list(options.keys()), 
            max_selections=3, 
            key="history_multiselect_control"
        )
    
    # 3. Radar Chart Comparatif (Restauré avec Fix Anti-Crash)
    with st.container():
        if selected_dates:
            fig = go.Figure()
            categories = [f"Type {i}" for i in range(1, 10)]
            
            all_scores = []
            
            for date in selected_dates:
                res = options[date]
                s = res['scores']
                r_vals = [s.get(str(i), s.get(i, 0)) for i in range(1, 10)]
                all_scores.extend(r_vals)
                
                fig.add_trace(go.Scatterpolar(
                    r=r_vals,
                    theta=categories,
                    fill='toself',
                    name=date,
                    opacity=0.6 # Transparence pour voir les superpositions
                ))
            
            # Ajustement de l'échelle automatique
            max_range = max(all_scores) + 5 if all_scores else 40
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, max_range])),
                showlegend=True,
                title="Comparaison des Profils"
            )
            
            # TECHNIQUE AVANCÉE ANTI-BUG : Clé temporelle unique
            # Force la reconstruction totale du widget Plotly à chaque rendu pour éviter NodeNotFoundError
            unique_key = f"radar_chart_{time.time()}"
            st.plotly_chart(fig, use_container_width=True, key=unique_key)

# ==========================================
# MAIN
# ==========================================

def main():
    init_db()
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_view' not in st.session_state:
        st.session_state.current_view = 'home'

    if not st.session_state.logged_in:
        login_page()
    else:
        # Sidebar Navigation
        with st.sidebar:
            st.title(f"👤 {st.session_state.username}")
            if st.button("🏠 Accueil", use_container_width=True):
                st.session_state.current_view = 'home'
                st.rerun()
            if st.button("📝 Passer le Test", use_container_width=True):
                st.session_state.current_view = 'test'
                st.rerun()
            if st.button("📊 Mes Résultats", use_container_width=True):
                st.session_state.current_view = 'results'
                st.rerun()
            if st.button("🕰️ Historique", use_container_width=True):
                st.session_state.current_view = 'history'
                st.rerun()
                
            st.divider()
            if st.button("Déconnexion", type="primary", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_id = None
                st.session_state.username = None
                st.session_state.current_view = 'home'
                st.rerun()

        # Routing Views
        if st.session_state.current_view == 'home':
            view_home()
        elif st.session_state.current_view == 'test':
            view_test()
        elif st.session_state.current_view == 'results':
            view_results()
        elif st.session_state.current_view == 'history':
            view_history()

if __name__ == "__main__":
    main()
