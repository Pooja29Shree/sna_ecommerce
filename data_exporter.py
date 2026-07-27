import pandas as pd

def export_network(nodes, edges, prefix=""):
    """
    nodes: list of dicts with keys: ['Product ID', 'Product Name', 'Category']
    edges: list of dicts with keys: ['Source Product ID', 'Target Product ID']
    """
    # Create DataFrames
    df_nodes = pd.DataFrame(nodes)
    if not df_nodes.empty:
        # Ensure correct column names
        df_nodes = df_nodes[['Product ID', 'Product Name', 'Category']]
        # Drop duplicates by Product ID
        df_nodes = df_nodes.drop_duplicates(subset=['Product ID'])
    else:
        df_nodes = pd.DataFrame(columns=['Product ID', 'Product Name', 'Category'])

    df_edges = pd.DataFrame(edges)
    if not df_edges.empty:
        df_edges = df_edges[['Source Product ID', 'Target Product ID']]
        # Add Type = Directed
        df_edges['Type'] = 'Directed'
        df_edges = df_edges.drop_duplicates()
    else:
        df_edges = pd.DataFrame(columns=['Source Product ID', 'Target Product ID', 'Type'])

    # Export to CSV
    df_nodes.to_csv(f"{prefix}nodes.csv", index=False)
    df_edges.to_csv(f"{prefix}edges.csv", index=False)

    # Export to Excel
    with pd.ExcelWriter(f"{prefix}recommendation_network.xlsx", engine='openpyxl') as writer:
        df_nodes.to_excel(writer, sheet_name='Nodes', index=False)
        df_edges.to_excel(writer, sheet_name='Edges', index=False)

    print(f"Data exported successfully to {prefix}nodes.csv, {prefix}edges.csv, and {prefix}recommendation_network.xlsx")
