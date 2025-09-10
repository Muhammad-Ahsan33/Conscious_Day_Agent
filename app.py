import streamlit as st
from datetime import date
from agent.conscious_agent import ConsciousAgent
from database.db_operations import DatabaseManager
from components.ui_components import render_form, render_previous_entries, render_sidebar, display_entry

# Page configuration
st.set_page_config(
    page_title="Conscious Day Agent",
    page_icon="🌅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = ConsciousAgent()
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()
if 'new_entry' not in st.session_state:
    st.session_state.new_entry = False


def main():
    """Main application function"""

    # Header
    st.title("🌅 Conscious Day Agent")
    st.markdown("*Reflect inward. Act with clarity.*")

    # Get all entries for sidebar history
    entries = st.session_state.db_manager.get_all_entries()
    selected_date = render_sidebar(entries)

    # New Entry
    if st.session_state.get('new_entry', False):
        render_today_page()
        return

    # Selected entry from history
    if selected_date:
        render_previous_entries(entries, selected_date)
    else:
        st.info("Use the sidebar to create a new entry or browse your history.")


def render_today_page():
    """Render the reflection form and processing"""
    st.header("📝 Create a New Morning Reflection")

    result = render_form()
    if result.get('submitted'):
        process_reflection(
            result['journal'],
            result['dream'],
            result['intention'],
            result['priorities']
        )
        st.session_state.new_entry = False


def process_reflection(journal, dream, intention, priorities):
    """Process the reflection inputs through the AI agent"""

    with st.spinner("🧠 Processing your reflection and generating insights..."):
        try:
            # Generate AI response
            response = st.session_state.agent.process_reflection(
                journal=journal,
                dream=dream,
                intention=intention,
                priorities=priorities
            )

            # Save to database
            entry_id = st.session_state.db_manager.save_entry(
                journal=journal,
                dream=dream,
                intention=intention,
                priorities=priorities,
                reflection=response.get('reflection', ''),
                strategy=response.get('strategy', ''),
                dream_interpretation=response.get('dream_interpretation', ''),
                mindset_insight=response.get('mindset_insight', '')
            )

            if entry_id:
                st.success("✅ Reflection processed and saved successfully!")

                # Display results
                entry_data = {
                    'journal': journal,
                    'dream': dream,
                    'intention': intention,
                    'priorities': priorities,
                    'reflection': response.get('reflection', ''),
                    'strategy': response.get('strategy', ''),
                    'dream_interpretation': response.get('dream_interpretation', ''),
                    'mindset_insight': response.get('mindset_insight', ''),
                    'date': date.today().strftime("%Y-%m-%d")
                }
                display_entry(entry_data)
            else:
                st.error("❌ Failed to save entry. Please try again.")

        except Exception as e:
            st.error(f"An error occurred while processing your reflection: {str(e)}")
            st.info("Please check your API configuration and try again.")


if __name__ == "__main__":
    main()
