import sentry_sdk

from core.settings import get_settings


def init_sentry() -> None:
    settings = get_settings()

    if not settings.sentry_dsn:
        return

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.env,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        send_default_pii=True,
        debug=settings.debug,
    )
