"""
Try get 'rich' module, expose either the true 'rich' module if available else it will
be a null value.
"""
try:
    import rich  # noqa: F401,F403
except ImportError:
    RICH_ENABLED = False
    # Set null value onto module name so it can be imported without error
    rich = None
else:
    RICH_ENABLED = True
