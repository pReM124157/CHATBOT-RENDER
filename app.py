import math
import re
from collections import Counter

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

financial_nlp_dataset = [
    {"text": "नमस्ते", "intent": "greeting"},
    {"text": "हेलो", "intent": "greeting"},
    {"text": "हाय", "intent": "greeting"},
    {"text": "नमस्कार", "intent": "greeting"},
    {"text": "राम राम भाई", "intent": "greeting"},
    {"text": "गुड मॉर्निंग", "intent": "greeting"},
    {"text": "सत् श्री अकाल", "intent": "greeting"},
    {"text": "अस्सलाम वालेकुम", "intent": "greeting"},
    {"text": "help help me मदद करो", "intent": "greeting"},
    {"text": "कोई है क्या यहाँ", "intent": "greeting"},
    {"text": "क्या आप मेरी मदद कर सकते हैं", "intent": "greeting"},
    {"text": "hi chatbot show me commands", "intent": "greeting"},
    {"text": "सुनो भाई हेल्प चाहिए", "intent": "greeting"},
    {"text": "म्यूचुअल फंड गाइड शुरू करो", "intent": "greeting"},
    {"text": "शुरुआती सहायता दिखाओ", "intent": "greeting"},
    {"text": "5000 रुपये का एसआईपी 12% दर पर 10 साल के लिए कितना होगा", "intent": "sip_calc"},
    {"text": "1000 monthly investment for 5 years at 15 percent return", "intent": "sip_calc"},
    {"text": "हर महीने 2000 रुपये डालना है 20 वर्ष तक रिटर्न 10 परसेंट मिलेगा", "intent": "sip_calc"},
    {"text": "एस आई पी कैलकुलेटर बताओ 10000 का निवेश 18% ब्याज 5 साल", "intent": "sip_calc"},
    {"text": "sip maturity value calculated for 500 rs per month 12% rate 3 years", "intent": "sip_calc"},
    {"text": "अगर मैं हर महीने 15000 का निवेश करूं 15% पर 25 साल तक तो कितना मिलेगा", "intent": "sip_calc"},
    {"text": "म्यूचुअल फंड एसआईपी कैलकुलेशन 25000 monthly 10% interest 15 years", "intent": "sip_calc"},
    {"text": "सिस्टमैटिक इन्वेस्टमेंट प्लान गणना करो 3000 रुपये 12% 7 साल", "intent": "sip_calc"},
    {"text": "एसआईपी कितना रिटर्न देगा 2000 प्रति माह 15% दर 10 वर्ष", "intent": "sip_calc"},
    {"text": "calculate sip maturity for 1000 rupees at 12 percentage for 6 years", "intent": "sip_calc"},
    {"text": "मैंने सोचा है कि 50000 का एसआईपी करूँ 14% रिटर्न मानकर 12 साल तक", "intent": "sip_calc"},
    {"text": "पर मंथ 12000 का इन्वेस्टमेंट 11% इंटरेस्ट रेट पर 8 साल का कैलकुलेशन", "intent": "sip_calc"},
    {"text": "महीने का 8000 बचाकर एसआईपी में डालना है 15% रिटर्न पर 18 साल के लिए", "intent": "sip_calc"},
    {"text": "प्रतिमाह 3500 का निवेश 10% की दर से 22 साल का कुल फंड कितना बनेगा", "intent": "sip_calc"},
    {"text": "sip calculation matching 6000 amount 13 percent 5 years tenure", "intent": "sip_calc"},
    {"text": "500000 का टोटल निवेश 5000 का एसडब्ल्यूपी 8% पर 5 साल", "intent": "swp_calc"},
    {"text": "1000000 principal investment with 10000 monthly swp withdrawal 9% rate 10 years", "intent": "swp_calc"},
    {"text": "पेंशन के लिए 2500000 जमा किया हर महीने 15000 निकालना है 12% ब्याज दर पर 15 साल", "intent": "swp_calc"},
    {"text": "मासिक निकासी गणना एसडब्ल्यूपी 5000000 का निवेश 30000 विड्रॉल 10% दर 20 साल", "intent": "swp_calc"},
    {"text": "swp balance sheet calculator 200000 lumpsum 2000 payout 8% return 5 years", "intent": "swp_calc"},
    {"text": "अगर मैं 1200000 रुपये जमा करके 8000 महीना निकालूं 9% पर 8 साल तक तो क्या बचेगा", "intent": "swp_calc"},
    {"text": "एस आई पी से मिले पैसे का swp करना है 1500000 अमाउंट 12000 विड्रॉल 10% 12 साल", "intent": "swp_calc"},
    {"text": "सिस्टमैटिक विड्रॉल प्लान बताओ 800000 का कुल फंड 6000 मंथली पेंशन 7% ब्याज 6 साल", "intent": "swp_calc"},
    {"text": "lumpsum amount 3500000 withdraw 25000 monthly rate 11 percent years 15 computation", "intent": "swp_calc"},
    {"text": "रिटायरमेंट के बाद 4000000 जमा करके 35000 हर महीने निकालने पर 8% दर से 10 साल में क्या बचेगा", "intent": "swp_calc"},
    {"text": "एसडब्ल्यूपी कैलकुलेशन 1800000 का जमा 15000 का मासिक विड्रॉल 10% ब्याज 12 वर्ष", "intent": "swp_calc"},
    {"text": "monthly withdrawal swp matching 600000 total 4000 monthly 9% rate 4 years", "intent": "swp_calc"},
    {"text": "मुझे sbi म्यूचुअल फंड का लाइव रेट देखना है", "intent": "fund_info"},
    {"text": "hdfc का आज का एनएवी भाव क्या चल रहा है", "intent": "fund_info"},
    {"text": "parag parikh flexi cap fund details nav today check", "intent": "fund_info"},
    {"text": "एसबीआई ब्लूचिप फंड का भाव क्या है", "intent": "fund_info"},
    {"text": "एचडीएफसी मिडकैप फंड का आज का लाइव रेट बताओ", "intent": "fund_info"},
    {"text": "parag parikh direct growth plan updates current price check", "intent": "fund_info"},
    {"text": "म्यूचुअल फंड स्कीम डिटेल्स लाइव एनएवी ट्रेक करो", "intent": "fund_info"},
    {"text": "sbi growth fund performance check history price today", "intent": "fund_info"},
    {"text": "पराग पारिख म्यूचुअल फंड का भाव कितना है अभी", "intent": "fund_info"},
    {"text": "hdfc top mutual fund scheme rate analysis information", "intent": "fund_info"},
    {"text": "एसबीआई स्माल कैप फंड की एनएवी कितनी चल रही है", "intent": "fund_info"},
    {"text": "चेक लाइव एनएवी ऑफ एचडीएफसी टैक्स सेवर फंड", "intent": "fund_info"},
    {"text": "parag parikh arbitrage scheme direct nav calculation quotes", "intent": "fund_info"},
    {"text": "क्या आप मुझे आज का म्यूचुअल फंड का रेट दे सकते हैं", "intent": "fund_info"},
    {"text": "फंड की स्कीम डिटेल्स और करंट एनएवी स्टेटस शो करो", "intent": "fund_info"},
    {"text": "कौन सा म्यूचुअल फंड अच्छा है", "intent": "fund_info"},
    {"text": "सबसे अच्छी शिप", "intent": "fund_info"},
    {"text": "बेस्ट एसआईपी", "intent": "fund_info"},
    {"text": "सबसे अच्छा SIP", "intent": "fund_info"},
    {"text": "मेरी आय के अनुसार कौन सा म्यूचुअल फंड अच्छा है", "intent": "fund_info"},
    {"text": "कितनी कमाई पर कौन सा फंड लें", "intent": "fund_info"},
    {"text": "मेरी सैलरी 20 लाख है कौन सा फंड अच्छा रहेगा", "intent": "fund_info"},
    {"text": "बेस्ट फंड कौन सा है", "intent": "fund_info"},
]

KNOWLEDGE_BASE = {
    "sbi bluechip fund": {
        "name": "SBI Bluechip Fund (Direct - Growth)",
        "nav": "₹ 62.50",
        "date": "2024-07-25",
        "min_sip": "₹ 500",
        "risk": "High",
        "category": "Large Cap",
        "details": "यह एक लार्ज कैप इक्विटी फंड है जो मुख्य रूप से बड़ी कंपनियों में निवेश करता है।",
    },
    "hdfc mid-cap opportunities fund": {
        "name": "HDFC Mid-Cap Opportunities Fund (Direct - Growth)",
        "nav": "₹ 165.75",
        "date": "2024-07-25",
        "min_sip": "₹ 1000",
        "risk": "Very High",
        "category": "Mid Cap",
        "details": "यह फंड मध्यम आकार की कंपनियों में निवेश करता है जिनमें विकास की उच्च क्षमता होती है।",
    },
    "parag parikh flexi cap fund": {
        "name": "Parag Parikh Flexi Cap Fund (Direct - Growth)",
        "nav": "₹ 78.90",
        "date": "2024-07-25",
        "min_sip": "₹ 1000",
        "risk": "High",
        "category": "Flexi Cap",
        "details": "यह एक फ्लेक्सी कैप फंड है जो लार्ज, मिड और स्मॉल कैप कंपनियों में निवेश कर सकता है।",
    },
}


def format_indian_currency(amount):
    amount = int(amount)
    if amount >= 10000000:
        return f"₹ {amount / 10000000:.2f} करोड़"
    if amount >= 100000:
        return f"₹ {amount / 100000:.2f} लाख"
    return f"₹ {amount:,}"


class HindiFinancialNLP:
    def __init__(self, dataset_list):
        grouped_dataset = {}
        for item in dataset_list:
            intent = item["intent"]
            text = item["text"]
            grouped_dataset[intent] = f"{grouped_dataset.get(intent, '')} {text}".strip()

        self.dataset = {text: intent for intent, text in grouped_dataset.items()}
        self.X_train, self.intents = self.train_model()

    def tokenize(self, text):
        return re.findall(r"\b\w+\b", text.lower().strip(), re.UNICODE)

    def train_model(self):
        corpus = [Counter(self.tokenize(text)) for text in self.dataset.keys()]
        intents = list(self.dataset.values())
        X_train = corpus
        return X_train, intents

    def predict(self, text):
        query_vec = Counter(self.tokenize(text))
        similarities = [self.cosine_similarity(query_vec, train_vec) for train_vec in self.X_train]
        max_idx = max(range(len(similarities)), key=similarities.__getitem__)
        if similarities[max_idx] < 0.10:
            return "unknown"
        return self.intents[max_idx]

    def cosine_similarity(self, vec_a, vec_b):
        intersection = set(vec_a) & set(vec_b)
        numerator = sum(vec_a[token] * vec_b[token] for token in intersection)
        norm_a = math.sqrt(sum(value * value for value in vec_a.values()))
        norm_b = math.sqrt(sum(value * value for value in vec_b.values()))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return numerator / (norm_a * norm_b)


def calculate_sip(monthly, rate, years):
    monthly_rate = (rate / 100) / 12
    months = years * 12
    future_value = monthly * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
    invested = monthly * months
    returns = future_value - invested
    return round(future_value), round(invested), round(returns)


def calculate_swp(principal, withdrawal, rate, years):
    monthly_rate = (rate / 100) / 12
    months = years * 12
    balance = principal
    withdrawn = 0
    for _ in range(months):
        if balance <= 0:
            break
        balance = (balance * (1 + monthly_rate)) - withdrawal
        withdrawn += withdrawal
    return max(0, round(balance)), round(withdrawn)


def contains_sip_signal(user_input_lower):
    sip_keywords = ["sip", "एसआईपी", "एस आई पी"]
    monthly_keywords = ["monthly", "per month", "हर महीने", "हर महिने", "mahine", "mahina", "month", "महीने"]
    year_keywords = ["saal", "sal", "year", "years", "yr", "yrs", "वर्ष", "साल"]

    has_sip_word = any(keyword in user_input_lower for keyword in sip_keywords)
    has_monthly_word = any(keyword in user_input_lower for keyword in monthly_keywords)
    has_year_word = any(keyword in user_input_lower for keyword in year_keywords)
    return has_sip_word or (has_monthly_word and has_year_word)


def extract_years(user_input_lower):
    match = re.search(r"(\d+)\s*(saal|sal|year|years|yr|yrs|वर्ष|साल)", user_input_lower)
    return int(match.group(1)) if match else None


def extract_rate(user_input_lower):
    match = re.search(r"(\d+)\s*(%|percent|percentage|return|rate|interest|ब्याज|दर)", user_input_lower)
    return int(match.group(1)) if match else None


def extract_sip_amount(user_input, years=None, rate=None):
    numbers = [int(s) for s in re.findall(r"\d+", user_input)]
    remaining_numbers = numbers[:]

    if years in remaining_numbers:
        remaining_numbers.remove(years)
    if rate in remaining_numbers:
        remaining_numbers.remove(rate)

    return remaining_numbers[0] if remaining_numbers else None


def generate_hindi_response(user_input):
    intent = nlp_model.predict(user_input)
    numbers = [int(s) for s in re.findall(r"\d+", user_input)]
    user_input_lower = user_input.lower()

    if any(word in user_input_lower for word in ["stock", "शेयर", "crypto", "क्रिप्टो"]):
        return (
            "माफ कीजिए, मैं अभी मुख्य रूप से mutual funds, SIP, SWP और basic financial planning पर मदद करता हूँ। "
            "स्टॉक या क्रिप्टो पर मैं सलाह नहीं देता।"
        )

    if any(word in user_input_lower for word in ["निफ्टी", "risk", "जोखिम", "volatility", "उतार", "गिरावट"]):
        return (
            "निफ्टी में जोखिम समझने के लिए 4 चीज़ें देखें: "
            "1. उतार-चढ़ाव कितना है, 2. आपका निवेश समय कितना लंबा है, "
            "3. गिरावट में आप कितना नुकसान सह सकते हैं, 4. क्या आपका पैसा diversified है। "
            "अगर लक्ष्य short-term है, तो equity risk ज्यादा महसूस होगा; long-term horizon में SIP और diversification मदद करते हैं।"
        )

    if intent == "greeting":
        return (
            "नमस्ते! मैं HindiFinancialNLP v2 हूँ। मैं SIP, SWP, mutual fund जानकारी और basic financial planning में आपकी मदद कर सकता हूँ।"
        )

    if intent == "sip_calc" or contains_sip_signal(user_input_lower):
        years = extract_years(user_input_lower)
        rate = extract_rate(user_input_lower) or 12
        monthly = extract_sip_amount(user_input, years=years, rate=rate if extract_rate(user_input_lower) else None)

        if monthly and years:
            future_value, invested, returns = calculate_sip(monthly, rate, years)
            return (
                "📊 SIP गणना परिणाम:\n"
                f"हर महीने निवेश: {format_indian_currency(monthly)}\n"
                f"अनुमानित वार्षिक रिटर्न: {rate}%\n"
                f"कुल निवेश: {format_indian_currency(invested)}\n"
                f"अनुमानित मुनाफा: {format_indian_currency(returns)}\n"
                f"{years} साल बाद कुल वैल्यू: {format_indian_currency(future_value)}\n"
                "यह अनुमान monthly SIP और compounding के आधार पर निकाला गया है।"
            )
        return (
            "कृपया SIP गणना के लिए कम से कम monthly amount और कितने साल निवेश करना है, यह बताएं। "
            "अगर return rate नहीं देंगे तो मैं 12% default मान लूंगा।"
        )

    if intent == "swp_calc":
        if len(numbers) >= 4:
            principal, withdrawal, rate, years = numbers[0], numbers[1], numbers[2], numbers[3]
            balance, withdrawn = calculate_swp(principal, withdrawal, rate, years)
            return (
                "📊 SWP गणना परिणाम:\n"
                f"प्रारंभिक निवेश: {format_indian_currency(principal)}\n"
                f"मासिक निकासी: {format_indian_currency(withdrawal)}\n"
                f"कुल निकासी: {format_indian_currency(withdrawn)}\n"
                f"{years} साल बाद बचा बैलेंस: {format_indian_currency(balance)}"
            )
        return "कृपया SWP गणना के लिए कुल निवेश, मासिक निकासी, ब्याज दर और वर्षों की संख्या बताएं।"

    if intent == "fund_info":
        for fund_key, fund_data in KNOWLEDGE_BASE.items():
            if fund_key in user_input_lower:
                return (
                    "📈 फंड जानकारी:\n"
                    f"स्कीम: {fund_data['name']}\n"
                    f"NAV: {fund_data['nav']}\n"
                    f"तारीख: {fund_data['date']}\n"
                    f"न्यूनतम SIP: {fund_data['min_sip']}\n"
                    f"जोखिम स्तर: {fund_data['risk']}\n"
                    f"श्रेणी: {fund_data['category']}\n"
                    f"विवरण: {fund_data['details']}"
                )
        return (
            "म्यूचुअल फंड चुनते समय अपने goal, time horizon और risk capacity को ध्यान में रखें। "
            "अगर आप चाहें तो किसी specific fund का नाम पूछें, जैसे SBI Bluechip, HDFC Mid-Cap, या Parag Parikh Flexi Cap."
        )

    return (
        "मैं आपकी mutual funds, SIP, SWP और निवेश जोखिम से जुड़ी basic queries में मदद कर सकता हूँ। "
        "अगर आप चाहें तो अपना सवाल थोड़ा और specific लिखें."
    )


nlp_model = HindiFinancialNLP(financial_nlp_dataset)


def get_bot_reply(message):
    return generate_hindi_response(message)


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    message = data.get("message", "")

    if not message:
        return jsonify({"error": "Message is required"}), 400

    reply = get_bot_reply(message)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
