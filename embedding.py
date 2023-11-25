import pandas as pd
import nltk
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

# nltk 다운로드
nltk.download('punkt')

# KoBERT 모델 로딩
tokenizer = AutoTokenizer.from_pretrained("monologg/kobert")
model = AutoModel.from_pretrained("monologg/kobert")

# 데이터 불러오기
card_data = pd.read_csv('C:/finchatbot/card_data.csv')

# '내용' 열에 있는 문장을 분할하고 임베딩 값을 계산하여 'embedding' 열에 저장
def embed_card_benefits(sentence):
    # 문장을 토큰화하고 KoBERT 모델을 통해 임베딩 값을 계산
    tokens = nltk.sent_tokenize(sentence)  # 문장을 토큰화
    sentence_embeddings = []

    for token in tokens:
        inputs = tokenizer(token, return_tensors="pt")
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze().detach().numpy()
        sentence_embeddings.append(embedding)

    # 각 문장의 임베딩 값을 평균하여 문장 전체의 임베딩 값 계산
    embedding = torch.tensor(np.array(sentence_embeddings)).mean(dim=0).numpy()
    return embedding

# '내용' 열에 대해 임베딩 값을 계산하고 'embedding' 열에 저장
card_data['embedding'] = card_data['내용'].apply(embed_card_benefits)

# 임베딩 값을 저장한 CSV 파일로 저장
card_data.to_csv('C:/finchatbot/embedded_card_data.csv', index=False)
