import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
import os
from dotenv import load_dotenv
import urllib3

# Load environment variables
load_dotenv()

# Constants
API_BASE_URL = "http://api.quotable.io"  # Changed from https to http
QUOTES_FILE = "quotes.csv"
TIMEOUT_SECONDS = 5
CATEGORIES = [
    "happiness", "inspirational", "life", "love", 
    "philosophy", "success", "wisdom"
]  # Limited to actually supported categories

# Configure the page
st.set_page_config(
    page_title="Quote of the Day",
    page_icon="📚",
    layout="centered"
)

# Add a title
st.title("✨ Quote of the Day App")
st.markdown("Discover and save inspiring quotes!", unsafe_allow_html=True)
# Add custom CSS
    
# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@st.cache_data(ttl=3600)
def get_random_quote() -> Optional[Dict]:
    """Fetch a random quote from the Quotable API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/random",
            timeout=TIMEOUT_SECONDS,
            verify=False  # Disable SSL verification
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching quote: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def get_authors() -> List[str]:
    """Fetch list of authors from the API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/authors",
            timeout=TIMEOUT_SECONDS,
            verify=False
        )
        response.raise_for_status()
        return [author['name'] for author in response.json()['results']]
    except requests.RequestException as e:
        st.error(f"Error fetching authors: {str(e)}")
        return []

@st.cache_data(ttl=3600)
def search_quotes(query: str = "", author: str = None) -> Dict:
    """Search quotes by content and/or author"""
    try:
        all_results = []
        page = 1
        total_pages = 1
        
        # If searching content with All Authors, fetch multiple pages
        while page <= total_pages and (page <= 5 or author != "All Authors"):
            params = {
                'limit': 50,
                'maxLength': 1000,
                'page': page
            }
            
            # Add author filter if specified
            if author and author != "All Authors":
                params['author'] = author
                
            response = requests.get(
                f"{API_BASE_URL}/quotes",
                params=params,
                timeout=TIMEOUT_SECONDS,
                verify=False
            )
            response.raise_for_status()
            results = response.json()
            
            all_results.extend(results['results'])
            total_pages = results.get('totalPages', 1)
            page += 1
        
        # Client-side content filtering
        if query:
            filtered_results = [
                quote for quote in all_results
                if query.lower() in quote['content'].lower()
            ]
            # Don't limit results when searching all authors with content
            if author and author != "All Authors":
                filtered_results = filtered_results[:10]
            
            return {
                'count': len(filtered_results),
                'results': filtered_results
            }
        else:
            # If no content search, just return the first page results
            return {
                'count': len(all_results),
                'results': all_results[:10] if author and author != "All Authors" else all_results
            }
            
    except requests.RequestException as e:
        st.error(f"Error searching quotes: {str(e)}")
        return {"count": 0, "results": []}

@st.cache_data(ttl=60)  # Cache for 1 minute
def load_saved_quotes() -> pd.DataFrame:
    """Load saved quotes from CSV file"""
    try:
        return pd.read_csv(QUOTES_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=['quote', 'author', 'date_saved'])
    except Exception as e:
        st.error(f"Error loading quotes: {str(e)}")
        return pd.DataFrame(columns=['quote', 'author', 'date_saved'])

def save_quote(quote: str, author: str) -> bool:
    """Save a quote to CSV file"""
    try:
        df = load_saved_quotes()
        # Check for duplicates
        if df[(df['quote'] == quote) & (df['author'] == author)].empty:
            new_quote = pd.DataFrame({
                'quote': [quote],
                'author': [author],
                'date_saved': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            })
            df = pd.concat([df, new_quote], ignore_index=True)
            df.to_csv(QUOTES_FILE, index=False)
            st.cache_data.clear()  # Clear cache to refresh saved quotes
            return True
        else:
            st.warning("This quote is already saved!")
            return False
    except Exception as e:
        st.error(f"Error saving quote: {str(e)}")
        return False

def display_quote(quote_data: Dict, key_suffix: str) -> None:
    """Display a quote with consistent formatting"""
    st.markdown(f"### _{quote_data['content']}_")
    st.markdown(f"**— {quote_data['author']}**")
    
    # Create a container for the save button/message
    save_container = st.container()
    
    # Check if quote is already saved
    df = load_saved_quotes()
    is_saved = not df[(df['quote'] == quote_data['content']) & 
                     (df['author'] == quote_data['author'])].empty
    
    with save_container:
        if not is_saved:
            if st.button("Save Quote", key=f"save_{key_suffix}"):
                if save_quote(quote_data['content'], quote_data['author']):
                    st.success("Quote saved successfully!")
                    st.rerun()  # Refresh the page to update the UI
        else:
            st.success("Quote already saved!")

def main():
    # Initialize session state for current quote
    if 'current_quote' not in st.session_state:
        st.session_state.current_quote = None

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Daily Quote", "Search Quotes", "Saved Quotes"])
    
    # Tab 1: Daily Quote
    with tab1:
        if st.button("Get New Quote", key="random_quote"):
            st.session_state.current_quote = get_random_quote()
        
        if st.session_state.current_quote:
            display_quote(
                st.session_state.current_quote,
                f"daily_{str(st.session_state.current_quote['_id'])}"
            )

    # Tab 2: Search Quotes
    with tab2:
        st.write("Search quotes:")
        
        # Create two columns for search controls
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_query = st.text_input(
                "Search by content:",
                placeholder="Enter keywords to search..."
            )
        
        with col2:
            authors = ["All Authors"] + get_authors()
            selected_author = st.selectbox(
                "Filter by author:",
                options=authors,
                index=0
            )
        
        # Search button to trigger the search
        if st.button("Search", key="search_button") or search_query or selected_author != "All Authors":
            # Get search results
            search_results = search_quotes(
                query=search_query,
                author=selected_author
            )
            quotes = search_results.get('results', [])
            
            if quotes:
                if selected_author != "All Authors" and search_query:
                    st.write(f"Showing {len(quotes)} quotes by {selected_author} containing '{search_query}'")
                elif selected_author != "All Authors":
                    st.write(f"Showing {len(quotes)} quotes by {selected_author}")
                else:
                    st.write(f"Found {len(quotes)} quotes containing '{search_query}'")
                if len(quotes) == 150:
                    st.caption("(Showing maximum number of results. Try a more specific search term for better results)")
                elif len(quotes) > 10:
                    st.caption(f"(Showing all {len(quotes)} matching quotes)")
                else:
                    st.caption("(Search shows up to 10 results at a time)")
                
                # Display quotes
                for quote in quotes:
                    display_quote(quote, f"search_{quote['_id']}")
            else:
                st.info("No quotes found matching your criteria.")
    
    # Tab 3: Saved Quotes
    with tab3:
        saved_quotes = load_saved_quotes()
        if not saved_quotes.empty:
            for _, row in saved_quotes.iterrows():
                st.markdown(f"### _{row['quote']}_")
                st.markdown(f"**— {row['author']}**")
                st.caption(f"Saved on: {row['date_saved']}")
                st.divider()
        else:
            st.info("No saved quotes yet. Start saving some quotes!")

if __name__ == "__main__":
    main()