import streamlit as st
import pickle
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
from wordcloud import STOPWORDS
from sklearn.feature_extraction.text import TfidfVectorizer


stemmer = SnowballStemmer("english")

app = FastAPI() 

pickle_in = open("Regression_logistic_model.pkl", "rb")
model = pickle.load(pickle_in)

stopwords_set = set(STOPWORDS).union({'com', 'http', 'html', 'https'})

def remove_stopwords(text):
    words = word_tokenize(text)
    cleaned_words = [word.lower() for word in words if word.lower() not in stopwords_set and len(word) > 3]
    return ' '.join(cleaned_words)

vect_in = open("vectorizer.pkl","rb")
vectorizer = pickle.load(vect_in)

@app.get("/home")
def home():
    return {"message": "Hello sur mon api de fishing detection"}

@app.post("/prediction_lien")
def prediction_lien(lien: str):
    try:   
        doc_no_stop_word = remove_stopwords(' '.join([stemmer.stem(word) for word in word_tokenize(lien)]))
        lien_pres = vectorizer.transform([doc_no_stop_word])
        prediction = model.predict(lien_pres)
        
        if prediction == 1:
            return {"message": "Ce lien est un phishing."}
        elif prediction == 0:
            return {"message": "Ce lien est légitime, ne vous inquiétez pas."}
        
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

st.title("DETECTEUR DE LIEN PHISHING ")

upload = st.text_input("Entrer le lien puis appuyer sur Entrer de votre clavier pour connaître la nature de ce lien ", key="name")
c1, c2 = st.columns(2)

message = " "  

if st.button("Vérifier le lien"):
    if upload:
        
        data = prediction_lien(upload)

        if data == {"message": "Ce lien est un phishing."}:
            message = "Ce lien est un phishing"
        elif data ==  {"message": "Ce lien est légitime, ne vous inquiétez pas."} :
            message =  "Ce lien est légitime, ne vous inquiétez pas."


st.write(message)
