import streamlit as st
import requests
from pydantic import BaseModel

# Définissez une classe de modèle Pydantic pour les données d'entrée de votre API
class QueryRequest(BaseModel):
    question: str

# Titre de l'application
st.title("ChatBot Documentation RH")

# Affichage du message d'avertissement en haut de la page
st.markdown("___")
st.write("Pour bénéficier d'un remboursement, vous devez être en mission en dehors de votre résidence administrative (RA = ville du lieu de travail) et de votre résidence familiale (RF = ville du domicile).")
st.markdown("___")

st.write("Le chatbot est une IA et peut faire des erreurs. Pensez à vérifier les informations importantes dans les documents sources.")
st.markdown("___")

st.write("Si vous avez besoin de renseignement complémentaire adressez un mail sur cette boite mail : email@email.com .")

st.markdown("___")




# Champ de saisie pour la requête de l'utilisateur
query_input = st.text_input("Message :")

# Initialiser l'état de session pour le suivi de la réponse et de son statut
if 'response_text' not in st.session_state:
    st.session_state.response_text = ""
if 'query' not in st.session_state:
    st.session_state.query = ""
if 'history' not in st.session_state:
    st.session_state.history = []

# Bouton pour soumettre la requête à l'API
if st.button("Obtenir la réponse"):
    st.session_state.response_text = ""
    st.session_state.query = query_input

    # Appel de l'API uniquement si la requête n'est pas vide
    if query_input:
        # Affichage de l'animation de chargement pendant que l'API répond
        with st.spinner('Chargement...'):
            try:
                # Appel de l'API avec la requête utilisateur
                response = requests.post("http://127.0.0.1:8000/predict", json={"question": query_input})

                # Vérification de la réponse de l'API
                if response.status_code == 200:
                    response_json = response.json()
                    if "Réponse" in response_json:
                        result = response_json["Réponse"]
                        st.session_state.response_text = result
                        # Ajouter la requête et la réponse à l'historique uniquement si elles sont nouvelles
                        st.session_state.history.append({'query': query_input, 'response': result})
                    elif "Erreur" in response_json:
                        st.error(f"Erreur de l'API : {response_json['Erreur']}")
                    else:
                        st.error("Réponse inattendue de l'API.")
                else:
                    st.error("Une erreur s'est produite lors de la récupération de la réponse de l'API.")
            except requests.exceptions.RequestException as e:
                st.error(f"Erreur de connexion : {e}")
    else:
        st.warning("Veuillez entrer un message avant de soumettre la requête.")

# Afficher la réponse une fois reçue
if st.session_state.response_text:
    st.success(f"Réponse : {st.session_state.response_text}")

# Affichage de l'historique des réponses
if st.session_state.history:
    st.header("Historique des réponses")
    for i, entry in enumerate(st.session_state.history):
        with st.expander(f"Requête {i+1} : {entry['query']}"):
            st.write(f"**Réponse** : {entry['response']}")
