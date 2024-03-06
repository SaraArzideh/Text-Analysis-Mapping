import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from community import community_louvain

#Step1: Loading the CSV file
df = pd.read_csv('filtered_articles_subset.csv')

#Step2: Preparing the dictionary for co-occurrent terms and their alternatives
#Defining all co-occurrent terms and their alternatives
co_occurrent_terms = {
    'human factors': ['human factors', 'Human factors', 'human factor', 'Human factor'],
    #'usability': ['usability', 'Usability'],
    'human-computer interaction': ['human-computer interaction', 'human computer interaction', 'human computer', 'human-computer','Human computer'],
    #'user centered design': ['user centered design', 'User centered',  'user centered', 'user-centered', 'user centred', 'user-centred', 'User-centric',  'user-centric', 'User centeric',  'user centric', 'User centered care','user centered care'],
    'perceived ease of use': ['perceived ease of use','perceived ease', 'Perceived ease', 'ease of use', 'Ease of use', 'Ese of Use'],
    'perceived usefulness':['perceived usefulness', 'Perceived usefulness', 'usefulness', 'Usefulness'],
    'reliability':['reliability','Reliability', 'reliable',  'reliabilities'],
    'health behaviour change':['health behaviour change', 'Health behaviour change', 'health behavior change', 'behaviour change', 'behavior change'],
    'usability assessment': ['usability assessment', 'Usability assessment',  'usability evaluation',  'Usability evaluation',  'Usability testing',  'usability testing',  'Usability test',  'usability test'],
    'user experience':['user experience', 'User experience', 'experience', 'Experience', 'experiences', 'patient experience',  'Patient experience'],
    'health outcomes': ['health outcomes', 'health outcome', 'Health outcomes',  'Health outcome'],
    'medication adherence': ['medication adherence', 'Medication adherence', 'adherence', 'Adherence'],
    'quality-of-life': ['quality-of-life', 'quality of life', 'Quality-of-life', 'Quality of life'],
    'technology acceptance': ['technology acceptance', 'Technology acceptance', 'technology acceptance model', 'Acceptance', 'acceptance', 'tam', 'TAM', 'taut', 'TAUT'],
    'technology adoption':['technology adoption', 'Technology adoption', 'adoption', 'Adoption'],
    'user empowerment':  [ 'user empowerment', 'User empowerment',  'patient empowerment',  'Patient empowerment'],
    'user engagement': ['user engagement', 'User engagement',  'patient engagement',  'Patient engagement'],
    #'utility':[ 'utility', 'Utility', 'utilities', 'Utilities'],
    'adaptation':['adaptation', 'Adaptation'],
    'ethics':['ethics', 'Ethics', 'ethic', 'Ethic', 'Ethical'],
    'privacy': ['privacy', 'Privacy'],
    'security': ['security', 'Security', 'secure', 'Secure'],
    'trust': ['trust', 'Trust'],
    'accessibility': ['accessibility', 'Accessibility', 'accessible', 'Accessible'],
    'digital divide':['digital divide', 'Digital divide'],
    'digital health literacy': ['digital health literacy', 'Digital health literacy', 'digital literacy', 'Digital literacy', 'digital illiteracy', 'Digital illiteracy'],
    'health literacy': ['health literacy', 'Health literacy', 'health illiteracy', 'Health illiteracy'],
    'healthcare disparities':['healthcare disparities', 'Healthcare disparities', 'disparities', 'Disparities', 'disparity', 'Disparity', 'Health care disparities', 'health care disparities', 'Health disparities', 'health disparities', 'digital disparities', 'Digital disparities'],
    #'sustainability' :['sustainability', 'Sustainability',  'sustainable',  'Sustainable'],
    'human factors':[ 'human factors', 'Human factors', 'human factor', 'Human factor'],
    #'usability': ['usability', 'Usability'],
    'user satisfaction': ['user satisfaction', 'User satisfaction', 'satisfaction', 'Satisfaction', 'Patient satisfaction', 'patient satisfaction'],
}

# Initialize a dictionary to count frequencies
term_frequencies = {key: 0 for key in co_occurrent_terms}

# Function to count term frequencies
def count_term_frequencies(row, term_frequencies):
    for term, variations in co_occurrent_terms.items():
        if any(var.lower() in row.lower() for var in variations):
            term_frequencies[term] += 1

# Iterate over DataFrame and count frequencies
for index, row in df.iterrows():
    # Concatenating 'Title', 'Abstract', and 'Author Keywords' for each row
    concatenated_text = str(row['Title']) + " " + str(row['Abstract']) + " " + str(row['Author Keywords'])
    count_term_frequencies(concatenated_text, term_frequencies)

# Convert the frequencies dictionary to a DataFrame
freq_df = pd.DataFrame(list(term_frequencies.items()), columns=['Term', 'Frequency'])

# Saving the frequencies to a CSV file
freq_df.to_csv('term_frequencies.csv', index=False)


# Function to normalize terms
def normalize_term(term):
    term_lower = term.lower()
    for key, values in co_occurrent_terms.items():
        if term_lower in [v.lower() for v in values]:
            return key
    return None

#Step3: Analyzing the co-occurrences of terms and concepts
# Creating an empty network graph
G = nx.Graph()

# Iterate over rows in the DataFrame
for index, row in df.iterrows():
    if isinstance(row['Concepts'], str):        # Ensuring that 'Concepts' is a string before splitting
        concepts = row['Concepts'].split(', ')
    else:
        concepts = []

    # Extracting terms from Title, Abstract, and Author Keywords
    # Tokenizing and normalizing terms
    tokens = row['Title'].split() + row['Abstract'].split() + str(row['Author Keywords']).split()
    normalized_terms = [normalize_term(t) for t in tokens if normalize_term(t)] # Removing None values
 
    # Debugging print
    #print(f"Row {index}: Extracted Terms - {normalized_terms}")

#Step4: Building a network with NetworkX
    # Iterating over each concept and term pair and adding them to the graph
    for concept in concepts:
        for term in normalized_terms:
            if term in co_occurrent_terms:  # Checking if term is one of the co-occurrent terms
                if G.has_edge(concept, term):
                    G[concept][term]['weight'] += 1
                else:
                    G.add_edge(concept, term, weight=1)


# Exporting the network to a GEXF file
nx.write_gexf(G, 'network_graph.gexf')

#Step5: Creating clusters based on concepts


#Step6: Visualizing the network
# Node size based on degree
node_size = [100 * G.degree(node) for node in G.nodes()]

# Node color based on degree
node_color = [G.degree(node) for node in G.nodes()]

# Edge width based on weight
edge_width = [0.15 * G[u][v]['weight'] for u, v in G.edges()]

# Using a layout to spread nodes apart
pos = nx.spring_layout(G, k=0.15, iterations=20)

# Draw the network
plt.figure(figsize=(15, 15))
pos = nx.spring_layout(G, k=0.15)  # k regulates the distance between nodes
nx.draw(G, pos, with_labels=True, node_size=node_size, node_color=node_color,
        width=edge_width, edge_color='grey', alpha=0.7, cmap=plt.cm.Blues, font_size=10)
plt.title("Clustered Network of Co-occurrent Terms")
plt.show()
