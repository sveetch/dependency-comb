# First try to get Rich
try:
    import rich
except ImportError:
    RICH_ENABLED = False
    # Set null value onto module name so it can be imported without error
    rich = None
else:
    RICH_ENABLED = True

# Then Rich-click
try:
    import rich_click
except ImportError:
    RICH_CLICK_ENABLED = False
    # Set null value onto module name so it can be imported without error
    rich_click = None
else:
    RICH_CLICK_ENABLED = True
