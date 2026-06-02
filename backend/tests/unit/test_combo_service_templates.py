from app.database import Base
from app.models import ComboTemplate
from app.services.combo_service import ComboService


def test_list_templates_returns_existing_rows_in_expected_buckets():
    service = ComboService("sqlite:///:memory:")

    with service._session_factory() as db:
        Base.metadata.create_all(db.get_bind())
        db.add_all(
            [
                ComboTemplate(
                    name="prebuilt_template",
                    description="Prebuilt strategy",
                    is_prebuilt=True,
                    is_example=False,
                    is_readonly=True,
                    template_data={"indicators": [], "entry_logic": "x", "exit_logic": "y"},
                ),
                ComboTemplate(
                    name="Example: Demo",
                    description="Example strategy",
                    is_prebuilt=False,
                    is_example=True,
                    is_readonly=False,
                    template_data={"indicators": [], "entry_logic": "x", "exit_logic": "y"},
                ),
                ComboTemplate(
                    name="custom_template",
                    description="Custom strategy",
                    is_prebuilt=False,
                    is_example=False,
                    is_readonly=False,
                    template_data={"indicators": [], "entry_logic": "x", "exit_logic": "y"},
                ),
            ]
        )
        db.commit()

    templates = service.list_templates()

    assert [item["name"] for item in templates["prebuilt"]] == ["prebuilt_template"]
    assert [item["name"] for item in templates["examples"]] == ["Example: Demo"]
    assert [item["name"] for item in templates["custom"]] == ["custom_template"]
    assert templates["prebuilt"][0]["is_readonly"] is True
    assert all("description" in item for bucket in templates.values() for item in bucket)


def test_list_templates_seeds_runtime_when_initial_query_is_empty(monkeypatch):
    service = ComboService.__new__(ComboService)
    service._session_factory = object()

    prebuilt = ComboTemplate(
        name="seeded_template",
        description="Seeded strategy",
        is_prebuilt=True,
        is_example=False,
        is_readonly=False,
        template_data={"indicators": [], "entry_logic": "x", "exit_logic": "y"},
    )
    calls = {"list": 0, "seed": 0}

    def fake_list_rows():
        calls["list"] += 1
        return [] if calls["list"] == 1 else [prebuilt]

    def fake_seed():
        calls["seed"] += 1

    monkeypatch.setattr(service, "_list_template_rows", fake_list_rows)
    monkeypatch.setattr(service, "_seed_runtime_templates_if_empty", fake_seed)

    templates = service.list_templates()

    assert calls == {"list": 2, "seed": 1}
    assert [item["name"] for item in templates["prebuilt"]] == ["seeded_template"]
