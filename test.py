import pandas as pd
from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity

<<<<<<< HEAD

=======
>>>>>>> 21b134ddd316b5e53174f5499b1d24184913dc98
# KoBERT 토크나이저와 모델 불러오기
tokenizer = BertTokenizer.from_pretrained("monologg/kobert")
model = BertModel.from_pretrained("monologg/kobert")

# 사용자 응답을 임베딩하는 함수
def embed_user_response(user_response):
    tokens = tokenizer.batch_encode_plus(user_response, return_tensors='pt', padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**tokens)
    user_embedding = outputs.last_hidden_state.mean(dim=1)
    return user_embedding

# 카드 혜택을 임베딩하는 함수
def embed_card_benefits(card_benefits):
    tokens = tokenizer.batch_encode_plus(card_benefits, return_tensors='pt', padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**tokens)
    card_embedding = outputs.last_hidden_state.mean(dim=1)
    return card_embedding

# 유사도를 계산하는 함수
def calculate_similarity(embedding1, embedding2):
    return cosine_similarity(embedding1, embedding2)[0][0]

# 사용자에게 선호하는 카드의 혜택을 입력받음 (가정: 터미널에서 입력)
user_preference = input("선호하는 카드의 혜택을 입력하세요: ")

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

print("추천 카드 상품:", best_match)






<<<<<<< HEAD

=======
>>>>>>> 21b134ddd316b5e53174f5499b1d24184913dc98
