
import streamlit as st
import pandas as pd
import numpy as np

# App title
st.title("🎉 My First Streamlit App!")

# Header
st.header("Welcome to Streamlit")

# Subheader
st.subheader("This is a subheader")

# Text
st.text("This is some regular text")

# Markdown
st.markdown("**This is bold text in markdown**")
st.markdown("*This is italic text*")

# Simple metric
st.metric(label="Temperature", value="25°C", delta="2°C")

# Success message
st.success("🎯 Congratulations! You've created your first Streamlit app!")
