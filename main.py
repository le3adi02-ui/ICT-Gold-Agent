import yfinance as yf
import google.generativeai as genai
import requests

# --- حط الكودات ديالك هنا ---
GEMINI_API_KEY = "AQ.Ab8RN6J5T-q9IOIm6P3YRJxsVVzs4o1gVr58-O9cEhvHiBFbyQ"
TELEGRAM_TOKEN = "8859402714:AAEWCleyZwGU90J9Vccf5Og864YFIEz7cgI"
CHAT_ID = "1617045979"

# 1. جلب البيانات (فريم 5 دقائق)
gold = yf.Ticker("XAUUSD=X")
df = gold.history(period="2d", interval="5m")

last_candle = df.iloc[-2]
body = abs(last_candle['Open'] - last_candle['Close'])
upper_wick = last_candle['High'] - max(last_candle['Open'], last_candle['Close'])
lower_wick = min(last_candle['Open'], last_candle['Close']) - last_candle['Low']

pa_signal = "شمعة عادية"
if lower_wick > body * 2 and upper_wick < body:
    pa_signal = "🟢 Pin Bar شرائي (رفض من الأسفل)"
elif upper_wick > body * 2 and lower_wick < body:
    pa_signal = "🔴 Pin Bar بيعي (رفض من الأعلى)"

resistance = df['High'].iloc[-50:].max()
support = df['Low'].iloc[-50:].min()
current_price = df['Close'].iloc[-1]

df['ATR'] = df['High'] - df['Low']
atr_value = df['ATR'].iloc[-14:].mean()

# 2. تحليل الذكاء الاصطناعي
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

prompt = f"""
أنت متداول Intraday محترف تدمج بين SMC، العرض والطلب، والبرايس أكشن.
بيانات الذهب (XAU/USD) على فريم 5 دقائق الآن:
- السعر الحالي: {current_price:.2f}$
- أقرب مقاومة (Supply): {res:.2f}$
- أقرب دعم (Demand): {sup:.2f}$
- البرايس أكشن: {pa_signal}
- معدل الحركة (ATR): {atr:.2f}$

شروط إدارة المخاطر الصارمة (إلزامية):
1. الحد الأقصى لوقف الخسارة (SL): لا يتجاوز 150 نقطة (15.00$).
2. العائد مقابل المخاطرة (Risk/Reward): الهدف (TP) يجب أن يكون 1:1 كأضعف الإيمان، ويفضل 1:2.

تنسيق الرد الإلزامي:
🎯 **الاستراتيجية:**
🛒 **القرار:** (Sell أو Buy أو Wait)
📌 **نقطة الدخول:** 
🛑 **وقف الخسارة (SL):** 
💰 **الهدف (TP):** 
📝 **التحليل:** 
"""

try:
    response = model.generate_content(prompt)
    analysis = response.text
    
    if "Wait" not in analysis and "انتظار" not in analysis:
        message = f"⚡ **رصد فرصة Intraday حية (XAU/USD)** ⚡\n\n{analysis}"
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=payload)
        print("✅ تم رصد فرصة وإرسالها إلى تليغرام.")
    else:
        print("⏳ السوق غير مناسب، سيتم الفحص مجدداً بعد 10 دقائق...")
except Exception as e:
    print(f"Error: {e}")
