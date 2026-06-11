AgenticHealthAI 🏥🤖
AgenticHealthAI is an AI-powered healthcare assistant that helps users assess symptoms, receive risk-based triage recommendations, access medical literature insights, chat with an AI medical assistant, and locate nearby healthcare professionals.

Features
1. User Authentication
- Secure user registration and login
- Password hashing using BCrypt
- User-specific session management

2. Medical Profile Management
- Store user blood group
- Store allergy information
- Profile retrieval and updates
                                                                            
3. Symptom Risk Assessment
- Rule-based triage engine
- Detects potentially dangerous symptoms
- Categorizes symptoms into:
    . Low Risk
    . Moderate-High Risk
    . High Risk

4. AI Medical Assistant
- Conversational medical chatbot
- Context-aware follow-up conversations
- Persistent conversation memory
- Clinical interpretation generation

5. Medical Literature Retrieval
- MCP-powered PubMed integration
- Retrieves relevant medical research
- Generates literature summaries
- Provides evidence-based insights

6. Doctor Discovery
- Location-based doctor search
- Finds nearest healthcare professionals
- Distance calculation using Haversine formula
- Contact information display

7. Conversation History
- Stores all user interactions
- Displays previous symptom assessments
- User-specific chat history

8. Modern Frontend Experience
- Responsive UI
- Dark/Light mode
- WHO medical news feed
- Profile dropdown panel
- ECG-style loading animation
- Smooth transitions and hover effects

--> Technology Stack
- Frontend
. HTML5
. CSS3
. JavaScript (Vanilla JS)
. Tailwind CSS
. Font Awesome

- Backend
. Python
. FastAPI
. AI & LLM
. LangGraph
. LangChain
. Groq LLM
. MCP (Model Context Protocol)

- Database
. MySQL

- Security
. BCrypt password hashing

- External Services
. PubMed MCP Server
. WHO RSS Feed
. Geolocation Services
