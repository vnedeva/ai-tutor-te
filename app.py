import streamlit as st
import google.generativeai as genai

# --- КОНФИГУРАЦИЯ НА СТРАНИЦАТА ---
st.set_page_config(page_title="ТЕ-1 Асистент", page_icon="⚡")

# --- СКРИВАНЕ НА МЕНЮТАТА (За да изглежда като част от Moodle) ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- ВЗИМАНЕ НА API КЛЮЧА ---
# Ключът ще се вземе от "Secrets" в Streamlit, за да не е публичен тук
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("Липсва API ключ! Моля, настройте го в Streamlit Secrets.")
    st.stop()

# --- СИСТЕМЕН ПРОМПТ (МОЗЪКЪТ НА БОТА) ---
SYSTEM_PROMPT = """
РОЛЯ:
Ти си "AI Тутор по Теоретична електротехника - Част 1".
Твоята цел е да подготвиш студентите за семестриален изпит (тест).

ОСНОВНИ ПРАВИЛА:
1. Език: Български.
2. Имагинерна единица: Винаги използвай 'j' (j), а НЕ 'i'.
3. Формули: Използвай LaTeX формат ($...$).
4. Педагогика: Не давай верния отговор веднага. Накарай студента да мисли.

ТЕМИТЕ (КОНСПЕКТ):
1. Основни величини и топология.
2. Пасивни елементи (R, L, C).
3. Закони на Ом и Кирхоф.
4. Преобразуване на пасивни вериги.
5. Мощност и енергия.
6. Източници на напрежение и ток.
7. Метод на клоновите токове (МКТ).
8. Метод на контурните токове.
9. Метод на възловите потенциали.
10. Теорема на Тевенен и Нортън.
11. Принцип на налагането.
12. Синусоидални величини и вектори.
13. Комплексен символичен метод.
14. Закони на Ом и Кирхоф в комплексна форма.
15. Мощност в променливотокови вериги.
16. Изследване на неразклонени вериги (RL, RC, RLC).
17. Резонанс на напреженията.
18. Паралелно свързване и резонанс на токовете.
19. Символичен метод за разклонени вериги.
20. Индуктивно свързани вериги.
21. Трансформаторно включване.
22. Трифазни системи (Звезда/Триъгълник).
23. Мощност в трифазни системи.

РЕЖИМ "ИЗПИТВАНЕ" (QUIZ MODE):
Когато студент поиска "въпрос", "тест" или "задача":
1. Попитай за коя тема (1-23) или избери случайна.
2. Генерирай въпрос с 3 опции (А, Б, В).
3. Изчакай отговора.
   - ГРЕШЕН: Обясни защо.
   - ВЕРЕН: Потвърди и обясни кратко.

ПРИМЕРНИ ВЪПРОСИ ЗА СТИЛ:
- Векторни диаграми: Искай разпознаване на дължина/ъгъл.
- Комплексни числа: Искай превърщане в комплексен вид (напр. 60/sqrt(2)).
- Трифазни: Връзка между линейни и фазови величини (корен от 3).
"""

# --- ЗАРЕЖДАНЕ НА МОДЕЛА ---
# Използваме flash модела за бързина
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", 
    system_instruction=SYSTEM_PROMPT
)

# --- ЧАТ ИНТЕРФЕЙС ---
st.title("⚡ ТЕ-1: Виртуален Асистент")

if "messages" not in st.session_state:
    st.session_state.messages = []
    # Първоначално съобщение
    welcome_msg = "Здравей! Аз съм твоят тутор по Теоретична електротехника. Искаш ли да преговорим някоя тема или да ти дам пробен въпрос за теста?"
    st.session_state.messages.append({"role": "model", "parts": [welcome_msg]})

# Показване на историята
for message in st.session_state.messages:
    role = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message["parts"][0])

# Обработка на нов въпрос
if prompt := st.chat_input("Напиши тук... (напр. 'Дай ми въпрос за Трифазни системи')"):
    # 1. Показваме въпроса на студента
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "parts": [prompt]})

    # 2. Питаме Gemini
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            # Изпращаме историята за контекст
            chat = model.start_chat(history=st.session_state.messages[:-1])
            response = chat.send_message(prompt)
            message_placeholder.markdown(response.text)
            
            # Запазваме отговора
            st.session_state.messages.append({"role": "model", "parts": [response.text]})
        except Exception as e:
            message_placeholder.error(f"Възникна грешка: {str(e)}")
