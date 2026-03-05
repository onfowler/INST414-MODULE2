# Mapping the Fundamentals of Cybersecurity

This repository contains the code, data, and visualizations for a network analysis project designed to identify the foundational concepts of cybersecurity. By analyzing Wikipedia hyperlink structures, this project determines which topics are most critical for new IT professionals and risk managers to learn first.

This project was developed for **INST414: Data Science Techniques**. The full write-up and analysis can be found on Medium.

## 📌 Project Overview

The field of Information Risk Management is vast and overwhelming. To build an effective training curriculum, educators need to know which topics serve as the prerequisites for everything else. 

Instead of relying on industry trends or guesswork, this project uses a Breadth-First Search (BFS) algorithm to scrape Wikipedia, building a directed network graph of 400 highly connected cybersecurity articles. By calculating the **PageRank Centrality** of each node, the algorithm mathematically identifies the core concepts that the rest of the field relies upon to explain itself.

## 🗂️ Repository Contents

### Code
* `cyber_wikipedia_scraper.py`: The main Python script. It utilizes `requests` and `BeautifulSoup` to scrape Wikipedia, `networkx` to build the graph and calculate PageRank, and `matplotlib` to generate initial visualizations. It also exports the network data for use in Gephi.

### Data Files (Reproducibility)
* `cyber_nodes.csv`: Contains the 400 scraped Wikipedia articles (nodes) and their calculated PageRank scores.
* `cyber_edges.csv`: Contains the directed links (edges) between the articles.
* `cyber_network.graphml`: The complete network structure exported in GraphML format, ready to be imported into advanced visualization tools like Gephi.

### Visualizations
* `Cyber_Web.png` / `Cyber_Web.pdf` / `Cyber_Web.svg`: High-resolution, publication-ready network visualizations created using Gephi (ForceAtlas 2 layout). These highlight the distinct clusters of the cybersecurity domain.
* `cyber_network.png`: The initial network graph generated directly via Python and NetworkX.
* `pagerank_barchart.png`: A horizontal bar chart visualizing the Top 10 most central nodes in the network.

## 📊 Key Findings

The PageRank algorithm identified three primary "pillars" of cybersecurity knowledge:
1. **The Mathematical Foundation:** **Cryptography** (Score: 0.0169) is the undisputed core of the field.
2. **The Attack Surface:** Wireless and legacy protocols like **Wi-Fi, Bluetooth, and 3G/2G** (~0.0100) are the primary vulnerabilities connecting digital systems to the physical world.
3. **The Business Motivation:** **Finance, Business, and Physical Security** (~0.0095) act as massive central hubs, proving that cybersecurity is fundamentally a risk management discipline focused on protecting real-world assets.

## 🚀 How to Run the Code

To reproduce this analysis, ensure you have Python installed along with the following libraries:

```bash
pip install requests beautifulsoup4 networkx matplotlib
