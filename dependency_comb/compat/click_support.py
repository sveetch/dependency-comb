"""
Expose a 'click' module that can be 'rich-click' if installed else fallback to use
original 'click' module.

* RICH_CLICK_ENABLED: Will be true only if 'rich-click' is installed;
* ABORT_ENDING: Ending character of 'click.Abort()' change depending 'rich-click' is
  available or not;
"""
try:
    import rich_click as click  # noqa: F401,F403
except ImportError:
    import click  # noqa: F401,F403
    RICH_CLICK_ENABLED = False
    ABORT_ENDING = "!"
else:
    RICH_CLICK_ENABLED = True
    ABORT_ENDING = "."
