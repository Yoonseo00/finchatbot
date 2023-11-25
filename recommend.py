from flask import Flask, render_template, request
import pandas as pd
from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('cardopt.html')

@app.route('/creditcard')
def show_credit_card():
    return render_template('creditcard.html')

@app.route('/checkcard')
def show_check_card():
    return render_template('checkcard.html')

@app.route('/selec')
def show_selec_spend():
    return render_template('selecspend.html')

# KoBERT 관련 설정
tokenizer = BertTokenizer.from_pretrained("monologg/kobert")
model = BertModel.from_pretrained("monologg/kobert")

# KoBERT를 활용한 함수들
def embed_user_response(user_response):
    # 사용자 응답을 임베딩하는 함수
    tokens = tokenizer.batch_encode_plus(user_response, return_tensors='pt', padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**tokens)
    user_embedding = outputs.last_hidden_state.mean(dim=1)
    return user_embedding

def embed_card_benefits(card_benefits):
    # 카드 혜택을 임베딩하는 함수
    tokens = tokenizer.batch_encode_plus(card_benefits, return_tensors='pt', padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**tokens)
    card_embedding = outputs.last_hidden_state.mean(dim=1)
    return card_embedding

def calculate_similarity(embedding1, embedding2):
    # 유사도를 계산하는 함수
    return cosine_similarity(embedding1, embedding2)[0][0]

@app.route('/recom')
def recom():
    return render_template('recomcard.html')

@app.route('/get_recommendation', methods=['POST'])
def get_recommendation():
    if request.method == 'POST':
        user_preference = request.form['user_preference']

        # 사용자 응답을 임베딩
        user_embedding = embed_user_response([user_preference])

        # embedded_card_data.csv 파일을 불러와 카드 혜택의 임베딩값을 저장
        card_data = pd.read_csv('C:/finchatbot/embedded_card_data.csv')

        # 유사도 계산 및 추천
        best_match = None
        highest_similarity = 0.0

        for index, row in card_data.iterrows():
            card_embedding = embed_card_benefits([row['embedding']])
            similarity = calculate_similarity(card_embedding, user_embedding)

            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = row['카드명']

        return render_template('recomcard.html', recommendation=best_match, user_input=user_preference)


if __name__ == '__main__':
    app.run(debug=True)
