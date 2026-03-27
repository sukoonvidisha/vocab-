import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)


def _build_prompt(words_list, size_guide, theme_guide, count, language, existing_story=None):
    """Build a single prompt for given language — fresh or convert."""

    words_display = ", ".join(words_list)

    word_info_sections = "\n\n".join([
        f"📖 **Word Info: {w}**\n"
        f"🇮🇳 **Hindi Meaning:** (2-3 words in Hindi)\n"
        f"🔁 **Synonyms:** (3-4 similar English words)\n"
        f"🔄 **Antonyms:** (3-4 opposite English words)\n"
        f"📝 **Context:** (1 line — how '{w}' was used in the story)"
        for w in words_list
    ])

    if language == "Hindi":
        lang_rules = """Language: Hindi (Devanagari script only)
- Write everything — narration, dialogues, moral — fully in Hindi
- Bold each target word in Hindi transliteration every time it appears"""

    elif language == "Hinglish":
        lang_rules = """Language: Hinglish — exactly how Indians speak in real daily life

GOLDEN RULE: Base is HINDI. Only those English words come naturally that Indians say without thinking.
Natural English words Indians always use: school, time, class, office, phone, problem, ready, okay, done, break, free, busy, tired, tension, chill, mood, plan, idea, try, chance, update, seriously, basically, actually, anyway

AVOID:
- Full English sentences
- Awkward English verbs like "come karo", "go karo", "finish karo" — Indians don't say this
- Forcing English to sound Hinglish

BAD: "Miya school se come karti hai. Uska homework finish karna tha."
GOOD: "Miya school se aayi. Homework khatam karna tha, lekin mood nahi tha. 'Ek break lete hain,' usne socha."
GOOD: "Usse lagta tha yeh problem solve nahi hogi, but usne try kiya aur result acha aaya."

Bold each target vocabulary word every time it appears."""

    else:
        lang_rules = """Language: English
- Write the entire story in simple, clear English
- Bold each target word every time it appears like **word**"""

    if existing_story:
        story_instruction = f"""Convert the story below into {language}. Keep the SAME plot, characters, events and moral. Only change the language.

--- ORIGINAL STORY ---
{existing_story}
--- END ---"""
    else:
        story_instruction = f"""Write a brand new story using ALL these words: {words_display}
- Theme: {theme_guide}
- Size: {size_guide} (Short=100-120 words, Medium=200-250 words, Long=350-400 words)
- Each target word must appear at least {count} times
- Use each word in different sentence types: dialogue, question, statement, description
- Never define any word directly — show meaning through context
- Story must feel like a real daily life situation, engaging and easy to understand
- End with a one-line moral that includes at least one target word"""

    return f"""You are a vocabulary learning story writer for Indian English learners.

{lang_rules}

{story_instruction}

After the story, add this Word Info section for each word:

---
{word_info_sections}
---"""


def generate_all_languages(words, size=None, theme=None, count=None, first_language="English"):
    """
    Generate story in all 3 languages at once and return a dict.
    First generates in first_language, then converts to the other two.
    This way user never needs to call AI again just to switch language.
    """
    words_list = [w.strip() for w in words if w.strip()]
    size_guide = size if size and size != "Auto" else "best length suitable for the complexity of all words"
    theme_guide = theme if theme and theme != "Auto" else "most suitable real-life theme for these words"
    count = count or 3

    all_languages = ["English", "Hinglish", "Hindi"]
    other_languages = [l for l in all_languages if l != first_language]

    # Step 1: Generate fresh story in selected language
    prompt = _build_prompt(words_list, size_guide, theme_guide, count, first_language)
    first_result = llm.invoke(prompt).content

    # Step 2: Extract just the story part (before ---) to use as base for conversion
    if "---" in first_result:
        base_story = first_result.split("---")[0].strip()
    else:
        base_story = first_result.strip()

    # Step 3: Convert to other 2 languages
    results = {first_language: first_result}
    for lang in other_languages:
        prompt = _build_prompt(words_list, size_guide, theme_guide, count, lang, existing_story=base_story)
        results[lang] = llm.invoke(prompt).content

    return results


def check_sentences(words, sentence1, sentence2):
    """Single prompt to check if student used vocabulary words correctly."""

    words_display = ", ".join(words) if isinstance(words, list) else words

    prompt = f"""You are a friendly English teacher for Indian learners.

Target words: {words_display}

Student's sentences:
1. "{sentence1}"
2. "{sentence2}"

CHECK ONLY THIS:
- Is the target word used with the correct meaning and in the right context?
- Does the sentence make logical sense?

COMPLETELY IGNORE: spelling, capitalization, punctuation, grammar — none of that matters. Only meaning and usage of the target word matters. If the meaning is right, it's a pass.

Reply in EXACTLY this format:

SENTENCE 1:
Status: ✅ Correct / ❌ Wrong
Mistake: (only if word is used with wrong meaning — else skip this line)
Correct: (corrected sentence — else skip this line)

SENTENCE 2:
Status: ✅ Correct / ❌ Wrong
Mistake: (only if word is used with wrong meaning — else skip this line)
Correct: (corrected sentence — else skip this line)

OVERALL:
(1 encouraging line in Hinglish)"""

    response = llm.invoke(prompt)
    return response.content