"""
Social Graph - Network-Aware Agent Intelligence

Graph-based models for agent relationships and interactions:
- Nodes (agents, users, entities)
- Edges (relationships, interactions)
- Graph Analysis
- Network Dynamics
- Influence Propagation
- Community Detection
"""
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict, deque
import uuid
import math


# ============================================================
# Graph Structure
# ============================================================

class NodeType:
    AGENT = "agent"
    USER = "user"
    GROUP = "group"
    ORGANIZATION = "organization"
    RESOURCE = "resource"
    TOPIC = "topic"


class RelationshipType:
    KNOWS = "knows"
    WORKS_WITH = "works_with"
    REPORTS_TO = "reports_to"
    MENTORS = "mentors"
    COMPETITOR = "competitor"
    PROVIDER = "provider"
    CUSTOMER = "customer"
    ALLIES = "allies"
    FOLLOWS = "follows"
    REFERENCES = "references"


@dataclass
class GraphNode:
    """Node in social graph"""
    id: str
    node_type: str = "agent"
    
    name: str = ""
    attributes: Dict = field(default_factory=dict)
    
    centrality: float = 0
    influence: float = 0
    prestige: float = 0
    
    status: str = "active"  # active, inactive, pending
    last_active: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "node_type": self.node_type,
            "name": self.name,
            "centrality": self.centrality,
            "influence": self.influence,
            "status": self.status,
        }


@dataclass
class GraphEdge:
    """Edge (relationship)"""
    id: str
    source: str
    target: str
    
    relationship_type: str = "knows"
    
    weight: float = 0.5  # 0-1
    strength_type: str = "neutral"  # strong, weak, neutral
    
    directed: bool = False
    
    created_at: str = ""
    last_interaction: str = ""
    interaction_count: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "relationship_type": self.relationship_type,
            "weight": self.weight,
        }


@dataclass
class SocialGraph:
    """Full social graph"""
    id: str
    name: str = ""
    
    nodes: Dict[str, GraphNode] = field(default_factory=dict)
    edges: List[GraphEdge] = field(default_factory=list)
    
    # Adjacency list
    adjacency: Dict[str, List[Tuple[str, float]] = field(default_factory=lambda: defaultdict(list))
    reverse_adjacency: Dict[str, List[Tuple[str, float]]] = field(default_factory=lambda: defaultdict(list))
    
    is_directed: bool = False
    is_weighted: bool = True
    
    # Metrics
    density: Optional[float] = None
    clustering_coefficient: Optional[float] = None
    average_path_length: Optional[float] = None
    
    # Communities
    communities: List[List[str]] = field(default_factory=list)
    
    def add_node(self, node: GraphNode):
        """Add node"""
        self.nodes[node.id] = node
    
    def add_edge(self, edge: GraphEdge):
        """Add edge"""
        self.edges.append(edge)
        
        # Update adjacency
        self.adjacency[edge.source].append((edge.target, edge.weight))
        if not edge.directed:
            self.adjacency[edge.target].append((edge.source, edge.weight))
        else:
            self.reverse_adjacency[edge.target].append((edge.source, edge.weight))
    
    def node_count(self) -> int:
        """Number of nodes"""
        return len(self.nodes)
    
    def edge_count(self) -> int:
        """Number of edges"""
        return len(self.edges)
    
    def get_neighbors(self, node_id: str) -> List[str]:
        """Get neighbors"""
        return [n[0] for n in self.adjacency.get(node_id, [])]
    
    def calculate_density(self) -> float:
        """Calculate density"""
        n = self.node_count()
        if n <= 1:
            return 0
        
        max_edges = n * (n - 1) if self.is_directed else n * (n - 1) / 2
        self.density = self.edge_count() / max_edges
        return self.density
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "node_count": self.node_count(),
            "edge_count": self.edge_count(),
            "density": self.calculate_density(),
            "communities": self.communities,
        }


# ============================================================
# Graph Analysis
# ============================================================

@dataclass
class CentralityMetrics:
    """Centrality metrics"""
    node_id: str
    
    degree_centrality: float = 0
    in_degree_centrality: float = 0
    out_degree_centrality: float = 0
    
    betweenness_centrality: float = 0
    closeness_centrality: float = 0
    eigenvector_centrality: float = 0
    
    page_rank: float = 0
    
    def calculate_degree(self, graph: SocialGraph):
        """Calculate degree centrality"""
        n = graph.node_count()
        if n > 1:
            neighbors = len(graph.get_neighbors(self.node_id))
            self.degree_centrality = neighbors / (n - 1)
    
    def calculate_pagerank(self, graph: SocialGraph, damping: float = 0.85, iterations: int = 100):
        """Calculate PageRank"""
        n = graph.node_count()
        if n == 0:
            return
        
        # Initialize
        ranks = {node: 1/n for node in graph.nodes}
        
        for _ in range(iterations):
            new_ranks = {}
            for node_id in graph.nodes:
                rank = (1 - damping) / n
                
                for src, _ in graph.reverse_adjacency.get(node_id, []):
                    neighbors = graph.get_neighbors(src)
                    if neighbors:
                        rank += damping * ranks[src] / len(neighbors)
                
                new_ranks[node_id] = rank
            
            ranks = new_ranks
        
        self.page_rank = ranks.get(self.node_id, 0)
    
    def to_dict(self) -> Dict:
        return {
            "node_id": self.node_id,
            "degree_centrality": self.degree_centrality,
            "betweenness_centrality": self.betweenness_centrality,
            "page_rank": self.page_rank,
        }


@dataclass
class PathAnalysis:
    """Path analysis"""
    from_node: str
    to_node: str
    
    shortest_path: List[str] = field(default_factory=list)
    shortest_path_length: Optional[float] = None
    
    all_paths: List[List[str]] = field(default_factory=list)
    path_count: int = 0
    
    def bfs(self, graph: SocialGraph) -> List[str]:
        """BFS to find shortest path"""
        if self.from_node == self.to_node:
            return [self.from_node]
        
        visited = {self.from_node}
        queue = deque([(self.from_node, [self.from_node])])
        
        while queue:
            current, path = queue.popleft()
            
            for neighbor, _ in graph.adjacency.get(current, []):
                if neighbor == self.to_node:
                    self.shortest_path = path + [neighbor]
                    self.shortest_path_length = len(path)
                    return self.shortest_path
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return self.shortest_path
    
    def to_dict(self) -> Dict:
        return {
            "from": self.from_node,
            "to": self.to_node,
            "shortest_path": self.shortest_path,
            "shortest_path_length": self.shortest_path_length,
        }


# ============================================================
# Community Detection
# ============================================================

@dataclass
class Community:
    """Community"""
    id: str
    members: List[str] = field(default_factory=list)
    
    size: int = 0
    density: float = 0
    conductance: float = 0
    
    leaders: List[str] = field(default_factory=list)
    bridge_members: List[str] = field(default_factory=list)
    peripheral_members: List[str] = field(default_factory=list)
    
    def calculate_metrics(self, graph: SocialGraph):
        """Calculate community metrics"""
        self.size = len(self.members)
        
        if self.size < 2:
            return
        
        # Internal edges
        internal = 0
        for m in self.members:
            for n, _ in graph.adjacency.get(m, []):
                if n in self.members:
                    internal += 1
        
        # Density
        max_internal = self.size * (self.size - 1) / 2
        self.density = internal / max_internal if max_internal > 0 else 0
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "size": self.size,
            "density": self.density,
            "leaders": self.leaders,
        }


class CommunityDetection:
    """Community detection algorithms"""
    
    @staticmethod
    def louvain(graph: SocialGraph) -> List[Community]:
        """Louvain community detection"""
        # Simplified implementation
        communities = []
        
        # Initialize each node as community
        node_to_community = {node: i for i, node in enumerate(graph.nodes)}
        
        # Merge communities
        merged = True
        while merged:
            merged = False
            # Would need full implementation
        
        # Return as communities
        for i in range(len(set(node_to_community.values())):
            members = [n for n, c in node_to_community.items() if c == i]
            if members:
                community = Community(id=str(i), members=members)
                community.calculate_metrics(graph)
                communities.append(community)
        
        graph.communities = [c.members for c in communities]
        return communities


# ============================================================
# Influence Propagation
# ============================================================

class InfluenceModel:
    """Influence model"""
    LINEAR_THRESHOLD = "linear_threshold"
    INDEPENDENT_CASCADE = "independent_cascade"
    TRIGGERING = "triggering"


@dataclass
class InfluenceSpread:
    """Influence spread"""
    node_id: str
    
    reached_nodes: List[str] = field(default_factory=list)
    reach_count: int = 0
    
    spread_over_time: Dict[str, int] = field(default_factory=dict)
    
    cascade: List[Dict] = field(default_factory=list)
    
    def simulate(self, graph: SocialGraph, seed: List[str],
                 threshold: float = 0.5, iterations: int = 100):
        """Simulate influence spread"""
        activated = set(seed)
        frontier = set(seed)
        
        reached_nodes = []
        
        for _ in range(iterations):
            new_activated = set()
            
            for node in frontier:
                neighbors = graph.get_neighbors(node)
                
                # Count activated neighbors
                activated_neighbors = len([n for n in neighbors if n in activated])
                threshold_needed = int(len(neighbors) * threshold)
                
                if activated_neighbors >= threshold_needed:
                    for n in neighbors:
                        if n not in activated:
                            new_activated.add(n)
            
            if not new_activated:
                break
            
            activated |= new_activated
            frontier = new_activated
            reached_nodes.extend(list(new_activated))
        
        self.reached_nodes = list(activated)
        self.reach_count = len(activated)
        
        return self.reached_nodes
    
    def to_dict(self) -> Dict:
        return {
            "node_id": self.node_id,
            "reach_count": self.reach_count,
            "cascade": self.cascade,
        }


# ============================================================
# Network Embeddings
# ============================================================

class EmbeddingType:
    NODE2VEC = "node2vec"
    DEEPWALK = "deepwalk"
    LINE = "line"
    GRAPH_SAGE = "graph_sage"


@dataclass
class NodeEmbedding:
    """Node embedding"""
    node_id: str
    embedding: List[float] = field(default_factory=list)
    
    embedding_type: str = "node2vec"
    similar_nodes: List[Tuple[str, float]] = field(default_factory=list)
    
    def find_similar(self, all_embeddings: Dict[str, List[float]], top_k: int = 10):
        """Find similar nodes"""
        if not self.embedding:
            return []
        
        similarities = []
        for node_id, emb in all_embeddings.items():
            if node_id == self.node_id:
                continue
            
            # Cosine similarity
            sim = self._cosine(self.embedding, emb)
            similarities.append((node_id, sim))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        self.similar_nodes = similarities[:top_k]
        
        return self.similar_nodes
    
    def _cosine(self, a: List[float], b: List[float]) -> float:
        """Cosine similarity"""
        if len(a) != len(b) or not a:
            return 0
        
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0
    
    def to_dict(self) -> Dict:
        return {
            "node_id": self.node_id,
            "embedding": self.embedding[:10],  # First 10 dims
            "similar_nodes": self.similar_nodes[:5],
        }


# ============================================================
# Factory
# ============================================================

def create_social_graph(id: str, name: str = "") -> SocialGraph:
    """Create social graph"""
    return SocialGraph(id=id, name=name)


def add_agent_to_graph(graph: SocialGraph, agent_id: str, name: str = "") -> GraphNode:
    """Add agent node"""
    node = GraphNode(id=agent_id, node_type=NodeType.AGENT, name=name)
    graph.add_node(node)
    return node


def create_relationship(graph: SocialGraph, src: str, tgt: str,
                        rel_type: str = RelationshipType.KNOWS,
                        weight: float = 0.5) -> GraphEdge:
    """Create relationship"""
    edge = GraphEdge(
        id=str(uuid.uuid4()),
        source=src,
        target=tgt,
        relationship_type=rel_type,
        weight=weight,
    )
    graph.add_edge(edge)
    return edge


__all__ = [
    'NodeType', 'RelationshipType',
    'GraphNode', 'GraphEdge', 'SocialGraph',
    'CentralityMetrics', 'PathAnalysis',
    'Community', 'CommunityDetection',
    'InfluenceSpread', 'InfluenceModel',
    'NodeEmbedding', 'EmbeddingType',
    'create_social_graph', 'add_agent_to_graph', 'create_relationship'
]