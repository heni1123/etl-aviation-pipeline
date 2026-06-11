import os
import pytest
import httpx
from unittest.mock import patch

@pytest.fixture
def mock_api_response():
    return [
        {
            "name": {"common": "United States", "official": "United States of America"},
            "capital": ["Washington, D.C."],
            "population": 331002651,
            "area": 9372610,
            "region": "Americas",
            "subregion": "North America",
            "languages": {"eng": "English"},
            "currencies": {"USD": {"name": "United States dollar", "symbol": "$"}},
        },
        {
            "name": {"common": "Canada", "official": "Canada"},
            "capital": ["Ottawa"],
            "population": 37742154,
            "area": 9984670,
            "region": "Americas",
            "subregion": "North America",
            "languages": {"eng": "English", "fra": "French"},
            "currencies": {"CAD": {"name": "Canadian dollar", "symbol": "$"}},
        },
    ]

@pytest.mark.asyncio
async def test_api_response(mock_api_response):
    with patch('httpx.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_api_response
        
        response = await httpx.get("https://restcountries.com/v3.1/all")
        assert response.status_code == 200
        assert len(response.json()) == 2

@pytest.mark.asyncio
async def test_data_transformation(mock_api_response):
    transformed_data = [
        {
            "country_name": country["name"]["common"],
            "capital_city": country["capital"][0],
            "population": country["population"],
            "area": country["area"],
            "region": country["region"],
            "subregion": country["subregion"],
            "primary_language": list(country["languages"].values())[0],
            "currency_name": list(country["currencies"].values())[0]["name"],
            "currency_symbol": list(country["currencies"].values())[0]["symbol"],
        }
        for country in mock_api_response
    ]
    
    assert len(transformed_data) == 2
    assert transformed_data[0]["country_name"] == "United States"
    assert transformed_data[1]["capital_city"] == "Ottawa"
    assert transformed_data[0]["population"] == 331002651

@pytest.mark.asyncio
async def test_integration_flow(mock_api_response):
    with patch('httpx.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_api_response
        
        response = await httpx.get("https://restcountries.com/v3.1/all")
        assert response.status_code == 200
        
        transformed_data = [
            {
                "country_name": country["name"]["common"],
                "capital_city": country["capital"][0],
                "population": country["population"],
                "area": country["area"],
                "region": country["region"],
                "subregion": country["subregion"],
                "primary_language": list(country["languages"].values())[0],
                "currency_name": list(country["currencies"].values())[0]["name"],
                "currency_symbol": list(country["currencies"].values())[0]["symbol"],
            }
            for country in response.json()
        ]
        
        assert len(transformed_data) == 2

@pytest.mark.asyncio
async def test_data_validation(mock_api_response):
    for country in mock_api_response:
        assert isinstance(country["name"]["common"], str)
        assert isinstance(country["capital"], list)
        assert isinstance(country["population"], int)
        assert isinstance(country["area"], int)
        assert isinstance(country["region"], str)
        assert isinstance(country["subregion"], str)
        assert isinstance(country["languages"], dict)
        assert isinstance(country["currencies"], dict)

@pytest.mark.asyncio
async def test_load_performance(mock_api_response):
    import time
    start_time = time.time()
    
    for _ in range(1000):  # Simulate loading data multiple times
        transformed_data = [
            {
                "country_name": country["name"]["common"],
                "capital_city": country["capital"][0],
                "population": country["population"],
                "area": country["area"],
                "region": country["region"],
                "subregion": country["subregion"],
                "primary_language": list(country["languages"].values())[0],
                "currency_name": list(country["currencies"].values())[0]["name"],
                "currency_symbol": list(country["currencies"].values())[0]["symbol"],
            }
            for country in mock_api_response
        ]
    
    end_time = time.time()
    assert (end_time - start_time) < 2  # Ensure it runs within 2 seconds for 1000 iterations