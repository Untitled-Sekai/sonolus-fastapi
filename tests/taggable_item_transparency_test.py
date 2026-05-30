from pydantic import BaseModel
from sonolus_models import (
    BackgroundItem,
    EffectItem,
    EngineItem,
    LevelItem,
    LevelSection,
    ParticleItem,
    ServerItemInfo,
    SkinItem,
    Srl,
)

import sonolus_fastapi  # noqa: F401
from sonolus_fastapi.utils.taggable_item import TaggableItem


def test_section_items_accept_taggable_items():
    item = LevelItem.model_construct(name="level")

    section = LevelSection(title="Levels", items=[TaggableItem(item)])

    assert section.items == [item]


def test_server_item_info_accepts_taggable_items_in_section_dicts():
    item = LevelItem.model_construct(name="level")

    info = ServerItemInfo.model_validate(
        {
            "sections": [
                {
                    "title": "Levels",
                    "itemType": "level",
                    "items": [TaggableItem(item)],
                }
            ]
        }
    )

    assert isinstance(info.sections[0], LevelSection)
    assert info.sections[0].items == [item]


def test_item_model_fields_accept_taggable_items():
    resource = Srl(hash="hash", url="/resource")
    skin = SkinItem.model_construct(name="skin")
    background = BackgroundItem.model_construct(name="background")
    effect = EffectItem.model_construct(name="effect")
    particle = ParticleItem.model_construct(name="particle")

    engine = EngineItem(
        name="engine",
        title="Engine",
        author="Author",
        description="",
        tags=[],
        subtitle="",
        skin=TaggableItem(skin),
        background=TaggableItem(background),
        effect=TaggableItem(effect),
        particle=TaggableItem(particle),
        thumbnail=resource,
        playData=resource,
        watchData=resource,
        previewData=resource,
        tutorialData=resource,
        configuration=resource,
    )

    assert engine.skin == skin
    assert engine.background == background
    assert engine.effect == effect
    assert engine.particle == particle


def test_plain_pydantic_fields_accept_taggable_sonolus_models():
    class EngineContainer(BaseModel):
        engine: EngineItem

    engine = EngineItem.model_construct(name="engine")

    container = EngineContainer(engine=TaggableItem(engine))

    assert container.engine == engine
