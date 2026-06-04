import streamlit as st
from dotenv import load_dotenv
import os
import json
load_dotenv()
api_key=os.getenv("API_KEY")
from google import genai
client=genai.Client(api_key=api_key)
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

#header
st.markdown("## 🧾 GST Saathi")
st.markdown("##### Enter your transactions in Hindi or English.")
st.divider()

#input area
st.markdown("**📝 Write or speak your transactions for today:**")
transaction = st.text_area(
    label="transactions",
    label_visibility="collapsed",
    placeholder="Example:\n20kg atta ₹800 mein becha\nRamesh Traders se mustard oil aaya ₹1200\nLight bill bhara ₹450",
    height=180
)

analyse = st.button("🔍 Analyse Transactions", use_container_width=True, type="primary")

#output
if analyse:
    if not transaction.strip():
        st.warning("Enter something! Transactions are empty.")
    else:
        with st.spinner("Analysing..."):
            try:
                results = transaction_analyser(transaction)

                st.divider()
                st.markdown("### 📊 Transaction Summary")

                # Separate by type
                sales      = [r for r in results if r["type"] == "Sale"]
                purchases  = [r for r in results if r["type"] == "Purchase"]
                expenses   = [r for r in results if r["type"] == "Expense"]

                def render_table(items, label, color):
                    if not items:
                        return
                    st.markdown(f"**{label}**")
                    cols = st.columns([3, 1.2, 1.2, 1, 1.2])
                    headers = ["Item", "HSN/SAC", "Amount (₹)", "GST %", "GST (₹)"]
                    for col, h in zip(cols, headers):
                        col.markdown(f"<small><b>{h}</b></small>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin:4px 0 8px'>", unsafe_allow_html=True)
                    for item in items:
                        cols = st.columns([3, 1.2, 1.2, 1, 1.2])
                        cols[0].write(item["description"])
                        cols[1].write(item["hsn_code"])
                        cols[2].write(f"₹{item['amount']:,.0f}")
                        cols[3].write(f"{item['gst_rate']}%")
                        cols[4].write(f"₹{item['gst_amount']:,.0f}")

                render_table(sales,     "🟢 Sales",     "green")
                render_table(purchases, "🔵 Purchases", "blue")
                render_table(expenses,  "🟠 Expenses",  "orange")


                st.divider()
                st.markdown("### 🧮 GST Summary")

                total_sales_base    = sum(r["amount"]     for r in sales)
                total_sales_gst     = sum(r["gst_amount"] for r in sales)
                total_purchase_gst  = sum(r["gst_amount"] for r in purchases)
                itc                 = total_purchase_gst  # Input Tax Credit
                net_gst_payable     = max(0, total_sales_gst - itc)

                c1, c2, c3 = st.columns(3)
                c1.metric("Total Sales", f"₹{total_sales_base:,.0f}")
                c2.metric("GST Collected (Sales)", f"₹{total_sales_gst:,.0f}")
                c3.metric("ITC (on Purchases)", f"₹{itc:,.0f}")

                st.markdown("<br>", unsafe_allow_html=True)

                # Net payable highlight
                st.markdown(
                    f"""
                    <div style='background:#e8f5e9;border-radius:10px;padding:16px 20px;border:1px solid #a5d6a7'>
                        <h4 style='margin:0;color:#2e7d32'>💰 Net GST Payable This Month</h4>
                        <h2 style='margin:4px 0 0;color:#1b5e20'>₹{net_gst_payable:,.0f}</h2>
                        <small style='color:#388e3c'>GST Collected − Input Tax Credit = ₹{total_sales_gst:,.0f} − ₹{itc:,.0f}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.divider()
                st.info("📅 **GSTR-3B filing deadline: 20th of next month.** Send this summary to your CA — their work will be done in 10 minutes.")

            except json.JSONDecodeError:
                st.error("Some error occured. Write in detail and clear way. Avoid mixing too many transactions in one line. Try to follow the example format.")
            except Exception as e:
                st.error(f"Some error occured: {e}")


