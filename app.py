import streamlit as st
import numpy as np
import pandas as pd

# ---- Task 1: User Inputs ----
st.title("CPG Brand Success Probability Tool")

st.header("1. Product & Pricing Structure")
cogs = st.slider("Cost of Goods Sold (COGs)", 0.5, 20.0, 5.0, 0.1)
include_distributor = st.checkbox("Include Distributor (e.g., KEHE/UNFI)?")
distributor_margin = st.slider("Distributor Margin %", 5, 30, 15) if include_distributor else 0
retailer_margin = st.slider("Retailer Margin %", 20, 60, 40)
brand_margin_goal = st.slider("Brand Margin Goal %", 20, 80, 50)

# ---- Task 2: Brand Awareness ----
st.header("2. Brand Awareness & Exposure")
social_followers = st.number_input("Social Media Followers", 0, 10000000, 50000, step=1000)
engagement_rate = st.slider("Engagement Rate (%)", 0.0, 20.0, 3.0, 0.1)
virality_score = np.log1p(social_followers) * (engagement_rate / 100)

# ---- Task 3: Competitive Benchmarking ----
st.header("3. Competitive Benchmark")
st.subheader("Enter Benchmark Brands")
benchmark_data = {
    'Brand': [],
    'Followers': [],
    'Engagement (%)': [],
    'Virality Score': []
}

for i in range(3):
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input(f"Brand {i+1} Name", key=f"b{i}_name")
    with col2:
        followers = st.number_input(f"Brand {i+1} Followers", 0, 10000000, 100000, step=1000, key=f"b{i}_followers")
    with col3:
        engagement = st.slider(f"Brand {i+1} Engagement Rate %", 0.0, 20.0, 2.0, 0.1, key=f"b{i}_engage")
    if name:
        score = np.log1p(followers) * (engagement / 100)
        benchmark_data['Brand'].append(name)
        benchmark_data['Followers'].append(followers)
        benchmark_data['Engagement (%)'].append(engagement)
        benchmark_data['Virality Score'].append(score)

st.dataframe(pd.DataFrame(benchmark_data))

# ---- Task 4: Pricing and Margins Calculation ----
intermediate_price = cogs / (1 - (brand_margin_goal / 100))
if include_distributor:
    distributor_price = intermediate_price / (1 - (distributor_margin / 100))
    shelf_price = distributor_price / (1 - (retailer_margin / 100))
else:
    shelf_price = intermediate_price / (1 - (retailer_margin / 100))

# ---- Task 5: Outputs ----
st.header("4. Pricing Summary")
st.write(f"**Shelf Price Estimate:** ${shelf_price:.2f}")
st.write(f"**Brand Net Margin:** {(shelf_price - cogs) / shelf_price * 100:.1f}%")

# ---- Task 6: Probability Model ----
st.header("5. Success Probability Estimate")

# Quantitative Factors
margin_score = min((shelf_price - cogs) / shelf_price * 100 / 50, 1.0)

# Awareness Score scaled to 1
awareness_score = min(virality_score / 2.5, 1.0)  # benchmark scaling

# Qualitative Adjustment (Manually Tuned)
retailer_difficulty = {
    'Sprouts': 0.7,
    'Target': 0.5,
    'ULTA': 0.6
}
retailer = st.selectbox("Choose Retailer", list(retailer_difficulty.keys()))
retailer_modifier = retailer_difficulty[retailer]

# Final Probability Calculation
probability_of_success = round((margin_score * 0.4 + awareness_score * 0.5) * retailer_modifier * 100, 1)

st.metric("Likelihood of Success", f"{probability_of_success}%")

# ---- Task 7: Gap Identification ----
st.header("6. Gap & Risk Assessment")
if margin_score < 0.5:
    st.warning("⚠️ Brand margin appears too low. Consider raising price or lowering COGs.")
if awareness_score < 0.3:
    st.warning("⚠️ Social virality is low. Improve engagement or follower count.")
if probability_of_success < 40:
    st.error("🚫 Success likelihood is low. Reassess positioning, price, or promotion.")
elif probability_of_success < 70:
    st.info("🟡 Moderate chance. May require strong retail support.")
else:
    st.success("🟢 High chance of success given inputs!")
