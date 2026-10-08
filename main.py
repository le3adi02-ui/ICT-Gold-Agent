import os
import yfinance as yf
import google.generativeai as genai
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

try:
    # جلب بيانات العقود الآجلة للذهب (أكثر استقراراً في Yahoo Finance)
    gold = yf.Ticker("GC=F")
    df = gold.history(period="2d", interval="5m")

    # حماية من الكراش إذا كان السيرفور مبلوكي من طرف Yahoo
    if df is None or df.empty or len(df) < 14:
        print("⏳ بيانات الذهب غير متوفرة حالياً. سيتم المحاولة بعد 10 دقائق...")
        exit()

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

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')

    prompt = f"""
    أنت متداول Intraday محترف تدمج بين SMC، العرض والطلب، والبرايس أكشن.
    بيانات الذهب (GC=F) على فريم 5 دقائق الآن:
    - السعر الحالي: {current_price:.2f}$
    - أقرب مقاومة (Supply): {resistance:.2f}$
    - أقرب دعم (Demand): {support:.2f}$
    - البرايس أكشن: {pa_signal}
    - معدل الحركة (ATR): {atr_value:.2f}$

    شروط إدارة المخاطر الصارمة (إلزامية):
    1. الحد الأقصى لوقف الخسارة (SL): لا يتجاوز 150 نقطة (15.00$).
    2. العائد مقابل المخاطرة (Risk/Reward): الهدف (TP) يجب أن يكون 1:1 كأضعف الإيمان، ويفضل 1:2 أو 1:3.

    تنسيق الرد الإلزامي:
    🎯 **الاستراتيجية:**
    🛒 **القرار:** (Sell أو Buy أو Wait)
    📌 **نقطة الدخول:** 
    🛑 **وقف الخسارة (SL):** 
    💰 **الهدف (TP):** 
    📝 **التحليل:** 
    """

    response = model.generate_content(prompt)
    analysis = response.text
    
    if "Wait" not in analysis and "انتظار" not in analysis:
        message = f"⚡ **رصد فرصة Intraday حية (Gold)** ⚡\n\n{analysis}"
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=payload)
        print("✅ تم رصد فرصة وإرسالها إلى تليغرام.")
    else:
        print("⏳ السوق غير مناسب الآن (Wait).")
        
except Exception as e:
    print(f"Error: {e}")
