secret_key='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'
import openai
openai.api_key=secret_key

prompt="What's your name?"

output=openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
    max_tokens=100,
    n=1,
    temperature=1
)

message = output.choices[0].message.content

print(message)