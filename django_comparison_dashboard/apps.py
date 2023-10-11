"""Config for django app"""

from appconf import AppConf


class DashboardConf(AppConf):
    """Config for django-comparison-dashboard app"""

    name = "django_comparison_dashboard"

    SCALAR_MODEL = "django_comparison_dashboard.ScalarData"
    TIMESERIES_MODEL = "django_comparison_dashboard.TimeseriesData"

    # pylint:disable=R0903
    class Meta:
        """
        App config meta

        Sets prefix to be used in settings, so that i.e. "SCALAR_MODEL" becomes "DASHBOARD_SCALAR_MODEL".
        """

        prefix = "DASHBOARD"
