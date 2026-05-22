import streamlit as st
import pandas as pd
from itertools import permutations

def calculate_srm_logic(input_odds):
    # 1. Calculate Market Percentages (1 / input value)
    market_probs = [1.0 / float(o) for o in input_odds]
    
    # We use indices to track which horse is which in permutations
    indices = list(range(len(input_odds)))
    perms = list(permutations(indices))
    
    permutation_results = []

    for perm in perms:
        # Get the order of indices for this permutation
        idx1, idx2, idx3, idx4 = perm
        
        # Original Odds (Input Values)
        v1, v2, v3, v4 = input_odds[idx1], input_odds[idx2], input_odds[idx3], input_odds[idx4]
        
        # Original Market Percentages
        p1, p2, p3, p4 = market_probs[idx1], market_probs[idx2], market_probs[idx3], market_probs[idx4]
        
        try:
            # Step-by-step Adjusted Odds logic derived from your check:
            # Calc 1: Just Input 1
            x1 = v1
            
            # Calc 2: Input 2 * (1 - Prob 1)
            x2 = v2 * (1.0 - p1)
            
            # Calc 3: Input 3 * (1 - (Prob 1 + Prob 2))
            x3 = v3 * (1.0 - (p1 + p2))
            
            # Calc 4: Input 4 * (1 - (Prob 1 + Prob 2 + Prob 3))
            x4 = v4 * (1.0 - (p1 + p2 + p3))
            
            # Product of the adjusted values
            product = x1 * x2 * x3 * x4
            
            # Reciprocal of the product
            inv_product = 1.0 / product
            permutation_results.append(inv_product)
            
        except ZeroDivisionError:
            # Handle cases where market % sums to 1.0+ to prevent crash
            permutation_results.append(0)

    # Sum all 24 results
    total_sum = sum(permutation_results)
    
    # Final SRM Odds calculation: 1 / total_sum
    if total_sum <= 0:
        return 0
    
    srm_odds = 1.0 / total_sum
    return srm_odds, total_sum

# --- Streamlit UI ---
st.set_page_config(page_title="SRM Permutation Engine", layout="centered")

st.title("🏆 SRM Odds Calculator")
st.markdown("This engine calculates geometric permutation weights based on market percentage decay.")

# Input layout
col1, col2, col3, col4 = st.columns(4)
with col1:
    h1 = st.number_input("Horse 1", min_value=1.01, value=2.50, step=0.1, format="%.2f")
with col2:
    h2 = st.number_input("Horse 2", min_value=1.01, value=8.00, step=0.1, format="%.2f")
with col3:
    h3 = st.number_input("Horse 3", min_value=1.01, value=14.00, step=0.1, format="%.2f")
with col4:
    h4 = st.number_input("Horse 4", min_value=1.01, value=19.00, step=0.1, format="%.2f")

if st.button("Calculate SRM Odds", use_container_width=True):
    inputs = [h1, h2, h3, h4]
    
    # # Check if sum of probabilities is valid for the 4th runner calculation
    # if sum(1/x for x in inputs[:3]) >= 1.0:
    #     st.warning("Warning: The market percentages of the first three runners sum to 100% or more. This will cause a zero-division error in the permutation chain.")
    
    result, total_sum = calculate_srm_logic(inputs)
    
    st.divider()
    
    # Display Results
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Total Sum (%)", f"{total_sum*100:.4f}%")
    with c2:
        st.metric("Final SRM Odds", f"${result:,.2f}")

    # Validation table for the user's specific example
    with st.expander("Show Calculation Verification"):
        p1, p2, p3, p4 = 1/h1, 1/h2, 1/h3, 1/h4
        data = {
            "Step": ["Horse 1", "Horse 2", "Horse 3", "Horse 4"],
            "Market %": [f"{p1:.2%}", f"{p2:.2%}", f"{p3:.2%}", f"{p4:.2%}"],
            "Adj Odds Logic": [
                f"{h1}", 
                f"{h2} * (1 - {p1:.3f})", 
                f"{h3} * (1 - {p1+p2:.3f})", 
                f"{h4} * (1 - {p1+p2+p3:.3f})"
            ],
            "Adj Value": [
                h1, 
                h2 * (1-p1), 
                h3 * (1-(p1+p2)), 
                h4 * (1-(p1+p2+p3))
            ]
        }
        st.table(pd.DataFrame(data))
        prod = h1 * (h2*(1-p1)) * (h3*(1-(p1+p2))) * (h4*(1-(p1+p2+p3)))
        st.write(f"**Product of Path 1-2-3-4:** {prod:.2f}")
        st.write(f"**1 / Product:** {1/prod:.6f}")