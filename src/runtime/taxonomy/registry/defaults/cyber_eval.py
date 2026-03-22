from ...schema import TaxonomySpec, TaxonomyDimension, TaxonomyNode

# -------------------------------------------------------------------------

# Evaluation Type dimension - What kind of evaluation

eval_type_nodes = [
    TaxonomyNode(
        id="knowledge",
        name="Knowledge",
        description="Testing factual knowledge and recall",
        aliases=["factual", "recall"],
    ),
    TaxonomyNode(
        id="reasoning",
        name="Reasoning",
        description="Testing logical reasoning and problem-solving",
        aliases=["logic", "problem_solving"],
    ),
    TaxonomyNode(
        id="practical",
        name="Practical",
        description="Hands-on task execution",
        aliases=["hands_on", "execution"],
    ),
    TaxonomyNode(
        id="creative",
        name="Creative",
        description="Novel solution generation",
        aliases=["novel", "innovative"],
    ),
]

eval_type_dim = TaxonomyDimension(
    id="eval_type",
    name="Evaluation Type",
    description="The type of evaluation being performed",
    required=False,
    multi_select=False,
    nodes=eval_type_nodes,
)

