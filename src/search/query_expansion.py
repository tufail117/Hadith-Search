"""Query expansion with Islamic terminology mappings."""

# Islamic terminology synonym mappings
TERM_MAPPINGS = {
    # Prayer
    "prayer": ["salah", "salat", "namaz", "pray", "praying", "prayers"],
    "salah": ["prayer", "salat", "namaz", "pray"],
    "salat": ["prayer", "salah", "namaz", "pray"],
    "namaz": ["prayer", "salah", "salat", "pray"],
    
    # Prayer positions and actions
    "rafa": ["raising", "raise", "lifted", "hands", "yadain"],
    "yadain": ["hands", "raising", "rafa", "lifted"],
    "raising": ["rafa", "yadain", "hands", "lifted", "takbir"],
    "hands": ["rafa", "yadain", "raising"],
    "takbir": ["allahu akbar", "raising hands", "rafa", "opening"],
    "ruku": ["bowing", "bow", "bent"],
    "bowing": ["ruku", "bow", "bent"],
    "sujud": ["prostration", "prostrate", "sajdah"],
    "prostration": ["sujud", "sajdah", "prostrate"],
    "sajdah": ["sujud", "prostration", "prostrate"],
    "qiyam": ["standing", "stand"],
    "standing": ["qiyam", "stand"],

    # Fasting
    "fasting": ["sawm", "siyam", "roza", "ramadan", "fast", "fasts", "saum"],
    "sawm": ["fasting", "siyam", "roza", "fast", "saum"],
    "saum": ["fasting", "sawm", "siyam", "fast"],
    "siyam": ["fasting", "sawm", "roza", "fast"],
    "ramadan": ["fasting", "sawm", "siyam", "fast", "saum"],
    "fast": ["fasting", "sawm", "siyam", "ramadan", "saum"],
    
    # Fasting invalidators (what breaks the fast)
    "break": ["invalidate", "nullify", "void", "cancel", "breaks", "breaking", "broke"],
    "breaks": ["break", "invalidate", "nullify", "void", "broke", "breaking"],
    "broke": ["break", "breaks", "invalidate", "nullify"],
    "invalidate": ["break", "nullify", "void", "cancel", "breaks"],
    "nullify": ["break", "invalidate", "void", "cancel"],
    "void": ["break", "invalidate", "nullify", "cancel"],
    
    # Fasting actions
    "eat": ["eating", "food", "ate", "swallow", "consume"],
    "eating": ["eat", "food", "ate", "swallow", "consume"],
    "drink": ["drinking", "water", "drank", "beverage"],
    "drinking": ["drink", "water", "drank", "beverage"],
    "intercourse": ["sexual", "relations", "spouse", "intimacy", "intimate"],
    "sexual": ["intercourse", "relations", "intimacy", "intimate"],
    "vomit": ["vomiting", "intentional", "deliberate"],
    "cupping": ["hijama", "bloodletting"],
    "hijama": ["cupping", "bloodletting"],
    
    # Ramadan specifics
    "iftar": ["breaking fast", "sunset", "maghrib", "break"],
    "suhoor": ["sahur", "sehri", "pre-dawn", "sahoor"],
    "sahur": ["suhoor", "sehri", "pre-dawn"],

    # Charity
    "charity": ["zakat", "sadaqah", "alms", "giving", "donate"],
    "zakat": ["charity", "sadaqah", "alms", "obligatory charity"],
    "sadaqah": ["charity", "zakat", "alms", "voluntary charity"],
    "alms": ["charity", "zakat", "sadaqah"],

    # Pilgrimage
    "pilgrimage": ["hajj", "umrah", "mecca", "kaaba", "pilgrim"],
    "hajj": ["pilgrimage", "umrah", "mecca", "kaaba"],
    "umrah": ["pilgrimage", "hajj", "mecca", "kaaba"],
    "mecca": ["hajj", "umrah", "kaaba", "pilgrimage"],
    "kaaba": ["hajj", "umrah", "mecca", "pilgrimage"],

    # Family
    "parents": ["mother", "father", "walidayn", "birr", "parent"],
    "mother": ["parents", "father", "walidayn", "umm"],
    "father": ["parents", "mother", "walidayn", "abb"],
    "children": ["child", "son", "daughter", "offspring", "kids"],
    "wife": ["spouse", "marriage", "nikah", "husband", "wives"],
    "husband": ["spouse", "marriage", "nikah", "wife"],
    "marriage": ["nikah", "wedding", "spouse", "wife", "husband"],
    "nikah": ["marriage", "wedding", "spouse"],

    # Neighbors
    "neighbor": ["neighbours", "neighbors", "jar", "neighbourhood"],
    "neighbours": ["neighbor", "neighbors", "jar"],
    "neighbors": ["neighbor", "neighbours", "jar"],

    # Virtues
    "honest": ["honesty", "truthful", "truth", "sidq", "truthfulness"],
    "honesty": ["honest", "truthful", "truth", "sidq"],
    "truthful": ["honest", "honesty", "truth", "sidq"],
    "patience": ["sabr", "patient", "perseverance", "endurance"],
    "sabr": ["patience", "patient", "perseverance"],
    "kind": ["kindness", "ihsan", "good", "gentle", "merciful"],
    "kindness": ["kind", "ihsan", "good", "gentle", "mercy"],
    "ihsan": ["kindness", "excellence", "perfection", "good"],
    "mercy": ["merciful", "rahma", "compassion", "kind"],
    "merciful": ["mercy", "rahma", "compassion", "kind"],

    # Afterlife
    "death": ["dying", "mawt", "deceased", "die", "dead"],
    "paradise": ["jannah", "heaven", "garden", "gardens"],
    "jannah": ["paradise", "heaven", "garden"],
    "heaven": ["paradise", "jannah", "garden"],
    "hell": ["jahannam", "hellfire", "fire", "punishment"],
    "jahannam": ["hell", "hellfire", "fire"],
    "hellfire": ["hell", "jahannam", "fire"],

    # Faith
    "faith": ["iman", "belief", "believe", "believer"],
    "iman": ["faith", "belief", "believe"],
    "believer": ["faith", "iman", "muslim", "mumin"],
    "islam": ["muslim", "religion", "deen"],
    "muslim": ["islam", "believer", "mumin"],

    # Knowledge
    "knowledge": ["ilm", "learn", "learning", "scholar", "wisdom"],
    "ilm": ["knowledge", "learn", "learning"],
    "scholar": ["knowledge", "alim", "ulama", "learned"],

    # Worship
    "worship": ["ibadah", "devotion", "obedience"],
    "ibadah": ["worship", "devotion", "obedience"],
    "dua": ["supplication", "prayer", "invocation", "asking"],
    "supplication": ["dua", "prayer", "invocation"],

    # Prophet
    "prophet": ["messenger", "rasul", "nabi", "muhammad"],
    "messenger": ["prophet", "rasul", "nabi"],

    # Actions
    "sin": ["sins", "sinful", "transgression", "wrongdoing", "evil"],
    "good": ["righteous", "virtue", "virtuous", "goodness"],
    "evil": ["bad", "sin", "wrong", "wicked"],
    "forgive": ["forgiveness", "pardon", "mercy", "maghfira"],
    "forgiveness": ["forgive", "pardon", "mercy"],
    "repent": ["repentance", "tawba", "tawbah", "return"],
    "repentance": ["repent", "tawba", "tawbah"],

    # Daily life
    "food": ["eating", "eat", "drink", "halal", "haram"],
    "eating": ["food", "eat", "meals"],
    "sleep": ["sleeping", "rest", "night"],
    "travel": ["journey", "traveling", "traveler"],
    "wealth": ["money", "rich", "poor", "property"],
    "money": ["wealth", "gold", "silver", "property"],
    "poor": ["poverty", "needy", "miskin", "faqir"],
    "rich": ["wealthy", "wealth", "money"],

    # Social
    "friend": ["friends", "friendship", "companion", "brother"],
    "enemy": ["enemies", "hatred", "enmity"],
    "guest": ["guests", "hospitality", "host"],
    "rights": ["right", "haqq", "obligation", "duty"],

    # Clothing
    "clothes": ["clothing", "dress", "garment", "wear"],
    "hijab": ["covering", "modesty", "veil"],

    # Misc
    "anger": ["angry", "wrath", "rage", "temper"],
    "lying": ["lie", "lies", "falsehood", "liar"],
    "backbiting": ["gheeba", "gossip", "slander"],
    "arrogance": ["arrogant", "pride", "kibr", "proud"],
    "humble": ["humility", "modest", "modesty"],
    "clean": ["cleanliness", "purity", "tahara", "wudu"],
    "wudu": ["ablution", "purity", "cleanliness"],
    "ablution": ["wudu", "cleanliness", "purity"],
    "friday": ["jumuah", "jummah", "congregation"],
    "jumuah": ["friday", "jummah", "congregation"],
    "mosque": ["masjid", "prayer place"],
    "masjid": ["mosque", "prayer place"],
    "quran": ["book", "scripture", "recitation"],
    "sunnah": ["tradition", "practice", "way"],
    "hadith": ["tradition", "narration", "saying"],
    "jihad": ["struggle", "striving", "effort"],
    "war": ["battle", "fight", "fighting", "combat"],
    "peace": ["salam", "peaceful", "reconciliation"],
}


def expand_query(query: str) -> str:
    """Expand query with Islamic terminology synonyms.

    Args:
        query: Original user query.

    Returns:
        Expanded query with added synonyms.
    """
    words = query.lower().split()
    expanded_terms = set(words)

    for word in words:
        # Check if word is in mappings
        if word in TERM_MAPPINGS:
            expanded_terms.update(TERM_MAPPINGS[word])

        # Also check without trailing 's' for plurals
        singular = word.rstrip('s')
        if singular in TERM_MAPPINGS:
            expanded_terms.update(TERM_MAPPINGS[singular])

    return " ".join(expanded_terms)
