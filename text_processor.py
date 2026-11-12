import re
import TTS.tts.layers.xtts.tokenizer as xtts_tokenizer

# ---------------------------------------------------------
# 1. Hindi Number Expansion Engine
# ---------------------------------------------------------
HINDI_NUMS_0_TO_99 = [
    "शून्य", "एक", "दो", "तीन", "चार", "पांच", "छह", "सात", "आठ", "नौ",
    "दस", "ग्यारह", "बारह", "तेरह", "चौदह", "पंद्रह", "सोलह", "सत्रह", "अठारह", "उन्नीस",
    "बीस", "इक्कीस", "बाईस", "तेईस", "चौबीस", "पच्चीस", "छब्बीस", "सत्ताईस", "अट्ठाईस", "उनतीस",
    "तीस", "इकतीस", "बत्तीस", "तैंतीस", "चौंतीस", "पैंतीस", "छत्तीस", "सैंतीस", "अड़तीस", "उनतालीस",
    "चालीस", "इकतालीस", "बयालीस", "तैंतालीस", "चवालीस", "पैंतालीस", "छियालीस", "सैंतालीस", "अड़तालीस", "उनचास",
    "पचास", "इक्यावन", "बावन", "तिरपन", "चौवन", "पचपन", "छप्पन", "सत्तावन", "अट्ठावन", "उनसठ",
    "साठ", "इकसठ", "बासठ", "तिरसठ", "चौंसठ", "पैंसठ", "छियासठ", "सड़सठ", "अड़सठ", "उनहत्तर",
    "सत्तर", "इकहत्तर", "बहत्तर", "तिहत्तर", "चौहत्तर", "पचहत्तर", "छिहत्तर", "सतहत्तर", "अठहत्तर", "उन्यासी",
    "अस्सी", "इक्यासी", "बयासी", "तिरासी", "चौरासी", "पचासी", "छियासी", "सत्तासी", "अट्ठासी", "नवासी",
    "नब्बे", "इक्यानवे", "बानवे", "तिरानवे", "चौरानवे", "पचानवे", "छियानवे", "सत्तानवे", "अठानवे", "निन्यानवे",
]


def hindi_num2words(n: int) -> str:
    """Converts integers up to crores into natural Hindi Devanagari words."""
    if n < 0:
        return "माइनस " + hindi_num2words(-n)
    if n < 100:
        return HINDI_NUMS_0_TO_99[n]
    if n < 1000:
        hundreds = n // 100
        rem = n % 100
        res = HINDI_NUMS_0_TO_99[hundreds] + " सौ"
        if rem > 0:
            res += " " + HINDI_NUMS_0_TO_99[rem]
        return res
    if n < 100000:
        thousands = n // 1000
        rem = n % 1000
        res = hindi_num2words(thousands) + " हज़ार"
        if rem > 0:
            res += " " + hindi_num2words(rem)
        return res
    if n < 10000000:
        lakhs = n // 100000
        rem = n % 100000
        res = hindi_num2words(lakhs) + " लाख"
        if rem > 0:
            res += " " + hindi_num2words(rem)
        return res
    crores = n // 10000000
    rem = n % 10000000
    res = hindi_num2words(crores) + " करोड़"
    if rem > 0:
        res += " " + hindi_num2words(rem)
    return res


# Monkey-patch XTTS tokenizer for safe Hindi number handling
orig_expand_number = xtts_tokenizer._expand_number
orig_expand_ordinal = xtts_tokenizer._expand_ordinal
orig_expand_decimal = xtts_tokenizer._expand_decimal_point


def safe_expand_number(m, lang="en"):
    if lang == "hi":
        try:
            return hindi_num2words(int(m.group(0)))
        except Exception:
            return m.group(0)
    try:
        return orig_expand_number(m, lang=lang)
    except Exception:
        return m.group(0)


def safe_expand_ordinal(m, lang="en"):
    if lang == "hi":
        try:
            val = int(m.group(1))
            ordinal_map = {1: "पहला", 2: "दूसरा", 3: "तीसरा", 4: "चौथा", 5: "पांचवां"}
            return ordinal_map.get(val, hindi_num2words(val) + "वां")
        except Exception:
            return m.group(1)
    try:
        return orig_expand_ordinal(m, lang=lang)
    except Exception:
        return m.group(1)


def safe_expand_decimal_point(m, lang="en"):
    amount = m.group(1).replace(",", ".")
    if lang == "hi":
        try:
            parts = amount.split(".")
            int_part = hindi_num2words(int(parts[0])) if parts[0] else "शून्य"
            if len(parts) > 1 and parts[1]:
                dec_digits = " ".join(hindi_num2words(int(d)) for d in parts[1])
                return f"{int_part} दशमलव {dec_digits}"
            return int_part
        except Exception:
            return amount
    try:
        return orig_expand_decimal(m, lang=lang)
    except Exception:
        return amount


xtts_tokenizer._expand_number = safe_expand_number
xtts_tokenizer._expand_ordinal = safe_expand_ordinal
xtts_tokenizer._expand_decimal_point = safe_expand_decimal_point

# ---------------------------------------------------------
# 2. Hinglish Loanword Dictionary (150+ Words & Names)
# ---------------------------------------------------------
HINDI_LOANWORDS = {
    # Workspace & Everyday objects
    "desk": "डेस्क",
    "tiffin": "टिफिन",
    "office": "ऑफिस",
    "school": "स्कूल",
    "college": "कॉलेज",
    "class": "क्लास",
    "student": "स्टूडेंट",
    "teacher": "टीचर",
    "principal": "प्रिंसिपल",
    "hospital": "अस्पताल",
    "doctor": "डॉक्टर",
    "nurse": "नर्स",
    "clinic": "क्लिनिक",
    "medicine": "दवा",
    "patient": "मरीज",
    "ambulance": "एंबुलेंस",
    # Tech & gadgets
    "phone": "फ़ोन",
    "mobile": "मोबाइल",
    "call": "कॉल",
    "laptop": "लैपटॉप",
    "computer": "कंप्यूटर",
    "screen": "स्क्रीन",
    "mouse": "माउस",
    "keyboard": "कीबोर्ड",
    "charger": "चार्जर",
    "cable": "केबल",
    "battery": "बैटरी",
    "camera": "कैमरा",
    "video": "वीडियो",
    "photo": "फ़ोटो",
    "audio": "ऑडियो",
    "film": "फिल्म",
    "movie": "मूवी",
    "message": "मैसेज",
    "chat": "चैट",
    "post": "पोस्ट",
    "status": "स्टेटस",
    "link": "लिंक",
    "site": "साइट",
    "website": "वेबसाइट",
    "app": "ऐप",
    "online": "ऑनलाइन",
    "offline": "ऑफलाइन",
    "net": "नेट",
    "internet": "इंटरनेट",
    "wifi": "वाईफ़ाई",
    "password": "पासवर्ड",
    "data": "डेटा",
    "system": "सिस्टम",
    "software": "सॉफ्टवेयर",
    # Transportation & Places
    "car": "कार",
    "bike": "बाइक",
    "bus": "बस",
    "train": "ट्रेन",
    "station": "स्टेशन",
    "metro": "मेट्रो",
    "flight": "फ्लाइट",
    "airport": "एयरपोर्ट",
    "taxi": "टैक्सी",
    "auto": "ऑटो",
    "driver": "ड्राइवर",
    "road": "रोड",
    "highway": "हाईवे",
    "traffic": "ट्रैफिक",
    "bridge": "ब्रिज",
    "hotel": "होटल",
    "restaurant": "रेस्टोरेंट",
    "cafe": "कैफे",
    "mall": "मॉल",
    "market": "मार्केट",
    "shop": "शॉप",
    "bank": "बैंक",
    "atm": "एटीएम",
    "park": "पार्क",
    "garden": "गार्डन",
    "gym": "जिम",
    # Home & Furniture
    "room": "रूम",
    "table": "टेबल",
    "chair": "चेयर",
    "bed": "बेड",
    "door": "डोर",
    "window": "विंडो",
    "light": "लाइट",
    "fan": "फैन",
    "switch": "स्विच",
    "bottle": "बोतल",
    "bag": "बैग",
    "box": "बॉक्स",
    "packet": "पैकेट",
    "plate": "प्लेट",
    "glass": "ग्लास",
    "cup": "कप",
    "lock": "लॉक",
    "key": "चाबी",
    # Food & Daily Routine
    "lunch": "लंच",
    "dinner": "डिनर",
    "breakfast": "ब्रेकफ़ास्ट",
    "snack": "स्नैक",
    "tea": "चाय",
    "coffee": "कॉफ़ी",
    "water": "वॉटर",
    "juice": "जूस",
    "milk": "दूध",
    "cake": "केक",
    "chocolate": "चॉकलेट",
    "ice cream": "आइसक्रीम",
    # Workplace, Business & Money
    "job": "जॉब",
    "interview": "इंटरव्यू",
    "salary": "सैलरी",
    "bonus": "बोनस",
    "meeting": "मीटिंग",
    "presentation": "प्रेजेंटेशन",
    "project": "प्रोजेक्ट",
    "target": "टारगेट",
    "client": "क्लाइंट",
    "service": "सर्विस",
    "order": "ऑर्डर",
    "delivery": "डिलीवरी",
    "money": "मनी",
    "cash": "कैश",
    "bill": "बिल",
    "card": "कार्ड",
    "manager": "मैनेजर",
    "boss": "बॉस",
    "staff": "स्टाफ",
    "sir": "सर",
    "madam": "मैडम",
    "police": "पुलिस",
    "company": "कंपनी",
    "business": "बिजनेस",
    "contract": "कॉन्ट्रैक्ट",
    "deal": "डील",
    "offer": "ऑफर",
    "shift": "शिफ्ट",
    # Entertainment & Sports
    "game": "गेम",
    "match": "मैच",
    "team": "टीम",
    "player": "प्लेयर",
    "coach": "कोच",
    "ground": "ग्राउंड",
    "party": "पार्टी",
    "club": "क्लब",
    "song": "गाना",
    "music": "म्यूज़िक",
    "dance": "डांस",
    # Emotions, Conversational Words & Slang
    "problem": "प्रॉब्लम",
    "tension": "टेंशन",
    "issue": "इश्यू",
    "idea": "आइडिया",
    "plan": "प्लान",
    "secret": "सीक्रेट",
    "surprise": "सरप्राइज़",
    "gift": "गिफ्ट",
    "ticket": "टिकट",
    "help": "हेल्प",
    "please": "प्लीज़",
    "thanks": "थैंक्स",
    "thank you": "थैंक यू",
    "sorry": "सॉरी",
    "hello": "हैलो",
    "hi": "हाय",
    "bye": "बाय",
    "goodbye": "गुडबाय",
    "ok": "ओके",
    "okay": "ओके",
    "yes": "यस",
    "no": "नो",
    "sure": "श्योर",
    "fine": "फाइन",
    "cool": "कूल",
    "super": "सुपर",
    "ready": "रेडी",
    "start": "स्टार्ट",
    "stop": "स्टॉप",
    "wait": "वेट",
    "relax": "रिलैक्स",
    # Common English / Roman Names inside Hindi Scripts
    "priya": "प्रीया",
    "supriya": "सुप्रीया",
    "riya": "रीया",
    "siya": "सीया",
    "rahul": "राहुल",
    "amit": "अमित",
    "neha": "नेहा",
    "pooja": "पूजा",
    "rohit": "रोहित",
    "vikas": "विकास",
    "gaurav": "गौरव",
    "simran": "सिमरन",
    "anjali": "अंजलि",
    "karan": "करण",
    "arjun": "अर्जुन",
    "raj": "राज",
    "ravi": "रवि",
    "sonia": "सोनिया",
    "mona": "मोना",
    "tina": "टीना",
    "anita": "अनिता",
    "sunita": "सुनीता",
    "geeta": "गीता",
    "seema": "सीमा",
    "rekha": "रेखा",
    "deepak": "दीपक",
    "manoj": "मनोज",
    "sanjay": "संजय",
    "vijay": "विजय",
    "ajay": "अजय",
}

# Root Hindi verbs that must preserve their native spelling
PROTECTED_HINDI_VERBS = {"किया", "दिया", "लिया", "पिया", "जिया", "सिया"}

# ---------------------------------------------------------
# 3. Universal Devanagari Normalization Engine
# ---------------------------------------------------------
def preprocess_script_text(text: str, lang_code: str) -> str:
    """Comprehensive linguistic & phonetic pre-processing engine:
    1. Strips invisible formatting & zero-width noise (ZWJ, ZWNJ, BOM).
    2. Transliterates common English / Hinglish loanwords into clean Devanagari.
    3. Normalizes Hindi numerals, fractions, decimals, clock times, percentages, and currencies.
    4. Resolves BPE tokenization pitfalls for ALL Devanagari conjuncts & names (प्रिया -> प्रीया, शुक्रिया -> शुक्रीया).
    5. Resolves greedy matra collapse on feminine plurals (कहानियां -> कहानीयां, गाड़ियां -> गाड़ीयां, रोटियां -> रोटीयां).
    6. Normalizes Chandrabindu (ँ) to Anusvara (ं) to leverage fused subwords (हँसना -> हंसना).
    7. Cleans unhandled Nukta characters and Visarga breaks (दुःख -> दुख, स्वतः -> स्वत).
    8. Unifies hyphens in reduplicated words (गरमा-गरम -> गरमा गरम, धीरे-धीरे -> धीरे धीरे).
    9. Ensures clean punctuation spacing for breath-aligned sentence segmentation.
    """
    if not text:
        return ""
    text = text.strip()

    if lang_code == "hi":
        # 1. Strip invisible Unicode junk (ZWJ, ZWNJ, ZWSP, BOM, soft hyphen)
        text = re.sub(r"[\u200b-\u200f\ufeff\u00ad]", "", text)

        # 2. Convert Devanagari numerals (०-९) to standard digits (0-9)
        text = text.translate(str.maketrans("०१२३४५६७८९", "0123456789"))

        # 3. Transliterate English loanwords into clean Devanagari
        for en_word, hi_word in HINDI_LOANWORDS.items():
            text = re.sub(rf"\b{re.escape(en_word)}\b", hi_word, text, flags=re.IGNORECASE)

        # 4. Clock / Time format (e.g., '1:30' or '10:00 बजे' -> 'एक बजकर तीस मिनट' / 'दस बजे')
        def _time_repl(m):
            hr, mn = int(m.group(1)), int(m.group(2))
            if mn == 0:
                return f"{hindi_num2words(hr)} बजे "
            return f"{hindi_num2words(hr)} बजकर {hindi_num2words(mn)} मिनट "
        text = re.sub(r"\b(\d{1,2}):(\d{2})(?:\s*बजे)?", _time_repl, text)

        # 5. Common fractions & decimals
        text = re.sub(r"\b1/2\b", "आधा", text)
        text = re.sub(r"\b1/4\b", "एक चौथाई", text)
        text = re.sub(r"\b3/4\b", "तीन चौथाई", text)
        text = re.sub(r"\b1\.5\b", "डेढ़", text)
        text = re.sub(r"\b2\.5\b", "ढाई", text)

        # 6. Currency symbols and percentages
        text = re.sub(r"₹\s*(\d+)", r"\1 रुपये", text)
        text = re.sub(r"\$\s*(\d+)", r"\1 डॉलर", text)
        text = re.sub(r"(\d+)\s*%", r"\1 प्रतिशत", text)

        # 7. Pre-expand standalone numbers into spoken Hindi words
        def _replace_num(match):
            try:
                return hindi_num2words(int(match.group(0)))
            except Exception:
                return match.group(0)
        text = re.sub(r"\b\d+\b", _replace_num, text)

        # 8. Chandrabindu (ँ) to Anusvara (ं) - enables XTTS pre-fused subwords (हँसना -> हंसना, गाँव -> गांव)
        text = text.replace("ँ", "ं")

        # 9. Visarga (ः) cleanup - avoids mid-word tokenization breaks (दुःख -> दुख, स्वतः -> स्वत)
        text = text.replace("दुःख", "दुख").replace("दु:ख", "दुख")
        text = re.sub(r"([क-ह])ः", r"\1", text)

        # 10. Nukta normalization for characters that lack native pre-fused subwords in XTTS
        text = re.sub(r"क़", "क", text)
        text = re.sub(r"ख़", "ख", text)
        text = re.sub(r"ग़", "ग", text)
        text = re.sub(r"ज़ि", "जि", text)
        text = re.sub(r"फ़ि", "फि", text)
        text = re.sub(r"([क-ह])ाफ़\b", r"\1ाफ", text)

        # 11. Hyphens between Devanagari reduplicated words (धीरे-धीरे -> धीरे धीरे, गरमा-गरम -> गरमा गरम)
        text = re.sub(r"([क-ह]़?[\u093e-\u094c]?)-([क-ह])", r"\1 \2", text)

        # 12. Universal 'िया' / 'ियों' / 'ियां' / 'िए' normalization
        # Resolves tokenization breaks across names, conjuncts and feminine plurals
        def _iya_repl(m):
            full = m.group(0)
            if full in PROTECTED_HINDI_VERBS:
                return full
            prefix = m.group(1)
            suffix = m.group(2)
            return prefix + "ी" + suffix

        iya_pattern = r"([क-ह]़?(?:्[क-ह]़?)*)ि(य[ाोे][ंँ]?)"
        text = re.sub(iya_pattern, _iya_repl, text)

        # 13. Dramatic pause normalization (... or -- to clean clause boundaries)
        text = re.sub(r"\.{3,}", "। ", text)
        text = re.sub(r"--+", ", ", text)
        text = text.replace("॥", "।")

        # 14. Ensure sentence terminators have trailing spaces for clean sentence segmentation
        text = re.sub(r"([।!?])([^\s])", r"\1 \2", text)
        text = re.sub(r"(\.)([^\s\d])", r"\1 \2", text)

        # 15. Collapse excessive whitespace
        text = re.sub(r"\s+", " ", text).strip()

    else:
        # English text cleaning
        text = re.sub(r"[\u200b-\u200f\ufeff\u00ad]", "", text)
        text = re.sub(r"\$\s*(\d+)", r"\1 dollars", text)
        text = re.sub(r"(\d+)\s*%", r"\1 percent", text)
        text = re.sub(r"\.{3,}", ". ", text)
        text = re.sub(r"--+", ", ", text)
        text = re.sub(r"\s+", " ", text).strip()

    return text

