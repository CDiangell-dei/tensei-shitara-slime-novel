import glob
import json
import re

patterns = [
    (r'\bMy\b', 'My'),
    (r'\bYour\b', 'Your'),
    (r'\bHis\b', 'His'),
    (r'\bHer\b', 'Her'),
    (r'\bOur\b', 'Our'),
    (r'\bTheir\b', 'Their'),
    (r'\bSkill\b', 'Skill'),
    (r'\bSkills\b', 'Skills'),
    (r'\bBoss\b', 'Boss'),
    (r'\bFloor\b', 'Floor'),
    (r'\bUltimate Skill\b', 'Ultimate Skill'),
    (r'\bUnique Skill\b', 'Unique Skill'),
    (r'\bExtra Skill\b', 'Extra Skill'),
    (r'\bIntrinsic Skill\b', 'Intrinsic Skill'),
    (r'\bCommon Skill\b', 'Common Skill'),
    (r'\bTrue Dragon\b', 'True Dragon'),
    (r'\bCook\b', 'Cook'),
    (r'\bChef\b', 'Chef'),
    (r'\bGreat Sage\b', 'Great Sage'),
    (r'\bPredator\b', 'Predator'),
    (r'\bGluttony\b', 'Gluttony'),
    (r'\bBeelzebub\b', 'Beelzebub'),
    (r'\bBeelzebuth\b', 'Beelzebuth'),
    (r'\bMerciless\b', 'Merciless'),
    (r'\bHeartless\b', 'Heartless'),
    (r'\bDegenerate\b', 'Degenerate'),
    (r'\bDeviant\b', 'Deviant'),
    (r'\bShapeshifter\b', 'Shapeshifter'),
    (r'\bBerserker\b', 'Berserker'),
    (r'\bShadow Step\b', 'Shadow Step'),
    (r'\bShadow Motion\b', 'Shadow Motion'),
    (r'\bBlack Lightning\b', 'Black Lightning'),
    (r'\bBlack Flame\b', 'Black Flame'),
    (r'\bDark Flame\b', 'Dark Flame'),
    (r'\bMagic Sense\b', 'Magic Sense'),
    (r'\bMagic Perception\b', 'Magic Perception'),
    (r'\bMultilayer Barrier\b', 'Multilayer Barrier'),
    (r'\bMulti-barrier\b', 'Multi-barrier'),
    (r'\bUniversal Sense\b', 'Universal Sense'),
    (r'\bUniversal Perception\b', 'Universal Perception'),
    (r'\bThought Acceleration\b', 'Thought Acceleration'),
    (r'\bParallel Operation\b', 'Parallel Operation'),
    (r'\bParallel Processing\b', 'Parallel Processing'),
    (r'\bCast Cancel\b', 'Cast Cancel'),
    (r'\bChant Annulment\b', 'Chant Annulment'),
    (r'\bAll of Creation\b', 'All of Creation'),
    (r'\bAnalyze and Assess\b', 'Analyze and Assess'),
    (r'\bAnalytical Appraisal\b', 'Analytical Appraisal'),
    (r'\bLaw Manipulation\b', 'Law Manipulation'),
    (r'\bSpace-Time Manipulation\b', 'Space-Time Manipulation'),
    (r'\bSpacetime Manipulation\b', 'Spacetime Manipulation'),
    (r'\bMulti-Dimensional Barrier\b', 'Multi-Dimensional Barrier'),
    (r'\bFuture Attack Prediction\b', 'Future Attack Prediction'),
]

files = sorted(glob.glob('data/light_novel/vol-*.json'))
results = {}

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        content = fp.read()
    file_hits = {}
    for pat, label in patterns:
        hits = len(re.findall(pat, content))
        if hits > 0:
            file_hits[label] = hits
    if file_hits:
        results[f] = file_hits

print(json.dumps(results, indent=2))
