# Import libraries
import networkx as nx           # networkx for graph manipulation and analysis
import wikipedia                # wikipedia API for fetching page data
import matplotlib.pyplot as plt # matplotlib for plotting
import time                     # time for measuring execution duration
from operator import itemgetter # itemgetter for sorting and accessing items

def stops(seed):
    # Open file containing invalid page names to reading
    with open(f'Assets/Pages/{seed}/invalid.txt', 'r') as file:
        content = file.read()

    # Split content by commas to get individual elements and remove extra whitespace from each element
    elements = content.split(',')  
    elements = [element.strip() for element in elements]

    # Return elements as a tuple
    return tuple(elements)

def network(invalids, seed):
    start = time.time()  # Record start time for execution measurement
    
    # Initialize list of pages, set to track pages to be processed and pages already processed
    todo_lst = [(0, seed)]
    todo_set = set(seed)
    done_set = set()

    # Create a directed graph object
    g = nx.DiGraph()

    # Get the initial layer and page
    layer, page = todo_lst[0]

    # Open file to write valid pages
    with open(f'Assets/Pages/{seed}/valid.txt', 'w', encoding='utf-8') as file:  
        file.write(f'{page},')

    # Continue until processing up to layer 2
    while layer < 2:  
        del todo_lst[0]  # Remove the processed page from the list

        # Mark page as done
        done_set.add(page)

        try:
             # Fetch Wikipedia page
            wiki = wikipedia.page(page)
        except:
            # Get the next page in case of failure and skip to the next iteration
            layer, page = todo_lst[0] 
            continue

        # Iterate over links in the Wikipedia page
        for link in wiki.links: 
            # Get the title of the link
            link = link.title()

            # Check if link is valid
            if link not in invalids and not link.startswith("List Of"):
                # Check if link needs to be processed
                if link not in todo_set and link not in done_set:
                    todo_lst.append((layer + 1, link))  # Add link to the list of pages to process
                    todo_set.add(link)                  # Mark link as to be processed
                g.add_edge(page, link)  # Add edge to the graph

                # Open file to append valid pages
                with open(f'Assets/Pages/{seed}/valid.txt', 'a', encoding='utf-8') as file:
                    file.write(f'{link},')
            # If link is not in invalids
            elif link not in invalids:
                # Open file to append invalid pages
                with open(f'Assets/Pages/{seed}/invalid.txt', 'a', encoding='utf-8') as file:
                    file.write(f'{link},')

        # Get the next page in the list
        layer, page = todo_lst[0] 

    # Print execution time and return the constructed graph
    print(f"\n{seed} - Execution Time: {time.time() - start}")
    return g 

def preprocess(graph):
    graph.remove_edges_from(nx.selfloop_edges(graph))  # Remove self-loops from the graph

    # Find duplicate nodes with appended 's'
    duplicates = [(node, node + "s")  
                for node in graph if node + "s" in graph
              ]

    # Merge and print duplicate nodes and 
    for dup in duplicates:
        graph = nx.contracted_nodes(graph, *dup, self_loops=False)  
    print(duplicates)

    # Find more duplicates with replaced hyphens
    duplicates = [(x, y) for x, y in [(node, node.replace("-", " ")) for node in graph] if x != y and y in graph]

    # Merge more duplicates
    for dup in duplicates:
        graph = nx.contracted_nodes(graph, *dup, self_loops=False)  

    # Set node and edge attribute 'contraction' to 0
    nx.set_node_attributes(graph, 0,"contraction")  
    nx.set_edge_attributes(graph, 0,"contraction")

    # Return the preprocessed graph
    return graph

def histogram(seed, graph):
    plt.style.use("default")  # Set the plotting style to default

    # Get and sort degree sequence
    degree_sequence = sorted([d for n, d in graph.degree()], reverse=True)  

    # Create subplots
    fig, ax = plt.subplots(1, 2, figsize=(8, 4))

    # Plot histogram of degree sequence and histogram with specific bins
    ax[0].hist(degree_sequence) 
    ax[1].hist(degree_sequence, bins=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    ax[0].set_title("Degree Histogram") # Set title for the first subplot
    ax[0].set_ylabel("Count")           # Set y-axis label for the first subplot
    ax[0].set_xlabel("Degree")          # Set x-axis label for the first subplot
    ax[0].set_ylim(0, 15000)            # Set y-axis limit for the first subplot

    ax[1].set_title("Degree Histogram - Zoom")  # Set title for the second subplot
    ax[1].set_ylabel("Count")                   # Set y-axis label for the second subplot
    ax[1].set_xlabel("Degree")                  # Set x-axis label for the second subplot
    ax[1].set_xlim(0, 10)                       # Set x-axis limit for the second subplot
    ax[1].set_ylim(0, 15000)                    # Set y-axis limit for the second subplot

    # Adjust layout to prevent overlap and save histogram as a PNG file
    plt.tight_layout() 
    plt.savefig(f"Assets/Images/Histogram/{seed}.png", format='png')

def graph(seed, graph):
    core = [node for node, deg in dict(graph.degree()).items() if deg >= 2]  # Get nodes with degree >= 2

    # Create subgraph with core nodes
    gsub = nx.subgraph(graph, core)  

    # Save subgraph as a GraphML file
    nx.write_graphml(gsub, f"Assets/Graphs/{seed}.graphml")  

    # Open file to write top nodes
    with open(f'Assets/Pages/{seed}/top.txt', 'w', encoding='utf-8') as file:  
        file.write(f'{",".join(map(lambda t: "{} {}".format(*reversed(t)), sorted(dict(gsub.in_degree()).items(), reverse=True, key=itemgetter(1))[:100]))}')  

    # Return the subgraph
    return gsub  

def summarize(seed, network, preprocess, gsub):
    print(f"{seed}\n")                                                                                                          # Print seed name
    print(f"Original Nodes: {len(network)}")                                                                                    # Print number of original nodes
    print(f"Original Edges: {nx.number_of_edges(network)}\n")                                                                   # Print number of original edges
    print(f"Preprocess Nodes: {len(preprocess)}")                                                                               # Print number of preprocessed nodes
    print("Nodes removed from original: {:.2f}%".format(100*(1 - len(preprocess)/len(network))))                                # Print percentage of nodes removed
    print(f"Preprocess Edges: {nx.number_of_edges(preprocess)}")                                                                # Print number of preprocessed edges
    print("Edges removed from original: {:.2f}%".format(100*(1 - nx.number_of_edges(preprocess)/nx.number_of_edges(network))))  # Print percentage of edges removed
    print("Edges per nodes: {:.2f}\n".format(len(network)/len(preprocess)))                                                     # Print edges per node ratio
    print(f"Final Nodes: {len(gsub)}")                                                                                          # Print number of final nodes
    print("Nodes removed from preprocess: {:.2f}%".format(100*(1 - len(gsub)/len(preprocess))))                                 # Print percentage of nodes removed
    print(f"Final Edges: {nx.number_of_edges(gsub)}")                                                                           # Print number of final edges
    print("Edges removed from preprocess: {:.2f}%".format(100*(1 - nx.number_of_edges(gsub)/nx.number_of_edges(preprocess))))   # Print percentage of edges removed
    print("Edges per nodes: {:.2f}".format(len(preprocess)/len(gsub)))                                                          # Print edges per node ratio

    # Generate histogram for preprocessed graph
    histogram(seed, preprocess)

def network_gen(invalid, seed):
    ng = network(invalid, seed)             # Generate network
    ng_preprocess = preprocess(ng)          # Preprocess the network
    ng_gsub = graph(seed, ng_preprocess)    # Generate subgraph

    # Return original, preprocessed, and subgraph networks
    return ng, ng_preprocess, ng_gsub
