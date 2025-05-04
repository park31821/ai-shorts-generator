import openai
import datetime

client = openai.OpenAI(api_key="YOUR_API_KEY")

prompt = """Generate a short, engaging AI fact or tip that is not too technical and is interesting to a general audience. Summarize it in 200 characters or less."""

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7
)

fact = response.choices[0].message.content.strip()

# Save with today's date
filename = f"ai_short_{datetime.date.today()}.txt"
with open(filename, "w", encoding="utf-8") as f:
    f.write(fact)

print("✅ Saved:", filename)
print(fact) 