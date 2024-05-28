#
# import openai
#
# openai.api_key = 'sk-sample-gs3UJQsNnmoccGZZCn40T3BlbkFJ46rEBY9U3yepvd0eUuMQ'
#
#
# class GPTClient:
#     def __init__(self, model="whisper-1", temperature=0.7):
#         self.model = model
#         self.temperature = temperature
#
#     def generate(self, prompt, max_tokens=150):
#         response = openai.ChatCompletion.create(
#             model=self.model,
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=max_tokens,
#             temperature=self.temperature,
#             n=1,
#             stop=None
#         )
#         return response.choices[0].message['content']