import numpy as np  # Library for numerical operations and array manipulation
from langdetect import detect  # Library for language detection

# Function for extracting affiliations from author information strings
def extractAffiliations(authorsWithAffiliations):
    affiliations = []
    authorsList = authorsWithAffiliations.split(';')

    for authorInfo in authorsList:
        parts = authorInfo.split(',')
        if len(parts) > 1:
            language = detect(parts[1])
            if language in {'pt', 'en'}:
                affiliation = parts[2].strip() if language == 'en' and len(parts) > 2 else parts[1].strip()
            else:
                affiliation = parts[1].strip()
            affiliations.append(affiliation)
        else:
            affiliations.append('Unknown')
    return affiliations

# Function to construct a graph from author data in a DataFrame
def createGraph(df, graph):
    for _, row in df.iterrows():
        authors = [author.strip() for author in row['Authors'].split(';')]
        authorsId = [author_id.strip() for author_id in row['Author(s) ID'].split(';')]
        affiliations = extractAffiliations(row['Authors with affiliations'])
        
        # Creates a dictionary with author information
        authorData = {
            authorsId[i] if i < len(authorsId) else 'Unknown': {
                'name': authors[i],
                'affiliation': affiliations[i].split(', ')[0] if i < len(affiliations) else 'Unknown'
            }
            for i in range(len(authors))
        }

        # Adds the authors as nodes in the graph
        for author_id, data in authorData.items():
            if not graph.has_node(author_id):  
                graph.add_node(author_id, name=data['name'], affiliation=data['affiliation'])

        # Creates a list of author IDs
        authorIds = list(authorData.keys())

        # Adds edges between all pairs of authors
        for i in range(len(authorIds)):
            for j in range(i + 1, len(authorIds)):
                graph.add_edge(authorIds[i], authorIds[j])

# Function to visualise the relationship between node degree and average neighbour degree
def plotGraph(ax, degree, averageNeighborDegree, title):
    ax.plot(degree, averageNeighborDegree, 'o')
    ax.plot(degree, np.poly1d(np.polyfit(degree, averageNeighborDegree, 1))(degree))
    ax.set_ylabel('Average Neighbor Degree')
    ax.set_xlabel('Node Degree')
    ax.set_title(title)
    ax.grid(True)