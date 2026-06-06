import streamlit as st
from dotenv import load_dotenv
import os
import json
import sqlite3
from datetime import datetime

load_dotenv()
api_key=os.getenv("API_KEY")
from google import genai
client=genai.Client(api_key=api_key)

def init_db():
    conn = sqlite3.connect("transactions.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS raw_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_transaction(text):
    conn = sqlite3.connect("transactions.db")
    c = conn.cursor()
    c.execute("INSERT INTO raw_transactions (text, date) VALUES (?, ?)",
              (text, datetime.now().strftime("%d %b %Y, %I:%M %p")))
    conn.commit()
    conn.close()

def get_all_transactions():
    conn = sqlite3.connect("transactions.db")
    c = conn.cursor()
    c.execute("SELECT id, text, date FROM raw_transactions ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def delete_transaction(tid):
    conn = sqlite3.connect("transactions.db")
    c = conn.cursor()
    c.execute("DELETE FROM raw_transactions WHERE id = ?", (tid,))
    conn.commit()
    conn.close()

def clear_all_transactions():
    conn = sqlite3.connect("transactions.db")
    c = conn.cursor()
    c.execute("DELETE FROM raw_transactions")
    conn.commit()
    conn.close()

init_db()


SYSTEM_PROMPT = '''
You are a GST filing assistant for small Indian traders.
The user will describe their transactions in Hindi or English or a mix of both.
 
For each transaction, extract and return a JSON array like this:
 
[
  {
    "description": "Short description of item/service in English",
    "hsn_code": "HSN or SAC code",
    "amount": 000,
    "gst_rate": 00,
    "gst_amount": 00,
    "type": "Sale or Purchase or Expense"
  }
]
 
Rules:
- amount is the base amount BEFORE GST (in rupees, number only)
- gst_rate is the percentage 
- gst_amount = amount * gst_rate / 100
- type: "Sale" if sold something, "Purchase" if bought stock, "Expense" if it's an overhead
- If the user mentions a return or refund, set amount as negative
- Return ONLY the JSON array. No explanation, no markdown, no extra text.
'''
def transaction_analyser(transaction):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            f'''{SYSTEM_PROMPT}
                Transaction: {transaction}''',
        ]
    )
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

#webpage now
st.set_page_config(page_title="GST Saathi", page_icon="🧾", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poiret+One&family=Rubik+80s+Fade&family=Tektur&display=swap');


html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

#MainMenu, footer, header { visibility: hidden; }

.block-container { max-width: 780px; padding: 2.5rem 2rem; }

.hero{
    text-align:center;
    padding-top:10px;
    padding-bottom:20px;
}
.hero-logo{
    font-family:'Rubik 80s Fade', cursive;
    font-size:5rem;
    line-height:1;
    margin-bottom:18px;

    background:linear-gradient(
        90deg,
        #60a5fa,
        #a78bfa,
        #34d399
    );
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;

    text-shadow:
        0 0 20px rgba(96,165,250,0.3),
        0 0 40px rgba(167,139,250,0.2);
}

.hero-tagline{
    font-family:'Tektur', sans-serif;
    font-size:1.3rem;
    font-weight:600;
    color:white;
    margin-bottom:10px;
    letter-spacing:2px;
}

.hero-sub{
    font-family:'Poiret One', sans-serif;
    font-size:1.15rem;
    color:#cbd5e1;
    max-width:650px;
    margin:auto;
}
.hero h1 {
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.4rem;
}
.hero p { color: #94a3b8; font-size: 1rem; font-weight: 300; }

.glass {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    backdrop-filter: blur(10px);
}

.section-label {
    font-size: 0.8rem;
    font-weight: 700;
    color: #a78bfa;
    letter-spacing: 2px;
    margin-bottom: 10px;
}
/* DB entry rows */
.entry-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 14px; border-radius: 10px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 8px;
}
.entry-text { font-size: 0.9rem; color: #e2e8f0; flex: 1; }
.entry-date { font-size: 0.75rem; color: #475569; margin-left: 12px; white-space: nowrap; }

.tbl-header {
    display: grid;
    gap: 8px;
    padding: 8px 12px;
    background: rgba(255,255,255,0.03);
    border-radius: 8px;
    margin-bottom: 4px;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #475569;
}
.tbl-row {
    display: grid;
    gap: 8px;
    padding: 10px 12px;
    border-radius: 8px;
    font-size: 0.88rem;
    color: #e2e8f0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    align-items: center;
}
.tbl-row:hover { background: rgba(255,255,255,0.04); }
.grid-5 { grid-template-columns: 2.5fr 1fr 1fr 0.8fr 1fr; }

.badge {
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.badge-sale     { background: rgba(52,211,153,0.15); color: #34d399; border: 1px solid rgba(52,211,153,0.3); }
.badge-purchase { background: rgba(96,165,250,0.15); color: #60a5fa; border: 1px solid rgba(96,165,250,0.3); }
.badge-expense  { background: rgba(251,191,36,0.15); color: #fbbf24; border: 1px solid rgba(251,191,36,0.3); }

.metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 1.2rem; }
.metric-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1rem 1.2rem;
}
.metric-label { font-size: 0.72rem; color: #64748b; font-weight: 500; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 4px; }
.metric-value { font-size: 1.4rem; font-weight: 700; color: #f1f5f9; }

.net-card {
    background: linear-gradient(135deg, rgba(167,139,250,0.2), rgba(96,165,250,0.2));
    border: 1px solid rgba(167,139,250,0.4);
    border-radius: 16px;
    padding: 1.5rem 1.8rem;
    text-align: center;
}
.net-label { font-size: 0.8rem; color: #a78bfa; font-weight: 500; text-transform: uppercase; letter-spacing: 0.1em; }
.net-amount { font-size: 2.8rem; font-weight: 700; color: #fff; margin: 4px 0; }
.net-sub { font-size: 0.8rem; color: #94a3b8; }

.info-pill {
    background: rgba(96,165,250,0.1);
    border: 1px solid rgba(96,165,250,0.2);
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    font-size: 0.85rem;
    color: #93c5fd;
    text-align: center;
    margin-top: 1rem;
}

.stTextArea textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
}
.stTextArea textarea:focus {
    border-color: rgba(167,139,250,0.5) !important;
    box-shadow: 0 0 0 3px rgba(167,139,250,0.1) !important;
}
.stTextArea textarea::placeholder { color: #475569 !important; }

.stButton > button {
    background: linear-gradient(135deg, #a78bfa, #60a5fa) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 2rem !important;
    transition: opacity 0.2s !important;
    width: 100% !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

.custom-divider { border: none; border-top: 1px solid rgba(255,255,255,0.07); margin: 1.5rem 0; }
            
</style>

<!-- Voice recognition script -->
<script>
function startVoice() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert('Voice not supported in this browser. Please use Chrome.');
        return;
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'hi-IN';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    const btn = document.getElementById('voiceBtn');
    btn.innerText = '🔴 Bol rahe hain...';
    btn.style.background = 'rgba(239,68,68,0.3)';

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        // Put transcript into the Streamlit text area
        const textarea = window.parent.document.querySelectorAll('textarea')[0];
        if (textarea) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
            nativeInputValueSetter.call(textarea, transcript);
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
        }
        btn.innerText = '🎙️ Voice Input';
        btn.style.background = 'rgba(167,139,250,0.2)';
    };

    recognition.onerror = function() {
        btn.innerText = '🎙️ Voice Input';
        btn.style.background = 'rgba(167,139,250,0.2)';
    };

    recognition.start();
}
</script>
""", unsafe_allow_html=True)

#header
st.markdown("""
<div class="hero">
    <div class="hero-logo"
         style="
         color:white;
         -webkit-text-fill-color:white;
         ">
         GST SAATHI
    </div>
</div>
""", unsafe_allow_html=True)

# Voice button (HTML button calling JS)
st.markdown("""
<button id="voiceBtn" onclick="startVoice()" style="
    background: rgba(167,139,250,0.2);
    border: 1px solid rgba(167,139,250,0.4);
    color: #a78bfa; border-radius: 10px;
    padding: 8px 18px; font-size: 0.85rem;
    font-weight: 600; cursor: pointer;
    margin-bottom: 10px; font-family: Inter, sans-serif;
    transition: all 0.2s;
">🎙️ Voice Input</button>
""", unsafe_allow_html=True)

transaction_input = st.text_area(
    label="transaction_input",
    label_visibility="collapsed",
    placeholder="Enter or speak your transaction\nExample: 20kg atta ₹800 mein becha",
    height=100,
    key="tx_input"
)

if st.button("➕ Add to Database"):
    if transaction_input.strip():
        save_transaction(transaction_input.strip())
        st.success("✅ Transaction saved!")
        st.rerun()
    else:
        st.warning("Enter something before adding!")

st.markdown('</div>', unsafe_allow_html=True)


#output
# ── SECTION 2: Transaction Database ──────────────────────────
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown('<div class="section-label">🗄️ Saved Transactions</div>', unsafe_allow_html=True)

rows = get_all_transactions()

if not rows:
    st.markdown('<div class="empty-state">Abhi koi transaction nahi hai. Upar se add karo!</div>', unsafe_allow_html=True)
else:
    for row in rows:
        tid, text, date = row
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(
                '<div class="entry-row">'
                '<span class="entry-text">' + text + '</span>'
                '<span class="entry-date">' + date + '</span>'
                '</div>',
                unsafe_allow_html=True
            )
        with col2:
            if st.button("🗑️", key=f"del_{tid}", help="Delete"):
                delete_transaction(tid)
                st.rerun()

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    col_a, col_b = st.columns([3, 1])
    with col_a:
        analyse_btn = st.button("🔍 Analyse All Transactions", type="primary")
    with col_b:
        if st.button("🧹 Clear All"):
            clear_all_transactions()
            st.rerun()

    if analyse_btn:
        all_text = "\n".join([r[1] for r in rows])
        with st.spinner("Gemini analyse kar raha hai..."):
            try:
                results = transaction_analyser(all_text)

                sales     = [r for r in results if r["type"] == "Sale"]
                purchases = [r for r in results if r["type"] == "Purchase"]
                expenses  = [r for r in results if r["type"] == "Expense"]

                st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
                st.markdown('<div class="section-label">📊 Transaction Breakdown</div>', unsafe_allow_html=True)

                def render_table(items, badge_class, badge_label):
                    if not items:
                        return
                    header = (
                        '<div class="tbl-header grid-5">'
                        '<span>Item</span><span>HSN/SAC</span>'
                        '<span>Amount</span><span>GST%</span><span>GST ₹</span>'
                        '</div>'
                    )
                    st.markdown(header, unsafe_allow_html=True)
                    for item in items:
                        desc    = item['description']
                        hsn     = item['hsn_code']
                        amount  = "₹{:,.0f}".format(item['amount'])
                        rate    = str(item['gst_rate']) + "%"
                        gst_amt = "₹{:,.0f}".format(item['gst_amount'])
                        row = (
                            '<div class="tbl-row grid-5">'
                            '<span>' + desc + ' <span class="badge ' + badge_class + '">' + badge_label + '</span></span>'
                            '<span style="color:#64748b">' + hsn + '</span>'
                            '<span>' + amount + '</span>'
                            '<span style="color:#94a3b8">' + rate + '</span>'
                            '<span>' + gst_amt + '</span>'
                            '</div>'
                        )
                        st.markdown(row, unsafe_allow_html=True)

                st.markdown('<div class="glass">', unsafe_allow_html=True)
                render_table(sales,     "badge-sale",     "Sale")
                render_table(purchases, "badge-purchase", "Purchase")
                render_table(expenses,  "badge-expense",  "Expense")
                st.markdown('</div>', unsafe_allow_html=True)

                total_sales_base   = sum(r["amount"]     for r in sales)
                total_sales_gst    = sum(r["gst_amount"] for r in sales)
                total_purchase_gst = sum(r["gst_amount"] for r in purchases)
                itc                = total_purchase_gst
                net_gst_payable    = max(0, total_sales_gst - itc)

                st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
                st.markdown('<div class="section-label">🧮 GST Summary</div>', unsafe_allow_html=True)

                st.markdown(
                    '<div class="metrics-grid">'
                    '<div class="metric-card"><div class="metric-label">Total Sales</div>'
                    '<div class="metric-value">₹' + "{:,.0f}".format(total_sales_base) + '</div></div>'
                    '<div class="metric-card"><div class="metric-label">GST Collected</div>'
                    '<div class="metric-value">₹' + "{:,.0f}".format(total_sales_gst) + '</div></div>'
                    '<div class="metric-card"><div class="metric-label">ITC (Input Credit)</div>'
                    '<div class="metric-value">₹' + "{:,.0f}".format(itc) + '</div></div>'
                    '</div>'
                    '<div class="net-card">'
                    '<div class="net-label">Net GST Payable This Month</div>'
                    '<div class="net-amount">₹' + "{:,.0f}".format(net_gst_payable) + '</div>'
                    '<div class="net-sub">GST Collected ₹' + "{:,.0f}".format(total_sales_gst) +
                    ' &minus; ITC ₹' + "{:,.0f}".format(itc) + '</div>'
                    '</div>'
                    '<div class="info-pill">'
                    '📅 GSTR-3B filing deadline: <strong>20th of next month</strong> &nbsp;·&nbsp;'
                    'Yeh summary apne CA ko bhej do — unka kaam 10 minute mein ho jayega ✓'
                    '</div>',
                    unsafe_allow_html=True
                )

            except json.JSONDecodeError:
                st.error("Response parse nahi hua. Thoda detail mein likho aur dobara try karo.")
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown('</div>', unsafe_allow_html=True)
