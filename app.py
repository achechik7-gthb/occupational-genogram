import streamlit as st
import google.generativeai as genai

# הגדרת כותרת וממשק
st.set_page_config(page_title="ג'נוגרם תעסוקתי", layout="wide")
st.title("🌳 סוכן ג'נוגרם תעסוקתי")
st.write("בוא נמפה יחד את עץ המשפחה התעסוקתי שלך כדי לחלץ תובנות ודפוסים לקריירה.")

# שליפת מפתח ה-API מתוך ה-Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("מפתח API לא הוגדר במערכת. אנא הגדר GEMINI_API_KEY בהגדרות המערכת.")
    st.stop()

# הגדרת המפתח עבור הספרייה של גוגל
genai.configure(api_key=api_key)

# הנחיות המערכת עבור הסוכן
SYSTEM_INSTRUCTION = """
אתה סוכן AI מומחה באבחון ותכנון קריירה באמצעות "עץ משפחה תעסוקתי" (ג'נוגרם תעסוקתי).
תפקידך לאסוף מהמשתמש נתונים בצורה מדורגת, לייצר תרשים Mermaid, ולהשיב לשאלות.

הנחיות לשיחה:
1. שאל שאלה אחת או שתיים בכל פעם בלבד (אל תציף).
2. אסוף: דור המשתמש, דור ההורים (מקצועות, מ"מ - מצליחים מקצועית, סגנון חיים מוערך, ומסרים על עבודה), ודור הסבים במידה ויודע.
3. כשהמידע מספיק, ספק תרשים Mermaid תקני בתוך בלוק קוד של ```mermaid ... ```, ולאחר מכן הצע 2-3 תובנות על דפוסים בין-דוריים שעולים מהעץ.
4. לאחר השלמת התרשים, ענה על כל שאלה של המשתמש לגבי תובנות, Job Crafting, או הכוונה תעסוקתית מתוך הממצאים.
"""

# אתחול המודל היציב
model = genai.GenerativeModel(
    model_name="models/gemini-pro",
    system_instruction=SYSTEM_INSTRUCTION
)

# ניהול היסטוריית שיחה
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
    # הודעת פתיחה של הסוכן
    first_message = "שלום! נעים מאוד. כדי שנוכל לבנות יחד את עץ המשפחה התעסוקתי שלך, נתחיל בך: מה המקצוע או התחום העיקרי שבו אתה עוסק כיום (או עסקת בעבר), ומאיזה סגנון חיים היית רוצה ליהנות?"
    st.session_state.messages = [{"role": "model", "text": first_message}]

# הצגת היסטוריית השיחה
for msg in st.session_state.messages:
    role_label = "🧑‍💼 אתה" if msg["role"] == "user" else "🤖 סוכן ג'נוגרם"
    with st.chat_message(msg["role"]):
        st.write(msg["text"])

# קלט מהמשתמש
if user_input := st.chat_input("קליד/י את תשובתך כאן..."):
    # הצגת הודעת המשתמש
    st.session_state.messages.append({"role": "user", "text": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # שליחת התשובה למודל
    with st.chat_message("model"):
        with st.spinner("מעבד נתונים..."):
            try:
                response = st.session_state.chat.send_message(user_input)
                st.write(response.text)
                st.session_state.messages.append({"role": "model", "text": response.text})
            except Exception as e:
                st.error(f"ארעה שגיאה בתקשורת: {e}")
