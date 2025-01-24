import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime
import json
import os
from app import (
    get_random_quote,
    get_authors,
    search_quotes,
    load_saved_quotes,
    save_quote
)
import requests

# Test data
MOCK_QUOTE = {
    "_id": "123",
    "content": "Test quote content",
    "author": "Test Author"
}

MOCK_AUTHORS = {
    "count": 2,
    "results": [
        {"name": "Author 1"},
        {"name": "Author 2"}
    ]
}

MOCK_SEARCH_RESULTS = {
    "count": 2,
    "totalPages": 1,
    "results": [
        {
            "_id": "1",
            "content": "First test quote about experience",
            "author": "Author 1"
        },
        {
            "_id": "2",
            "content": "Second quote by same author",
            "author": "Author 1"
        }
    ]
}

@pytest.fixture
def mock_csv_file(tmp_path):
    """Create a temporary CSV file for testing"""
    df = pd.DataFrame({
        'quote': ['Test quote'],
        'author': ['Test Author'],
        'date_saved': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    })
    csv_path = tmp_path / "test_quotes.csv"
    df.to_csv(csv_path, index=False)
    return csv_path

@pytest.fixture
def mock_response():
    """Create a mock response object"""
    response = MagicMock()
    response.status_code = 200
    return response

def test_get_random_quote(mock_response):
    """Test getting a random quote"""
    mock_response.json.return_value = MOCK_QUOTE
    
    with patch('requests.get', return_value=mock_response):
        quote = get_random_quote()
        assert quote == MOCK_QUOTE
        assert quote['content'] == "Test quote content"
        assert quote['author'] == "Test Author"

def test_get_authors(mock_response):
    """Test getting authors list"""
    mock_response.json.return_value = MOCK_AUTHORS
    
    with patch('requests.get', return_value=mock_response):
        authors = get_authors()
        assert len(authors) == 2
        assert authors == ["Author 1", "Author 2"]

def test_search_quotes_content_filter(mock_response):
    """Test searching quotes with content filter"""
    mock_response.json.return_value = MOCK_SEARCH_RESULTS
    
    with patch('requests.get', return_value=mock_response):
        results = search_quotes(query="experience", author="All Authors")
        filtered_quotes = results['results']
        assert len(filtered_quotes) == 1
        assert all("experience" in quote['content'].lower() for quote in filtered_quotes)

def test_search_quotes_author_filter(mock_response):
    """Test searching quotes with author filter"""
    # Create specific mock data for author filter test
    author_results = {
        "count": 2,
        "totalPages": 1,
        "results": [
            {
                "_id": "1",
                "content": "Quote by Author 1",
                "author": "Author 1"
            },
            {
                "_id": "2",
                "content": "Another quote by Author 1",
                "author": "Author 1"
            }
        ]
    }
    
    mock_response.json.return_value = author_results
    
    with patch('requests.get', return_value=mock_response):
        results = search_quotes(author="Author 1")
        assert len(results['results']) <= 10
        assert len(results['results']) > 0  # Make sure we got some results
        assert all(quote['author'] == "Author 1" for quote in results['results'])

def test_load_saved_quotes(mock_csv_file):
    """Test loading saved quotes"""
    with patch('app.QUOTES_FILE', str(mock_csv_file)):
        df = load_saved_quotes()
        assert len(df) == 1
        assert df.iloc[0]['quote'] == 'Test quote'
        assert df.iloc[0]['author'] == 'Test Author'

def test_save_quote(mock_csv_file):
    """Test saving a new quote"""
    with patch('app.QUOTES_FILE', str(mock_csv_file)):
        result = save_quote("New quote", "New Author")
        assert result == True
        
        # Verify the quote was saved
        df = pd.read_csv(mock_csv_file)
        assert len(df) == 2
        assert df.iloc[1]['quote'] == 'New quote'
        assert df.iloc[1]['author'] == 'New Author'

def test_save_duplicate_quote(mock_csv_file):
    """Test saving a duplicate quote"""
    with patch('app.QUOTES_FILE', str(mock_csv_file)):
        # Try to save the same quote that's already in the test CSV
        result = save_quote("Test quote", "Test Author")
        assert result == False
        
        # Verify no duplicate was added
        df = pd.read_csv(mock_csv_file)
        assert len(df) == 1

def test_api_error_handling(mock_response):
    """Test API error handling"""
    mock_response.raise_for_status.side_effect = requests.RequestException("API Error")
    
    with patch('requests.get', return_value=mock_response):
        quote = get_random_quote()
        assert quote is None
        
        authors = get_authors()
        assert authors == []
        
        results = search_quotes("test")
        assert results['count'] == 0
        assert len(results['results']) == 0

# Add new test for pagination
def test_search_quotes_pagination(mock_response):
    """Test quote search with pagination"""
    # Mock first page response
    first_page = {
        "count": 4,
        "totalPages": 2,
        "results": [
            {"_id": "1", "content": "Quote 1", "author": "Author 1"},
            {"_id": "2", "content": "Quote 2", "author": "Author 1"}
        ]
    }
    # Mock second page response
    second_page = {
        "count": 4,
        "totalPages": 2,
        "results": [
            {"_id": "3", "content": "Quote 3", "author": "Author 1"},
            {"_id": "4", "content": "Quote 4", "author": "Author 1"}
        ]
    }
    
    mock_response.json.side_effect = [first_page, second_page]
    
    with patch('requests.get', return_value=mock_response):
        results = search_quotes(author="Author 1")
        assert len(results['results']) <= 10
        assert all(quote['author'] == "Author 1" for quote in results['results']) 