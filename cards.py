from enum import Enum, auto
from pathlib import Path


class Type(Enum):
  City = auto()
  Flag = auto()
  Map = auto()
  Bollard = auto()

  @classmethod
  def all_types(cls):
      return [choice.value for choice in cls]

type_names = {
  Type.City.value: 'city',
  Type.Flag.value: 'flag',
  Type.Map.value: 'map',
  Type.Bollard.value: 'bollard'
}


def is_image_type(type):
  if type == Type.Bollard.value or type == Type.Flag.value:
    return True
  else:
    return False


class CardInfo:
  def __init__(self, deck, region, default_rating, hint, 
      hint_required, subregion, default_subregion_rating):
    self.deck = deck
    self.region = region
    self.default_rating = default_rating
    self.default_subregion_rating = default_subregion_rating
    self.hint = hint
    self.hint_required = hint_required
    self.subregion = subregion


class CityInfo(CardInfo):
  def __init__(self, deck, prompt, region, default_rating, hint, 
      hint_required, subregion, default_subregion_rating):
    super().__init__(deck=deck, region=region, default_rating=default_rating, hint=hint, 
      hint_required=hint_required, subregion=subregion, default_subregion_rating=default_subregion_rating)
    self.prompt = prompt

  def __str__(self):
    return f'Deck: {self.deck}, prompt: {self.prompt}, region: {self.region}' \
      f', subregion: {self.subregion}, hint: {self.hint}' \
      f', hint_required: {self.hint_required}' \
      f', default rating: {self.default_rating}, default subregion rating: {self.default_subregion_rating}'


class ImageInfo(CardInfo):
  def __init__(self, deck, image_path, region, default_rating, hint, 
      hint_required, subregion, default_subregion_rating):
    super().__init__(deck=deck, region=region, default_rating=default_rating, hint=hint, 
      hint_required=hint_required, subregion=subregion, default_subregion_rating=default_subregion_rating)
    self.image_path = image_path

  def __str__(self):
    return f'Deck: {self.deck}, image path: {self.image_path}, region: {self.region}' \
      f', subregion: {self.subregion}, hint: {self.hint}' \
      f', hint_required: {self.hint_required}' \
      f', default rating: {self.default_rating}, default subregion rating: {self.default_subregion_rating}'