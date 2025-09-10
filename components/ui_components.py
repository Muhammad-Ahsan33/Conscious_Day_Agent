import streamlit as st
from typing import Dict, List


def render_sidebar(entries: List[Dict]) -> str:
    """Render sidebar with New Entry button and history of past entries"""
    st.sidebar.markdown("### 🌅 Conscious Day Agent")
    
    # New entry button
    if st.sidebar.button("➕ Create New Entry", type="primary"):
        st.session_state.new_entry = True
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📜 Entry History")

    if not entries:
        st.sidebar.info("No previous entries found.")
        return None

    # Each entry identified by id + date
    entry_labels = [f"{e['date']} - #{e['id']}" for e in entries]
    selected = st.sidebar.radio("Select an entry:", entry_labels, label_visibility="collapsed")
    return selected



def render_form() -> Dict[str, str]:
    """Render the main reflection form"""

    with st.form("conscious_day_form"):
        st.subheader("📝 Morning Reflection")

        journal = st.text_area(
            "Morning Journal",
            placeholder="How are you feeling this morning? What's on your mind?",
            height=120,
        )

        dream = st.text_area(
            "Dream",
            placeholder="Describe any dreams you remember...",
            height=100,
        )

        intention = st.text_input(
            "Intention of the Day",
            placeholder="What do you want to embody today?",
        )

        priorities = st.text_area(
            "Top 3 Priorities",
            placeholder="1. First priority\n2. Second priority\n3. Third priority",
            height=80,
        )

        submitted = st.form_submit_button("✨ Generate Insights", type="primary")

        if submitted:
            return {
                'journal': journal,
                'dream': dream,
                'intention': intention,
                'priorities': priorities,
                'submitted': True
            }

        return {'submitted': False}


def render_previous_entries(entries: List[Dict], selected_label: str) -> None:
    """Render only the selected entry from history"""
    if not selected_label:
        st.info("Select an entry from the sidebar to view.")
        return

    # Extract ID from label
    selected_id = int(selected_label.split("#")[-1])
    entry = next((e for e in entries if e['id'] == selected_id), None)

    if entry:
        display_entry(entry)


def display_entry(entry: Dict) -> None:
    """Display a single entry with all its components"""

    st.header(f"📅 Reflection from {entry['date']}")

    col1, col2 = st.columns(2)

    with col1:
        if entry.get('reflection'):
            st.subheader("🔍 Inner Reflection")
            st.write(entry['reflection'])
        if entry.get('dream_interpretation'):
            st.subheader("💭 Dream Interpretation")
            st.write(entry['dream_interpretation'])

    with col2:
        if entry.get('mindset_insight'):
            st.subheader("🧠 Mindset Insight")
            st.write(entry['mindset_insight'])
        if entry.get('strategy'):
            st.subheader("📋 Day Strategy")
            st.write(entry['strategy'])

    with st.expander("📂 View Original Inputs"):
        st.write("**Journal:**", entry.get('journal', 'N/A'))
        st.write("**Dream:**", entry.get('dream', 'No dream recorded'))
        st.write("**Intention:**", entry.get('intention', 'N/A'))
        st.write("**Priorities:**", entry.get('priorities', 'N/A'))
