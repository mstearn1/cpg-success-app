import streamlit as st
import numpy as np
import pandas as pd

# ---- App Title ----
st.title("CPG Brand Success Probability Tool")

# ---- Section 1: Product & Pricing Structure ----
st.header("1. Product & Pricing Structure")
cogs = st.slider("Cost of Goods Sold (COGs)", 0.5, 20.0, 5.0, 0.1)
brand_margin_goal = st.slider("Brand Margin Goal %", 20, 80, 50)
intermediate_price = cogs / (1 - (brand_margin_goal / 100))

include_distributor = st.checkbox("Include Distributor (e.g., KEHE/UNFI)?")
distributor_margin = st.slider("Distributor Margin %", 5, 30, 15) if include_distributor else 0

if include_distributor:
    distributor_price = intermediate_price / (1 - (distributor_margin / 100))
else:
    distributor_price = intermediate_price

retailer_margin = st.slider("Retailer Margin %", 20, 60, 40)
shelf_price = distributor_price / (1 - (retailer_margin / 100))

st.header("2. Promotional Spend")
digital_spend = st.slider("Digital Promotion Spend per Month ($)", 0, 50000, 5000, 1000)
offline_spend = st.slider("Offline Promotion Spend per Month ($)", 0, 50000, 2000, 1000)
total_promo_spend = digital_spend + offline_spend

# ---- Section 3: Brand Awareness ----
st.header("3. Brand Awareness")
unaided_awareness = st.slider("Unaided Brand Awareness (%)", 0.0, 100.0, 5.0, 0.5)
top_of_mind = st.slider("Top-of-Mind Brand Awareness (%)", 0.0, 100.0, 2.0, 0.5)
awareness_factor = (unaided_awareness * 0.6 + top_of_mind * 0.4) / 100

# ---- Section 4: Competitive Benchmarking ----
st.header("4. Competitive Benchmark")
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

# ---- Section 5: Pricing Summary ----
st.header("5. Pricing Summary")
st.write(f"**Shelf Price Estimate:** ${shelf_price:.2f}")
st.write(f"**Brand Net Margin:** {(shelf_price - cogs) / shelf_price * 100:.1f}%")

# ---- Section 6: Success Probability Estimate ----
st.header("6. Success Probability Estimate")

# Margin Score
margin_score = min((shelf_price - cogs) / shelf_price * 100 / 50, 1.0)

# Awareness Score (Social media impact reduced)
social_followers = sum(benchmark_data['Followers']) if benchmark_data['Followers'] else 10000
engagement_rate = sum(benchmark_data['Engagement (%)']) / len(benchmark_data['Engagement (%)']) if benchmark_data['Engagement (%)'] else 2.0
virality_score = np.log1p(social_followers) * (engagement_rate / 100)
virality_score_normalized = min(virality_score / 2.5, 1.0)

# Promotion Spend Score
promo_score = min(total_promo_spend / 20000, 1.0)  # Max out at $20K spend

# Final Awareness Composite Score
awareness_score = min(awareness_factor * 0.7 + virality_score_normalized * 0.3, 1.0)

# Retailer Modifiers
retailer_difficulty = {
    'Sprouts': 0.7,
    'Target': 0.5,
    'ULTA': 0.6
}
retailer = st.selectbox("Choose Retailer", list(retailer_difficulty.keys()))
retailer_modifier = retailer_difficulty[retailer]

# Final Probability Calculation
probability_of_success = round((margin_score * 0.4 + awareness_score * 0.4 + promo_score * 0.2) * retailer_modifier * 100, 1)

st.metric("Likelihood of Success", f"{probability_of_success}%")

# ---- Section 7: Gap & Risk Assessment ----
st.header("7. Gap & Risk Assessment")
if margin_score < 0.5:
    st.warning("⚠️ Brand margin appears too low. Consider raising price or lowering COGs.")
if awareness_score < 0.3:
    st.warning("⚠️ Brand awareness is low. Improve unaided/top-of-mind brand recognition.")
if promo_score < 0.3:
    st.warning("⚠️ Promotional spend is limited. Increase digital or offline budget.")
if probability_of_success < 40:
    st.error("🚫 Success likelihood is low. Reassess positioning, pricing, or marketing strategy.")
elif probability_of_success < 70:
    st.info("🟡 Moderate chance. May require strong retail or trade support.")
else:
    st.success("🟢 High chance of success given current assumptions!")
