"""Main Streamlit Application for the RWA Team"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import nest_asyncio
import asyncio
from agents.rwa_workflow import rwa_workflow, arun_rwa_workflow
from app.utils import display_messages, add_message, clear_chat_history, process_uploaded_files, create_agno_images_from_bytes

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Configure the page
st.set_page_config(
    page_title="Enhanced Agno Streamlit App",
    page_icon="🤖",
    layout="wide",
)


def main():
    # App header
    st.title("🏢 RWA Asset Tokenization Platform")
    st.markdown("Professional RWA Asset Verification, Valuation and Tokenization Service Platform")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ System Settings")
        
        # Session controls
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            clear_chat_history()
            if "uploaded_files_data" in st.session_state:
                del st.session_state.uploaded_files_data
            st.rerun()
        
        # File clear button
        if "uploaded_files_data" in st.session_state and st.session_state.uploaded_files_data:
            if st.button("📁 Clear Uploaded Files", use_container_width=True, type="secondary"):
                del st.session_state.uploaded_files_data
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 📁 File Upload")
        
        # File uploader for asset verification
        uploaded_files = st.file_uploader(
            "Upload Asset-related Files",
            type=["pdf", "jpg", "jpeg", "png", "doc", "docx"],
            accept_multiple_files=True,
            help="Supports uploading property certificates, land certificates and other asset proof documents"
        )
        
        # Process and store uploaded files
        if uploaded_files:
            st.success(f"✅ Uploaded {len(uploaded_files)} file(s)")
            # Store files in session state
            st.session_state.uploaded_files_data = process_uploaded_files(uploaded_files)
            
            # Display uploaded files info
            st.markdown("**Uploaded Files:**")
            for file_info in st.session_state.uploaded_files_data:
                st.markdown(f"📄 {file_info['name']} ({file_info['size_mb']:.2f}MB)")
        
        st.markdown("---")
        st.markdown("### 💡 About RWA Workflow")
        st.markdown("""
        **Workflow Steps:**
        - 🔍 **Asset Verification**: Verify the authenticity and legality of asset files
        - 💰 **Asset Valuation**: Conduct professional asset market evaluation
        - ⛓️ **Token Deployment**: Deploy ERC20 tokens on Ethereum Sepolia testnet
        
        **Process Features:**
        1. Smart Conditional Logic: Determine subsequent steps based on verification results
        2. Asynchronous Execution: Efficiently handle multiple agent calls
        3. Complete Report: Generate detailed tokenization report
        4. Error Handling: Automatically abort and provide reasons upon failure
        """)
    
    # Initialize RWA workflow session
    # The workflow maintains its own state and memory across interactions
    
    # Initialize conversation history if not exists
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message
        welcome_message = """
        👋 Welcome to the RWA Asset Tokenization Platform!
        
        I am a professional RWA workflow system that can help you:
        - 🔍 Verify the authenticity and legality of asset files
        - 💰 Conduct professional asset value evaluation
        - ⛓️ Issue asset tokens on the blockchain
        
        **Usage Steps:**
        1. Upload your asset proof documents (such as property certificates, land certificates, etc.)
        2. Provide detailed asset information (type, location, area, age, etc.)
        3. Set token parameters (name, symbol, supply, etc.)
        4. The system will automatically complete the entire tokenization process
        
        Please first upload your asset proof documents, then tell me your tokenization requirements.
        """
        add_message("assistant", welcome_message)
    
    # Display chat history
    display_messages()
    
    # Chat input
    if prompt := st.chat_input("Please enter your question..."):
        # Check if there are uploaded files and create agno Image objects
        agno_images = []
        file_info = ""
        
        if "uploaded_files_data" in st.session_state and st.session_state.uploaded_files_data:
            # Create agno Image object list (for image files)
            agno_images = create_agno_images_from_bytes(st.session_state.uploaded_files_data)
            
            # Create File information text (for all files)
            file_names = [f['name'] for f in st.session_state.uploaded_files_data]
            file_info = f"\n\n[Uploaded Files: {', '.join(file_names)}]"
            
            # Display uploaded file information
            if agno_images:
                st.info(f"🖼️ Uploaded {len(agno_images)} image file(s), will perform visual analysis")
        
        # Build complete message
        complete_message = prompt + file_info
        
        # Add user message to chat history
        add_message("user", prompt)
        
        # Generate workflow response (asynchronous execution)
        with st.chat_message("assistant"):
            with st.spinner("RWA workflow is processing your request..."):
                try:
                    # Prepare additional_data
                    additional_data = {
                        "has_files": "uploaded_files_data" in st.session_state and bool(st.session_state.uploaded_files_data),
                        "files_count": len(st.session_state.uploaded_files_data) if "uploaded_files_data" in st.session_state and st.session_state.uploaded_files_data else 0
                    }
                    
                    # Run asynchronous workflow using asyncio
                    if agno_images:
                        # If there are images, pass both message and images
                        response = asyncio.run(arun_rwa_workflow(
                            message=complete_message,
                            images=agno_images,
                            additional_data=additional_data
                        ))
                    else:
                        # Text message only
                        response = asyncio.run(arun_rwa_workflow(
                            message=complete_message,
                            additional_data=additional_data
                        ))
                    
                    # Process response
                    if hasattr(response, 'content'):
                        response_content = response.content
                    else:
                        response_content = str(response)
                    
                    # Display response
                    st.markdown(response_content)
                    
                    # Add workflow response to chat history
                    add_message("assistant", response_content)
                    
                    # Display workflow execution status (if available)
                    if hasattr(response, 'workflow_metrics') and response.workflow_metrics:
                        with st.expander("📊 Workflow Execution Details", expanded=False):
                            try:
                                metrics = response.workflow_metrics
                                if hasattr(metrics, 'total_steps'):
                                    st.success(f"✅ Workflow execution completed, executed {metrics.total_steps} step(s)")
                                else:
                                    st.info("✅ Workflow execution completed")
                                
                                # Display asynchronous execution information
                                st.info("⚡ Workflow uses asynchronous execution for better performance")
                            except Exception as e:
                                st.info(f"Workflow execution completed (failed to get details: {e})")
                    
                except Exception as e:
                    error_message = f"❌ Error occurred while processing request: {str(e)}"
                    st.error(error_message)
                    add_message("assistant", error_message)


if __name__ == "__main__":
    main()