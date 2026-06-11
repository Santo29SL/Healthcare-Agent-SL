from langgraph.graph import MessagesState
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver  
from dotenv import load_dotenv
import os
import asyncio
import operator
import json
from langchain_core.messages import AnyMessage, AIMessage
from typing_extensions import Annotated, TypedDict
from mcp_use import MCPAgent, MCPClient




# Ensure API key is set
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")

model = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    groq_api_key=GROQ_API_KEY
)


# model = ChatGroq(model_name="meta-llama/llama-4-scout-17b-16e-instruct") # Updated model name to a known valid one or kept user's if sure

class GraphState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

async def mcp_call(state: GraphState) -> GraphState:
    """Calls the MCP server with the current graph state and updates the graph state with the response"""
    
    with open("config_mcp.json", "r") as f:
        config = json.load(f)
  
    client = MCPClient.from_dict(config)
    mcp_agent = MCPAgent(model, client=client, max_steps=50)
    
    
    messages = state["messages"]
    if len(messages) > 1:
        
        conversation_history = "\n".join([
            f"{'User' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}"
            for msg in messages
        ])
        query = (
            "Here is our conversation so far:\n"
            f"{conversation_history}\n\n"
            "Please respond to the latest User message above, considering the full conversation context."
        )
    else:
        
        query = messages[-1].content
    
    response_content = await mcp_agent.run(query)
    summary_prompt = [SystemMessage(content="""
    You are a clinical decision support assistant.

    Based on the retrieved medical literature below:

    1. Provide a concise summary.
    2. Offer clinical interpretation.
    3. Mention possible causes.
    4. Suggest next steps (non-diagnostic).
    5. Include a disclaimer that this is not medical advice.
    """),
    HumanMessage(content=f"""
            User Query:
            {query}
            Retrieved Medical Literature:
            {response_content}
            Now provide your structured clinical perspective.
    """)]

    llm_response = model.invoke(summary_prompt)
    final_output = f"""
    {response_content}

    {llm_response.content}
    """
    
    return {"messages": [AIMessage(content=str(final_output))]}


graph = StateGraph(GraphState)
graph.add_node("mcp_call", mcp_call)
checkpointer = InMemorySaver()  

graph.set_entry_point("mcp_call")
graph.set_finish_point("mcp_call") 

app = graph.compile(checkpointer=checkpointer)

# Persistent event loop — reused across calls so the checkpointer state survives
_loop = asyncio.new_event_loop()

def get_response(query: str, user_id: str = "1") -> str:
    """Interface for app.py to get a response from the agent."""
    config = {"configurable": {"thread_id": str(user_id)}, "recursion_limit": 50}
    input_state = {"messages": [HumanMessage(content=query)]}
    
    try:
        result = _loop.run_until_complete(app.ainvoke(input_state, config))
        return result["messages"][-1].content
    except Exception as e:
        return f"Error in agent: {e}"

if __name__ == "__main__":
    while True:
        print("\n--- AI Medical Agent ---")
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        
        print("Agent:", get_response(user_input))


        print("GROQ KEY =", GROQ_API_KEY[:15] if GROQ_API_KEY else "NOT FOUND")