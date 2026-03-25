import os
from langchain_google_genai import ChatGoogleGenerativeAI

import streamlit as st
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)


def generate_story(word, size=None, theme=None, count=None):

    if not size or size == "Auto":
        size_guide = "best length suitable for the word's complexity"
    else:
        size_guide = size

    if not theme or theme == "Auto":
        theme_guide = "most suitable real-life related theme for this word"
    else:
        theme_guide = theme

    if not count:
        count = 8

    prompt = f"""
Write an interesting and engaging story for vocabulary learning.

Target vocabulary word: "{word}"
Theme: {theme_guide}
Size: {size_guide} (Short=150-200 words, Medium=300-350 words, Long=500-600 words)
Word repeat count: Use "{word}" naturally at least {count} times

Rules:
- Use "{word}" in different types of sentences (questions, dialogues, statements, descriptions)
- Never define "{word}" directly — let the reader understand its meaning through context
- Bold "{word}" every time it appears like **{word}**
- Keep the story relatable to real life situations people actually face daily
- Make it engaging, emotional, and easy to understand for anyone learning English
- End the story with a one line moral or takeaway that includes "{word}"

Auto-selection Guide (use when theme or size is set to auto):
- Emotional words (grief, joy) → Real Life / Family theme
- Action words (persist, strive) → Motivation / Career theme
- Social words (empathy, rude) → School / Friendship theme
- Complex/rare words → Adventure or Mystery theme
- Simple word → Short length
- Medium complexity → Medium length
- Complex word → Long length

Do not explain the meaning directly. Let the reader feel it through the story.

After the story, add a section in EXACTLY this format:

---
📖 **Word Info: {word}**

🇮🇳 **Hindi Meaning:** (Hindi mein matlab — 2-3 Hindi words)

🔁 **Synonyms:** (3-4 similar English words)

🔄 **Antonyms:** (3-4 opposite English words)

📝 **Story Summary:** (1-2 lines — how was "{word}" used in the story context above)
---
"""

    response = llm.invoke(prompt)
    return response.content


def check_sentences(word, sentence1, sentence2):
    """
    Deep grammar check for user sentences including:
    - Word usage correctness
    - Verb forms (V1/V2/V3/V4/V5)
    - Tenses
    - Subject-verb agreement
    - Articles (a/an/the)
    - Prepositions
    - Spelling
    - Sentence structure
    """

    prompt = f"""
You are a friendly English teacher for Indian learners.

Target word: "{word}"

Student's sentences:
Sentence 1: "{sentence1}"
Sentence 2: "{sentence2}"

Check each sentence for:
- Is "{word}" used correctly? (meaning, correct form, correct part of speech)
- Any grammar mistake? (verb form, tense, subject-verb agreement, articles, prepositions, spelling)

Return in EXACTLY this format — keep it very short:

SENTENCE 1:
Status: ✅ Correct / ❌ Wrong
Mistake: (1 line only — what is wrong, skip if correct)
Correct: (corrected sentence, skip if correct)

SENTENCE 2:
Status: ✅ Correct / ❌ Wrong
Mistake: (1 line only — what is wrong, skip if correct)
Correct: (corrected sentence, skip if correct)

OVERALL:
(1 short encouraging line in Hinglish)
"""

    response = llm.invoke(prompt)
    return response.content
