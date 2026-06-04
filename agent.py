from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama.llms import OllamaLLM
from langchain_core.messages import HumanMessage, AIMessage

# Define the State of our Agentic Graph
class GraphState(TypedDict):
    question: str
    chat_history: List[dict]
    documents: str
    generation: str
    needs_rewrite: bool
    retries: int

llm = OllamaLLM(model="llama3.2")

# --- NODE: Retrieve ---
def retrieve_node(state: GraphState, retriever):
    print("---RETRIEVING DOCUMENTS---")
    docs = retriever.invoke(state["question"])
    context = "\n\n".join([doc.page_content for doc in docs])
    return {"documents": context}

# --- NODE: Grade Relevance ---
def grade_documents_node(state: GraphState):
    print("---GRADING DOCUMENT RELEVANCE---")
    # A simple prompt to act as an evaluator agent
    grader_prompt = ChatPromptTemplate.from_template(
        "You are a strict grader. Does the following context contain information relevant to the question? "
        "Answer ONLY with 'yes' or 'no'.\n\nContext: {context}\n\nQuestion: {question}"
    )
    chain = grader_prompt | llm
    result = chain.invoke({"context": state["documents"], "question": state["question"]})
    
    needs_rewrite = "no" in result.lower()
    return {"needs_rewrite": needs_rewrite}

# --- NODE: Rewrite Query ---
def rewrite_query_node(state: GraphState):
    print("---REWRITING QUERY---")
    rewrite_prompt = ChatPromptTemplate.from_template(
        "Look at the original question and formulate a better, more optimized search query "
        "to find the answer in a vector database.\nOriginal: {question}\nOptimized:"
    )
    chain = rewrite_prompt | llm
    better_question = chain.invoke({"question": state["question"]})
    
    return {"question": better_question, "retries": state.get("retries", 0) + 1}

# --- NODE: Generate ---
def generate_node(state: GraphState):
    print("---GENERATING ANSWER WITH MEMORY---")
    
    # UPGRADE: Added MessagesPlaceholder to inject conversational memory
    generate_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert research assistant. Use the context to answer the question."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "Context: {context}\n\nQuestion: {question}")
    ])
    
    # Format the raw dictionary history into LangChain message objects
    formatted_history = []
    for msg in state.get("chat_history", []):
        if msg["role"] == "user":
            formatted_history.append(HumanMessage(content=msg["content"]))
        else:
            formatted_history.append(AIMessage(content=msg["content"]))

    chain = generate_prompt | llm
    answer = chain.invoke({
        "context": state["documents"], 
        "question": state["question"],
        "chat_history": formatted_history
    })
    
    return {"generation": answer}

# --- EDGE: Routing Logic ---
def decide_to_generate(state: GraphState):
    if state["needs_rewrite"] and state.get("retries", 0) < 2:
        return "rewrite"
    return "generate"

# --- COMPILE THE GRAPH ---
def build_rag_agent(retriever):
    workflow = StateGraph(GraphState)
    
    # Add Nodes
    workflow.add_node("retrieve", lambda state: retrieve_node(state, retriever))
    workflow.add_node("grade", grade_documents_node)
    workflow.add_node("rewrite", rewrite_query_node)
    workflow.add_node("generate", generate_node)
    
    # Add Edges
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "grade")
    workflow.add_conditional_edges(
        "grade",
        decide_to_generate,
        {
            "rewrite": "rewrite",
            "generate": "generate"
        }
    )
    workflow.add_edge("rewrite", "retrieve") # Loop back after rewriting
    workflow.add_edge("generate", END)
    
    return workflow.compile()