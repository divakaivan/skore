from skore._externals._pandas_accessors import _register_accessor
from skore._sklearn._cross_validation.metrics_accessor import _MetricsAccessor
from skore._sklearn._cross_validation.report import (
    CrossValidationReport,
)

_register_accessor("metrics", CrossValidationReport)(_MetricsAccessor)

__all__ = ["CrossValidationReport"]
