async def extract_hotel_data(kernel, hotel_name, search_results=None):
    """
    Extract hotel data using the ExtractionAgent plugin
    
    Args:
        kernel: The semantic kernel instance
        hotel_name: Name of the hotel to extract data for
        search_results: Optional search results from Azure AI Search
        
    Returns:
        A JSON string containing the extracted hotel data
    """
    # Get the extraction plugin
    extraction_plugin = kernel.plugins.get("ExtractionAgent")
    extraction_function = extraction_plugin.functions["ExtractHotelData"]
    
    # Prepare the context with available information
    context_variables = kernel.create_new_context()
    context_variables["hotelName"] = hotel_name
    
    if search_results:
        context_variables["searchResults"] = str(search_results)
        context_variables["dataSource"] = "azure_search"
    else:
        context_variables["dataSource"] = "generated"
    
    # Run the semantic function
    result = await kernel.invoke(extraction_function, variables=context_variables)
    return str(result)
