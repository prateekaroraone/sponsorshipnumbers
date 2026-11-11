import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="UK Sponsorship Lookup", page_icon="🔎", layout="centered")
st.markdown("""
<style>
#MainMenu,footer,header{visibility:hidden}
.block-container{max-width:900px;padding-top:2.2rem;padding-bottom:3rem}
h1{letter-spacing:-.04em;margin-bottom:.25rem}
div[data-testid="stRadio"]>div{gap:.5rem}
div[data-testid="stRadio"] label{border:1px solid #d8dee8;border-radius:9px;padding:.55rem .85rem;background:#f8fafc;font-weight:500}
div[data-testid="stRadio"] label:has(input:checked){background:#102a56;color:white;border-color:#102a56}
div[data-testid="stTextInput"] input{border-radius:9px;min-height:3rem}
.result-name{font-size:1.15rem;font-weight:650;margin:1rem 0 .5rem}
</style>
""",unsafe_allow_html=True)
st.title("UK Sponsorship Lookup")
st.caption("Search organisation sponsorship figures by year.")

ROUTES={"Skilled Worker":"FOI Data - Skilled Worker","Global Business Mobility":"FOI Data - GBM"}
YEARS=["2021","2022","2023","2024","Grand Total"]
FILE=Path("data/sponsorship_data.xlsx")

@st.cache_data
def load_sheet(path,sheet):
    df=pd.read_excel(path,sheet_name=sheet)
    df.columns=[str(c).strip() for c in df.columns]
    df["Organisation Name"]=df["Organisation Name"].fillna("").astype(str).str.strip()
    return df[df["Organisation Name"]!=""][["Organisation Name",*YEARS]]

route=st.radio("Visa route",list(ROUTES),horizontal=True,label_visibility="collapsed")
if not FILE.exists():
    st.info("Add your workbook at `data/sponsorship_data.xlsx` to activate search.")
    st.stop()
try:
    df=load_sheet(str(FILE),ROUTES[route])
except Exception as e:
    st.error(f"Unable to read the workbook: {e}")
    st.stop()

query=st.text_input("Search organisation",placeholder="e.g. Amazon, Google, NHS",label_visibility="collapsed")
if query.strip():
    found=df[df["Organisation Name"].str.contains(query.strip(),case=False,regex=False,na=False)]
    st.caption(f"{len(found):,} result{'s' if len(found)!=1 else ''}")
    if found.empty: st.info("No organisations found.")
    else:
        def fmt(v):
            if pd.isna(v): return "—"
            if isinstance(v,(int,float)) and not isinstance(v,bool):
                return f"{int(v):,}" if float(v).is_integer() else f"{v:,.2f}".rstrip("0").rstrip(".")
            return str(v).strip() or "—"
        for _,r in found.iterrows():
            st.markdown(f'<div class="result-name">{r["Organisation Name"]}</div>',unsafe_allow_html=True)
            st.dataframe(pd.DataFrame([[fmt(r[y]) for y in YEARS]],columns=YEARS),hide_index=True,use_container_width=True)
else:
    st.caption("Start typing to see matching organisations.")
