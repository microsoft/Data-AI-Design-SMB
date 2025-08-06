# sk_planner.py
import os
import json
import httpx
import asyncio
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai import PromptExecutionSettings

from dotenv import load_dotenv
load_dotenv()

from semantic_kernel.functions.kernel_function_decorator import kernel_function
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient

# --- Configuration for Azure Services ---
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_BRAND_FIELDS = os.getenv("AZURE_SEARCH_BRAND_FIELDS", "brand")
AZURE_SEARCH_CITY_FIELD = os.getenv("AZURE_SEARCH_CITY_FIELD")
AZURE_SEARCH_STATE_FIELD = os.getenv("AZURE_SEARCH_STATE_FIELD")
AZURE_SEARCH_HOTEL_NAME_FIELD = os.getenv("AZURE_SEARCH_HOTEL_NAME_FIELD", "name")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
BING_SEARCH_API_KEY = os.getenv("BING_SEARCH_API_KEY")


# --- Semantic Kernel Setup ---

kernel = sk.Kernel()
service_id = "chat_completion"

if all([AZURE_OPENAI_CHAT_DEPLOYMENT_NAME, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY]):
    kernel.add_service(
        AzureChatCompletion(
            service_id=service_id,
            deployment_name=AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
            endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
        ),
    )
else:
    print("WARNING: Azure OpenAI environment variables not set. Kernel service not added.")


# Function to estimate tokens (simple approach without tiktoken)
def estimate_tokens(text):
    """Estimate the number of tokens in a text string"""
    # Rough estimate: 1 token is approximately 4 characters for English text
    return len(text) // 4


# --- Agent Implementations as Semantic Kernel Plugins ---

class WebLookupAgent:
    @kernel_function(name="getHotelInfoFromWeb")
    async def get_hotel_info_from_web(self, hotel_name: str, location: str) -> str:
        print(f"INFO: [Web Lookup] Getting geo data for: {hotel_name}")
        query = f"{hotel_name}, {location}"
        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
        headers = {'User-Agent': 'SemanticKernelHotelApp/1.0'}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                if data:
                    return json.dumps({
                        "name": hotel_name,
                        "latitude": float(data[0]["lat"]),
                        "longitude": float(data[0]["lon"]),
                        "address": data[0].get("display_name", "Address not found")
                    })
                return "Error: Could not find geo data."
        except Exception as e:
            return f"Error: {e}"

class ConfidenceAgent:
    @kernel_function(name="generateConfidenceScore")
    def generate_confidence_score(self, discrepancies: str) -> str:
        print(f"INFO: [Confidence Agent] Generating score based on: {discrepancies}")
        
        # Analyze the discrepancies and provide detailed reasoning
        score = 0.98
        human_review_needed = False
        reasoning = []
        
        if discrepancies and "No existing record" not in discrepancies and "None" not in discrepancies:
            score = 0.85
            human_review_needed = True
            reasoning.append("Data discrepancies found between database and web sources")
            
            # Check for specific types of discrepancies
            if "address" in discrepancies.lower():
                reasoning.append("Address differences detected - may require verification")
            if "phone" in discrepancies.lower() or "telephone" in discrepancies.lower():
                reasoning.append("Phone number discrepancy - contact information may be outdated")
            if "name" in discrepancies.lower():
                reasoning.append("Hotel name mismatch - could indicate rebranding or data error")
            if "coordinates" in discrepancies.lower() or "location" in discrepancies.lower():
                reasoning.append("Geographic coordinate differences - location accuracy affected")
                
        elif "No existing record" in discrepancies:
            score = 0.75
            human_review_needed = True
            reasoning.append("No existing database record found - relying solely on web data")
            reasoning.append("Higher validation risk due to lack of historical data")
        elif "None" in discrepancies or not discrepancies or discrepancies.strip() == "":
            reasoning.append("No discrepancies found - data is consistent across sources")
            reasoning.append("High confidence based on matching information")
        
        # Provide recommendation based on score
        if score >= 0.95:
            recommendation = "Data is highly reliable and can be used immediately"
        elif score >= 0.85:
            recommendation = "Data is generally reliable but should be reviewed before use"
        elif score >= 0.75:
            recommendation = "Data requires verification and manual review before use"
        else:
            recommendation = "Data quality is poor - extensive review required"
        
        return json.dumps({
            "confidence_score": score,
            "human_review_needed": human_review_needed,
            "confidence_reasoning": reasoning,
            "recommendation": recommendation
        })

kernel.add_plugin(WebLookupAgent(), "WebLookupAgent")
kernel.add_plugin(ConfidenceAgent(), "ConfidenceAgent")

# --- Main Workflow Functions ---

async def search_accounts_in_db(query: str):
    """Directly searches the Azure AI Search index."""
    print(f"INFO: [Direct Search] Searching for: '{query}'")
    if not all([AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_INDEX_NAME, AZURE_SEARCH_KEY]):
        return {"error": "Azure Search not configured."}
    
    search_results = []
    try:
        search_client = SearchClient(endpoint=AZURE_SEARCH_ENDPOINT, index_name=AZURE_SEARCH_INDEX_NAME, credential=AzureKeyCredential(AZURE_SEARCH_KEY))
        async with search_client:
            results = await search_client.search(search_text=query, top=1)
            async for result in results:
                result.pop("@search.score", None)
                result.pop("@search.reranker_score", None)
                search_results.append(result)
        print(f"INFO: [Direct Search] Found {len(search_results)} results.")
        return search_results
    except Exception as e:
        print(f"ERROR: [Direct Search] Failed to query Azure AI Search: {e}")
        return {"error": str(e)}

async def find_hotels_in_db(company: str, location: str):
    """Helper function to query Azure AI Search for hotels."""
    print(f"INFO: [DB Search] Finding all '{company}' hotels in '{location}'")
    if not all([AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_INDEX_NAME, AZURE_SEARCH_KEY]):
        print("WARN: [DB Search] Azure Search not configured.")
        return []
    
    hotels = []
    try:
        search_client = SearchClient(endpoint=AZURE_SEARCH_ENDPOINT, index_name=AZURE_SEARCH_INDEX_NAME, credential=AzureKeyCredential(AZURE_SEARCH_KEY))
        async with search_client:
            
            # Convert company to uppercase for matching (as seen in debug output)
            company_upper = company.upper()
            
            # Build brand filter - try both original and uppercase versions
            brand_fields = [field.strip() for field in AZURE_SEARCH_BRAND_FIELDS.split(',')]
            brand_filter_parts = []
            
            for field in brand_fields:
                # For chainId, use company name directly (e.g., "Hilton" -> "HILTON")
                if field.lower() == 'chainid':
                    brand_filter_parts.append(f"{field} eq '{company_upper}'")
                else:
                    # For brandId, we need to search more flexibly as it may be different
                    # Use contains approach via search.ismatch for brandId
                    brand_filter_parts.append(f"search.ismatch('{company}', '{field}')")
            
            # Try the filter approach first
            if len(brand_filter_parts) > 1:
                brand_expression = f"({ ' or '.join(brand_filter_parts) })"
            else:
                brand_expression = brand_filter_parts[0]
            
            filter_parts = [brand_expression]
            search_query = "*"

            # Handle location filtering
            location_parts = [part.strip() for part in location.split(',')]
            
            if len(location_parts) == 2:
                city, state = location_parts[0], location_parts[1]
                if AZURE_SEARCH_CITY_FIELD:
                    filter_parts.append(f"{AZURE_SEARCH_CITY_FIELD} eq '{city}'")
                if AZURE_SEARCH_STATE_FIELD:
                    filter_parts.append(f"{AZURE_SEARCH_STATE_FIELD} eq '{state}'")
            elif len(location_parts) == 1:
                single_location = location_parts[0]
                if len(single_location) == 2 and AZURE_SEARCH_STATE_FIELD:
                     filter_parts.append(f"{AZURE_SEARCH_STATE_FIELD} eq '{single_location}'")
                elif AZURE_SEARCH_CITY_FIELD:
                     filter_parts.append(f"{AZURE_SEARCH_CITY_FIELD} eq '{single_location}'")
                else:
                    search_query = location

            filter_expression = " and ".join(filter_parts)
            
            print(f"INFO: [DB Search] Using search query: '{search_query}' and filter: '{filter_expression}'")
            
            try:
                results = await search_client.search(search_text=search_query, filter=filter_expression, top=50)
                async for result in results:
                    result.pop("@search.score", None)
                    result.pop("@search.reranker_score", None)
                    hotels.append(result)
                
                print(f"INFO: [DB Search] Found {len(hotels)} hotels with filtering.")
                
            except Exception as filter_error:
                print(f"WARN: [DB Search] Filter failed: {filter_error}")
                print("INFO: [DB Search] Falling back to text search approach...")
                
                # Fallback: Use text search with location filtering
                fallback_query = f"{company}"
                fallback_filter_parts = []
                
                if len(location_parts) == 2:
                    city, state = location_parts[0], location_parts[1]
                    if AZURE_SEARCH_CITY_FIELD:
                        fallback_filter_parts.append(f"{AZURE_SEARCH_CITY_FIELD} eq '{city}'")
                    if AZURE_SEARCH_STATE_FIELD:
                        fallback_filter_parts.append(f"{AZURE_SEARCH_STATE_FIELD} eq '{state}'")
                elif len(location_parts) == 1:
                    single_location = location_parts[0]
                    if len(single_location) == 2 and AZURE_SEARCH_STATE_FIELD:
                         fallback_filter_parts.append(f"{AZURE_SEARCH_STATE_FIELD} eq '{single_location}'")
                    elif AZURE_SEARCH_CITY_FIELD:
                         fallback_filter_parts.append(f"{AZURE_SEARCH_CITY_FIELD} eq '{single_location}'")
                
                fallback_filter = " and ".join(fallback_filter_parts) if fallback_filter_parts else None
                
                print(f"INFO: [DB Search] Fallback - Query: '{fallback_query}', Filter: '{fallback_filter}'")
                
                results = await search_client.search(
                    search_text=fallback_query, 
                    filter=fallback_filter,
                    top=50
                )
                
                async for result in results:
                    result.pop("@search.score", None)
                    result.pop("@search.reranker_score", None)
                    
                    # Additional filtering to ensure we match the company
                    chain_id = result.get('chainId', '').upper()
                    brand_id = result.get('brandId', '').upper()
                    
                    if (company_upper in chain_id or 
                        company_upper in brand_id or 
                        company.upper() in chain_id or 
                        company.upper() in brand_id):
                        hotels.append(result)
                
                print(f"INFO: [DB Search] Fallback found {len(hotels)} hotels.")
        
        return hotels
        
    except Exception as e:
        print(f"ERROR: [DB Search] Failed to query Azure AI Search: {e}")
        print(f"ERROR: [DB Search] Full exception details: {type(e).__name__}: {str(e)}")
        return []

async def process_single_hotel(hotel_from_db: dict, location: str):
    """Uses an agent to process one hotel."""
    hotel_name = hotel_from_db.get(AZURE_SEARCH_HOTEL_NAME_FIELD)
    if not hotel_name:
        print(f"WARNING: Hotel name field '{AZURE_SEARCH_HOTEL_NAME_FIELD}' not found in search result. Full record: {hotel_from_db}")
        hotel_name = "Unknown Hotel (Check Logs)"

    # Generate a more reliable task ID
    task_id = f"{hotel_from_db.get('id', '')}"
    if not task_id or task_id == "":
        # Fallback: use hotel name and location as ID
        task_id = f"{hotel_name}_{location}".replace(" ", "_").lower()
    
    print(f"--- Processing single hotel: {hotel_name} (Task ID: {task_id}) ---")

    agent = ChatCompletionAgent(
        kernel=kernel,
        instructions="""You are an AI assistant that validates and enriches a single hotel record.
        You have tools to get fresh data from the web and generate a confidence score.
        Your final task is to create a consolidated JSON report for this one hotel.
        
        Transformation Rules:
        - The user will provide you with the existing database record for a hotel.
        - Your first step is to get fresh information from the web.
        - Then, compare the fresh web data to the provided database record. List any differences in a 'data_discrepancies' field.
        - Create a 'clean_record' field that contains the most accurate and up-to-date information, preferring web data.
        - Use your web search capabilities (grounding) to infer details like brand, chain, room counts, etc., for the 'clean_record'.
        - Use the 'data_discrepancies' result to generate a confidence score.
        - Ensure your final response is ONLY the JSON object.
        """
    )
    
    prompt = f"""
    Please process the hotel named '{hotel_name}' in '{location}'.
    The existing database record is: {json.dumps(hotel_from_db)}
    
    Follow this plan:
    1. Use the `WebLookupAgent_getHotelInfoFromWeb` tool to get the latest address and geo-coordinates.
    2. Compare the result from step 1 with the provided database record. Also use your grounded web search to find other details. Create a summary of any differences found. Let's call this 'discrepancy_summary'.
    3. Use the `ConfidenceAgent_generateConfidenceScore` tool with the 'discrepancy_summary' as input.
    4. Finally, produce a single JSON object that contains the 'clean_record', the 'discrepancy_summary', and the confidence score information.
    """

    settings = PromptExecutionSettings(service_id=service_id)
    if BING_SEARCH_API_KEY:
        settings.extension_data["data_sources"] = [{"type": "BingSearch", "parameters": {"key": BING_SEARCH_API_KEY}}]
    
    final_answer = ""
    token_usage = {"input_tokens": 0, "output_tokens": 0}
    
    # Estimate the input tokens
    input_tokens = estimate_tokens(prompt)
    token_usage["input_tokens"] = input_tokens
    
    try:
        async for message in agent.invoke(prompt, settings=settings):
            if message.content:
                content = str(message.content)
                final_answer += content
                # Estimate tokens in each message response
                estimated_tokens = estimate_tokens(content)
                token_usage["output_tokens"] += estimated_tokens
                print(f"INFO: Estimated output tokens for content: {estimated_tokens}")
            
            # Also try to extract token usage from metadata if available
            try:
                if hasattr(message, 'metadata') and message.metadata:
                    usage = message.metadata.get('usage', {})
                    if usage:
                        # If available from the API, use these counts instead
                        if 'prompt_tokens' in usage:
                            token_usage["input_tokens"] = usage.get('prompt_tokens', 0)
                            print(f"INFO: Got input tokens from metadata: {usage.get('prompt_tokens', 0)}")
                        if 'completion_tokens' in usage:
                            token_usage["output_tokens"] = usage.get('completion_tokens', 0)
                            print(f"INFO: Got output tokens from metadata: {usage.get('completion_tokens', 0)}")
            except Exception as usage_error:
                # Silently ignore errors in token extraction
                print(f"INFO: Could not extract token usage from metadata: {usage_error}")
        
        print(f"INFO: Final token usage before adding to result: {token_usage}")
        
        if "```json" in final_answer:
            final_json_str = final_answer.split("```json\n")[1].split("\n```")[0]
        else:
            start_index = final_answer.find('{')
            end_index = final_answer.rfind('}')
            final_json_str = final_answer[start_index:end_index+1] if start_index != -1 and end_index != -1 else final_answer
        
        result = json.loads(final_json_str)
        # Add token usage to the result
        print(f"INFO: Adding token usage to result: {token_usage}")
        result["token_usage"] = {
            "input_tokens": token_usage["input_tokens"],
            "output_tokens": token_usage["output_tokens"]
        }
        
        # Save the agent result
        save_success = await save_agent_result(task_id=task_id, 
                         agent_name="PlannerAgent", 
                         result=result)
        
        if not save_success:
            print(f"WARNING: Failed to save result for {hotel_name}, but will return result anyway")
        
        return result

    except Exception as e:
        print(f"ERROR: Agent invocation failed for {hotel_name}. Error: {e}")
        print(f"INFO: Token usage at time of error: {token_usage}")
        error_result = {
            "error": f"Failed to process {hotel_name}", 
            "details": str(e),
            "token_usage": {
                "input_tokens": token_usage["input_tokens"],
                "output_tokens": token_usage["output_tokens"]
            }
        }
        
        # Save the error result
        save_success = await save_agent_result(task_id=task_id, 
                         agent_name="PlannerAgent", 
                         result=error_result)
        
        if not save_success:
            print(f"WARNING: Failed to save error result for {hotel_name}")
                         
        return error_result


# Function to save agent results
async def save_agent_result(task_id, agent_name, result):
    """Save agent processing results to the backend API"""
    try:
        # Check if token_usage exists in the result
        if isinstance(result, dict) and "token_usage" in result:
            print(f"INFO: Result includes token_usage: {result['token_usage']}")
        else:
            print(f"WARNING: Result does not include token_usage")
            
        # Use the app.py server endpoint instead of main.py
        url = f"http://localhost:5000/api/agent-results/{task_id}"
        payload = {
            "agent_name": agent_name,
            "result": result
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                print(f"ERROR: Failed to save agent result. Status: {response.status_code}, Response: {response.text}")
                return False
            print(f"INFO: Successfully saved result for task {task_id}, agent {agent_name}")
            return True
                
    except Exception as e:
        print(f"ERROR: Exception while saving agent result: {e}")
        return False


async def run_batch_workflow(data: dict):
    """Orchestrates the batch agent workflow."""
    if not kernel.get_service(service_id):
        raise ConnectionError("Azure OpenAI service is not configured.")

    companies = data.get("companies", [])
    location = data.get("location")
    if not all([companies, location]):
        return {"error": "Missing companies or location."}

    # 1. Find all hotels for the selected brands in the DB
    all_hotels_to_process = []
    for company in companies:
        hotels = await find_hotels_in_db(company, location)
        all_hotels_to_process.extend(hotels)

    if not all_hotels_to_process:
        print(f"INFO: No hotels found for companies {companies} in location {location}")
        # Create a special result to indicate no hotels were found
        special_task_id = "no_hotels_found"
        error_message = f"No hotels found for {', '.join(companies)} in {location}"
        
        await save_agent_result(
            task_id=special_task_id, 
            agent_name="PlannerAgent", 
            result={"error": error_message}
        )
        
        return [{"error": error_message}]

    # 2. Create a processing task for each hotel
    tasks = [process_single_hotel(hotel, location) for hotel in all_hotels_to_process]
    
    # 3. Run all tasks concurrently
    results = await asyncio.gather(*tasks)
    
    return results
