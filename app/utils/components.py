import streamlit as st

def kpi_card(label, value, delta=None, is_error=False):
    """A styled metric card for the top of the dashboard."""
    color = "#FF4B4B" if is_error else "#29B5E8"
    
    st.markdown(
        f"""
        <div style="padding: 20px; border-radius: 10px; background-color: #f0f2f6; border-left: 5px solid {color};">
            <h4 style="margin: 0; color: #5f6368; font-size: 14px;">{label}</h4>
            <h2 style="margin: 0; color: #1f1f1f;">{value}</h2>
            {f'<p style="color: green; margin: 0;">↑ {delta}</p>' if delta else ''}
        </div>
        """,
        unsafe_allow_code_all=True
    )

def section_header(title, subtitle=None):
    """Uniform header style for all pages."""
    st.title(title)
    if subtitle:
        st.caption(subtitle)
    st.divider()
