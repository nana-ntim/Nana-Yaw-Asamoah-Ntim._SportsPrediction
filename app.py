import pickle as pkl
import pandas as pd
import streamlit as st

# Meta Data
st.title("Fifa Rating Prediction")
st.write("Predicts the rating for a player based on their profile data.")

# Saves the values
variables = ['potential', 'value_eur', 'wage_eur', 'passing', 'dribbling', 'movement_reactions', 'mentality_composure']
user_inputs = {}

user_inputs['potential'] = st.number_input("Potential", min_value=0, max_value=100, step=1)
user_inputs['value_eur'] = st.number_input(
    "Value (EUR)", min_value=0)
user_inputs['wage_eur'] = st.number_input("Wage (EUR)", min_value=0, value=0, step=1)
user_inputs['passing'] = st.number_input("Passing", min_value=0, max_value=100)
user_inputs['dribbling'] = st.number_input(
    "Dribbling (0 - 100)", min_value=0, max_value=100)
user_inputs['movement_reactions'] = st.number_input(
    "Movement Reactions (0 to 100)", min_value=0, max_value=100)
user_inputs['mentality_composure'] = st.number_input(
    "Mentality Composure (0 - 100)", min_value=0, max_value=100)


if st.button("Get The Rating"):
    data_df = pd.DataFrame([user_inputs])

    # Prediction data
    # Imports the model
    with open('Regression_Model .pkl', 'rb') as model_file:
      prediction_model = pkl.load(model_file)

    print(data_df)

    # Gets the confidence score and rating
    rating = prediction_model.predict(data_df)

    # Brings out the final data
    st.header("Here's the Predicted Data")
    st.write(f"**Predicted Rating:** {rating[0]}")
    # st.write(f"**Confidence Level:** {conf_score * 100:.2f}%")
