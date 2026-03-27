import streamlit as st
import llm_learn

# llm_learn.py must have convert_story_language() — see updated llm_learn.py

def _update_story(result, lang):
    """Parse result and update story + word_info in session state."""
    if "Word Info" in result:
        parts = result.split("---")
        st.session_state["story"] = parts[0].strip()
        info_parts = [p.strip() for p in parts[1:] if "Word Info" in p or "Hindi Meaning" in p]
        st.session_state["word_info"] = "\n\n---\n\n".join(info_parts)
    else:
        st.session_state["story"] = result
        st.session_state["word_info"] = ""
    st.session_state["story_language"] = lang
    st.session_state["feedback"] = None

st.set_page_config(page_title="VocabStory", page_icon="📖")

st.title("📖 VocabStory — Learn English Through Stories")
st.markdown("Enter words and we'll build a story that teaches you how to use them naturally!")

# ─────────────────────────────────────
# STEP 1 — Word Input (Comma-separated)
# ─────────────────────────────────────
st.markdown("### ✏️ Enter Words")
st.markdown("Enter multiple words **separated by commas** — e.g. `resilient, empathy, persevere`")

words_input = st.text_input(
    "Your vocabulary words",
    placeholder="e.g. resilient, empathy, persevere, diligent",
    key="words_input"
)

# Parse words from comma-separated input
if words_input.strip():
    word_list = [w.strip() for w in words_input.split(",") if w.strip()]
    # Deduplicate (case-insensitive), preserve order
    seen = set()
    unique_words = []
    for w in word_list:
        if w.lower() not in seen:
            seen.add(w.lower())
            unique_words.append(w)
    word_list = unique_words
else:
    word_list = []

# Show parsed word chips
if word_list:
    st.markdown("**Words detected:**")
    chip_html = " ".join(
        f'<span style="background:#e8f4fd; border:1px solid #90caf9; border-radius:20px; padding:3px 12px; margin:3px; display:inline-block; font-size:0.9em;">📌 {w}</span>'
        for w in word_list
    )
    st.markdown(chip_html, unsafe_allow_html=True)
    st.caption(f"✅ {len(word_list)} word(s) ready")
elif words_input.strip():
    st.warning("⚠️ Could not parse any words. Please separate words with commas.")

# ─────────────────────────────────────
# STEP 2 — Preferences
# ─────────────────────────────────────
st.markdown("### ⚙️ Preferences")

col1, col2, col3, col4 = st.columns(4)

with col1:
    size = st.selectbox(
        "📏 Story Size",
        options=["Auto", "Short", "Medium", "Long"]
    )

with col2:
    theme = st.selectbox(
        "🎭 Theme",
        options=["Auto", "Real Life", "Adventure", "Mystery",
                 "Romance", "Sci-Fi", "Motivation", "Friendship"]
    )

with col3:
    language = st.selectbox(
        "🌐 Language",
        options=["English", "Hinglish", "Hindi"]
    )

with col4:
    count = st.slider("🔁 Word repeat", min_value=2, max_value=8, value=3)

# ─────────────────────────────────────
# STEP 3 — Generate
# ─────────────────────────────────────
if st.button("🚀 Generate Story", type="primary"):
    if not word_list:
        st.warning("⚠️ Please enter at least one word!")
    else:
        with st.spinner("✨ Crafting your story..."):
            result = llm_learn.generate_story(
                word_list,
                size, theme, count, language
            )
            st.session_state["story_words"] = word_list.copy()
            _update_story(result, language)

# ─────────────────────────────────────
# DISPLAY ORDER:
# 1. Word Info
# 2. Story
# 3. Sentences
# 4. Feedback
# ─────────────────────────────────────
if "story" in st.session_state and st.session_state.get("story"):

    words = st.session_state.get("story_words", [])
    words_str = ", ".join(words)

    # ── 1. WORD INFO ──
    st.markdown("---")
    if st.session_state.get("word_info"):
        st.markdown(st.session_state["word_info"])
        st.markdown("---")

    # ── 2. STORY ──
    story_lang = st.session_state.get("story_language", "English")
    st.markdown(f"## 📖 Story")
    st.caption(f"Words: **{words_str}** &nbsp;|&nbsp; Language: **{story_lang}**")
    st.markdown(st.session_state["story"])

    # ── LANGUAGE CONVERTER ──
    st.markdown("#### 🌐 Convert Story Language")
    st.caption("Instantly retranslate the same story — no need to regenerate!")
    lang_col1, lang_col2, lang_col3 = st.columns(3)

    with lang_col1:
        if st.button("🇬🇧 English", use_container_width=True,
                     disabled=(story_lang == "English")):
            with st.spinner("Converting to English..."):
                result = llm_learn.generate_story(
                    words, language="English",
                    existing_story=st.session_state["story"]
                )
                _update_story(result, "English")
                st.rerun()

    with lang_col2:
        if st.button("🇮🇳 Hinglish", use_container_width=True,
                     disabled=(story_lang == "Hinglish")):
            with st.spinner("Converting to Hinglish..."):
                result = llm_learn.generate_story(
                    words, language="Hinglish",
                    existing_story=st.session_state["story"]
                )
                _update_story(result, "Hinglish")
                st.rerun()

    with lang_col3:
        if st.button("🕉️ Hindi", use_container_width=True,
                     disabled=(story_lang == "Hindi")):
            with st.spinner("Converting to Hindi..."):
                result = llm_learn.generate_story(
                    words, language="Hindi",
                    existing_story=st.session_state["story"]
                )
                _update_story(result, "Hindi")
                st.rerun()

    st.markdown("---")

    # ── 3. SENTENCE WRITING ──
    st.markdown("## ✍️ Now Your Turn!")
    st.markdown(f"Write **2 sentences** using any of these words: **{words_str}**")

    with st.expander("💡 Need a hint?"):
        st.markdown(f"""
        - Use any word from: **{words_str}**
        - Statement: *"I was very {words[0]} during the tough time."*
        - Question: *"Are you {words[0]} enough to face this?"*
        - Past tense: *"She showed {words[0]} in her work."*
        """)

    sentence1 = st.text_area(
        "📝 Sentence 1",
        placeholder=f"Write your first sentence using any of: {words_str}",
        height=80, key="s1"
    )
    sentence2 = st.text_area(
        "📝 Sentence 2",
        placeholder=f"Write your second sentence using any of: {words_str}",
        height=80, key="s2"
    )

    if st.button("🤖 Check My Sentences"):
        if sentence1.strip() == "" or sentence2.strip() == "":
            st.warning("⚠️ Please write both sentences!")
        else:
            s1_has_word = any(w.lower() in sentence1.lower() for w in words)
            s2_has_word = any(w.lower() in sentence2.lower() for w in words)

            if not s1_has_word:
                st.warning(f"⚠️ Sentence 1 mein koi bhi word use karo: **{words_str}**")
            elif not s2_has_word:
                st.warning(f"⚠️ Sentence 2 mein koi bhi word use karo: **{words_str}**")
            else:
                with st.spinner("🤖 Checking..."):
                    feedback = llm_learn.check_sentences(words, sentence1, sentence2)
                    st.session_state["feedback"] = feedback

    # ── 4. FEEDBACK ──
    if st.session_state.get("feedback"):
        st.markdown("---")
        st.markdown("## 🤖 AI Feedback")

        feedback_text = st.session_state["feedback"]

        parts = feedback_text.strip().split("SENTENCE 2:")
        s1_block = parts[0].replace("SENTENCE 1:", "").strip() if parts else ""
        s2_overall = parts[1].strip() if len(parts) > 1 else ""
        s2_parts = s2_overall.split("OVERALL:")
        s2_block = s2_parts[0].strip()
        overall_block = s2_parts[1].strip() if len(s2_parts) > 1 else ""

        if s1_block:
            if "✅" in s1_block:
                st.success(f"**Sentence 1:**\n\n{s1_block}")
            else:
                st.error(f"**Sentence 1:**\n\n{s1_block}")

        if s2_block:
            if "✅" in s2_block:
                st.success(f"**Sentence 2:**\n\n{s2_block}")
            else:
                st.error(f"**Sentence 2:**\n\n{s2_block}")

        if overall_block:
            st.info(f"💬 {overall_block}")

        st.markdown("---")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔄 Try Again"):
                st.session_state["feedback"] = None
                st.rerun()
        with col_b:
            if st.button("➡️ New Words"):
                for key in ["story", "story_words", "word_info", "feedback"]:
                    if key in st.session_state:
                        st.session_state[key] = None
                st.rerun()