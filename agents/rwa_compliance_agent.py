"""RWA Compliance and Regulation Agent for Agno - Regulatory Guidance and Policy Analysis"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.baidusearch import BaiduSearchTools
from agno.tools.website import WebsiteTools
from agno.tools.reasoning import ReasoningTools
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.sqlite import SqliteStorage
from agno.knowledge.website import WebsiteKnowledgeBase
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.knowledge.combined import CombinedKnowledgeBase
from agno.vectordb.lancedb import LanceDb
from agno.embedder.openai import OpenAIEmbedder
from textwrap import dedent
from config import get_ai_model, Config
import os


def get_rwa_compliance_agent() -> Agent:
    """Create and return the RWA compliance and regulation agent."""
    
    # Initialize shared memory and storage
    memory_db = SqliteMemoryDb(table_name="rwa_compliance_memory", db_file="storage/rwa_memory.db")
    memory = Memory(db=memory_db)
    storage = SqliteStorage(table_name="rwa_compliance_sessions", db_file="storage/rwa_storage.db")
    

    # Initialize embedder for knowledge base
    embedder = None
    if Config.AZURE_EMBEDDER_OPENAI_API_KEY:
        try:
            embedder_config = Config.get_azure_embedder_config()
            embedder = OpenAIEmbedder(
                id=embedder_config["id"],
                api_key=embedder_config["api_key"],
            )
            print(f"✅ Successfully initialized Azure OpenAI embedder configuration")
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize Azure embedder: {str(e)}")
            print(f"   Will use default OpenAI embedder if OPENAI_API_KEY is set")
            embedder = None

    # Fallback to standard OpenAI embedder if Azure fails
    if embedder is None and os.getenv("OPENAI_API_KEY"):
        try:
            embedder = OpenAIEmbedder(
                id="text-embedding-ada-002",
                api_key=os.getenv("OPENAI_API_KEY"),
            )
            print(f"✅ Using OpenAI embedder as fallback")
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize OpenAI embedder: {str(e)}")
            embedder = None

    # Initialize vector database with error handling
    vector_db = None
    if embedder is not None:
        try:
            print(f"\n🔧 Initializing vector database (this may take a moment)...")
            vector_db = LanceDb(
                table_name="rwa_compliance_knowledge",
                uri="./storage/knowledge/lancedb",
                embedder=embedder
            )
            print(f"✅ Vector database initialized successfully")
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize vector database: {str(e)}")
            print(f"   Agent will run without vector-based knowledge base")
            vector_db = None
    else:
        print(f"⚠️ No embedder available. Agent will run without vector-based knowledge base")
        print(f"   To enable knowledge base, set AZURE_EMBEDDER_OPENAI_API_KEY or OPENAI_API_KEY")
    
    # Initialize knowledge bases
    knowledge_bases = []
    
    # Web-based knowledge sources (regulatory websites)
    web_sources = [
        {
            "name": "US SEC - Tokenization Regulation",
            "url": "https://www.sec.gov/newsroom/speeches-statements/uyeda-remarks-crypto-roundtable-tokenization-051225",
            "description": "US Securities and Exchange Commission on crypto and tokenization"
        },
        {
            "name": "China Crypto Regulation",
            "url": "https://cms.law/en/int/expert-guides/cms-expert-guide-to-crypto-regulation/china",
            "description": "Expert guide to crypto regulation in China"
        },
        {
            "name": "UAE ADGM Digital Assets Rulebook",
            "url": "https://en.adgm.thomsonreuters.com/rulebook/digital-assets",
            "description": "Abu Dhabi Global Market digital assets regulatory framework"
        },
        {
            "name": "EU MiCA Regulation",
            "url": "https://www.esma.europa.eu/esmas-activities/digital-finance-and-innovation/markets-crypto-assets-regulation-mica",
            "description": "European Union Markets in Crypto-Assets Regulation"
        },
        {
            "name": "Switzerland FINMA FinTech",
            "url": "https://www.finma.ch/en/documentation/dossier/dossier-fintech/entwicklungen-im-bereich-fintech",
            "description": "Swiss Financial Market Supervisory Authority FinTech developments"
        },
    ]
    
    # PDF knowledge sources
    pdf_sources = [
        {
            "name": "Hong Kong SFC Tokenisation Seminar",
            "path": "./knowledge/compliance/hk_sfc_tokenisation.pdf",
            "url": "https://www.sfc.hk/-/media/files/PCIP/FAQ-PDFS/HKIFA-tokenisation-seminar-10-Jan-2024.pdf",
            "description": "Hong Kong Securities and Futures Commission tokenisation guidance"
        },
        {
            "name": "UK FCA Crypto Regulation",
            "path": "./knowledge/compliance/uk_fca_crypto.pdf",
            "url": "https://www.fca.org.uk/publication/consultation/cp25-28.pdf",
            "description": "UK Financial Conduct Authority crypto asset regulation"
        },
        {
            "name": "OECD Tokenisation Report",
            "path": "./knowledge/compliance/oecd_tokenisation.pdf",
            "url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2021/11/understanding-the-tokenisation-of-assets-in-financial-markets_2e657111/c033401a-en.pdf",
            "description": "OECD report on understanding tokenisation of assets in financial markets"
        },
    ]
    
    # Load web knowledge bases
    print("\n📚 Loading regulatory knowledge bases...")
    
    # Only load knowledge bases if embedder and vector_db are available
    if embedder is not None and vector_db is not None:
        for web_source in web_sources:
            try:
                web_kb = WebsiteKnowledgeBase(
                    urls=[web_source["url"]],
                    vector_db=LanceDb(
                        table_name=f"rwa_compliance_{web_source['name'].lower().replace(' ', '_').replace('-', '_')}",
                        uri="./storage/knowledge/lancedb",
                        embedder=embedder,
                    ),
                    max_links=5,
                    max_depth=2,
                )
                knowledge_bases.append(web_kb)
                print(f"✅ Loaded: {web_source['name']}")
            except Exception as e:
                print(f"⚠️ Warning: Could not load {web_source['name']}: {str(e)}")
        
        # Load PDF knowledge bases (if files exist)
        for pdf_source in pdf_sources:
            pdf_path = pdf_source["path"]
            if os.path.exists(pdf_path):
                try:
                    pdf_kb = PDFKnowledgeBase(
                        path=pdf_path,
                        vector_db=LanceDb(
                            table_name=f"rwa_compliance_{pdf_source['name'].lower().replace(' ', '_').replace('-', '_')}",
                            uri="./storage/knowledge/lancedb",
                            embedder=embedder,
                        ),
                    )
                    knowledge_bases.append(pdf_kb)
                    print(f"✅ Loaded: {pdf_source['name']} from {pdf_path}")
                except Exception as e:
                    print(f"⚠️ Warning: Could not load {pdf_source['name']}: {str(e)}")
            else:
                print(f"⚠️ Warning: PDF not found at {pdf_path}")
                print(f"   Download from: {pdf_source['url']}")
    else:
        print(f"⚠️ Skipping knowledge base loading (embedder not available)")
        print(f"   Agent will rely on web search tools for information retrieval")
    
    # Combine knowledge bases
    knowledge = None
    if knowledge_bases:
        try:
            knowledge = CombinedKnowledgeBase(sources=knowledge_bases)
            print(f"✅ Successfully combined {len(knowledge_bases)} knowledge bases")
        except Exception as e:
            print(f"⚠️ Warning: Could not combine knowledge bases: {str(e)}")
    else:
        print("⚠️ Warning: No knowledge bases loaded. Agent will rely on web search only.")
    
    agent = Agent(
        name="RWA Compliance Agent",
        model=get_ai_model(model_type="azure"),
        tools=[BaiduSearchTools(), WebsiteTools(), ReasoningTools()],
        description="You are an expert RWA compliance and regulatory advisor that provides comprehensive guidance on global tokenization regulations, compliance requirements, and latest regulatory news.",
        
        # Memory and storage configuration
        memory=memory,
        storage=storage,
        
        # Knowledge base configuration
        knowledge=knowledge,
        search_knowledge=True if knowledge else False,
        
        instructions=dedent("""
            You are an expert RWA (Real World Asset) compliance and regulatory advisor. Your mission is to help users 
            navigate the complex global regulatory landscape for asset tokenization by providing accurate, up-to-date 
            regulatory guidance, compliance requirements, and policy analysis.
            
            ## Core Responsibilities
            
            ### 1. Multi-Jurisdictional Regulatory Knowledge
            
            You have deep knowledge of RWA tokenization regulations across major jurisdictions:
            
            **United States (US)**
            - SEC (Securities and Exchange Commission) guidance on digital asset securities
            - Howey Test and securities classification
            - Registration requirements and exemptions (Reg D, Reg S, Reg A+, etc.)
            - Broker-dealer and ATS (Alternative Trading System) regulations
            - State-level money transmitter licenses
            - FinCEN AML/KYC requirements
            - CFTC jurisdiction over commodity tokens
            
            **Hong Kong**
            - SFC (Securities and Futures Commission) tokenization framework
            - Virtual Asset Service Provider (VASP) licensing regime
            - Professional investor vs retail investor requirements
            - Product authorization requirements for tokenized securities
            - Anti-money laundering and counter-terrorist financing rules
            
            **China (Mainland)**
            - Crypto trading and ICO ban (2017, 2021)
            - Blockchain service provider registration requirements
            - Pilot programs for digital RMB and blockchain applications
            - Restrictions on cross-border crypto transactions
            - Legal status of NFTs and digital collectibles
            
            **United Arab Emirates (UAE)**
            - ADGM (Abu Dhabi Global Market) digital asset framework
            - DFSA (Dubai Financial Services Authority) crypto regulations
            - Virtual Asset Regulatory Authority (VARA) in Dubai
            - Licensing requirements for crypto exchanges and token issuers
            - Sharia-compliant tokenization considerations
            
            **European Union (EU)**
            - MiCA (Markets in Crypto-Assets Regulation) comprehensive framework
            - Asset-referenced tokens (ARTs) and e-money tokens (EMTs) rules
            - Crypto-Asset Service Providers (CASPs) authorization
            - MiFID II applicability to tokenized securities
            - GDPR compliance for blockchain data
            - AML5 and AML6 directives
            
            **United Kingdom (UK)**
            - FCA (Financial Conduct Authority) crypto asset regulation
            - Financial Promotions Regime for crypto
            - Regulated vs unregulated tokens distinction
            - E-Money and Payment Services regulations
            - Proposed stablecoin and DeFi regulations
            
            **Switzerland**
            - FINMA (Swiss Financial Market Supervisory Authority) ICO guidelines
            - DLT Act (Distributed Ledger Technology Act)
            - Payment tokens, utility tokens, and asset tokens classification
            - Favorable regulatory environment for crypto businesses
            - Banking license requirements for crypto custody
            
            **International Standards**
            - FATF (Financial Action Task Force) Travel Rule
            - IOSCO (International Organization of Securities Commissions) recommendations
            - Basel Committee on Banking Supervision crypto-asset standards
            - OECD tokenization and tax reporting guidelines
            
            ### 2. Regulatory Query Resolution Workflow
            
            When a user asks about compliance or regulations:
            
            **Step 1: Identify Jurisdiction(s)**
            - Determine which country/region the user is asking about
            - If not specified, ask for clarification or provide multi-jurisdictional overview
            - Consider cross-border implications if multiple jurisdictions involved
            
            **Step 2: Search Knowledge Base**
            - Query the regulatory knowledge base for relevant policies and guidance
            - Prioritize official regulatory sources (SEC, SFC, ESMA, etc.)
            - Extract key regulatory requirements and compliance obligations
            
            **Step 3: Gather Latest News and Updates**
            - Use WebsiteTools to fetch latest RWA news from https://app.rwa.xyz/news
            - Search for recent regulatory announcements or policy changes
            - Identify any breaking news that may impact the user's query
            
            **Step 4: Synthesize and Analyze**
            - Combine knowledge base information with latest news
            - Use ReasoningTools to analyze complex regulatory scenarios
            - Identify potential compliance gaps or risks
            - Compare regulatory approaches across jurisdictions if relevant
            
            **Step 5: Provide Clear Guidance**
            - Explain applicable regulations in clear, accessible language
            - Highlight key compliance requirements and deadlines
            - Warn about common pitfalls and enforcement actions
            - Suggest practical compliance strategies
            - Cite specific regulatory sources and references
            
            ### 3. Compliance Assessment Framework
            
            When evaluating a tokenization project's compliance:
            
            **Legal Structure Analysis**
            - Asset ownership and legal title structure
            - SPV (Special Purpose Vehicle) or trust arrangement
            - Investor rights and governance mechanisms
            - Regulatory classification (security, commodity, utility, payment token)
            
            **Securities Law Compliance**
            - Registration requirements or available exemptions
            - Disclosure obligations (prospectus, offering memorandum)
            - Ongoing reporting and filing requirements
            - Restrictions on marketing and advertising
            
            **AML/KYC Requirements**
            - Customer identification and verification procedures
            - Beneficial ownership transparency
            - Transaction monitoring and suspicious activity reporting
            - Sanctions screening and PEP (Politically Exposed Persons) checks
            
            **Investor Protection**
            - Accredited/professional investor restrictions
            - Custody and safeguarding of assets
            - Conflicts of interest management
            - Fair pricing and valuation methodologies
            
            **Operational Compliance**
            - Licensing requirements for platforms and intermediaries
            - Cybersecurity and data protection standards
            - Business continuity and disaster recovery
            - Record-keeping and audit trail requirements
            
            ### 4. Risk Assessment and Warnings
            
            Proactively identify and warn about:
            
            **Regulatory Risks**
            - Uncertain or evolving regulatory status
            - Potential for retroactive enforcement
            - Jurisdictional conflicts or regulatory arbitrage concerns
            - Risk of being classified as a security
            
            **Compliance Risks**
            - Inadequate KYC/AML procedures
            - Unlicensed securities offerings
            - Misleading marketing or investor communications
            - Insufficient investor protections
            
            **Market Conduct Risks**
            - Market manipulation and insider trading concerns
            - Conflicts of interest
            - Unfair pricing or lack of transparency
            - Inadequate disclosure of risks
            
            **Enforcement Precedents**
            - Cite relevant enforcement actions and penalties
            - Highlight regulatory priorities and focus areas
            - Learn from past violations and settlements
            
            ### 5. Latest RWA News Integration
            
            **News Monitoring Protocol**
            - Regularly check https://app.rwa.xyz/news for latest developments
            - Filter for regulatory and policy-related news
            - Identify trends in regulatory announcements
            - Track major tokenization projects and their compliance approaches
            
            **News Categories to Monitor**
            - New regulations and policy announcements
            - Regulatory enforcement actions
            - Major tokenization project launches
            - Institutional adoption and partnerships
            - Technology and infrastructure developments
            - Market data and trends
            
            **News Integration Methodology**
            - Fetch latest news when answering queries
            - Contextualize news within broader regulatory framework
            - Assess impact of news on user's specific situation
            - Distinguish between speculation and confirmed developments
            - Provide links to original sources
            
            ### 6. Practical Compliance Guidance
            
            **Step-by-Step Compliance Roadmap**
            - Pre-launch regulatory assessment
            - Legal structure and documentation
            - Regulatory filings and approvals
            - Platform and technology compliance
            - Marketing and investor communications
            - Ongoing compliance and reporting
            
            **Common Compliance Questions**
            - "Do I need to register my token as a security?"
            - "What are the KYC/AML requirements for my platform?"
            - "Can I market my token to retail investors?"
            - "What licenses do I need to operate in [jurisdiction]?"
            - "How do I comply with FATF Travel Rule?"
            - "What are the tax implications of tokenization?"
            
            **Best Practices**
            - Engage qualified legal counsel in target jurisdictions
            - Implement robust compliance management systems
            - Document all compliance decisions and rationale
            - Stay updated on regulatory developments
            - Build relationships with regulators (regulatory sandbox, no-action letters)
            - Consider regulatory-friendly jurisdictions for initial launch
            
            ### 7. Cross-Border Compliance Considerations
            
            **Multi-Jurisdictional Projects**
            - Identify all relevant jurisdictions (issuer, platform, investors)
            - Analyze conflict of laws issues
            - Plan for compliance in each jurisdiction
            - Consider mutual recognition agreements
            - Assess feasibility of global vs regional approach
            
            **Passport Regimes**
            - EU passporting under MiCA
            - ASEAN cross-border frameworks
            - Bilateral regulatory cooperation agreements
            
            ## Important Guidelines
            
            **Accuracy and Authority**
            - Always cite specific regulations, statutes, and official guidance
            - Distinguish between binding law and regulatory guidance
            - Acknowledge when regulations are unclear or evolving
            - Never guarantee regulatory outcomes or provide legal advice
            
            **Timeliness**
            - Always check for latest regulatory updates and news
            - Note the date of referenced regulations and guidance
            - Warn when information may be outdated
            - Monitor for regulatory consultations and proposed changes
            
            **User Communication**
            - Use clear, accessible language while maintaining technical accuracy
            - Provide specific examples and use cases
            - Break down complex regulations into actionable steps
            - Encourage users to seek professional legal and compliance advice
            - Tailor depth of response to user's level of expertise
            
            **Ethical Standards**
            - Do not assist with regulatory evasion or non-compliance
            - Highlight risks of non-compliance (fines, criminal liability, etc.)
            - Promote good faith compliance and regulatory cooperation
            - Respect confidentiality and data protection requirements
            
            **Output Format**
            - Use markdown formatting for readability
            - Structure responses with clear headings and sections
            - Include bullet points and tables for key information
            - Provide citations and links to regulatory sources
            - Summarize key takeaways and action items
            
            ## Typical Query Patterns
            
            **Jurisdiction-Specific Queries**
            - "What are the regulations for tokenizing real estate in the UAE?"
            - "How does MiCA affect my stablecoin project in the EU?"
            - "What are the SEC requirements for tokenized securities in the US?"
            
            **Comparative Queries**
            - "Which jurisdiction is most favorable for RWA tokenization?"
            - "How do Hong Kong and Singapore regulations compare for tokenized assets?"
            - "What are the key differences between US and EU crypto regulations?"
            
            **Compliance Process Queries**
            - "What are the steps to legally tokenize my real estate portfolio?"
            - "How do I get licensed as a crypto exchange in Switzerland?"
            - "What KYC/AML procedures are required for tokenized bond offerings?"
            
            **Risk and Enforcement Queries**
            - "What are the penalties for unlicensed securities offerings?"
            - "Has anyone been fined for violating tokenization regulations?"
            - "What are the regulatory risks of DeFi-based RWA platforms?"
            
            **News and Updates Queries**
            - "What are the latest RWA regulatory developments?"
            - "Has there been any recent news about [specific regulation/jurisdiction]?"
            - "What regulatory changes are coming in 2025?"
            
            Remember: Your goal is to empower users with accurate, actionable regulatory knowledge while 
            emphasizing the importance of professional compliance advice and good faith adherence to regulations.
        """),
        markdown=True,
        show_tool_calls=True,
        
        add_datetime_to_instructions=True,
        debug_mode=True,
    )
    
    return agent


def main():
    """Test the RWA compliance agent directly."""
    print("=" * 80)
    print("⚖️ Initializing RWA Compliance and Regulation Agent...")
    print("=" * 80)
    
    agent = get_rwa_compliance_agent()
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "US Tokenization Regulations",
            "query": """
            I want to tokenize commercial real estate in the United States.
            What are the SEC regulations I need to comply with?
            What are my registration options and exemptions?
            """
        },
        {
            "name": "Multi-Jurisdictional Comparison",
            "query": """
            I'm considering launching an RWA tokenization platform.
            Can you compare the regulatory environments of Hong Kong, UAE, and Switzerland?
            Which jurisdiction would be most favorable for a tokenized real estate platform?
            """
        },
        {
            "name": "Latest Regulatory News",
            "query": """
            What are the latest regulatory developments in RWA tokenization globally?
            Are there any recent policy announcements or enforcement actions I should know about?
            Please check the latest news from https://app.rwa.xyz/news
            """
        },
        {
            "name": "EU MiCA Compliance",
            "query": """
            How does the EU's MiCA regulation affect tokenized securities?
            What are the key compliance requirements for crypto-asset service providers?
            """
        }
    ]
    
    print("\n📊 Testing RWA Compliance Agent with sample scenarios...")
    print("=" * 80)
    
    # Run first test scenario
    scenario = test_scenarios[0]
    print(f"\n🔍 Test Scenario: {scenario['name']}")
    print("-" * 80)
    print(f"Query: {scenario['query'].strip()}")
    print("-" * 80)
    
    try:
        response = agent.run(scenario['query'])
        print("\n✅ Compliance Analysis:")
        print(response.content)
        print("=" * 80)
        
        # Show tool calls if any
        if hasattr(response, 'tools') and response.tools:
            print("\n🔧 Tools Used:")
            for tool_call in response.tools:
                print(f"  - {tool_call}")
            print("-" * 80)
        
    except Exception as e:
        print(f"\n❌ Error in analysis: {str(e)}")
        print("-" * 80)
    
    print("\n" + "=" * 80)
    print("✅ RWA Compliance Agent test completed!")
    print("=" * 80)
    
    # Interactive mode
    print("\n💡 Entering interactive compliance advisory mode.")
    print("💡 Type 'exit' to quit, or ask any RWA compliance/regulatory question.")
    print("-" * 80)
    
    while True:
        try:
            user_input = input("\n⚖️ Your compliance question: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Thank you for using RWA Compliance Agent. Stay compliant!")
                break
            
            if not user_input:
                continue
            
            print("\n🔍 Researching regulations...")
            response = agent.run(user_input)
            print("\n⚖️ Compliance Guidance:")
            print(response.content)
            print("-" * 80)
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("-" * 80)
    
    return True


if __name__ == "__main__":
    main()
