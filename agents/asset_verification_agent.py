"""Asset Verification Agent for Agno Streamlit Application"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.baidusearch import BaiduSearchTools
from agno.tools.website import WebsiteTools
from agno.tools.reasoning import ReasoningTools
from agno.media import Image
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.sqlite import SqliteStorage
from textwrap import dedent
from config import get_ai_model
import os


def get_asset_verification_agent() -> Agent:
    """Create and return the asset verification agent."""
    
    # Initialize shared memory and storage (consistent with RWA team)
    memory_db = SqliteMemoryDb(table_name="rwa_memory", db_file="storage/rwa_memory.db")
    memory = Memory(db=memory_db)
    storage = SqliteStorage(table_name="rwa_sessions", db_file="storage/rwa_storage.db")
    
    agent = Agent(
        name="Asset Verification Agent",
        model=get_ai_model(model_type="azure"),
        tools=[BaiduSearchTools(),WebsiteTools(),ReasoningTools()],
        description="You are an expert asset verification agent that validates asset documents and images for authenticity and compliance.",
        # Memory and storage configuration
        memory=memory,
        storage=storage,
        instructions=dedent("""
            You are an expert asset verification agent. Your role is to validate uploaded asset documents and images for authenticity and legal compliance.
            
            Process Flow:
            1. Multi-modal Data Parsing:
               - Analyze uploaded documents and images
               - Extract key information (text, metadata, visual elements)
               - Identify document type and format
            
            2. Authenticity Verification:
               - Check document formatting consistency
               - Verify content integrity and logical coherence
               - Validate signatures, seals, and official markings
               - Cross-reference information using BaiduSearchTools to confirm document legitimacy
               - Look for signs of tampering or forgery
            
            3. Compliance Check:
               - Research applicable laws and regulations using BaiduSearchTools
               - Verify if the asset can be legally traded
               - Identify any restrictions or limitations on the asset
               - Check for required documentation or approvals
            
            4. Report Generation:
               - Provide a comprehensive verification report
               - Include findings on authenticity and compliance
               - Highlight any issues or concerns
               - Give a clear recommendation on asset validity
               - Format the report in markdown for clear presentation
            
            Important Guidelines:
            - Be thorough but concise in your analysis
            - Clearly distinguish between facts and opinions
            - If you're unsure about something, state your uncertainty rather than making assumptions
            - Focus on the specific asset documents provided
            - All output content is in English
            - Retrieve user asset information and incorporate key information into the model context
        """),
        markdown=True,
        show_tool_calls=True,
        # History and session
        add_state_in_messages=True,
        add_history_to_messages=True,
        num_history_runs=3,
        read_chat_history=True,
        enable_user_memories=True
    )
    
    return agent


def main():
    """Test the asset verification agent directly."""
    print("Initializing Asset Verification Agent...")
    agent = get_asset_verification_agent()
    
    # Test image processing if image file exists
    print("\nTesting image processing functionality...")
    print("="*50)
    
    # Check if sample image exists in the project directory
    image_path = "./house.webp"
    if os.path.exists(image_path):
        try:
            print(f"Processing image: {image_path}")
            response = agent.run(
                "Analyze this asset document image and verify its authenticity.",
                images=[Image(filepath=image_path)]
            )
            print("Image Analysis Response:")
            print(response.content)
            print("="*50)
        except Exception as e:
            print(f"Error processing image: {str(e)}")
    else:
        print(f"Sample image not found at {image_path}")
        print("To test image processing, please place a sample image named 'sample_asset.jpg' in the project directory.")
    
    return True


if __name__ == "__main__":
    main()





