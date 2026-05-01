"""
LangGraph CRM Agent for AI-HCP CRM.
Orchestrates AI interactions using LangGraph workflow.
"""

from typing import TypedDict, Annotated, Sequence, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from sqlalchemy.orm import Session

from tools.log_interaction import create_log_interaction_tool
from tools.edit_interaction import create_edit_interaction_tool
from tools.summarize_interaction import create_summarize_interaction_tool
from tools.followup_recommendation import create_followup_recommendation_tool
from tools.hcp_history import create_hcp_history_tool
from services.groq_service import get_groq_service


# Define the state type for the agent
class AgentState(TypedDict):
    """
    State definition for the CRM agent.
    Tracks messages, extracted data, and action results.
    """
    messages: Annotated[Sequence[Dict[str, str]], "add_message"]
    extracted_data: Optional[Dict[str, Any]]
    action: Optional[str]
    tool_result: Optional[Dict[str, Any]]
    interaction_id: Optional[int]
    error: Optional[str]


def create_crm_agent(db: Session):
    """
    Create and configure the LangGraph CRM agent.
    
    Args:
        db: SQLAlchemy database session
        
    Returns:
        Compiled LangGraph agent
    """
    # Create tool instances
    log_tool = create_log_interaction_tool(db)
    edit_tool = create_edit_interaction_tool(db)
    summarize_tool = create_summarize_interaction_tool(db)
    followup_tool = create_followup_recommendation_tool(db)
    history_tool = create_hcp_history_tool(db)
    
    # Define tools for LangGraph
    tools = {
        "log_interaction": log_tool,
        "edit_interaction": edit_tool,
        "summarize_interaction": summarize_tool,
        "followup_recommendation": followup_tool,
        "hcp_history": history_tool
    }
    
    def should_log(state: AgentState) -> str:
        """
        Determine if the user wants to log a new interaction.
        
        Args:
            state: Current agent state
            
        Returns:
            Decision: "log" or "analyze"
        """
        messages = state.get("messages", [])
        if not messages:
            return "analyze"
        
        last_message = messages[-1].get("content", "").lower()
        
        # Keywords indicating logging intent
        log_keywords = [
            "log", "record", "save", "add new", "create interaction",
            "visit with", "met with", "talked to", "spoke with",
            "had a meeting", "had a call"
        ]
        
        for keyword in log_keywords:
            if keyword in last_message:
                return "log"
        
        return "analyze"
    
    def analyze_intent(state: AgentState) -> AgentState:
        """
        Analyze user intent using Groq LLM.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with action and extracted data
        """
        messages = state.get("messages", [])
        user_message = messages[-1].get("content", "") if messages else ""
        
        groq_service = get_groq_service()
        
        # System prompt for intent analysis
        system_prompt = """You are an AI CRM assistant. Analyze the user's message and determine what action they want to take.
        
Available actions:
- "log": User wants to log a new interaction with an HCP
- "edit": User wants to edit an existing interaction
- "summarize": User wants to get or generate a summary of an interaction
- "followup": User wants follow-up recommendations
- "history": User wants to see HCP interaction history
- "chat": General conversation or question

Return a JSON object with:
{
  "action": "action_name",
  "extracted_data": {...},
  "confidence": 0.0-1.0
}

If the user wants to log a new interaction, also extract the interaction details from their message."""
        
        result = groq_service.generate_response(system_prompt, user_message)
        
        if result.get("success"):
            try:
                import json
                analysis = json.loads(result["content"])
                return {
                    **state,
                    "action": analysis.get("action", "chat"),
                    "extracted_data": analysis.get("extracted_data", {})
                }
            except json.JSONDecodeError:
                return {**state, "action": "chat", "extracted_data": {}}
        
        return {**state, "action": "chat", "extracted_data": {}}
    
    def execute_tool(state: AgentState) -> AgentState:
        """
        Execute the appropriate tool based on analyzed intent.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with tool result
        """
        action = state.get("action", "chat")
        extracted_data = state.get("extracted_data", {})
        
        try:
            if action == "log":
                # Extract data from user message if not already extracted
                if not extracted_data.get("hcp_name"):
                    messages = state.get("messages", [])
                    user_message = messages[-1].get("content", "") if messages else ""
                    groq_service = get_groq_service()
                    result = groq_service.extract_interaction_data(user_message)
                    if result.get("success"):
                        extracted_data = result.get("data", {})
                
                # Execute log tool
                result = log_tool.execute(extracted_data)
                return {
                    **state,
                    "tool_result": result,
                    "interaction_id": result.get("interaction_id")
                }
            
            elif action == "edit":
                interaction_id = extracted_data.get("interaction_id")
                update_data = extracted_data.get("update_data", {})
                if interaction_id:
                    result = edit_tool.execute(interaction_id, update_data)
                    return {
                        **state,
                        "tool_result": result,
                        "interaction_id": interaction_id
                    }
                return {**state, "tool_result": {"success": False, "message": "No interaction ID provided"}}
            
            elif action == "summarize":
                interaction_id = extracted_data.get("interaction_id")
                if interaction_id:
                    result = summarize_tool.execute(interaction_id)
                    return {
                        **state,
                        "tool_result": result,
                        "interaction_id": interaction_id
                    }
                return {**state, "tool_result": {"success": False, "message": "No interaction ID provided"}}
            
            elif action == "followup":
                interaction_id = extracted_data.get("interaction_id")
                if interaction_id:
                    result = followup_tool.execute(interaction_id)
                    return {
                        **state,
                        "tool_result": result,
                        "interaction_id": interaction_id
                    }
                return {**state, "tool_result": {"success": False, "message": "No interaction ID provided"}}
            
            elif action == "history":
                hcp_name = extracted_data.get("hcp_name")
                if hcp_name:
                    result = history_tool.execute(hcp_name)
                    return {**state, "tool_result": result}
                return {**state, "tool_result": {"success": False, "message": "No HCP name provided"}}
            
            else:
                # Chat action - generate conversational response
                messages = state.get("messages", [])
                user_message = messages[-1].get("content", "") if messages else ""
                
                groq_service = get_groq_service()
                system_prompt = """You are a helpful AI CRM assistant for a pharmaceutical sales team.
You help representatives log interactions with healthcare professionals, 
answer questions about HCPs, and provide insights.
Be concise, professional, and helpful."""
                
                result = groq_service.generate_response(system_prompt, user_message)
                
                if result.get("success"):
                    return {
                        **state,
                        "tool_result": {
                            "success": True,
                            "message": result["content"]
                        }
                    }
                else:
                    return {
                        **state,
                        "tool_result": {
                            "success": False,
                            "message": "I'm sorry, I couldn't process that request."
                        }
                    }
        
        except Exception as e:
            return {
                **state,
                "tool_result": {
                    "success": False,
                    "message": f"Error executing tool: {str(e)}"
                },
                "error": str(e)
            }
    
    def format_response(state: AgentState) -> AgentState:
        """
        Format the tool result into a user-friendly response.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with formatted response
        """
        tool_result = state.get("tool_result", {})
        action = state.get("action", "chat")
        
        if not tool_result.get("success"):
            response = tool_result.get("message", "An error occurred.")
        else:
            if action == "log":
                interaction_id = state.get("interaction_id")
                response = f"✅ Interaction logged successfully! (ID: {interaction_id})\n\n"
                if tool_result.get("data"):
                    data = tool_result["data"]
                    response += f"HCP: {data.get('hcp_name', 'N/A')}\n"
                    response += f"Type: {data.get('interaction_type', 'N/A')}\n"
                    response += f"Sentiment: {data.get('sentiment', 'N/A')}\n"
                    if data.get("summary"):
                        response += f"\nSummary: {data['summary']}"
            
            elif action == "edit":
                response = f"✅ Interaction updated successfully!\n\n{tool_result.get('message', '')}"
            
            elif action == "summarize":
                summary = tool_result.get("summary", "No summary available.")
                response = f"📝 **Interaction Summary:**\n\n{summary}"
            
            elif action == "followup":
                recommendations = tool_result.get("recommendations", "No recommendations available.")
                response = f"📋 **Follow-Up Recommendations:**\n\n{recommendations}"
            
            elif action == "history":
                interactions = tool_result.get("interactions", [])
                hcp_name = tool_result.get("hcp_name", "HCP")
                total = tool_result.get("total_interactions", 0)
                
                response = f"📊 **History for {hcp_name}:**\n\n"
                response += f"Total interactions: {total}\n\n"
                
                if tool_result.get("ai_summary"):
                    response += f"**AI Summary:** {tool_result['ai_summary']}\n\n"
                
                if interactions:
                    response += "**Recent Interactions:**\n"
                    for i, interaction in enumerate(interactions[:5], 1):
                        response += f"{i}. {interaction.get('interaction_type', 'N/A')} - {interaction.get('created_at', 'N/A')}\n"
                        response += f"   Sentiment: {interaction.get('sentiment', 'N/A')}\n"
                else:
                    response += "No previous interactions found."
            
            else:
                response = tool_result.get("message", "I'm here to help with your HCP interactions.")
        
        # Add response to messages
        messages = list(state.get("messages", []))
        messages.append({"role": "assistant", "content": response})
        
        return {**state, "messages": messages}
    
    # Build the state graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("analyze", analyze_intent)
    workflow.add_node("execute", execute_tool)
    workflow.add_node("respond", format_response)
    
    # Set entry point
    workflow.set_entry_point("analyze")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "analyze",
        should_log,
        {
            "log": "execute",
            "analyze": "execute"
        }
    )
    
    # Connect nodes
    workflow.add_edge("execute", "respond")
    workflow.add_edge("respond", END)
    
    # Compile the agent
    return workflow.compile()


def process_chat_message(
    db: Session,
    user_message: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process a chat message through the CRM agent.
    
    Args:
        db: Database session
        user_message: User's message
        context: Optional context data
        
    Returns:
        Dictionary with response and metadata
    """
    # Create the agent
    agent = create_crm_agent(db)
    
    # Initialize state
    initial_state = {
        "messages": [{"role": "user", "content": user_message}],
        "extracted_data": context or {},
        "action": None,
        "tool_result": None,
        "interaction_id": None,
        "error": None
    }
    
    # Run the agent
    result = agent.invoke(initial_state)
    
    # Extract response
    messages = result.get("messages", [])
    response = messages[-1].get("content", "") if messages else "No response"
    
    return {
        "response": response,
        "action": result.get("action"),
        "interaction_id": result.get("interaction_id"),
        "extracted_data": result.get("extracted_data"),
        "tool_result": result.get("tool_result")
    }