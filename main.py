import yfinance as yf
import google.generativeai as genai
import requests
import time
import pandas as pd

# --- حط الكودات ديالك هنا ---
GEMINI_API_KEY = "AQ.Ab8RN6J5T-q9IOIm6P3YRJxsVVzs4o1gVr58-O9cEhvHiBFbyQ"
TELEGRAM_TOKEN = "8859402714:AAEWCleyZwGU90J9Vccf5Og864YFIEz7cgI"
CHAT_ID = "1617045979"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-3.8-flash')

def get_market_data():
    gold = yf.Ticker("XAUUSD=X")
    df = gold.history(period="2d", interval="5m")

    # 1. البرايس أكشن
    last_candle = df.iloc[-2]
    body = abs(last_candle['Open'] - last_candle['Close'])
    upper_wick = last_candle['High'] - max(last_candle['Open'], last_candle['Close'])
    lower_wick = min(last_candle['Open'], last_candle['Close']) - last_candle['Low']

    pa_signal = "شمعة عادية"
    if lower_wick > body * 2 and upper_wick < body:
        pa_signal = "🟢 Pin Bar شرائي (رفض من الأسفل)"
    elif upper_wick > body * 2 and lower_wick < body:
        pa_signal = "🔴 Pin Bar بيعي (رفض من الأعلى)"

    # 2. العرض والطلب
    resistance = df['High'].iloc[-50:].max()
    support = df['Low'].iloc[-50:].min()
    current_price = df['Close'].iloc[-1]

    # 3. حساب ATR
    df['ATR'] = df['High'] - df['Low']
    atr_value = df['ATR'].iloc[-14:].mean()

    return current_price, resistance, support, pa_signal, atr_value

print("🟢 السيرفور اللايف خدام دابا... كيسكاني المارشي كل 5 دقايق (حبسو بيدك يلا بغيتي)")

while True:
    try:
        current_price, res, sup, pa_signal, atr = get_market_data()

        # التعديل الجديد صارم فيما يخص SL و TP
        prompt = f"""
        أنت متداول Intraday محترف تدمج بين SMC، العرض والطلب، والبرايس أكشن.
        بيانات الذهب (XAU/USD) على فريم 5 دقائق الآن:
        - السعر الحالي: {current_price:.2f}$
        - أقرب مقاومة (Supply): {res:.2f}$
        - أقرب دعم (Demand): {sup:.2f}$
        - البرايس أكشن: {pa_signal}
        - معدل الحركة (ATR): {atr:.2f}$

        شروط إدارة المخاطر الصارمة (إلزامية):
        1. الحد الأقصى لوقف الخسارة (SL): يجب ألا يتجاوز 150 نقطة (Pips)، أي ما يعادل 15.00$ كحد أقصى في حركة السعر.
        2. العائد مقابل المخاطرة (Risk/Reward): الهدف (TP) يجب أن يكون على الأقل 1:1 (أي مساوي لحجم SL)، ويُفضل جداً أن يكون 1:2 أو 1:3 إذا كانت أقرب منطقة سيولة تسمح بذلك.

        بناءً على هذه المعطيات، ابحث عن أقرب فرصة.
        تنسيق الرد الإلزامي:
        🎯 **الاستراتيجية:** (اذكر المدرسة الفنية)
        🛒 **القرار:** (Sell أو Buy أو Wait)
        📌 **نقطة الدخول:**
        🛑 **وقف الخسارة (SL):** (بحد أقصى 15.00$ من نقطة الدخول)
        💰 **الهدف (TP):** (RR 1:1 كحد أدنى)
        📝 **التحليل:**
        """

        response = model.generate_content(prompt)
        analysis = response.text

        if "Wait" not in analysis and "انتظار" not in analysis:
            message = f"⚡ **رصد فرصة Intraday حية (XAU/USD)** ⚡\n\n{analysis}"
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
            requests.post(url, data=payload)
            print(f"✅ فرصة تصيفطات مع {time.strftime('%H:%M:%S')}")
            time.sleep(1800) # انتظار نصف ساعة بعد إرسال الصفقة
        else:
            print(f"⏳ {time.strftime('%H:%M:%S')} - السوق غير واضح أو الـ SL سيتجاوز 150 بيبس، كنتسناو الشمعة الجاية...")

    except Exception as e:
        print(f"وقع خطأ: {e}")

    time.sleep(300)
