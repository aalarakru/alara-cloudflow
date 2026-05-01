# Cloud Load Balancing Network — Maximum Flow Optimization

## 1. Real-World Problem Context

Modern cloud computing platforms such as AWS, Microsoft Azure, and Google Cloud
serve millions of users across different geographic regions simultaneously.
Each request travels through a complex infrastructure: from the user's device,
through regional entry points, load balancers, and server clusters, before
reaching the central data processing core.

A critical challenge for cloud providers is **bandwidth capacity management** —
ensuring that no single link in this infrastructure becomes overloaded, while
maximizing the total data throughput the system can deliver.

This project models such an infrastructure and applies the **Maximum Flow
algorithm** to determine the highest possible data throughput from the internet
(source) to the data center core (sink).

---

## 2. Problem Definition

**Question:** Given a cloud infrastructure with capacity-constrained links,
what is the maximum amount of data (in Mbps) that can be routed from all
user zones to the central data center core simultaneously?

**Constraints:**
- Each network link has a maximum bandwidth capacity (Mbps)
- Traffic flows in one direction (directed graph)
- No link can carry more traffic than its stated capacity

---

## 3. Network Model

The network is represented as a **directed weighted graph** where:

- **Nodes** represent network components (user zones, load balancers, server clusters)
- **Edges** represent network links between components
- **Edge weights** represent maximum bandwidth capacity in **Mbps**

The graph has **10 nodes** and **15 directed edges**.

---

## 4. Nodes and Edges

### Nodes

| Node | Role | Description |
|------|------|-------------|
| S | Source | Virtual source — all incoming internet traffic |
| US | User Zone | North American user zone |
| EU | User Zone | European user zone |
| AS | User Zone | Asian user zone |
| LB1 | Load Balancer | Primary load balancer (West infrastructure) |
| LB2 | Load Balancer | Secondary load balancer (East infrastructure) |
| SC1 | Server Cluster | Server Cluster 1 |
| SC2 | Server Cluster | Server Cluster 2 |
| SC3 | Server Cluster | Server Cluster 3 |
| T | Sink | Central Data Center Core |

### Edges (Network Links)

| Source | Target | Capacity (Mbps) | Description |
|--------|--------|-----------------|-------------|
| S | US | 500 | Internet → North America |
| S | EU | 400 | Internet → Europe |
| S | AS | 350 | Internet → Asia |
| US | LB1 | 300 | North America → Load Balancer 1 |
| US | LB2 | 250 | North America → Load Balancer 2 |
| EU | LB1 | 200 | Europe → Load Balancer 1 |
| EU | LB2 | 250 | Europe → Load Balancer 2 |
| AS | LB2 | 300 | Asia → Load Balancer 2 |
| LB1 | SC1 | 250 | Load Balancer 1 → Server Cluster 1 |
| LB1 | SC2 | 200 | Load Balancer 1 → Server Cluster 2 |
| LB2 | SC2 | 150 | Load Balancer 2 → Server Cluster 2 |
| LB2 | SC3 | 300 | Load Balancer 2 → Server Cluster 3 |
| SC1 | T | 280 | Server Cluster 1 → Data Center Core |
| SC2 | T | 320 | Server Cluster 2 → Data Center Core |
| SC3 | T | 250 | Server Cluster 3 → Data Center Core |

**Column Definitions:**
- `capacity_mbps`: Maximum bandwidth the link can carry (Megabits per second)
- All values are hypothetical but representative of real cloud infrastructure ratios

---

## 5. Selected Algorithm — Maximum Flow

**Algorithm:** Maximum Flow (Push-Relabel, via NetworkX)

**Why Maximum Flow?**
The problem is a classic maximum flow problem: we want to push as much data
as possible from a single source (S) to a single sink (T), subject to capacity
constraints on each directed edge.

**How it works:**
The Push-Relabel algorithm maintains a "preflow" and iteratively pushes excess
flow from nodes toward the sink. It is more efficient than Ford-Fulkerson for
dense graphs (O(V²√E) complexity).

---

## 6. Python Implementation

The solution is built using **Python 3** with the following libraries:

| Library | Purpose |
|---------|---------|
| `networkx` | Graph creation and maximum flow algorithm |
| `matplotlib` | Network visualization |
| `pandas` | Loading and processing CSV data |

**The graph was created using NetworkX as a DiGraph (directed graph).**
Nodes represent cloud infrastructure components. Edges represent network links.
The `capacity` attribute on each edge represents the maximum bandwidth in Mbps.
The maximum flow algorithm calculates the highest possible data throughput
from the source node (S) to the sink node (T).

See `src/solution.py` for the full implementation with inline comments.

---

## 7. Results

> Run the code first to generate the visualization and output files.

- **Maximum Flow:** See `results/solution_output.txt`
- **Network Graph:** See `results/network_visualization.png`

---

## 8. Managerial Interpretation

The maximum flow result tells cloud infrastructure managers the **theoretical
upper bound** on system throughput given current link capacities.

**Key insights:**

1. **Bottleneck links** (edges where flow = capacity) are the most critical.
   Upgrading these links directly increases overall throughput.

2. **Load Balancer 2 (LB2)** aggregates traffic from all three user regions.
   It is a high-risk single point of failure — redundancy is recommended.

3. **Server Cluster 2 (SC2)** receives traffic from both load balancers,
   making it the most utilized server cluster.

4. If the company wants to handle more traffic, the bottleneck links should
   be upgraded before adding new servers — otherwise new servers would be idle.

---

## 9. How to Run the Code

### Prerequisites

```bash
pip install -r requirements.txt
```

### Run the Solution

```bash
python src/solution.py
```

This will:
1. Load `data/network_data.csv`
2. Build the directed graph
3. Run the maximum flow algorithm
4. Save the visualization to `results/network_visualization.png`
5. Save results to `results/solution_output.txt`

---

## 10. References

See `references/references.md` for full references.

- NetworkX Documentation: https://networkx.org/documentation/stable/
- Goldberg, A. V., & Tarjan, R. E. (1988). A new approach to the maximum-flow problem. *Journal of the ACM*, 35(4), 921–940.
- Ahuja, R. K., Magnanti, T. L., & Orlin, J. B. (1993). *Network Flows: Theory, Algorithms, and Applications*. Prentice Hall.
