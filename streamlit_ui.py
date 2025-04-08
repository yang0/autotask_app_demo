import streamlit as st
import sys
import json
from typing import Optional, Any, Dict
from application_tools import ToolsClient

def run_file_list(directory: str, pattern: str, include_dirs: bool, recursive: bool) -> Dict[str, Any]:
    """Execute the file list operation using ToolsClient"""
    client = ToolsClient()
    result = client.run_node_sync(
        class_path="autotask_core.nodes.file.FileListNode",
        inputs={
            "directory": directory,
            "pattern": pattern,
            "include_dirs": str(include_dirs).lower(),
            "recursive": str(recursive).lower()
        }
    )
    # Parse the result if it's a string
    if isinstance(result, str):
        result = json.loads(result)
    
    # Parse the files field if it's a string
    if isinstance(result.get('files'), str):
        try:
            result['files'] = json.loads(result['files'])
        except json.JSONDecodeError:
            st.error("Failed to parse files data")
            result['files'] = []
    
    return result

def main():
    """Main function for Streamlit UI"""
    # Configure page
    st.set_page_config(
        page_title="File Browser Demo",
        page_icon="📁",
        layout="wide"
    )

    # Main UI
    st.title("File Browser Demo 📁")
    st.markdown("Browse and search files in your system")

    # Create search form
    with st.form("file_browser_form"):
        # Directory input
        directory = st.text_input(
            "Directory Path",
            value="",
            help="Enter the directory path to browse"
        )
        
        # File pattern input
        pattern = st.text_input(
            "File Pattern",
            value="",
            help="Enter file pattern (e.g., *.txt, *.py)"
        )
        
        # Include directories checkbox
        include_dirs = st.checkbox(
            "Include Directories",
            value=True,
            help="Include directories in the results"
        )
        
        # Recursive search checkbox
        recursive = st.checkbox(
            "Recursive Search",
            value=False,
            help="Search in subdirectories"
        )
        
        # Search button
        if st.form_submit_button("List Files"):
            with st.spinner("Scanning files..."):
                try:
                    # Execute file list operation
                    result = run_file_list(directory, pattern, include_dirs, recursive)
                    
                    if result.get('success') == 'true':  # Changed to string comparison
                        files = result.get('files', [])
                        
                        # Display results
                        st.success(f"Found {len(files)} items")
                        
                        # Create a table of files
                        if files:
                            file_data = []
                            for file in files:
                                file_data.append({
                                    "Name": file.get('name', ''),
                                    "Path": file.get('path', ''),
                                    "Type": "Directory" if file.get('is_dir', False) else "File",
                                    "Size": f"{file.get('size', 0):,} bytes" if not file.get('is_dir', False) else "-"
                                })
                            
                            st.dataframe(
                                file_data,
                                use_container_width=True,
                                column_config={
                                    "Name": st.column_config.TextColumn("Name", width="medium"),
                                    "Path": st.column_config.TextColumn("Path", width="large"),
                                    "Type": st.column_config.TextColumn("Type", width="small"),
                                    "Size": st.column_config.TextColumn("Size", width="medium")
                                }
                            )
                    else:
                        st.error("Failed to list files")
                        if 'error' in result:
                            st.error(f"Error: {result['error']}")
                            
                except Exception as e:
                    st.error(f"Operation failed: {str(e)}")

    # Add footer
    st.markdown("---")
    st.markdown("Made with ❤️ using Streamlit and AutoTask")

if __name__ == "__main__":
    main() 