import streamlit as st
from itertools import permutations

def calculate_exotics(h1, h2):
    """Calculates Exactas and Quinella based on specific user formulas."""
    # Market percentage (Probability)
    p1 = 1.0 / h1
    p2 = 1.0 / h2
    
    # Exacta 1-2: horse 1 input * 1/(1 / horse 2 input/(1-(1 / horse 1 input)))
    exacta_1_2 = h1 * (1.0 / (p2 / (1.0 - p1)))
    
    # Exacta 2-1: horse 2 input * 1/(1 / horse 1 input/(1-(1 / horse 2 input)))
    exacta_2_1 = h2 * (1.0 / (p1 / (1.0 - p2)))
    
    # Quinella: 1.0 / ((1 / exacta_1_2) + ( 1 / exacta_2_1))
    quinella = 1.0 / ((1.0 / exacta_1_2) + (1.0 / exacta_2_1))
    
    return exacta_1_2, exacta_2_1, quinella

def calculate_srm_full(input_odds):
    """Full 24-permutation calculation for 4 runners."""
    market_probs = [1.0 / float(o) for o in input_odds]
    indices = list(range(len(input_odds)))
    perms = list(permutations(indices))
    
    permutation_results = []
    for perm in perms:
        idx1, idx2, idx3, idx4 = perm
        v1, v2, v3, v4 = input_odds[idx1], input_odds[idx2], input_odds[idx3], input_odds[idx4]
        p1, p2, p3, p4 = market_probs[idx1], market_probs[idx2], market_probs[idx3], market_probs[idx4]
        
        try:
            # Geometric decay logic
            x1 = v1
            x2 = v2 * (1.0 - p1)
            x3 = v3 * (1.0 - (p1 + p2))
            x4 = v4 * (1.0 - (p1 + p2 + p3))
            
            product = x1 * x2 * x3 * x4
            inv_product = 1.0 / product
            permutation_results.append(inv_product)
        except ZeroDivisionError:
            permutation_results.append(0)

    total_sum = sum(permutation_results)
    return (1.0 / total_sum) if total_sum > 0 else 0

# --- Streamlit UI Configuration ---
st.set_page_config(page_title="SRM Pricing Tool", layout="centered")

st.title("🏇 Exotic & SRM Odds Calculator")
st.write("Enter horse odds below. Set to 0.00 to ignore a runner.")

# Currency Inputs - Defaulted to 0.00
col1, col2, col3, col4 = st.columns(4)
with col1: h1 = st.number_input("Horse 1", min_value=0.0, value=0.00, step=0.01, format="%.2f")
with col2: h2 = st.number_input("Horse 2", min_value=0.0, value=0.00, step=0.01, format="%.2f")
with col3: h3 = st.number_input("Horse 3", min_value=0.0, value=0.00, step=0.01, format="%.2f")
with col4: h4 = st.number_input("Horse 4", min_value=0.0, value=0.00, step=0.01, format="%.2f")

if st.button("Generate Pricing", use_container_width=True):
    # Filter active inputs (Must be > 1.0 to be valid odds)
    active_odds = [h for h in [h1, h2, h3, h4] if h > 1.0]
    
    if len(active_odds) < 2:
        st.warning("⚠️ Please enter at least Horse 1 and Horse 2 odds (greater than 1.0) to see results.")
    else:
        # 1. Exotic Calculations (Only if H1 and H2 are valid)
        if h1 > 1.0 and h2 > 1.0:
            e12, e21, quin = calculate_exotics(h1, h2)
            
            st.subheader("📍 Exotic Market Pricing")
            res_col1, res_col2, res_col3 = st.columns(3)
            
            res_col1.metric("Exacta (1 / 2)", f"${e12:,.2f}")
            res_col2.metric("Exacta (2 / 1)", f"${e21:,.2f}")
            res_col3.metric("Quinella", f"${quin:,.2f}")
        else:
            st.error("Exotic Pricing requires valid Horse 1 and Horse 2 odds.")

        # 2. SRM Calculation (Only if all 4 horses provided)
        if len(active_odds) == 4:
            srm_odds = calculate_srm_full(active_odds)
            st.divider()
            st.subheader("🧬 SRM Permutation Pricing")
            st.metric("Final SRM Odds", f"${srm_odds:,.2f}")
        elif len(active_odds) == 3:
            st.info("💡 Enter a 4th Horse value to calculate the full SRM Permutation Odds.")

