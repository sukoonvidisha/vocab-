import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)


def generate_story(words, size=None, theme=None, count=None, language="English"):

    words_list = [w.strip() for w in words if w.strip()]
    words_display = ", ".join(words_list)

    if not size or size == "Auto":
        size_guide = "best length suitable for the complexity of all words together"
    else:
        size_guide = size

    if not theme or theme == "Auto":
        theme_guide = "most suitable real-life related theme for these words"
    else:
        theme_guide = theme

    if not count:
        count = 3

    lang_instruction = _lang_instruction(language)

    word_info_sections = "\n\n".join([
        f"📖 **Word Info: {w}**\n"
        f"🇮🇳 **Hindi Meaning:** (Hindi mein 2-3 words)\n"
        f"🔁 **Synonyms:** (3-4 similar English words)\n"
        f"🔄 **Antonyms:** (3-4 opposite English words)\n"
        f"📝 **Context:** (1 line — how '{w}' was used in the story)"
        for w in words_list
    ])

    prompt = f"""
You are a vocabulary learning story writer.

Target vocabulary words: {words_display}
Language: {language}
Theme: {theme_guide}
Size: {size_guide}

Story Size Guide:
- Short  = 100-120 words
- Medium = 200-250 words
- Long   = 350-400 words

Language Instructions:
{lang_instruction}

Story Rules:
- Use EVERY word from this list in the story: {words_display}
- Each word must appear at least {count} times
- Use each word in different sentence types (question, dialogue, statement, description)
- Never define any word directly — show meaning through context
- All words should feel naturally connected in one single flowing story
- Story must be relatable to real daily life situations
- Make it engaging and easy to understand
- End with a one line moral that includes at least one target word

After the story, add this section for EACH word:

---
{word_info_sections}
---

Do not explain word meanings directly. Let reader feel it through story.
"""

    response = llm.invoke(prompt)
    return response.content


def convert_story_language(existing_story, words, target_language):
    """
    Convert an already-generated story into a different language
    (English / Hinglish / Hindi) while keeping the same plot and words.
    Also regenerates the Word Info section in the new language.
    """
    if isinstance(words, list):
        words_display = ", ".join(words)
    else:
        words_display = words

    lang_instruction = _lang_instruction(target_language)

    word_info_sections = "\n\n".join([
        f"📖 **Word Info: {w}**\n"
        f"🇮🇳 **Hindi Meaning:** (Hindi mein 2-3 words)\n"
        f"🔁 **Synonyms:** (3-4 similar English words)\n"
        f"🔄 **Antonyms:** (3-4 opposite English words)\n"
        f"📝 **Context:** (1 line — how '{w}' was used in the story)"
        for w in (words if isinstance(words, list) else words.split(", "))
    ])

    prompt = f"""
You are a vocabulary learning story writer.

Below is an existing story. Convert it into {target_language} while keeping:
- The SAME plot, characters, and events
- All target vocabulary words still present and bolded
- The same moral at the end

Target vocabulary words: {words_display}
Target language: {target_language}

Language Instructions:
{lang_instruction}

--- ORIGINAL STORY ---
{existing_story}
--- END OF ORIGINAL STORY ---

Output the converted story first, then add the Word Info section below:

---
{word_info_sections}
---
"""

    response = llm.invoke(prompt)
    return response.content


def _lang_instruction(language):
    if language == "Hindi":
        return """Write the ENTIRE story in Hindi (Devanagari script).
All dialogues, narration and moral must be in Hindi only.
Bold each target word in Hindi transliteration every time it appears."""
    elif language == "Hinglish":
        return """Write the story in Hinglish — a natural mix of Hindi and English.
Use English for the target vocabulary words and key sentences.
Use Hindi for dialogues, feelings and connecting sentences.
Example style: 'Rahul bahut resilient tha. Usne kabhi haar nahi maani.'
Bold each target English word every time it appears."""
    else:
        return """Write the entire story in simple English.
Bold each target word every time it appears like **word**."""


def check_sentences(words, sentence1, sentence2):

    if isinstance(words, list):
        words_display = ", ".join(words)
    else:
        words_display = words

    prompt = f"""
You are a friendly English teacher for Indian learners.

Target words: "{words_display}"

Student's sentences:
Sentence 1: "{sentence1}"
Sentence 2: "{sentence2}"

Check each sentence for:
- Are the target words used correctly? (meaning, correct form, correct part of speech)
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