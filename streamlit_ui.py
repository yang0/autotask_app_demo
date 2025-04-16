import streamlit as st
import sys
import json
from typing import Optional, Any, Dict
from application_tools import ToolsClient

def get_current_time(format_string: str = "%Y-%m-%d %H:%M:%S", timezone: str = "UTC") -> Dict[str, Any]:
    """Execute the time node operation using ToolsClient"""
    client = ToolsClient()
    result = client.run_node_sync(
        class_path="autotask_core.nodes.time.TimeNode",
        inputs={
            "format_string": format_string,
            "timezone": timezone
        }
    )
    # Parse the result if it's a string
    if isinstance(result, str):
        result = json.loads(result)
    return result

def main():
    """Main function for Streamlit UI"""
    # Configure page
    st.set_page_config(
        page_title="Time Display Demo",
        page_icon="⏰",
        layout="wide"
    )

    # Main UI
    st.title("Time Display Demo ⏰")
    st.markdown("Display current time in different formats and timezones")

    # Create time display form
    with st.form("time_display_form"):
        # Time format input
        format_string = st.text_input(
            "Time Format",
            value="%Y-%m-%d %H:%M:%S",
            help="Enter time format (e.g., %Y-%m-%d %H:%M:%S)"
        )
        
        # Timezone input
        timezone = st.text_input(
            "Timezone",
            value="UTC",
            help="Enter timezone (e.g., UTC, America/New_York, Asia/Shanghai)"
        )
        
        # Get time button
        if st.form_submit_button("Get Current Time"):
            try:
                # Execute time node operation
                result = get_current_time(format_string, timezone)
                
                if result.get('success'):
                    # Display time in large format
                    st.success("Current Time:")
                    st.header(result.get('current_time', ''))
                    
                    # Display additional time information
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info("Time Details:")
                        st.write(f"🌐 Timezone: {result.get('timezone', timezone)}")
                        st.write(f"⚡ Timestamp: {result.get('timestamp', '')}")
                    with col2:
                        st.info("Format Settings:")
                        st.write(f"📝 Format: {format_string}")
                        st.write(f"🔄 ISO Format: {result.get('iso_format', '')}")
                else:
                    st.error("Failed to get current time")
                    if 'error' in result:
                        st.error(f"Error: {result['error']}")
                        
            except Exception as e:
                st.error(f"Operation failed: {str(e)}")

    # Add footer
    st.markdown("---")
    st.markdown("Made with ❤️ using Streamlit and AutoTask")

if __name__ == "__main__":
    main() 