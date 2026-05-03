# =============================================================================
# Cloud Load Balancing Network — Maximum Flow Analysis
# MIS Network Optimization Project
# =============================================================================
#
# SCENARIO:
# This project models a global cloud computing infrastructure (similar to AWS
# or Microsoft Azure). User requests from three geographic zones (North America,
# Europe, Asia) travel through load balancers and server clusters before
# reaching the central data center core.
#
# GOAL:
# Find the maximum amount of data (Mbps) that can flow from the internet
# (source) to the data center core (sink) without exceeding any link's capacity.
#
# ALGORITHM:
# Maximum Flow — using NetworkX's push-relabel algorithm.
# This algorithm finds the highest possible throughput in a capacity-constrained
# directed network.
# =============================================================================

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import os


# -----------------------------------------------------------------------------
# STEP 1: LOAD DATA
# -----------------------------------------------------------------------------
# We read the network topology from a CSV file.
# Each row is a directed link (edge) with a maximum bandwidth capacity in Mbps.

def load_network(csv_path):
    """Load network edge data from a CSV file into a DataFrame."""
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} links from {csv_path}")
    print(df[['source', 'target', 'capacity_mbps']].to_string(index=False))
    return df


# -----------------------------------------------------------------------------
# STEP 2: BUILD THE DIRECTED GRAPH
# -----------------------------------------------------------------------------
# We use a DiGraph (Directed Graph) because data flows in one direction only:
# from user zones → load balancers → server clusters → data center core.
# Each edge carries a 'capacity' attribute representing maximum Mbps.

def build_graph(df):
    """Build a directed graph from the edge DataFrame."""
    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(
            row['source'],
            row['target'],
            capacity=int(row['capacity_mbps'])
        )
    print(f"\nGraph created: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


# -----------------------------------------------------------------------------
# STEP 3: RUN MAXIMUM FLOW ALGORITHM
# -----------------------------------------------------------------------------
# NetworkX's maximum_flow() uses the Push-Relabel algorithm by default.
# - SOURCE (S): virtual node representing all incoming internet traffic
# - SINK (T): the central data center core
#
# The algorithm finds which links carry how much traffic such that:
#   1. No link exceeds its capacity
#   2. Total flow from S to T is maximized

def run_max_flow(G, source='S', sink='T'):
    """
    Run the maximum flow algorithm and return:
    - flow_value: total Mbps that can flow from S to T
    - flow_dict: dictionary showing exact flow on each edge
    """
    flow_value, flow_dict = nx.maximum_flow(G, source, sink)
    return flow_value, flow_dict


# -----------------------------------------------------------------------------
# STEP 3b: MIN-CUT ANALYSIS
# -----------------------------------------------------------------------------
# The Max-Flow Min-Cut theorem states that the maximum flow equals the capacity
# of the minimum cut — the smallest set of edges whose removal disconnects S from T.
# These are the true bottleneck edges of the network.

def run_min_cut(G, source='S', sink='T'):
    """
    Find the minimum cut of the network.
    Returns cut_value and the two partitions of nodes.
    """
    cut_value, (reachable, non_reachable) = nx.minimum_cut(G, source, sink)

    print(f"\n{'='*55}")
    print(f"  MIN-CUT ANALYSIS  (Max-Flow Min-Cut Theorem)")
    print(f"{'='*55}")
    print(f"  Min-Cut Value = {cut_value} Mbps  (equals Maximum Flow)")
    print(f"  Source-side partition : {sorted(reachable)}")
    print(f"  Sink-side partition   : {sorted(non_reachable)}")
    print(f"\n  Cut edges (true bottlenecks):")
    for u in reachable:
        for v in non_reachable:
            if G.has_edge(u, v):
                cap = G[u][v]['capacity']
                print(f"    {u} → {v}  |  capacity: {cap} Mbps")

    return cut_value, reachable, non_reachable


# -----------------------------------------------------------------------------
# STEP 3c: SENSITIVITY ANALYSIS
# -----------------------------------------------------------------------------
# For each bottleneck edge, we estimate how much upgrading it by +50 Mbps
# would increase the overall maximum flow.

def sensitivity_analysis(G, flow_dict, flow_value, source='S', sink='T'):
    """
    For each saturated (bottleneck) edge, temporarily increase its capacity
    by 50 Mbps and recompute max flow to see the gain.
    """
    print(f"\n{'='*55}")
    print(f"  SENSITIVITY ANALYSIS  (+50 Mbps upgrade simulation)")
    print(f"{'='*55}")
    print(f"  {'Edge':<12} {'Current Cap':>12} {'New Flow':>10} {'Gain':>8}")
    print(f"  {'-'*44}")

    for u, v, data in G.edges(data=True):
        flow = flow_dict.get(u, {}).get(v, 0)
        if flow == data['capacity']:          # saturated edge
            original_cap = data['capacity']
            G[u][v]['capacity'] = original_cap + 50
            new_flow, _ = nx.maximum_flow(G, source, sink)
            gain = new_flow - flow_value
            G[u][v]['capacity'] = original_cap   # restore
            print(f"  {u}→{v:<8} {original_cap:>10} Mbps "
                  f"{new_flow:>8} Mbps  +{gain} Mbps")


# -----------------------------------------------------------------------------
# STEP 4: VISUALIZE THE NETWORK
# -----------------------------------------------------------------------------
# We draw the network in layers to clearly show the flow path:
#   Layer 0 (top)   : S — Source (all internet traffic)
#   Layer 1         : US, EU, AS — Geographic user zones
#   Layer 2         : LB1, LB2 — Load balancers
#   Layer 3         : SC1, SC2, SC3 — Server clusters
#   Layer 4 (bottom): T — Data center core (sink)
#
# Edge labels show: actual_flow / maximum_capacity

def visualize(G, flow_dict, flow_value, output_path='results/network_visualization.png'):
    """Draw the network graph and save it as a PNG image."""

    # Manual positions for a clean hierarchical layout
    pos = {
        'S':   (4.0, 4.0),
        'US':  (1.5, 3.0),
        'EU':  (4.0, 3.0),
        'AS':  (6.5, 3.0),
        'LB1': (2.5, 2.0),
        'LB2': (5.5, 2.0),
        'SC1': (1.0, 1.0),
        'SC2': (4.0, 1.0),
        'SC3': (7.0, 1.0),
        'T':   (4.0, 0.0),
    }

    # Node labels for display
    labels = {
        'S':   'S\n(Internet)',
        'US':  'US\nUsers',
        'EU':  'EU\nUsers',
        'AS':  'AS\nUsers',
        'LB1': 'LB1\nLoad Bal.',
        'LB2': 'LB2\nLoad Bal.',
        'SC1': 'SC1\nServer',
        'SC2': 'SC2\nServer',
        'SC3': 'SC3\nServer',
        'T':   'T\n(Data Center)',
    }

    # Color nodes by their role in the network
    color_map = {
        'S':   '#e74c3c',
        'US':  '#3498db', 'EU':  '#3498db', 'AS':  '#3498db',
        'LB1': '#f39c12', 'LB2': '#f39c12',
        'SC1': '#2ecc71', 'SC2': '#2ecc71', 'SC3': '#2ecc71',
        'T':   '#9b59b6'
    }
    node_colors = [color_map[n] for n in G.nodes()]

    # Edge labels: show how much flow is actually used out of capacity
    edge_labels = {}
    for u, v, data in G.edges(data=True):
        flow = flow_dict.get(u, {}).get(v, 0)
        cap  = data['capacity']
        edge_labels[(u, v)] = f"{flow}/{cap}"

    # Color and thickness based on utilization %
    # Green (low) → Yellow (medium) → Red (saturated bottleneck)
    edge_colors = []
    edge_widths = []
    for u, v, data in G.edges(data=True):
        flow = flow_dict.get(u, {}).get(v, 0)
        util = flow / data['capacity'] if data['capacity'] > 0 else 0
        edge_widths.append(1.0 + util * 5.0)   # 1px (empty) to 6px (full)
        if util == 1.0:
            edge_colors.append('#e74c3c')   # red — fully saturated bottleneck
        elif util >= 0.75:
            edge_colors.append('#f39c12')   # orange — high utilization
        else:
            edge_colors.append('#2ecc71')   # green — capacity available

    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor('#f8f9fa')
    ax.set_facecolor('#f8f9fa')

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                           node_size=2200, ax=ax, alpha=0.95)
    nx.draw_networkx_labels(G, pos, labels=labels,
                            font_size=8, font_weight='bold', ax=ax)

    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, arrows=True,
                           arrowsize=20, width=edge_widths, ax=ax,
                           connectionstyle='arc3,rad=0.08', alpha=0.85)

    # Draw edge labels
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                  font_size=7.5, ax=ax,
                                  bbox=dict(boxstyle='round,pad=0.2',
                                            fc='white', alpha=0.7))

    # Legend
    legend_elements = [
        mpatches.Patch(color='#e74c3c', label='Source — S (All Internet Traffic)'),
        mpatches.Patch(color='#3498db', label='User Zones — US / EU / AS'),
        mpatches.Patch(color='#f39c12', label='Load Balancers — LB1 / LB2'),
        mpatches.Patch(color='#2ecc71', label='Server Clusters — SC1 / SC2 / SC3'),
        mpatches.Patch(color='#9b59b6', label='Sink — T (Data Center Core)'),
        mpatches.Patch(color='#2ecc71', label='Green Edge = Low utilization (<75%)'),
        mpatches.Patch(color='#f39c12', label='Orange Edge = High utilization (≥75%)'),
        mpatches.Patch(color='#e74c3c', label='Red Edge = Bottleneck (100% saturated) — thicker = more flow'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=8,
              framealpha=0.9)

    ax.set_title(
        f'Cloud Load Balancing Network\nMaximum Flow: {flow_value} Mbps   |   '
        f'Edge Labels: actual_flow / capacity',
        fontsize=13, fontweight='bold', pad=15
    )
    ax.axis('off')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nVisualization saved → {output_path}")


# -----------------------------------------------------------------------------
# STEP 5: SAVE RESULTS TO TEXT FILE
# -----------------------------------------------------------------------------

def save_results(flow_value, flow_dict, G,
                 output_path='results/solution_output.txt'):
    """Write the flow results and managerial interpretation to a text file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w') as f:
        f.write("=" * 55 + "\n")
        f.write("  CLOUD NETWORK — MAXIMUM FLOW ANALYSIS RESULTS\n")
        f.write("=" * 55 + "\n\n")

        f.write(f"Maximum Throughput (Source → Sink): {flow_value} Mbps\n\n")

        f.write("Flow on Each Link:\n")
        f.write("-" * 40 + "\n")
        for u, targets in flow_dict.items():
            for v, flow in targets.items():
                cap = G[u][v]['capacity']
                util = (flow / cap * 100) if cap > 0 else 0
                status = " ← BOTTLENECK" if flow == cap else ""
                f.write(f"  {u:4s} → {v:4s} : {flow:4d} / {cap:4d} Mbps "
                        f"({util:.0f}%){status}\n")

        f.write("\n" + "-" * 40 + "\n")
        f.write("MANAGERIAL INTERPRETATION:\n")
        f.write("-" * 40 + "\n")
        f.write(
            f"The network can handle a maximum of {flow_value} Mbps of data\n"
            f"traffic from all user zones to the data center core.\n\n"
            f"Bottleneck links (100% utilized) represent the weakest points\n"
            f"in the infrastructure. Upgrading these links' capacity would\n"
            f"directly increase overall network throughput.\n\n"
            f"Load Balancer 2 (LB2) handles traffic from all three regions\n"
            f"and is likely a critical node — redundancy is recommended.\n"
        )

    print(f"Results saved → {output_path}")


# -----------------------------------------------------------------------------
# MAIN — Run Everything
# -----------------------------------------------------------------------------

if __name__ == "__main__":

    print("\n" + "=" * 55)
    print("  CLOUD NETWORK MAXIMUM FLOW — MIS PROJECT")
    print("=" * 55 + "\n")

    # Paths
    DATA_PATH  = os.path.join(os.path.dirname(__file__),
                              '..', 'data', 'network_data.csv')
    VIZ_PATH   = os.path.join(os.path.dirname(__file__),
                              '..', 'results', 'network_visualization.png')
    OUT_PATH   = os.path.join(os.path.dirname(__file__),
                              '..', 'results', 'solution_output.txt')

    # Run pipeline
    df            = load_network(DATA_PATH)
    G             = build_graph(df)
    flow_val, fd  = run_max_flow(G)

    print(f"\n{'='*55}")
    print(f"  MAXIMUM FLOW  =  {flow_val} Mbps")
    print(f"{'='*55}\n")

    run_min_cut(G)
    sensitivity_analysis(G, fd, flow_val)

    visualize(G, fd, flow_val, VIZ_PATH)
    save_results(flow_val, fd, G, OUT_PATH)

    print("\nAll done! Check the results/ folder.")
