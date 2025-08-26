# LangChain / LangGraph imports (ajusta si usas wrappers distintos)
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

# OpenAI
from openai import AsyncOpenAI

# Json
import json

# Pydantic
from pydantic import ValidationError

from core import SETTINGS
from db import get_db_client
from models import QueryModel, ResponseModel


TAVILY_TOOL = TavilySearch(max_results=SETTINGS.max_result_tavily, tavily_api_key=SETTINGS.tavily_key.get_secret_value())

@tool('retrieval_vector_db')
async def retrieval_vector_db(query : str):
    """Queries the vector database. Retrieves the n closest papers (titles, abstracts, and group).
    
    Args:
        query (str): query
    Returns:
        list
    """
    
    # OpenAI
    openai_client = AsyncOpenAI(api_key=SETTINGS.openai_key.get_secret_value())

    # Supabase
    supabase_client = await get_db_client()

    embedding_response = await openai_client.embeddings.create(
        model=SETTINGS.embedding_model,
        input=query
        )
    
    query_embedding = embedding_response.data[0].embedding
    
    response = await supabase_client.rpc("match_documents",
                              {
                                  "query_embedding": query_embedding,
                                  "match_threshold": SETTINGS.threshold,
                                  "match_count": SETTINGS.max_result_rag
                                  }).execute()
    return response.data

class AgentService:
    
    LLM = ChatOpenAI(model=SETTINGS.model, temperature=0, api_key=SETTINGS.openai_key.get_secret_value())
    
    PARSER = PydanticOutputParser(pydantic_object=ResponseModel)
    
    SYSTEM_TEMPLATE = """You are a scientific paper classifier.
    
    Your goal: classify the paper into one of these categories:
    - Cardiovascular
    - Neurological
    - Hepatorenal
    - Oncological
    
    {tools} {tool_names}
    
    You MUST use both tools to answer the question. 
    Never provide a final answer without invoking a tool.
    Note: It would be ideal if you could pass the ‘abstract’ as an input to ‘retrieval_vector_db’.
    
    Always reason step by step in the following format:
    
    Thought: describe what you are thinking
    Action: the tool name to use
    Action Input: the input for that tool
    Observation: the result of the tool
    
    Repeat Thought/Action/Observation as needed.
    
    When you are confident, stop and return the final result in EXACT JSON format:
    
    Final Answer:
    {{
        "category": "<one of the categories>",
        "confidence": <float between 0 and 1>,
        "rationale": "<short explanation>"
    }}
    
    DO NOT add 'Thought:' or 'Action:' after the Final Answer.
    
    {format_instructions}
    
    DO NOT ENCLOSE the result in triple `
    
    Paper:
    Title: {title}
    Abstract: {abstract}
    
    {agent_scratchpad}"""

    PROMPT = PromptTemplate(
        template=SYSTEM_TEMPLATE,
        input_variables=list(QueryModel.model_fields.keys()),
        partial_variables={"format_instructions": PARSER.get_format_instructions()}
        )

    TOOLS = [TAVILY_TOOL, retrieval_vector_db]


    @classmethod
    async def classify(cls, query : QueryModel) -> ResponseModel:
        
        agent = create_react_agent(
            AgentService.LLM,
            tools=AgentService.TOOLS,
            prompt=AgentService.PROMPT
        )
        
        agent_executor = AgentExecutor(agent=agent, tools=AgentService.TOOLS, verbose=True, max_iterations=10)
        
        response = await agent_executor.ainvoke(query.model_dump())
        
        raw_output = response.get("output")
        
        # Si el modelo devolvió un string con JSON, lo parseamos
        if isinstance(raw_output, str):
            try:
                raw_output = json.loads(raw_output)
            except json.JSONDecodeError as e:
                raise ValueError(f"❌ El modelo devolvió un JSON inválido:\n{raw_output}") from e

        try:
            return ResponseModel.model_validate(raw_output)
        except ValidationError as e:
            raise ValueError(f"❌ Error validando contra ResponseModel:\n{e}") from e