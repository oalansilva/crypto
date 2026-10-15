"""Private test Celery application: never imports/publishes the real queues."""

import os
from celery import Celery

app = Celery(
    "card1093-isolated", broker=os.environ["CARD1093_BROKER"], backend=os.environ["CARD1093_BROKER"]
)
app.conf.update(
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    broker_transport_options={"visibility_timeout": 5},
)


@app.task(name="card1093.private_loss", acks_late=True)
def private_loss(sweep_id, marker):
    from app.database import SessionLocal
    from app.services.discovery_service import DiscoveryService
    from app.services.combo_service import ComboService
    from app.services.discovery_recovery import Possession, heartbeat
    from app.services.discovery_supervisor import run_supervised
    from tests.unit.test_discovery_supervisor import _isolated_target

    # This test catalogue override exists only in the private fixture application.
    ComboService.get_template_metadata = lambda *_: {"name": "frozen", "indicators": []}
    with SessionLocal() as db:
        rows = DiscoveryService().claim_combinations(sweep_id, "private-celery", db=db)
        if not rows:
            return "no_claim"
        token = Possession.of(rows[0])

    def beat(events, supervisor):
        with SessionLocal() as db:
            heartbeat(db, token, events, supervisor)

    return run_supervised({"action": "wait", "marker": marker}, beat, _target=_isolated_target)
