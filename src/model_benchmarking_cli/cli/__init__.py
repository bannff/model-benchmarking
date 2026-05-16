from .main import main
from .pipeline import pipeline
from .evals import evals
from .taxonomy import taxonomy

# Wire up the CLI hierarchy
main.add_command(pipeline)
main.add_command(evals)
main.add_command(taxonomy)

def start():
    """Entry point for the mbenchmark console script."""
    main()

__all__ = ["main", "start"]
