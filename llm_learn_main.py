import streamlit as st
import llm_learn

st.set_page_config(page_title="VocabStory", page_icon="📖")

st.title("📖 VocabStory — Learn English Through Stories")
st.markdown("Enter a word and we'll build a story that teaches you how to use it naturally!")

# ─────────────────────────────────────
# STEP 1 — Word Input + Preferences
# ─────────────────────────────────────
word = st.text_input(
    "✏️ Enter a word",
    placeholder="e.g. resilient, empathy, persist..."
)

col1, col2, col3 = st.columns(3)
with col1:
    size = st.selectbox(
        "📏 Story Size",
        options=["Auto", "Short", "Medium", "Long"]
    )
with col2:
    theme = st.selectbox(
        "🎭 Choose Theme",
        options=["Auto", "Real Life", "Adventure", "Mystery",
                 "Romance", "Sci-Fi", "Motivation", "Friendship"]
    )
with col3:
    count = st.slider("🔁 Repeat word count", min_value=1, max_value=15, value=8)

# ─────────────────────────────────────
# STEP 2 — Generate
# ─────────────────────────────────────
if st.button("🚀 Generate Story"):
    if word.strip() == "":
        st.warning("Please enter a word first!")
    else:
        with st.spinner("✨ Crafting your story..."):
            result = llm_learn.generate_story(word, size, theme, count)
            st.session_state["story_word"] = word
            st.session_state["feedback"] = None

            # Split story and word info section
            if "Word Info" in result:
                parts = result.split("---")
                story_part = parts[0].strip()
                info_part = ""
                for p in parts[1:]:
                    if "Word Info" in p or "Hindi Meaning" in p:
                        info_part = p.strip()
                        break
                st.session_state["story"] = story_part
                st.session_state["word_info"] = info_part
            else:
                st.session_state["story"] = result
                st.session_state["word_info"] = ""

# ─────────────────────────────────────
# DISPLAY ORDER:
# 1. Word Info (Meaning, Syn, Ant, Context)
# 2. Story
# 3. Sentence Writing
# 4. AI Feedback
# ─────────────────────────────────────
if "story" in st.session_state and st.session_state["story"]:

    w = st.session_state["story_word"]

    # ── 1. WORD INFO ──
    st.markdown("---")
    if st.session_state.get("word_info"):
        st.markdown(st.session_state["word_info"])
        st.markdown("---")

    # ── 2. STORY ──
    st.markdown(f"## 📖 Story")
    st.markdown(st.session_state["story"])
    st.markdown("---")

    # ── 3. SENTENCE WRITING ──
    st.markdown("## ✍️ Now Your Turn!")
    st.markdown(
        f"Write **2 sentences** using **{w}** from your own life!"
    )

    with st.expander("💡 Need a hint?"):
        st.markdown(f"""
        - Statement: *"I was very {w} during the tough time."*
        - Question: *"Are you {w} enough to face this?"*
        - Past tense: *"She showed {w} in her work."*
        """)

    sentence1 = st.text_area(
        f"📝 Sentence 1 — use **{w}**",
        placeholder=f"Write your first sentence with '{w}'...",
        height=80, key="s1"
    )
    sentence2 = st.text_area(
        f"📝 Sentence 2 — use **{w}** again",
        placeholder=f"Write your second sentence with '{w}'...",
        height=80, key="s2"
    )

    if st.button("🤖 Check My Sentences"):
        if sentence1.strip() == "" or sentence2.strip() == "":
            st.warning("⚠️ Please write both sentences!")
        elif w.lower() not in sentence1.lower():
            st.warning(f"⚠️ Sentence 1 mein **{w}** use karo!")
        elif w.lower() not in sentence2.lower():
            st.warning(f"⚠️ Sentence 2 mein **{w}** use karo!")
        else:
            with st.spinner("🤖 Checking..."):
                feedback = llm_learn.check_sentences(w, sentence1, sentence2)
                st.session_state["feedback"] = feedback

    # ── 4. AI FEEDBACK ──
    if st.session_state.get("feedback"):
        st.markdown("---")
        st.markdown("## 🤖 AI Feedback")

        feedback_text = st.session_state["feedback"]

        # Parse sections
        parts = feedback_text.strip().split("SENTENCE 2:")
        s1_block = parts[0].replace("SENTENCE 1:", "").strip() if parts else ""
        s2_overall = parts[1].strip() if len(parts) > 1 else ""
        s2_parts = s2_overall.split("OVERALL:")
        s2_block = s2_parts[0].strip()
        overall_block = s2_parts[1].strip() if len(s2_parts) > 1 else ""

        # Sentence 1
        if s1_block:
            if "✅" in s1_block:
                st.success(f"**Sentence 1:**\n\n{s1_block}")
            else:
                st.error(f"**Sentence 1:**\n\n{s1_block}")

        # Sentence 2
        if s2_block:
            if "✅" in s2_block:
                st.success(f"**Sentence 2:**\n\n{s2_block}")
            else:
                st.error(f"**Sentence 2:**\n\n{s2_block}")

        # Overall
        if overall_block:
            st.info(f"💬 {overall_block}")

        st.markdown("---")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔄 Try Again"):
                st.session_state["feedback"] = None
                st.rerun()
        with col_b:
            if st.button("➡️ New Word"):
                for key in ["story", "story_word", "word_info", "feedback"]:
                    st.session_state[key] = None
                st.rerun()
