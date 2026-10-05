import yfinance as yf
import google.generativeai as genai
import requests

# --- حط الكودات ديالك هنا ---
GEMINI_API_KEY = "AQ.Ab8RN6J5T-q9IOIm6P3YRJxsVVzs4o1gVr58-O9cEhvHiBFbyQ"
TELEGRAM_TOKEN = "8859402714:AAEWCleyZwGU90J9Vccf5Og864YFIEz7cgI"
CHAT_ID = "1617045979"

print("⏳ كنجبدو الشموع ديال Spot Gold (XAUUSD)...")
# استعملنا XAUUSD=X باش يعطينا نفس الشارت ديال TradingView
gold = yf.Ticker("XAUUSD=X")
df = gold.history(period="5d", interval="15m")

def find_tight_ict_setup(df):
    for i in range(len(df)-1, 20, -1):
        
        # 1. إعداد البيع (Bearish)
        if df['High'].iloc[i] < df['Low'].iloc[i-2]:  
            fvg_top = df['Low'].iloc[i-2]
            
            # كنجبدو أعلى قمة فداك السوينغ بالضبط (الشمعة لي خدات السيولة)
            swing_high = df['High'].iloc[i-4:i-1].max() 
            prev_highs = df['High'].iloc[i-15:i-5].max()
            
            if swing_high > prev_highs: # تأكيد سحب السيولة (Sweep)
                entry = fvg_top
                sl = swing_high + 0.30 # ستوب لوز فوق الذيل بـ 30 سنت فقط
                risk = sl - entry
                
                # 🔥 فلتر الخسارة الصارم: إذا كان الستوب كبر من 3 دولار، الغي الصفقة
                if risk <= 3.00:
                    tp = entry - (risk * 3)
                    return f"🔴 **إعداد بيع (Bearish ICT)**\n- 📌 **الدخول (Sell Limit):** {entry:.2f}$\n- 🛑 **الستوب (SL):** {sl:.2f}$ (مخاطرة صغيرة: {risk:.2f}$)\n- 💰 **الهدف (TP):** {tp:.2f}$ (RR 1:3)"

        # 2. إعداد الشراء (Bullish)
        elif df['Low'].iloc[i] > df['High'].iloc[i-2]: 
            fvg_bottom = df['High'].iloc[i-2]
            
            # كنجبدو أدنى قاع فداك السوينغ
            swing_low = df['Low'].iloc[i-4:i-1].min()
            prev_lows = df['Low'].iloc[i-15:i-5].min()
            
            if swing_low < prev_lows: # تأكيد سحب السيولة
                entry = fvg_bottom
                sl = swing_low - 0.30 # ستوب لوز تحت الذيل بـ 30 سنت
                risk = entry - sl
                
                # 🔥 فلتر الخسارة الصارم: إذا كان الستوب كبر من 3 دولار، الغي الصفقة
                if risk <= 3.00:
                    tp = entry + (risk * 3)
                    return f"🟢 **إعداد شراء (Bullish ICT)**\n- 📌 **الدخول (Buy Limit):** {entry:.2f}$\n- 🛑 **الستوب (SL):** {sl:.2f}$ (مخاطرة صغيرة: {risk:.2f}$)\n- 💰 **الهدف (TP):** {tp:.2f}$ (RR 1:3)"

    return "⚪ **(Wait)** لا توجد فرصة محققة حالياً، أو أن الفرص المتاحة وقف خسارتها (SL) واسع جداً ولا يحترم خطة إدارة المخاطر."

setup_result = find_tight_ict_setup(df)
print(setup_result)

print("🧠 توجيه الذكاء الاصطناعي...")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-3.8-flash') 

prompt = f"""
أنت مساعد آلي يرسل تنبيهات ICT.
هذه هي البيانات الدقيقة:
{setup_result}
قم بصياغتها في رسالة تلغرام واضحة جداً، حافظ على نفس أرقام Entry و SL و TP والمخاطرة بدون أي تغيير.
"""

response = model.generate_content(prompt)
message = f"🚨 **تحديث ICT الدقيق (XAU/USD)** 🚨\n\n{response.text}"

url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
requests.post(url, data=payload)
print("✅ التوصية الدقيقة وصلات لتليغرام!")
