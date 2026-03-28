import streamlit as st
import llm_learn


def _parse_result(result):
    """Split a result string into (story, word_info)."""
    if "Word Info" in result:
        parts = result.split("---")
        story = parts[0].strip()
        info_parts = [p.strip() for p in parts[1:] if "Word Info" in p or "Hindi Meaning" in p]
        word_info = "\n\n---\n\n".join(info_parts)
    else:
        story = result.strip()
        word_info = ""
    return story, word_info


def _switch_language(lang):
    """Switch display to a stored language — zero API calls."""
    cached = st.session_state.get("all_languages", {})
    if lang in cached:
        story, word_info = _parse_result(cached[lang])
        st.session_state["story"] = story
        st.session_state["word_info"] = word_info
        st.session_state["story_language"] = lang
        st.session_state["feedback"] = None


# ─────────────────────────────────────
st.set_page_config(page_title="VocabStory", page_icon="📖")
st.title("📖 VocabStory — Learn English Through Stories")
st.markdown("Enter words and we'll build a story that teaches you how to use them naturally!")

# ─────────────────────────────────────
# STEP 1 — Word Input
# ─────────────────────────────────────
st.markdown("### ✏️ Enter Words")
st.markdown("Enter multiple words **separated by commas** — e.g. `resilient, empathy, persevere`")

words_input = st.text_input(
    "Your vocabulary words",
    placeholder="e.g. resilient, empathy, persevere, diligent",
    key="words_input"
)

# Parse + deduplicate
word_list = []
if words_input.strip():
    seen = set()
    for w in words_input.split(","):
        w = w.strip()
        if w and w.lower() not in seen:
            seen.add(w.lower())
            word_list.append(w)

# Show chips
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
    size = st.selectbox("📏 Story Size", options=["Auto", "Short", "Medium", "Long"])
with col2:
    theme = st.selectbox("🎭 Theme", options=["Auto", "Real Life", "Adventure", "Mystery",
                                               "Romance", "Sci-Fi", "Motivation", "Friendship"])
with col3:
    language = st.selectbox("🌐 Language", options=["English", "Hinglish", "Hindi"])
with col4:
    count = st.slider("🔁 Word repeat", min_value=2, max_value=8, value=3)

# ─────────────────────────────────────
# STEP 3 — Generate (all 3 languages at once)
# ─────────────────────────────────────
if st.button("🚀 Generate Story", type="primary"):
    if not word_list:
        st.warning("⚠️ Please enter at least one word!")
    else:
        with st.spinner("✨ Crafting your story in all 3 languages... (this takes ~15 seconds)"):
            all_results = llm_learn.generate_all_languages(
                word_list, size, theme, count, first_language=language
            )
            st.session_state["all_languages"] = all_results
            st.session_state["story_words"] = word_list.copy()
            _switch_language(language)

# ─────────────────────────────────────
# DISPLAY
# ─────────────────────────────────────
if st.session_state.get("story"):

    words = st.session_state.get("story_words", [])
    words_str = ", ".join(words)
    story_lang = st.session_state.get("story_language", "English")

    # ── 1. WORD INFO ──
    st.markdown("---")
    if st.session_state.get("word_info"):
        st.markdown(st.session_state["word_info"])
        st.markdown("---")

    # ── 2. STORY ──
    st.markdown("## 📖 Story")
    st.caption(f"Words: **{words_str}** &nbsp;|&nbsp; Language: **{story_lang}**")
    st.markdown(st.session_state["story"])

    # ── LANGUAGE SWITCH (instant — no API call) ──
    st.markdown("#### 🌐 Switch Language")
    st.caption("✅ All 3 versions already generated — switching is instant!")
    lang_col1, lang_col2, lang_col3 = st.columns(3)

    with lang_col1:
        if st.button("🇬🇧 English", use_container_width=True, disabled=(story_lang == "English")):
            _switch_language("English")
            st.rerun()
    with lang_col2:
        if st.button("🇮🇳 Hinglish", use_container_width=True, disabled=(story_lang == "Hinglish")):
            _switch_language("Hinglish")
            st.rerun()
    with lang_col3:
        if st.button("🕉️ Hindi", use_container_width=True, disabled=(story_lang == "Hindi")):
            _switch_language("Hindi")
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

    sentence1 = st.text_area("📝 Sentence 1",
                              placeholder=f"Write your first sentence using any of: {words_str}",
                              height=80, key="s1")
    sentence2 = st.text_area("📝 Sentence 2",
                              placeholder=f"Write your second sentence using any of: {words_str}",
                              height=80, key="s2")

    if st.button("🤖 Check My Sentences"):
        if not sentence1.strip() or not sentence2.strip():
            st.warning("⚠️ Please write both sentences!")
        else:
            s1_ok = any(w.lower() in sentence1.lower() for w in words)
            s2_ok = any(w.lower() in sentence2.lower() for w in words)
            if not s1_ok:
                st.warning(f"⚠️ Sentence 1 mein koi bhi word use karo: **{words_str}**")
            elif not s2_ok:
                st.warning(f"⚠️ Sentence 2 mein koi bhi word use karo: **{words_str}**")
            else:
                with st.spinner("🤖 Checking..."):
                    st.session_state["feedback"] = llm_learn.check_sentences(words, sentence1, sentence2)

    # ── 4. FEEDBACK ──
    if st.session_state.get("feedback"):
        st.markdown("---")
        st.markdown("## 🤖 AI Feedback")

        feedback_text = st.session_state["feedback"]
        parts = feedback_text.strip().split("SENTENCE 2:")
        s1_block = parts[0].replace("SENTENCE 1:", "").strip()
        s2_overall = parts[1].strip() if len(parts) > 1 else ""
        s2_parts = s2_overall.split("OVERALL:")
        s2_block = s2_parts[0].strip()
        overall_block = s2_parts[1].strip() if len(s2_parts) > 1 else ""

        if s1_block:
            (st.success if "✅" in s1_block else st.error)(f"**Sentence 1:**\n\n{s1_block}")
        if s2_block:
            (st.success if "✅" in s2_block else st.error)(f"**Sentence 2:**\n\n{s2_block}")
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
                for key in ["story", "story_words", "word_info", "feedback", "all_languages", "story_language"]:
                    st.session_state.pop(key, None)
                st.rerun()