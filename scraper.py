import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import json # Used for clean printing

# --- 1. Define the List of URLs (Editor's Input) ---
# Keep your URLs here

ARTICLE_URLS: List[str] = [
    "https://www.nytimes.com/2025/10/31/technology/ai-spending-accelerating.html#",
    "https://www.nytimes.com/2025/05/20/technology/personaltech/google-ai-mode-search.html",
    "https://www.nytimes.com/2025/10/22/technology/meta-plans-to-cut-600-jobs-at-ai-superintelligence-labs.html",
]

# ARTICLE_URLS: List[str] = [
#     "https://www.nytimes.com/2025/10/17/business/bull-market-trump-biden.html",
#     "https://www.nytimes.com/2025/10/31/business/interest-rates-money-markets-stocks-bonds.html",
#     "https://www.nytimes.com/2025/10/24/business/interest-rates-cds-savings-accounts.html",
# ]

# --- 2. Core Functions (Adding extract_section) ---

def fetch_url_content(url: str) -> Optional[str]:
    """Fetches the raw HTML content of a given URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() 
        return response.text
    except requests.exceptions.RequestException as e:
        # print(f"❌ Error fetching the URL {url}: {e}") # Comment out for cleaner output
        return None

def extract_title(soup: BeautifulSoup) -> str:
    # ... (Keep this function the same)
    title_tag = soup.find(attrs={'data-testid': 'headline'})
    if title_tag:
        return title_tag.text.strip()
    return "Title Not Found"

def extract_summary(soup: BeautifulSoup) -> str:
    # ... (Keep this function the same)
    summary_tag = soup.find(id='article-summary')
    if summary_tag:
        return summary_tag.text.strip()
    return "Summary Not Found"

def extract_image_url(soup: BeautifulSoup) -> str:
    # ... (Keep this function the same)
    image_tag = soup.find('img', class_='css-rq4mmj')
    if image_tag:
        image_url = image_tag.get('src')
        if image_url and image_url.startswith('//'):
            image_url = 'https:' + image_url
        return image_url if image_url else "Image Not Found"
    return "Image Not Found"

# --- NEW FUNCTION: Extract the Article Section/Category ---
def extract_section(soup: BeautifulSoup) -> str:
    """Finds the article section/category using its unique CSS class."""
    
    # We are looking for an <a> tag with the class 'css-nuvmzp'
    section_tag = soup.find('a', class_='css-nuvmzp')
    
    if section_tag:
        # Return the clean text content of the link
        return section_tag.text.strip()
    return "Section Not Found"


# --- 3. The Central Processing Function (UPDATED to include section) ---

def process_single_article(url: str) -> Dict[str, str]:
    """Fetches and extracts all required data for one article."""
    
    print(f"Processing: {url}")
    
    # 1. Initialize data dictionary with all required fields
    article_data: Dict[str, str] = {
        "url": url,
        "title": "N/A",
        "summary": "N/A",
        "image_url": "N/A",
        "section": "N/A", # New Field
    }
    
    # 2. Fetch Content
    html_content = fetch_url_content(url)
    if not html_content:
        return article_data
    
    # 3. Create Soup object and Extract
    soup = BeautifulSoup(html_content, 'html.parser')
    
    article_data["title"] = extract_title(soup)
    article_data["summary"] = extract_summary(soup)
    article_data["image_url"] = extract_image_url(soup)
    article_data["section"] = extract_section(soup) # New Extraction
    
    return article_data

# --- 4. Main Execution Block (Keep this the same) ---

# ... (Keep all your existing functions and imports above this line) ...

from jinja2 import Environment, FileSystemLoader, select_autoescape

# --- New Function: Generate HTML Output ---
def generate_newsletter_html(all_articles: List[Dict[str, str]]):
    """Generates the HTML output using Jinja2 and the collected data."""
    
    # Check if we have enough articles
    if len(all_articles) < 3:
        print("ERROR: Not enough articles provided. Need at least 3.")
        return

    # 1. Load Jinja2 Environment
    file_loader = FileSystemLoader('.') # Look for templates in the current directory
    env = Environment(
        loader=file_loader,
        autoescape=select_autoescape(['html', 'xml'])
    )
    # Define a truncate filter for summaries
    env.filters['truncate'] = lambda s, length, killwords: s[:length] + ('...' if len(s) > length else '')
    
    # 2. Load the template
    template = env.get_template('template.html')
    
    # 3. Assign articles to specific newsletter roles
    # The order the editor pastes them determines their role:
    main_article = all_articles[0]
    other_articles = all_articles[1:] # Articles 1 and 2 become sub/quick reads
    
    # 4. Render the template with the data
    html_output = template.render(
        main_article=main_article,
        other_articles=other_articles
    )
    
    # 5. Save the output to a file
    output_filename = "final_newsletter_content.html"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html_output)
    
    print("-" * 50)
    print(f"✅ SUCCESS: Newsletter HTML generated and saved to {output_filename}")
    print("You can open this file in your browser to view the result.")
    print("-" * 50)
    


# --- Main execution block (To call the HTML generator) ---

if __name__ == "__main__":
    
    
    
    all_articles: List[Dict[str, str]] = []
    
    print("-" * 50)
    print("STARTING BATCH PROCESSING")
    
    for url in ARTICLE_URLS:
        data = process_single_article(url)
        all_articles.append(data)
        
    # --- FINAL STEP ---
    if all_articles:
        generate_newsletter_html(all_articles)