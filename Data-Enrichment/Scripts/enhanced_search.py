#!/usr/bin/env python3
"""
Enhanced Azure AI Search helper with better error handling and debugging.
"""
import os
import asyncio
from typing import List, Dict, Any, Optional
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import SearchMode

class AzureSearchHelper:
    """Enhanced Azure AI Search helper class."""
    
    def __init__(self, endpoint: str, index_name: str, api_key: str):
        self.endpoint = endpoint
        self.index_name = index_name
        self.api_key = api_key
        self.search_client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(api_key)
        )
    
    async def search_hotels_by_brand_and_location(
        self, 
        brand_name: str, 
        location: str,
        brand_fields: List[str] = None,
        city_field: str = "city",
        state_field: str = "state",
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search for hotels by brand and location with robust error handling.
        
        Args:
            brand_name: Hotel brand/chain name (e.g., "Hilton", "Marriott")
            location: Location string (e.g., "New York, NY" or "CA")
            brand_fields: List of fields to search for brand (default: ["chainId", "brandId"])
            city_field: Field name for city
            state_field: Field name for state  
            max_results: Maximum number of results to return
            
        Returns:
            List of hotel documents
        """
        if brand_fields is None:
            brand_fields = ["chainId", "brandId"]
        
        hotels = []
        
        try:
            async with self.search_client:
                # Strategy 1: Try exact filtering first
                hotels = await self._try_exact_filtering(
                    brand_name, location, brand_fields, city_field, state_field, max_results
                )
                
                # Strategy 2: If exact filtering fails, try text search with location filter
                if not hotels:
                    print(f"INFO: Exact filtering returned no results, trying text search...")
                    hotels = await self._try_text_search_with_location_filter(
                        brand_name, location, city_field, state_field, max_results
                    )
                
                # Strategy 3: If still no results, try pure text search
                if not hotels:
                    print(f"INFO: Text search with location filter returned no results, trying pure text search...")
                    hotels = await self._try_pure_text_search(
                        brand_name, location, brand_fields, max_results
                    )
        
        except Exception as e:
            print(f"ERROR: Search failed: {e}")
            return []
        
        return hotels
    
    async def _try_exact_filtering(
        self, 
        brand_name: str, 
        location: str, 
        brand_fields: List[str],
        city_field: str,
        state_field: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Try exact OData filtering approach."""
        try:
            # Build brand filter with case variations
            brand_filter_parts = []
            brand_upper = brand_name.upper()
            
            for field in brand_fields:
                if field.lower() == 'chainid':
                    # Chain IDs are typically uppercase
                    brand_filter_parts.append(f"{field} eq '{brand_upper}'")
                else:
                    # Use search.ismatch for more flexible matching on other fields
                    brand_filter_parts.append(f"search.ismatch('{brand_name}', '{field}')")
            
            brand_expression = " or ".join(brand_filter_parts)
            if len(brand_filter_parts) > 1:
                brand_expression = f"({brand_expression})"
            
            # Build location filter
            location_filter = self._build_location_filter(location, city_field, state_field)
            
            # Combine filters
            filter_parts = [brand_expression]
            if location_filter:
                filter_parts.append(location_filter)
            
            filter_expression = " and ".join(filter_parts)
            
            print(f"INFO: Trying exact filter: {filter_expression}")
            
            results = await self.search_client.search(
                search_text="*",
                filter=filter_expression,
                top=max_results
            )
            
            hotels = []
            async for result in results:
                # Clean up search metadata
                result.pop("@search.score", None)
                result.pop("@search.reranker_score", None)
                result.pop("@search.highlights", None)
                result.pop("@search.captions", None)
                hotels.append(result)
            
            print(f"INFO: Exact filtering found {len(hotels)} hotels")
            return hotels
            
        except Exception as e:
            print(f"WARN: Exact filtering failed: {e}")
            return []
    
    async def _try_text_search_with_location_filter(
        self, 
        brand_name: str, 
        location: str,
        city_field: str,
        state_field: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Try text search with location filtering."""
        try:
            location_filter = self._build_location_filter(location, city_field, state_field)
            
            print(f"INFO: Trying text search for '{brand_name}' with location filter: {location_filter}")
            
            results = await self.search_client.search(
                search_text=brand_name,
                filter=location_filter,
                search_mode=SearchMode.Any,
                top=max_results
            )
            
            hotels = []
            async for result in results:
                # Additional filtering to ensure brand match
                if self._is_brand_match(result, brand_name):
                    result.pop("@search.score", None)
                    result.pop("@search.reranker_score", None)
                    result.pop("@search.highlights", None)
                    result.pop("@search.captions", None)
                    hotels.append(result)
            
            print(f"INFO: Text search with location filter found {len(hotels)} hotels")
            return hotels
            
        except Exception as e:
            print(f"WARN: Text search with location filter failed: {e}")
            return []
    
    async def _try_pure_text_search(
        self, 
        brand_name: str, 
        location: str,
        brand_fields: List[str],
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Try pure text search as last resort."""
        try:
            query = f"{brand_name} {location}"
            
            print(f"INFO: Trying pure text search for '{query}'")
            
            results = await self.search_client.search(
                search_text=query,
                search_mode=SearchMode.Any,
                top=max_results
            )
            
            hotels = []
            async for result in results:
                # Filter by brand and location
                if (self._is_brand_match(result, brand_name) and 
                    self._is_location_match(result, location)):
                    result.pop("@search.score", None)
                    result.pop("@search.reranker_score", None)
                    result.pop("@search.highlights", None)
                    result.pop("@search.captions", None)
                    hotels.append(result)
            
            print(f"INFO: Pure text search found {len(hotels)} hotels")
            return hotels
            
        except Exception as e:
            print(f"WARN: Pure text search failed: {e}")
            return []
    
    def _build_location_filter(self, location: str, city_field: str, state_field: str) -> Optional[str]:
        """Build location filter from location string."""
        if not location:
            return None
        
        location_parts = [part.strip() for part in location.split(',')]
        filter_parts = []
        
        if len(location_parts) == 2:
            # "New York, NY" format
            city, state = location_parts[0], location_parts[1]
            if city_field:
                filter_parts.append(f"{city_field} eq '{city}'")
            if state_field:
                filter_parts.append(f"{state_field} eq '{state}'")
        elif len(location_parts) == 1:
            single_location = location_parts[0]
            # If it's a 2-letter code, assume it's a state
            if len(single_location) == 2 and state_field:
                filter_parts.append(f"{state_field} eq '{single_location}'")
            # Otherwise, assume it's a city
            elif city_field:
                filter_parts.append(f"{city_field} eq '{single_location}'")
        
        return " and ".join(filter_parts) if filter_parts else None
    
    def _is_brand_match(self, hotel: Dict[str, Any], brand_name: str) -> bool:
        """Check if hotel matches the brand name."""
        brand_upper = brand_name.upper()
        
        # Check chainId
        chain_id = hotel.get('chainId', '').upper()
        if brand_upper in chain_id:
            return True
        
        # Check brandId
        brand_id = hotel.get('brandId', '').upper()
        if brand_upper in brand_id:
            return True
        
        # Check hotel name
        hotel_name = hotel.get('name', '').upper()
        if brand_upper in hotel_name:
            return True
        
        return False
    
    def _is_location_match(self, hotel: Dict[str, Any], location: str) -> bool:
        """Check if hotel matches the location."""
        location_upper = location.upper()
        
        # Check city
        city = hotel.get('city', '') or ''
        if city and city.upper() in location_upper:
            return True
        
        # Check state
        state = hotel.get('state', '') or ''
        if state and state.upper() in location_upper:
            return True
        
        return False

# Example usage function
async def enhanced_find_hotels_in_db(company: str, location: str) -> List[Dict[str, Any]]:
    """
    Enhanced hotel search function using the AzureSearchHelper class.
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get configuration from environment
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
    api_key = os.getenv("AZURE_SEARCH_KEY")
    brand_fields = os.getenv("AZURE_SEARCH_BRAND_FIELDS", "chainId,brandId").split(',')
    city_field = os.getenv("AZURE_SEARCH_CITY_FIELD", "city")
    state_field = os.getenv("AZURE_SEARCH_STATE_FIELD", "state")
    
    if not all([endpoint, index_name, api_key]):
        print("ERROR: Azure Search configuration missing")
        return []
    
    search_helper = AzureSearchHelper(endpoint, index_name, api_key)
    
    return await search_helper.search_hotels_by_brand_and_location(
        brand_name=company,
        location=location,
        brand_fields=[field.strip() for field in brand_fields],
        city_field=city_field,
        state_field=state_field,
        max_results=100
    )

if __name__ == "__main__":
    # Test the enhanced search
    async def test_enhanced_search():
        print("Testing enhanced search...")
        
        test_cases = [
            ("Hilton", "New York, NY"),
            ("Marriott", "CA"),
            ("Wyndham", "PA"),
            ("NonExistentBrand", "NY")
        ]
        
        for brand, location in test_cases:
            print(f"\n=== Testing {brand} in {location} ===")
            results = await enhanced_find_hotels_in_db(brand, location)
            print(f"Found {len(results)} hotels")
            
            if results:
                for hotel in results[:2]:  # Show first 2
                    print(f"- {hotel.get('name', 'Unknown')}: {hotel.get('city', 'Unknown')}, {hotel.get('state', 'Unknown')}")
    
    asyncio.run(test_enhanced_search())
