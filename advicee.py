import openai

secret_key = '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'
openai.api_key = secret_key

def generate_advice_response(user_message, current_month_data, current_category_data, current_exceed_category):
    system_role = (
        "You're the best consumption analyst in the world and there's no consumption history you can't analyze. "
        "We have a lot of consumption-related knowledge and can answer all questions clearly. "
        "You are a master of financial technology, and you can also give answers on how to save money."
        "The 'current_exceeded_category' contains information on the categories and excesses that were spent more than the average amount spent in the previous three months."
        "When you start chatting for the first time, please let me know your total consumption this month, your consumption by category, the categories you used more than the average of the previous three months, and the excess amount. And please give me at least two consumption advice on the categories you used more than the previous three-month average and the categories you used the most this month. Please enter a message if you need additional help. Please say that at the end of the answer."
        "You are a very kind person, and you can answer easily for user to recognize."    
    )

    # 사용자 및 시스템 메시지 설정
    messages = [
        {"role": "system", "content": system_role},
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": f"System: {current_month_data}, {current_category_data}, {current_exceed_category}"}
    ]

    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=1,
        max_tokens=700,
        n=1,
        stop=None
    )

    system_message=(completion.choices[0].message.content)
    return system_message