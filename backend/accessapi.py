secret_key='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'

import openai
openai.api_key=secret_key

output=openai.Completion.create(
    model='text-davinci-003',
    prompt= ,
    max_tokens=100,
    temperature=0
)

print(output)