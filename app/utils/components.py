import streamlit as st

def kpi_card(label, value, delta=None, is_error=False):
    """A styled metric card with corrected HTML rendering."""
    color = "#FF4B4B" if is_error else "#29B5E8"
    
    # Corrected parameter to unsafe_allow_html
    st.markdown(
        f"""
        <div style="padding: 20px; border-radius: 10px; background-color: #f0f2f6; border-left: 5px solid {color}; margin-bottom: 10px;">
            <h4 style="margin: 0; color: #5f6368; font-size: 14px;">{label}</h4>
            <h2 style="margin: 0; color: #1f1f1f;">{value}</h2>
            {f'<p style="color: green; margin: 0;">↑ {delta}</p>' if delta else ''}
        </div>
        """,
        unsafe_allow_html=True
    )

def section_header(title, subtitle=None):
    """Uniform header style for all pages."""
    st.title(title)
    if subtitle:
        st.caption(subtitle)
    st.divider()

def platform_badge(platform):
    """Visual indicator for source platform."""
    p_color = "#0085ff" if platform.lower() == 'bluesky' else "#ff0000"
    st.markdown(
        f'<span style="background-color:{p_color}; color:white; padding:2px 8px; border-radius:10px; font-size:10px;">{platform.upper()}</span>', 
        unsafe_allow_html=True
    )
