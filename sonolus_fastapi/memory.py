from .model.items.level import LevelItem
from .model.items.background import BackgroundItem
from .model.items.effect import EffectItem
from .model.items.particle import ParticleItem
from .model.items.skin import SkinItem
from .model.items.engine import EngineItem
from typing import List

class LevelMemory:
    """
    レベルメモリ管理クラス
    """
    def __init__(self):
        self.levels: List[LevelItem] = []
        
    def push(self, level: LevelItem):
        """
        レベルをメモリに追加する
        """
        self.levels.append(level)
        
    def unshift(self) -> LevelItem:
        """
        最初のレベルをメモリから取り出す
        """
        if self.levels:
            return self.levels.pop(0)
        raise IndexError("No levels in memory")
    
    def delete(self, level: LevelItem):
        """
        指定したレベルをメモリから削除する
        """
        self.levels = [l for l in self.levels if l != level]

    def get_name(self, name: str) -> LevelItem:
        """
        指定したnameのレベルをメモリから取得する
        """
        for level in self.levels:
            if level.name == name:
                return level
        raise ValueError(f"Level with name {name} not found in memory")
        
    def clear(self):
        """
        メモリをクリアする
        """
        self.levels = []
        
class BackgroundMemory:
    """
    背景メモリ管理クラス
    """
    def __init__(self):
        self.backgrounds: List[BackgroundItem] = []
        
    def push(self, background: BackgroundItem):
        """
        背景をメモリに追加する
        """
        self.backgrounds.append(background)
        
    def unshift(self) -> BackgroundItem:
        """
        最初の背景をメモリから取り出す
        """
        if self.backgrounds:
            return self.backgrounds.pop(0)
        raise IndexError("No backgrounds in memory")
    
    def delete(self, background: BackgroundItem):
        """
        指定した背景をメモリから削除する
        """
        self.backgrounds = [b for b in self.backgrounds if b != background]

    def get_name(self, name: str) -> BackgroundItem:
        """
        指定したnameの背景をメモリから取得する
        """
        for background in self.backgrounds:
            if background.name == name:
                return background
        raise ValueError(f"Background with name {name} not found in memory")
        
    def clear(self):
        """
        メモリをクリアする
        """
        self.backgrounds = []
        
class EffectMemory:
    """
    エフェクトメモリ管理クラス
    """
    def __init__(self):
        self.effects: List[EffectItem] = []
        
    def push(self, effect: EffectItem):
        """
        エフェクトをメモリに追加する
        """
        self.effects.append(effect)
        
    def unshift(self) -> EffectItem:
        """
        最初のエフェクトをメモリから取り出す
        """
        if self.effects:
            return self.effects.pop(0)
        raise IndexError("No effects in memory")
    
    def delete(self, effect: EffectItem):
        """
        指定したエフェクトをメモリから削除する
        """
        self.effects = [e for e in self.effects if e != effect]

    def get_name(self, name: str) -> EffectItem:
        """
        指定したnameのエフェクトをメモリから取得する
        """
        for effect in self.effects:
            if effect.name == name:
                return effect
        raise ValueError(f"Effect with name {name} not found in memory")
        
    def clear(self):
        """
        メモリをクリアする
        """
        self.effects = []
        
class ParticleMemory:
    """
    パーティクルメモリ管理クラス
    """
    def __init__(self):
        self.particles: List[ParticleItem] = []
        
    def push(self, particle: ParticleItem):
        """
        パーティクルをメモリに追加する
        """
        self.particles.append(particle)
        
    def unshift(self) -> ParticleItem:
        """
        最初のパーティクルをメモリから取り出す
        """
        if self.particles:
            return self.particles.pop(0)
        raise IndexError("No particles in memory")
    
    def delete(self, particle: ParticleItem):
        """
        指定したパーティクルをメモリから削除する
        """
        self.particles = [p for p in self.particles if p != particle]

    def get_name(self, name: str) -> ParticleItem:
        """
        指定したnameのパーティクルをメモリから取得する
        """
        for particle in self.particles:
            if particle.name == name:
                return particle
        raise ValueError(f"Particle with name {name} not found in memory")
        
    def clear(self):
        """
        メモリをクリアする
        """
        self.particles = []
        
class SkinMemory:
    """
    スキンメモリ管理クラス
    """
    def __init__(self):
        self.skins: List[SkinItem] = []
        
    def push(self, skin: SkinItem):
        """
        スキンをメモリに追加する
        """
        self.skins.append(skin)
        
    def unshift(self) -> SkinItem:
        """
        最初のスキンをメモリから取り出す
        """
        if self.skins:
            return self.skins.pop(0)
        raise IndexError("No skins in memory")
    
    def delete(self, skin: SkinItem):
        """
        指定したスキンをメモリから削除する
        """
        self.skins = [s for s in self.skins if s != skin]

    def get_name(self, name: str) -> SkinItem:
        """
        指定したnameのスキンをメモリから取得する
        """
        for skin in self.skins:
            if skin.name == name:
                return skin
        raise ValueError(f"Skin with name {name} not found in memory")
        
    def clear(self):
        """
        メモリをクリアする
        """
        self.skins = []
        
class EngineMemory:
    """
    エンジンメモリ管理クラス
    """
    def __init__(self):
        self.engines: List[EngineItem] = []
        
    def push(self, engine: EngineItem):
        """
        エンジンをメモリに追加する
        """
        self.engines.append(engine)
        
    def unshift(self) -> EngineItem:
        """
        最初のエンジンをメモリから取り出す
        """
        if self.engines:
            return self.engines.pop(0)
        raise IndexError("No engines in memory")
    
    def delete(self, engine: EngineItem):
        """
        指定したエンジンをメモリから削除する
        """
        self.engines = [e for e in self.engines if e != engine]

    def get_name(self, name: str) -> EngineItem:
        """
        指定したnameのエンジンをメモリから取得する
        """
        for engine in self.engines:
            if engine.name == name:
                return engine
        raise ValueError(f"Engine with name {name} not found in memory")
        
    def clear(self):
        """
        メモリをクリアする
        """
        self.engines = []