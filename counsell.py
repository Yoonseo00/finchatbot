import openai

secret_key = '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'
openai.api_key = secret_key

def generate_counsel_response(user_message):

    system_role = (
        "You're the best consumption analyst in the world and there's no consumption history you can't analyze. "
        "We have a lot of consumption-related knowledge and can answer all questions clearly. "
        "You are a master of financial technology, and you can also give answers on how to save money."
        "You can answer all questions related to financial information, and provide advice for personal situations."
        "Your name is finchatbot."   
    )

    # 사용자 및 시스템 메시지 설정
    messages = [
        {"role": "system", "content": system_role},
        {"role": "user", "content": user_message},
    ]

    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=1,
        max_tokens=700,
        n=1,
        stop=None
    )

    system_message = completion.choices[0].message.content
    return system_message
