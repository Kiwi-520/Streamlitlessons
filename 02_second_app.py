
import streamlit as st
import pandas as pd
import numpy as np

# App title
st.title('My Learning Portfolio')

# Header
st.header('About Me')

# Subheader
st.subheader('Skills and intrest')

# Text
st.text('Passionate Data scientist')

# Markdown
st.markdown('Machine Learning')
st.markdown('**Data Science**')
st.markdown('*Web Development*')
st.markdown(
"""
- Python
- AI/ML  
   - DL
- MERN 
""")

# Metrics
st.metric(label='Experience: ',value='Beginner/Fresher')
st.metric(label='Projects: ',value='3')
st.metric(label='Langugaes Known: ',value='Python, C++, Javascript')

# Success
st.success('Completed 1st streamlimit app about my self')
