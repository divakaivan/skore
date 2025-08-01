import matplotlib as mpl
import numpy as np
import pytest
from sklearn.base import clone
from skore import ComparisonReport, EstimatorReport
from skore._sklearn._plot import PrecisionRecallCurveDisplay
from skore._sklearn._plot.utils import sample_mpl_colormap
from skore._utils._testing import check_frame_structure, check_legend_position
from skore._utils._testing import (
    check_precision_recall_curve_display_data as check_display_data,
)


def test_binary_classification(pyplot, binary_classification_data):
    """Check the attributes and default plotting behaviour of the precision-recall curve
    plot with binary data."""
    estimator, X_train, X_test, y_train, y_test = binary_classification_data
    estimator_2 = clone(estimator).set_params(C=10).fit(X_train, y_train)
    report = ComparisonReport(
        reports={
            "estimator_1": EstimatorReport(
                estimator,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
            "estimator_2": EstimatorReport(
                estimator_2,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
        }
    )
    display = report.metrics.precision_recall()
    assert isinstance(display, PrecisionRecallCurveDisplay)
    check_display_data(display)

    display.plot()
    expected_colors = sample_mpl_colormap(pyplot.cm.tab10, 10)
    for idx, (estimator_name, line) in enumerate(
        zip(report.report_names_, display.lines_, strict=False)
    ):
        assert isinstance(line, mpl.lines.Line2D)
        average_precision = display.average_precision.query(
            f"label == {display.pos_label} & estimator_name == '{estimator_name}'"
        )["average_precision"].item()
        assert line.get_label() == f"{estimator_name} (AP = {average_precision:0.2f})"
        assert mpl.colors.to_rgba(line.get_color()) == expected_colors[idx]

    assert isinstance(display.ax_, mpl.axes.Axes)
    legend = display.ax_.get_legend()
    assert legend.get_title().get_text() == "Test set"
    assert len(legend.get_texts()) == 2

    assert display.ax_.get_xlabel() == "Recall\n(Positive label: 1)"
    assert display.ax_.get_ylabel() == "Precision\n(Positive label: 1)"
    assert display.ax_.get_adjustable() == "box"
    assert display.ax_.get_aspect() in ("equal", 1.0)
    assert display.ax_.get_xlim() == display.ax_.get_ylim() == (-0.01, 1.01)
    assert display.ax_.get_title() == "Precision-Recall Curve"


def test_multiclass_classification(pyplot, multiclass_classification_data):
    """Check the attributes and default plotting behaviour of the precision-recall curve
    plot with multiclass data."""
    estimator, X_train, X_test, y_train, y_test = multiclass_classification_data
    estimator_2 = clone(estimator).set_params(C=10).fit(X_train, y_train)
    report = ComparisonReport(
        reports={
            "estimator_1": EstimatorReport(
                estimator,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
            "estimator_2": EstimatorReport(
                estimator_2,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
        }
    )
    display = report.metrics.precision_recall()
    assert isinstance(display, PrecisionRecallCurveDisplay)
    check_display_data(display)

    class_labels = report.reports_[0].estimator_.classes_

    display.plot()
    assert isinstance(display.lines_, list)
    assert len(display.lines_) == len(class_labels) * 2
    default_colors = sample_mpl_colormap(pyplot.cm.tab10, 10)
    for idx, (estimator_name, expected_color) in enumerate(
        zip(report.report_names_, default_colors, strict=False)
    ):
        for class_label_idx, class_label in enumerate(class_labels):
            roc_curve_mpl = display.lines_[idx * len(class_labels) + class_label_idx]
            assert isinstance(roc_curve_mpl, mpl.lines.Line2D)
            average_precision = display.average_precision.query(
                f"label == {class_label} & estimator_name == '{estimator_name}'"
            )["average_precision"].item()
            assert roc_curve_mpl.get_label() == (
                f"{estimator_name} - {str(class_label).title()} "
                f"(AP = {average_precision:0.2f})"
            )
            assert roc_curve_mpl.get_color() == expected_color

    assert isinstance(display.ax_, mpl.axes.Axes)
    legend = display.ax_.get_legend()
    assert legend.get_title().get_text() == "Test set"
    assert len(legend.get_texts()) == 6

    assert display.ax_.get_xlabel() == "Recall"
    assert display.ax_.get_ylabel() == "Precision"
    assert display.ax_.get_adjustable() == "box"
    assert display.ax_.get_aspect() in ("equal", 1.0)
    assert display.ax_.get_xlim() == display.ax_.get_ylim() == (-0.01, 1.01)
    assert display.ax_.get_title() == "Precision-Recall Curve"


def test_binary_classification_kwargs(pyplot, binary_classification_data):
    """Check that we can pass keyword arguments to the precision-recall curve plot for
    cross-validation."""
    estimator, X_train, X_test, y_train, y_test = binary_classification_data
    estimator_2 = clone(estimator).set_params(C=10).fit(X_train, y_train)
    report = ComparisonReport(
        reports={
            "estimator_1": EstimatorReport(
                estimator,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
            "estimator_2": EstimatorReport(
                estimator_2,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
        }
    )
    display = report.metrics.precision_recall()
    pr_curve_kwargs = [{"color": "red"}, {"color": "blue"}]
    display.plot(pr_curve_kwargs=pr_curve_kwargs)
    assert display.lines_[0].get_color() == "red"
    assert display.lines_[1].get_color() == "blue"


@pytest.mark.parametrize(
    "fixture_name",
    ["binary_classification_data", "multiclass_classification_data"],
)
@pytest.mark.parametrize("pr_curve_kwargs", [[{"color": "red"}], "unknown"])
def test_wrong_kwargs(pyplot, fixture_name, request, pr_curve_kwargs):
    """Check that we raise a proper error message when passing an inappropriate
    value for the `pr_curve_kwargs` argument."""
    estimator, X_train, X_test, y_train, y_test = request.getfixturevalue(fixture_name)

    report = ComparisonReport(
        reports={
            "estimator_1": EstimatorReport(
                estimator,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
            "estimator_2": EstimatorReport(
                estimator,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
        }
    )
    display = report.metrics.precision_recall()
    err_msg = "You intend to plot multiple curves"
    with pytest.raises(ValueError, match=err_msg):
        display.plot(pr_curve_kwargs=pr_curve_kwargs)


@pytest.mark.parametrize("with_average_precision", [False, True])
def test_frame_binary_classification(
    binary_classification_data, with_average_precision
):
    """Test the frame method with binary classification comparison data."""
    estimator, X_train, X_test, y_train, y_test = binary_classification_data
    estimator_2 = clone(estimator).set_params(C=10).fit(X_train, y_train)
    report = ComparisonReport(
        reports={
            "estimator_1": EstimatorReport(
                estimator,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
            "estimator_2": EstimatorReport(
                estimator_2,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
        }
    )
    display = report.metrics.precision_recall()
    df = display.frame(with_average_precision=with_average_precision)

    expected_index = ["estimator_name"]
    expected_columns = ["threshold", "precision", "recall"]
    if with_average_precision:
        expected_columns.append("average_precision")

    check_frame_structure(df, expected_index, expected_columns)
    assert df["estimator_name"].nunique() == 2

    if with_average_precision:
        for (_), group in df.groupby(["estimator_name"], observed=True):
            assert group["average_precision"].nunique() == 1


@pytest.mark.parametrize("with_average_precision", [False, True])
def test_frame_multiclass_classification(
    multiclass_classification_data, with_average_precision
):
    """Test the frame method with multiclass classification comparison data."""
    estimator, X_train, X_test, y_train, y_test = multiclass_classification_data
    estimator_2 = clone(estimator).set_params(C=10).fit(X_train, y_train)
    report = ComparisonReport(
        reports={
            "estimator_1": EstimatorReport(
                estimator,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
            "estimator_2": EstimatorReport(
                estimator_2,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
        }
    )
    display = report.metrics.precision_recall()
    df = display.frame(with_average_precision=with_average_precision)

    expected_index = ["estimator_name", "label"]
    expected_columns = ["threshold", "precision", "recall"]
    if with_average_precision:
        expected_columns.append("average_precision")

    check_frame_structure(df, expected_index, expected_columns)
    assert df["estimator_name"].nunique() == 2

    if with_average_precision:
        for (_, _), group in df.groupby(["estimator_name", "label"], observed=True):
            assert group["average_precision"].nunique() == 1


def test_legend(pyplot, binary_classification_data, multiclass_classification_data):
    """Check the rendering of the legend for with a `ComparisonReport`."""

    # binary classification
    estimator, X_train, X_test, y_train, y_test = binary_classification_data
    report_1 = EstimatorReport(
        estimator, X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test
    )
    report_2 = EstimatorReport(
        estimator, X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test
    )
    report = ComparisonReport(
        reports={"estimator_1": report_1, "estimator_2": report_2}
    )
    display = report.metrics.precision_recall()
    display.plot()
    check_legend_position(display.ax_, loc="lower left", position="inside")

    # multiclass classification <= 5 classes
    estimator, X_train, X_test, y_train, y_test = multiclass_classification_data
    report_1 = EstimatorReport(
        estimator, X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test
    )
    report_2 = EstimatorReport(
        estimator, X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test
    )
    report = ComparisonReport(
        reports={"estimator_1": report_1, "estimator_2": report_2}
    )
    display = report.metrics.precision_recall()
    display.plot()
    check_legend_position(display.ax_, loc="upper left", position="outside")


def test_binary_classification_constructor(binary_classification_data):
    """Check that the dataframe has the correct structure at initialization."""
    estimator, X_train, X_test, y_train, y_test = binary_classification_data
    report_1 = EstimatorReport(
        estimator, X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test
    )
    report_2 = EstimatorReport(
        estimator, X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test
    )
    report = ComparisonReport(
        reports={"estimator_1": report_1, "estimator_2": report_2}
    )
    display = report.metrics.precision_recall()

    index_columns = ["estimator_name", "split_index", "label"]
    for df in [display.precision_recall, display.average_precision]:
        assert all(col in df.columns for col in index_columns)
        assert df["estimator_name"].unique().tolist() == report.report_names_
        assert df["split_index"].isnull().all()
        assert df["label"].unique() == 1

    assert len(display.average_precision) == 2


def test_multiclass_classification_constructor(multiclass_classification_data):
    """Check that the dataframe has the correct structure at initialization."""
    estimator, X_train, X_test, y_train, y_test = multiclass_classification_data
    report_1 = EstimatorReport(
        estimator, X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test
    )
    report_2 = EstimatorReport(
        estimator, X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test
    )
    report = ComparisonReport(
        reports={"estimator_1": report_1, "estimator_2": report_2}
    )
    display = report.metrics.precision_recall()

    index_columns = ["estimator_name", "split_index", "label"]
    for df in [display.precision_recall, display.average_precision]:
        assert all(col in df.columns for col in index_columns)
        assert df["estimator_name"].unique().tolist() == report.report_names_
        assert df["split_index"].isnull().all()
        np.testing.assert_array_equal(df["label"].unique(), np.unique(y_train))

    assert len(display.average_precision) == len(np.unique(y_train)) * 2
