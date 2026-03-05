import requests
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt
import time
import csv

# --- 1. CONFIGURATION ---
START_PAGE = "Computer_security"
MAX_NODES = 400 # Increased for a richer, more accurate PageRank distribution
WIKI_URL = "https://en.wikipedia.org/wiki/"

def get_wiki_links(page_title):
    """Scrapes a Wikipedia page and returns an ordered list of linked article titles within the main text."""
    url = WIKI_URL + page_title
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        content = soup.find("div", class_="mw-parser-output")
        if content is None:
            return []
            
        # Clean out all metadata, references, and sidebars
        unwanted_classes = ['reflist', 'reference', 'navbox', 'infobox', 'metadata', 'printfooter', 'noprint']
        for unwanted in content.find_all(['div', 'sup', 'table', 'span'], class_=unwanted_classes):
            unwanted.decompose() 
            
        raw_links = []
        
        # STRICT FILTER: We only want links inside actual paragraph text. 
        for tag in content.find_all('p'):
            for a in tag.find_all('a', href=True):
                href = a['href']
                
                if href.startswith('/wiki/') and ':' not in href:
                    title = href.split('/')[-1]
                    
                    # IRONCLAD BLACKLIST: Ignore generic hubs, publishers, countries, and drift topics
                    blacklist = [
                        'Wayback_Machine', 'Google', 'The_New_York_Times', 'The_Christian_Science_Monitor',
                        'identifier', 'Main_Page', 'International_Standard_Book_Number', 'doi',
                        'Nonpartisan_primary', 'Apportionment_(politics)', 'United_States', 'Sun_Microsystems',
                        'United_Kingdom', 'China', 'Russia', 'Europe', 'IBM', 'Microsoft', 'Apple_Inc.',
                        'English_language', 'World_War_II', 'ISSN',
                        # NEW: Stop Electrical & Broad Tech Drift
                        'Alternating_current', 'Direct_current', 'Transformer', 'Television', 
                        'Internet', 'Data', 'Information', 'Computer', 'Computer_science', 
                        'Electronics', 'Technology', 'Science', 'Mathematics', 'Telecommunication',
                        'Physics', 'Electricity'
                    ]
                    
                    if not any(bad.lower() in title.lower() for bad in blacklist):
                        raw_links.append(title)
        
        # Keep the chronological order: First links in a Wiki article are usually the most definitional
        unique_links = []
        for link in raw_links:
            if link not in unique_links:
                unique_links.append(link)
        
        return unique_links[:20] # Keep the top 20 most relevant concepts per page
    
    except Exception as e:
        print(f"Error fetching {page_title}: {e}")
        return []

# --- 2. DATA COLLECTION (Building the Graph) ---
print("Starting data collection...")
G = nx.DiGraph() # Directed Graph (A links to B)
queue = [START_PAGE]
visited = set()

while queue and len(visited) < MAX_NODES:
    current_page = queue.pop(0)
    
    if current_page not in visited:
        print(f"Scraping: {current_page} ({len(visited)+1}/{MAX_NODES})")
        visited.add(current_page)
        G.add_node(current_page)
        
        # Get links
        links = get_wiki_links(current_page)
        
        for link in links:
            G.add_edge(current_page, link)
            if link not in visited and link not in queue:
                queue.append(link)
                
        time.sleep(0.1) # Be polite to Wikipedia's servers

# --- 3. ANALYSIS (Finding "Importance") ---
print("\nCalculating Importance (PageRank)...")

# Create a subgraph containing ONLY the nodes we fully scraped to avoid dead-end bleeding
G_closed = G.subgraph(visited)

# Run PageRank on the closed network
pagerank = nx.pagerank(G_closed)

# Sort nodes by PageRank
top_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:10]

print("\nTop 10 Most Important Cybersecurity Concepts:")
for idx, (node, score) in enumerate(top_nodes):
    print(f"{idx+1}. {node} (Score: {score:.4f})")

# --- 4. VISUALIZATION ---
print("\nGenerating visualization...")
plt.figure(figsize=(14, 14))

# Make node sizes proportional to their PageRank score
node_sizes = [pagerank.get(n, 0) * 80000 for n in G_closed.nodes()]

# Calculate layout with a higher 'k' value to spread nodes out and avoid a hairball
pos = nx.spring_layout(G_closed, k=0.5, iterations=50)

nx.draw_networkx(
    G_closed, 
    pos=pos, 
    node_size=node_sizes, 
    with_labels=False, 
    node_color="skyblue", 
    edge_color="gray", 
    alpha=0.6,
    width=0.5
)

# Only label the top 10 nodes to keep the graph readable
labels = {node: node.replace('_', ' ') for node, score in top_nodes}
nx.draw_networkx_labels(
    G_closed, 
    pos=pos, 
    labels=labels, 
    font_size=11, 
    font_weight="bold", 
    font_color="darkred"
)

plt.title("The Cybersecurity Knowledge Web", fontsize=16, fontweight="bold")
plt.axis("off")
plt.tight_layout()
plt.savefig("cyber_network.png", format="PNG", dpi=300)
print("Graph saved as 'cyber_network.png'")

# --- 5. BAR CHART VISUALIZATION ---
plt.figure(figsize=(10, 6))

# Extract names and scores from the top_nodes list
names = [node[0].replace('_', ' ') for node in top_nodes][::-1] # Reverse for top-down display
scores = [node[1] for node in top_nodes][::-1]

# Create horizontal bar chart
plt.barh(names, scores, color='#4A90E2')
plt.xlabel('PageRank Score', fontweight='bold')
plt.title('Top 10 Foundational Cybersecurity Concepts', fontweight='bold', fontsize=14)
plt.tight_layout()
plt.savefig('pagerank_barchart.png', dpi=300)
print("Bar chart saved as 'pagerank_barchart.png'")


# --- 6. EXPORTING THE DATA ---
print("\nExporting data files...")

# 1. Export the Nodes and their PageRank scores to a CSV
with open('cyber_nodes.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Id', 'Label', 'PageRank_Score']) # 'Id' and 'Label' are standard for network software
    for node in G_closed.nodes():
        writer.writerow([node, node.replace('_', ' '), pagerank[node]])
print("- Saved 'cyber_nodes.csv'")

# 2. Export the Edges (Connections) to a CSV
with open('cyber_edges.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Source', 'Target', 'Type'])
    for source, target in G_closed.edges():
        writer.writerow([source, target, 'Directed'])
print("- Saved 'cyber_edges.csv'")

# 3. Export as a GraphML file (For advanced network software like Gephi)
nx.write_graphml(G_closed, "cyber_network.graphml")
print("- Saved 'cyber_network.graphml'")

print("\nData export complete! You can now upload these to GitHub.")