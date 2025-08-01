"""Global configuration state and functions for management."""

from __future__ import annotations

import threading
import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from skore._sklearn.types import PlotBackend

_global_config: dict[str, Any] = {
    "show_progress": True,
    "plot_backend": "matplotlib",
}
_threadlocal = threading.local()


def _get_threadlocal_config() -> dict[str, Any]:
    """Get a threadlocal **mutable** configuration.

    If the configuration does not exist, copy the default global configuration.
    """
    if not hasattr(_threadlocal, "global_config"):
        _threadlocal.global_config = _global_config.copy()
    return _threadlocal.global_config


def get_config() -> dict[str, Any]:
    """Retrieve current values for configuration set by :func:`set_config`.

    Returns
    -------
    config : dict
        Keys are parameter names that can be passed to :func:`set_config`.

    See Also
    --------
    config_context : Context manager for skore configuration.
    set_config : Set skore configuration.

    Examples
    --------
    >>> import skore
    >>> config = skore.get_config()
    >>> config.keys()
    dict_keys([...])
    """
    # Return a copy of the threadlocal configuration so that users will
    # not be able to modify the configuration with the returned dict.
    return _get_threadlocal_config().copy()


def set_config(
    *,
    show_progress: bool | None = None,
    plot_backend: PlotBackend | None = None,
) -> None:
    """Set skore configuration.

    Setting the configuration affects global settings meaning that it will be used
    by all skore functions and classes, even in the processes and threads spawned by
    skore.

    Parameters
    ----------
    show_progress : bool, default=None
        If True, show progress bars. Otherwise, do not show them.

    plot_backend : {"matplotlib", "plotly"}, default=None
        The plotting backend to be used.

        - `"matplotlib"`: Use Matplotlib for plotting
        - `"plotly"`: Use Plotly for plotting
        - `None`: Plotting backend is unchanged

    See Also
    --------
    config_context : Context manager for skore configuration.
    get_config : Retrieve current values of the configuration.

    Examples
    --------
    >>> # xdoctest: +SKIP
    >>> from skore import set_config
    >>> set_config(show_progress=False, plot_backend="plotly")
    """
    local_config = _get_threadlocal_config()

    if show_progress is not None:
        local_config["show_progress"] = show_progress
    if plot_backend is not None:
        local_config["plot_backend"] = plot_backend


@contextmanager
def config_context(
    *,
    show_progress: bool | None = None,
    plot_backend: PlotBackend | None = None,
) -> Generator[None, None, None]:
    """Context manager for skore configuration.

    Setting the configuration affects global settings meaning that it will be used
    by all skore functions and classes, even in the processes and threads spawned by
    skore.

    Parameters
    ----------
    show_progress : bool, default=None
        If True, show progress bars. Otherwise, do not show them.

    plot_backend : {"matplotlib", "plotly"}, default=None
        The plotting backend to be used.

        - `"matplotlib"`: Use Matplotlib for plotting
        - `"plotly"`: Use Plotly for plotting
        - `None`: Plotting backend is unchanged

    Yields
    ------
    None.

    See Also
    --------
    set_config : Set skore configuration.
    get_config : Retrieve current values of the configuration.

    Notes
    -----
    All settings, not just those presently modified, will be returned to
    their previous values when the context manager is exited.

    Examples
    --------
    >>> import skore
    >>> from skore import train_test_split
    >>> from sklearn.datasets import make_classification
    >>> from sklearn.linear_model import LogisticRegression
    >>> from skore import CrossValidationReport
    >>> with skore.config_context(show_progress=False, plot_backend="matplotlib"):
    ...     X, y = make_classification(random_state=42)
    ...     estimator = LogisticRegression()
    ...     report = CrossValidationReport(estimator, X=X, y=y, cv_splitter=2)
    """
    old_config = get_config()
    set_config(
        show_progress=show_progress,
        plot_backend=plot_backend,
    )

    try:
        yield
    finally:
        set_config(**old_config)


def _set_show_progress_for_testing(show_progress: bool, sleep_duration: float) -> bool:
    """Set the value of show_progress for testing purposes after some waiting.

    This function should exist in a Python module rather than in tests, otherwise
    joblib will not be able to pickle it.
    """
    with config_context(show_progress=show_progress):
        time.sleep(sleep_duration)
        return get_config()["show_progress"]
