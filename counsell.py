import openai
import re

secret_key = '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'
openai.api_key = secret_key

previous_messages = []

def generate_counsel_response(user_message):

    global previous_messages

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
        {"role": "assistant", "content": ""},
    ] + previous_messages

    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=1,
        max_tokens=700,
        n=1,
        stop=None
    )

    previous_messages = messages + [{"role": "user", "content": user_message}, {"role": "assistant", "content": completion.choices[0].message.content}]
    bot_response = completion.choices[0].message.content

    # HTML 태그로 줄바꿈 변환
    bot_response_with_html = re.sub(r'\n', '<br>', bot_response)

    return bot_response_with_html