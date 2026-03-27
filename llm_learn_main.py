import streamlit as st
import llm_learn

st.set_page_config(page_title="VocabStory", page_icon="📖")

st.title("📖 VocabStory — Learn English Through Stories")
st.markdown("Enter words and we'll build a story that teaches you how to use them naturally!")

# ─────────────────────────────────────
# STEP 1 — Word Input (Enter per word)
# ─────────────────────────────────────
st.markdown("### ✏️ Enter Words")
st.markdown("Press **Enter** after each word to add it to the list")

# Word input
new_word = st.text_input(
    "Type a word and press Enter",
    placeholder="e.g. resilient",
    key="word_input"
)

# Initialize word list in session
if "word_list" not in st.session_state:
    st.session_state["word_list"] = []

# Add word on input
col_add, col_clear = st.columns([1, 1])
with col_add:
    if st.button("➕ Add Word"):
        if new_word.strip() and new_word.strip().lower() not in [w.lower() for w in st.session_state["word_list"]]:
            st.session_state["word_list"].append(new_word.strip())
            st.rerun()
        elif new_word.strip() == "":
            st.warning("Please type a word first!")
        else:
            st.warning("Word already added!")

with col_clear:
    if st.button("🗑️ Clear All"):
        st.session_state["word_list"] = []
        st.rerun()

# Show added words as chips
if st.session_state["word_list"]:
    st.markdown("**Your words:**")
    cols = st.columns(min(len(st.session_state["word_list"]), 5))
    for i, w in enumerate(st.session_state["word_list"]):
        with cols[i % 5]:
            if st.button(f"❌ {w}", key=f"remove_{i}"):
                st.session_state["word_list"].pop(i)
                st.rerun()

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
    if not st.session_state["word_list"]:
        st.warning("⚠️ Please add at least one word!")
    else:
        with st.spinner("✨ Crafting your story..."):
            result = llm_learn.generate_story(
                st.session_state["word_list"],
                size, theme, count, language
            )
            st.session_state["story_words"] = st.session_state["word_list"].copy()
            st.session_state["feedback"] = None

            # Split story and word info
            if "Word Info" in result:
                parts = result.split("---")
                st.session_state["story"] = parts[0].strip()
                info_parts = [p.strip() for p in parts[1:] if "Word Info" in p or "Hindi Meaning" in p]
                st.session_state["word_info"] = "\n\n---\n\n".join(info_parts)
            else:
                st.session_state["story"] = result
                st.session_state["word_info"] = ""

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
    st.markdown(f"## 📖 Story")
    st.caption(f"Words: **{words_str}**")
    st.markdown(st.session_state["story"])
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
            # Check if at least one word used in each sentence
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
                for key in ["story", "story_words", "word_info", "feedback", "word_list"]:
                    st.session_state[key] = None
                st.rerun()