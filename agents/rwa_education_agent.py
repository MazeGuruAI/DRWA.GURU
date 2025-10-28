"""RWA Education Agent for Agno"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.baidusearch import BaiduSearchTools
from agno.tools.website import WebsiteTools
from agno.tools.reasoning import ReasoningTools
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.sqlite import SqliteStorage
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.vectordb.lancedb import LanceDb
from textwrap import dedent
from config import get_ai_model
import os


def get_rwa_education_agent() -> Agent:
    """Create and return the RWA education agent."""
    
    # Initialize shared memory and storage (consistent with RWA team)
    memory_db = SqliteMemoryDb(table_name="rwa_memory", db_file="storage/rwa_memory.db")
    memory = Memory(db=memory_db)
    storage = SqliteStorage(table_name="rwa_sessions", db_file="storage/rwa_storage.db")
    
    # Initialize knowledge base with RWA documentation
    pdf_path = "./agents/Rwa Tokenization Key Trends 2025 Market Outlook Report Brickken V2.pdf"
    knowledge = None
    
    if os.path.exists(pdf_path):
        try:
            knowledge = PDFKnowledgeBase(
                path=pdf_path,
                vector_db=LanceDb(
                    table_name="rwa_education",
                    uri="./storage/knowledge/lancedb",
                ),
            )
            print(f"✅ Successfully loaded RWA knowledge from {pdf_path}")
        except Exception as e:
            print(f"⚠️ Warning: Could not load RWA knowledge PDF: {str(e)}")
            print(f"   Knowledge base will rely on web search instead.")
    else:
        print(f"⚠️ Warning: RWA knowledge PDF not found at {pdf_path}")
        print(f"   Knowledge base will rely on web search instead.")
    
    agent = Agent(
        name="RWA Education Agent",
        model=get_ai_model(model_type="azure"),
        tools=[BaiduSearchTools(), WebsiteTools(), ReasoningTools()],
        description="You are an expert RWA (Real World Asset) education agent that helps users understand RWA concepts, tokenization process, market trends, and industry best practices.",
        
        # Memory and storage configuration
        memory=memory,
        storage=storage,
        
        # Knowledge base configuration (optional)
        knowledge=knowledge,
        search_knowledge=True if knowledge else False,  # Enable Agentic RAG if knowledge available
        
        instructions=dedent("""
            You are an expert RWA (Real World Asset) education agent. Your role is to educate users about RWA tokenization, 
            including concepts, processes, market trends, regulations, and best practices.
            
            Education Areas:
            
            1. **RWA Fundamentals**:
               - What is RWA (Real World Asset) and why it matters
               - Types of assets that can be tokenized (real estate, commodities, art, bonds, etc.)
               - Benefits of asset tokenization (liquidity, fractional ownership, transparency, etc.)
               - Differences between traditional assets and tokenized assets
            
            2. **Tokenization Process**:
               - Step-by-step guide to tokenizing real-world assets
               - Asset verification and legal compliance requirements
               - Asset valuation methods and considerations
               - Smart contract deployment and token standards (ERC20, ERC721, etc.)
               - Custody and asset backing mechanisms
            
            3. **Market Trends and Outlook**:
               - Use knowledge base to provide insights on 2025 RWA market outlook
               - Key trends in RWA tokenization industry
               - Major players and platforms in the RWA space
               - Regional differences and adoption rates
               - Future predictions and growth opportunities
            
            4. **Regulatory and Legal Framework**:
               - Regulatory requirements for RWA tokenization in different jurisdictions
               - Securities laws and compliance considerations
               - KYC/AML requirements for tokenized assets
               - Legal structure for asset-backed tokens
               - Investor protection and disclosure requirements
            
            5. **Technical Implementation**:
               - Blockchain platforms for RWA tokenization
               - Smart contract architecture and security
               - Oracle integration for real-world data
               - Token standards and their use cases
               - Custody solutions and multi-sig wallets
            
            6. **Risk Management**:
               - Risks associated with RWA tokenization
               - Market risk, liquidity risk, and regulatory risk
               - Technical risks and security considerations
               - Mitigation strategies and best practices
            
            7. **Use Cases and Case Studies**:
               - Real-world examples of successful RWA tokenization
               - Industry-specific applications (real estate, commodities, etc.)
               - Lessons learned from past projects
               - Best practices from leading platforms
            
            Important Guidelines:
            - Always search knowledge base first for RWA-specific information if available
            - Use BaiduSearchTools and WebsiteTools to find latest market data and news
            - Apply ReasoningTools to analyze complex concepts and provide clear explanations
            - Provide concrete examples and case studies when possible
            - Break down complex topics into easy-to-understand concepts
            - Use diagrams, flowcharts, or step-by-step guides when helpful
            - Always cite sources for market data and statistics
            - Distinguish between facts, trends, and predictions
            - Tailor explanations to the user's level of understanding
            - Encourage questions and provide follow-up explanations
            - All output content is in English unless user requests otherwise
            - Format responses in markdown for better readability
            
            When answering questions:
            1. First check if the answer is in the knowledge base (if available)
            2. Supplement with real-time web search if needed
            3. Provide structured, comprehensive answers
            4. Include relevant examples and case studies
            5. Highlight key takeaways and action items
            6. Suggest related topics for further learning
        """),
        markdown=True,
        show_tool_calls=True,
    )
    
    return agent


def main():
    """Test the RWA education agent directly."""
    print("=" * 60)
    print("🎓 Initializing RWA Education Agent...")
    print("=" * 60)
    
    agent = get_rwa_education_agent()
    
    # Test the agent with sample queries
    test_queries = [
        "What is RWA and why is it important?",
        "Can you explain the key trends in RWA tokenization for 2025?",
        "What are the main steps to tokenize a real estate asset?",
    ]
    
    print("\n📝 Testing agent with sample queries...")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test Query {i}: {query}")
        print("-" * 60)
        
        try:
            response = agent.run(query)
            print("\n✅ Agent Response:")
            print(response.content)
            print("=" * 60)
            
            # Show tool calls if any
            if hasattr(response, 'tools') and response.tools:
                print("\n🔧 Tool Calls Made:")
                for tool_call in response.tools:
                    print(f"  - {tool_call}")
                print("-" * 60)
            
        except Exception as e:
            print(f"\n❌ Error testing query '{query}': {str(e)}")
            print("-" * 60)
            continue
    
    print("\n" + "=" * 60)
    print("✅ RWA Education Agent test completed!")
    print("=" * 60)
    
    # Interactive mode
    print("\n💡 Entering interactive mode. Type 'exit' to quit.")
    print("-" * 60)
    
    while True:
        try:
            user_input = input("\n🤔 Your question: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\n💭 Thinking...")
            response = agent.run(user_input)
            print("\n📚 Answer:")
            print(response.content)
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("-" * 60)
    
    return True


if __name__ == "__main__":
    main()
