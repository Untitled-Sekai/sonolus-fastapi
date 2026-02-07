import json
from typing import TYPE_CHECKING
from sonolus_models.items import BackgroundItem
from sonolus_models.items import EffectItem
from sonolus_models.items import ParticleItem
from sonolus_models.items import SkinItem
from sonolus_models.items import PostItem
from sonolus_models import PackModel
from ..backend import StorageBackend

if TYPE_CHECKING:
    from ..index import Sonolus

def pack_2_ItemModel(pack: PackModel):
    """
    PackModelを各ItemModelに変換します。
    """
    # background
    background_items = []
    for background_pack_item in pack.backgrounds:
        background_item = BackgroundItem(
            name=background_pack_item.name,
            title=background_pack_item.title.en or "",
            subtitle=background_pack_item.subtitle.en or "",
            author=background_pack_item.author.en or "",
            description=background_pack_item.description.en or "",
            tags=background_pack_item.tags,
            data=background_pack_item.data,
            image=background_pack_item.image,
            thumbnail=background_pack_item.thumbnail,
            configuration=background_pack_item.configuration,
        )
        background_items.append(background_item)

    # effect
    effect_items = []
    for effect_pack_item in pack.effects:
        effect_item = EffectItem(
            name=effect_pack_item.name,
            title=effect_pack_item.title.en or "",
            subtitle=effect_pack_item.subtitle.en or "",
            author=effect_pack_item.author.en or "",
            description=effect_pack_item.description.en or "",
            tags=effect_pack_item.tags,
            data=effect_pack_item.data,
            thumbnail=effect_pack_item.thumbnail,
            audio=effect_pack_item.audio,
        )
        effect_items.append(effect_item)

    # particle
    particle_items = []
    for particle_pack_item in pack.particles:
        particle_item = ParticleItem(
            name=particle_pack_item.name,
            title=particle_pack_item.title.en or "",
            subtitle=particle_pack_item.subtitle.en or "",
            author=particle_pack_item.author.en or "",
            description=particle_pack_item.description.en or "",
            tags=particle_pack_item.tags,
            data=particle_pack_item.data,
            thumbnail=particle_pack_item.thumbnail,
            texture=particle_pack_item.texture,
        )
        particle_items.append(particle_item)

    # skin
    skin_items = []
    for skin_pack_item in pack.skins:
        skin_item = SkinItem(
            name=skin_pack_item.name,
            title=skin_pack_item.title.en or "",
            subtitle=skin_pack_item.subtitle.en or "",
            author=skin_pack_item.author.en or "",
            description=skin_pack_item.description.en or "",
            tags=skin_pack_item.tags,
            data=skin_pack_item.data,
            thumbnail=skin_pack_item.thumbnail,
            texture=skin_pack_item.texture,
        )
        skin_items.append(skin_item)

    return background_items, effect_items, particle_items, skin_items


def set_pack_memory(db_path: str, sonolus: "Sonolus"):
    """
    パックのjsonデータをメモリにセットします。
    """
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    pack = PackModel.parse_obj(data)
    background_items, effect_items, particle_items, skin_items = pack_2_ItemModel(pack)

    for item in background_items:
        sonolus.items.background.add(item)
    for item in effect_items:
        sonolus.items.effect.add(item)
    for item in particle_items:
        sonolus.items.particle.add(item)
    for item in skin_items:
        sonolus.items.skin.add(item)
    