import json
from ..model.items.background import BackgroundPackItem, BackgroundItem
from ..model.items.effect import EffectPackItem, EffectItem
from ..model.items.particle import ParticlePackItem, ParticleItem
from ..model.items.skin import SkinPackItem, SkinItem
from ..model.pack import PackModel
from ..memory import BackgroundMemory, EffectMemory, ParticleMemory, SkinMemory

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
            author=effect_pack_item.author.en or "",
            description=effect_pack_item.description.en or "",
            tags=effect_pack_item.tags,
            data=effect_pack_item.data,
            thumbnail=effect_pack_item.thumbnail,
            configuration=effect_pack_item.configuration,
        )
        effect_items.append(effect_item)

    # particle
    particle_items = []
    for particle_pack_item in pack.particles:
        particle_item = ParticleItem(
            name=particle_pack_item.name,
            title=particle_pack_item.title.en or "",
            author=particle_pack_item.author.en or "",
            description=particle_pack_item.description.en or "",
            tags=particle_pack_item.tags,
            data=particle_pack_item.data,
            thumbnail=particle_pack_item.thumbnail,
            configuration=particle_pack_item.configuration,
        )
        particle_items.append(particle_item)

    # skin
    skin_items = []
    for skin_pack_item in pack.skins:
        skin_item = SkinItem(
            name=skin_pack_item.name,
            title=skin_pack_item.title.en or "",
            author=skin_pack_item.author.en or "",
            description=skin_pack_item.description.en or "",
            tags=skin_pack_item.tags,
            data=skin_pack_item.data,
            thumbnail=skin_pack_item.thumbnail,
            configuration=skin_pack_item.configuration,
        )
        skin_items.append(skin_item)

    return background_items, effect_items, particle_items, skin_items


def set_pack_memory(db_path: str):
    """
    パックのjsonデータをメモリにセットします。
    """
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    pack = PackModel.parse_obj(data)
    background_items, effect_items, particle_items, skin_items = pack_2_ItemModel(pack)

    BackgroundMemory.push(background_items)
    EffectMemory.push(effect_items)
    ParticleMemory.push(particle_items)
    SkinMemory.push(skin_items)
    