import streamlit as st
from google import genai
from google.genai import types

# הגדרת כותרת וממשק
st.set_page_config(page_title="ג'נוגרם תעסוקתי", layout="wide")
st.title("🌳 סוכן ג'נוגרם תעסוקתי")
st.write("בוא נמפה יחד את עץ המשפחה התעסוקתי שלך כדי לחלץ תובנות ודפוסים לקריירה.")

# שליפת מפתח ה-API מתוך ה-Secrets
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("מפתח API לא הוגדר במערכת. אנא הגדר GEMINI_API_KEY בהגדרות המערכת.")
    st.stop()

# אתחול לקוח ה-API של גוגל (ה-SDK הנוכחי: google-genai)
client = genai.Client(api_key=api_key)

# alias שגוגל מתחזקת ומצביע תמיד על מודל ה-Flash היציב העדכני ביותר,
# כך שלא צריך לעדכן ידנית בכל פעם שגוגל משנה גרסאות
MODEL_NAME = "gemini-flash-latest"

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

# ניהול היסטוריית שיחה ב-session_state
if "messages" not in st.session_state:
    first_message = "שלום! נעים מאוד. כדי שנוכל לבנות יחד את עץ המשפחה התעסוקתי שלך, נתחיל בך: מה המקצוע או התחום העיקרי שבו אתה עוסק כיום (או עסקת בעבר), ומאיזה סגנון חיים היית רוצה ליהנות?"
    st.session_state.messages = [{"role": "model", "parts": [first_message]}]

# הצגת היסטוריית השיחה
for msg in st.session_state.messages:
    display_role = "user" if msg["role"] == "user" else "assistant"
    with st.chat_message(display_role):
        st.write(msg["parts"][0])

# קלט מהמשתמש
if user_input := st.chat_input("קליד/י את תשובתך כאן..."):
    # הצגת הודעת המשתמש
    st.session_state.messages.append({"role": "user", "parts": [user_input]})
    with st.chat_message("user"):
        st.write(user_input)

    # שליחת הבקשה
    with st.chat_message("assistant"):
        with st.spinner("מעבד נתונים..."):
            try:
                # היסטוריה עבור ה-API: כל ההודעות מלבד הודעת הפתיחה הקבועה
                # (שלא נוצרה ע"י המודל בפועל) וההודעה האחרונה, שנשלחת כעת בנפרד
                history = []
                for m in st.session_state.messages[1:-1]:
                    role = "user" if m["role"] == "user" else "model"
                    history.append(
                        types.Content(role=role, parts=[types.Part(text=m["parts"][0])])
                    )

                chat = client.chats.create(
                    model=MODEL_NAME,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
                    history=history,
                )
                response = chat.send_message(user_input)

                st.write(response.text)
                st.session_state.messages.append({"role": "model", "parts": [response.text]})
            except Exception as e:
                st.error(f"ארעה שגיאה בתקשורת: {e}")
