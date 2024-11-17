import streamlit as st
import streamlit.components.v1 as components
import json
from pathlib import Path
import tempfile
import base64

def escape_markdown_for_js(markdown_text):
    """Escape markdown content for JavaScript string."""
    return markdown_text.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')

def create_markmap_html(markdown_content):
    """Create an HTML file with Markmap visualization of markdown content."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Markdown Mind Map</title>
        <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
        <script src="https://cdn.jsdelivr.net/npm/markmap-lib@0.15.4/dist/browser/index.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/markmap-view@0.15.4/dist/browser/index.js"></script>
        <style>
        body {
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100vw;
            height: 100vh;
        }
        svg {
            width: 90%; /* Adjust as needed */
            height: 90%; /* Adjust as needed */
            display: block;
        }
    </style>
    </head>
    <body style="margin:0">
        <svg id="mindmap" style="width: 100%; height: 100%; display: block;"></svg>
        <script>
            (async function() {
                // Load scripts
                const { markmap } = window;
                const { Markmap, loadCSS, loadJS } = markmap;
                
                // Create markmap
                const svg = document.querySelector('#mindmap');
                const mm = await Markmap.create(svg);
                
                // Transform markdown
                const { Transformer } = window.markmap;
                const transformer = new Transformer();
                
                const markdown = `MARKDOWN_CONTENT`;
                const { root } = transformer.transform(markdown);
                
                // Render
                mm.setData(root);
                mm.fit();
            })();
        </script>
    </body>
    </html>
    """
    
    # Escape and inject markdown content
    escaped_content = escape_markdown_for_js(markdown_content)
    html_content = html_content.replace('MARKDOWN_CONTENT', escaped_content)

    return html_content
    

def get_binary_file_downloader_html(html_content, file_label='Mind Map'):
    """Generate a button to open the mind map in a new tab."""
    b64 = base64.b64encode(html_content.encode()).decode()
    return f'''
    <a href="data:text/html;base64,{b64}" download="mindmap.html" target="_blank">
        <button style="
            padding: 0.5em 1em; 
            background-color: #4CAF50; 
            color: white; 
            border: none; 
            border-radius: 4px; 
            cursor: pointer;
        ">
            {file_label}
        </button>
    </a>
    '''

def display_markmap(markdown_content, height=400):
    """Display a Markmap visualization of markdown content."""
    # Create HTML content
    html_content = create_markmap_html(markdown_content)
    
    # Display the mind map in Streamlit
    components.html(html_content, height=height)
    
    # Add button to open in new tab
    st.markdown(get_binary_file_downloader_html(html_content), unsafe_allow_html=True)

# Example Streamlit app
def main():
    st.title("RAG with Mind Map Visualization")
    
    # Your existing RAG query input
    query = st.text_input("Enter your question:")
    
    if query:
        # Mock response - replace this with your actual RAG response
        markdown_response = """
# Property Investment Suggestion: Westmead vs Toongabbie

## Overview 
This mind map aims to provide a comparative analysis for investing in properties in **Westmead** and **Toongabbie**, two suburbs in NSW.

## Westmead

### Area Profile
- **Size**: Approximately 2.9 square kilometers
- **Parks**: 17 parks, covering 5.4% of total area
- **Population**: 
  - 2011: 14,171
  - 2016: 16,303 (15% growth)
- **Predominant Age Group**: 30-39 years
- **Household Composition**: Mainly couples with children
- **Mortgage Repayment**: $1,800 - $2,399/month
- **Owner-occupied Homes**: 
  - 2011: 35.6%
  - 2016: 31.5%
- **Median Sales Price**: $1,635,000

### Property Market Trends
- **Average Tenure Period**: 
  - Houses: 15.4 years
  - Units: 10.4 years
- **Total Dwellings**:
  - Houses: 1,401
  - Units: 5,758
- **Total New Listings**: 39 (houses), 302 (units)

## Toongabbie

### Area Profile
- **Size**: Approximately 4.7 square kilometers
- **Parks**: 28 parks, covering 19.4% of total area
- **Population**: 
  - 2011: 13,003
  - 2016: 14,327 (10.2% growth)
- **Predominant Age Group**: 30-39 years
- **Household Composition**: Mainly couples with children
- **Mortgage Repayment**: $1,800 - $2,399/month
- **Owner-occupied Homes**: 
  - 2011: 69.7%
  - 2016: 66.7%
- **Median Sales Price**: $1,275,000

### Property Market Trends
- **Average Tenure Period**:
  - Houses: 14.6 years
  - Units: 8.0 years
- **Total Dwellings**:
  - Houses: 3,608
  - Units: 2,303
- **Total New Listings**: 39 (houses), 302 (units)

## Comparative Analysis

### Price Point
- **Median Sales Price**: Toongabbie ($1,275,000) is significantly lower than Westmead ($1,635,000), making it potentially more accessible for first-time buyers.

### Growth Potential
- **Population Growth**: Westmead shows a higher growth rate (15%) compared to Toongabbie's (10.2%), indicating a potentially higher demand for housing in Westmead going forward.

### Owner-occupied Rates
- Toongabbie has a higher owner-occupancy rate compared to Westmead, which may indicate a stronger community and potentially lower rental vacancies.

### Amenities and Green Spaces
- Toongabbie has more parks and green spaces (28 vs 17), which can enhance the suburb's livability and attractiveness for families.

## Investment Recommendation

### Buy in Toongabbie if:
- You are looking for more affordable housing.
- You prioritize community livability with more parks and green spaces.
- You wish to invest in an area with stable owner-occupancy and family-oriented demographics.

### Buy in Westmead if:
- You aim to tap into a rapidly growing suburb with higher demand.
- You are comfortable investing at a higher price point for potential better returns due to growth factors.

## Conclusion 
Both Westmead and Toongabbie have their strengths as investment options. The decision ultimately depends on your financial capacity, investment goals, and priorities regarding community living and growth potential.
"""
        
        # Display regular markdown response
        st.markdown("### Answer")
        st.markdown(markdown_response)
        
        # Add mind map visualization
        st.markdown("### Mind Map Visualization")
        display_markmap(markdown_response)

if __name__ == "__main__":
    main()