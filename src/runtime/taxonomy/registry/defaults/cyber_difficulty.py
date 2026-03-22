from ...schema import TaxonomySpec, TaxonomyDimension, TaxonomyNode

# -------------------------------------------------------------------------

# Difficulty dimension - Normalized difficulty levels

difficulty_nodes = [
    TaxonomyNode(
        id="level0",
        name="Level 0 - Trivial",
        description="Basic recall, simple lookups",
        aliases=["trivial", "beginner"],
    ),
    TaxonomyNode(
        id="level1",
        name="Level 1 - Easy",
        description="Single-step problems, basic concepts",
        aliases=["easy", "simple"],
    ),
    TaxonomyNode(
        id="level2",
        name="Level 2 - Medium",
        description="Multi-step problems, combined concepts",
        aliases=["medium", "intermediate"],
    ),
    TaxonomyNode(
        id="level3",
        name="Level 3 - Hard",
        description="Complex problems requiring deep understanding",
        aliases=["hard", "advanced"],
    ),
    TaxonomyNode(
        id="level4",
        name="Level 4 - Expert",
        description="Novel problems requiring creative solutions",
        aliases=["expert", "very_hard"],
    ),
    TaxonomyNode(
        id="level5",
        name="Level 5 - Research",
        description="Open research problems",
        aliases=["research", "cutting_edge"],
    ),
]

difficulty_dim = TaxonomyDimension(
    id="difficulty",
    name="Difficulty",
    description="Normalized difficulty level",
    required=False,
    multi_select=False,
    nodes=difficulty_nodes,
)

