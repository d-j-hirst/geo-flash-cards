from enum import Enum, auto
import random
import math
import re
from pathlib import Path
from random import uniform
from scipy.stats import logistic
from cards import CityInfo, ImageInfo, Type, is_image_type, type_names
from tkinter import messagebox


class Mode(Enum):
  Question = auto()
  Answer = auto()
  ConfigureMap = auto()

class Subregion_Setting(Enum):
  Either = auto()
  Always = auto()
  Never = auto()

class Hint_Setting(Enum):
  Either = auto()
  Always = auto()
  Never = auto()

class Question():
  def __init__(self, card, type, require_subregion, give_hint):
    self.card = card
    self.type = type
    self.require_subregion = require_subregion
    self.give_hint = give_hint

#Get a unique "key" identifying this particular card
def card_key(card):
  return getattr(card, 'prompt', '')+'$'+card.region+'$'+card.subregion+'$'+card.hint


def question_key(card, type, subregion, hint):
  return type_names[type] + '$' + ('t' if subregion else 'f') + \
    '$' + ('t' if hint else 'f') + '$' + card_key(card) + '$' + str(card.default_rating)

def file_line_to_image(line, deck, image_file_name):
  parts = line.split(';')
  if len(parts) < 1:
    return None
  #default values for anything that isn't completely filled out
  if len(parts) == 1:
    parts.append('1500')
  if len(parts) == 2:
    parts.append('')
  if len(parts) == 3:
    parts.append('False')
  if ',' in parts[0]:
    split_region = parts[0].split(',')
    parts[0] = split_region[0]
    parts.append(split_region[1])
  else:
    parts.append('')
  if ',' in parts[1]:
    split_rating = parts[1].split(',')
    parts[1] = split_rating[0]
    parts.append(split_rating[1])
  else:
    parts.append(str(int(parts[1]) + 300))
  image = ImageInfo(deck=deck.name, image_path=str(image_file_name), region=parts[0],
    default_rating=float(parts[1]), hint=parts[2], hint_required = (parts[3].strip() == 'True'),
    subregion=parts[4], default_subregion_rating=float(parts[5]))
  return image

def load_image_list(category):
  image_data = []
  root_path = Path('cards/')
  for deck in root_path.iterdir():
    if deck.is_dir():
      images_path = deck / category
      if images_path.is_dir():
        for image_filename in images_path.iterdir():
          line = image_filename.with_suffix('').name
          image = file_line_to_image(line, deck, image_filename)
          if image is None: 
            print('invalid image entry detected: ' + image_filename.name)
            continue
          image_data.append(image)
  return image_data

def file_line_to_city(line, deck):
  parts = line.split(';')
  if len(parts) < 2:
    return None
  #default values for anything that isn't completely filled out
  if len(parts) == 2:
    parts.append('1500')
  if len(parts) == 3:
    parts.append('')
  if len(parts) == 4:
    parts.append('False')
  if ',' in parts[1]:
    split_region = parts[1].split(',')
    parts[1] = split_region[0]
    parts.append(split_region[1])
  else:
    parts.append('')
  if ',' in parts[2]:
    split_rating = parts[2].split(',')
    parts[2] = split_rating[0]
    parts.append(split_rating[1])
  else:
    parts.append(str(int(parts[2]) + 300))
  city = CityInfo(deck=deck.name, prompt=parts[0], region=parts[1],
    default_rating=float(parts[2]), hint=parts[3], hint_required = (parts[4].strip() == 'True'),
    subregion=parts[5], default_subregion_rating=float(parts[6]))
  return city

#===================
# * Quiz Class *
# Handles all logic of the quiz
#===================

class Quiz:
  player_rating_mult = 10
  question_rating_mult = 120

  def __init__(self, username):
    self.reload(username)

  def reload(self, username=None):
    self.load_regions()
    self.load_city_cards()
    self.load_flag_cards()
    self.load_bollard_cards()
    self.load_maps()
    self.load_map_locations()
    self.load_user(username)

  def load_regions(self):
    self.regions = []
    region_path = Path('regions.txt')
    with region_path.open(mode='r', encoding='utf-8') as region_file:
      while True:
        line = region_file.readline()
        if len(line) == 0:
          break #end of file
        if line[0] == '#':
          continue #skip comments
        self.regions.append(tuple([word.strip().lower() for word in line.split(',')]))

  def load_city_cards(self):
    self.city_cards = []
    root_path = Path('cards/')
    for deck in root_path.iterdir():
      if deck.is_dir():
        cities_path = deck / 'cities'
        if cities_path.is_dir():
          for city_file in cities_path.iterdir():
            with city_file.open(mode='r', encoding='utf-8') as cities:
              while True:
                line = cities.readline()
                if len(line) == 0:
                  break #end of file
                if line[0] == '#':
                  continue #skip comments
                city = file_line_to_city(line, deck)
                if city is None:
                  print('invalid city entry detected in: ' + city_file.name)
                  continue
                self.city_cards.append(city)
    return self.city_cards

  def load_flag_cards(self):
    self.flag_cards = load_image_list('flags')

  def load_bollard_cards(self):
    self.bollard_cards = load_image_list('bollards')

  def load_maps(self):
    self.maps = {}
    map_path = Path('maps/')
    for map_file in map_path.iterdir():
      map_name = map_file.with_suffix('').name
      self.maps[map_name] = str(map_file)
    return self.maps

  def load_map_locations(self):
    self.map_locations = {}
    map_location_file = Path('map_locations.txt')
    with map_location_file.open(mode='r', encoding='utf-8') as locations_input:
      while True:
        line = locations_input.readline()
        if len(line) == 0:
          break
        if line[0] == '#':
          continue
        if line.count(';') != 2:
          break
        lineparts = line.split(';')
        self.map_locations[lineparts[0]] = (int(lineparts[1]), int(lineparts[2]))

  def load_user_rating(self, line):
    if line[0] == '#':
      return #skip comments
    if line[0] == '^':
      self.player_rating = float(line[1:])
    if line[0] == '`':
      parts = [a.strip() for a in line[1:].split('@')]
      if parts[0] == 'type_filters':
        for a in parts[1:]:
          segment = a.split(',')
          self.type_filters[int(segment[0])] = False if segment[1] == "False" else True
      elif parts[0] == 'subregion_setting':
        self.subregion_setting = int(parts[1])
      elif parts[0] == 'hint_setting':
        self.hint_setting = int(parts[1])
      elif parts[0] == 'prompt_filter':
        self.prompt_filter = parts[1]
      elif parts[0] == 'region_filter':
        self.region_filter = parts[1]
      return
    if line.count('@') != 1:
      return #malformed line
    key, rating = line.split('@')
    self.ratings[key] = float(rating)

  def load_user(self, username):
    if username is not None:
      self.username = username
    if len(self.username) == 0:
      self.username = 'default'
    self.username = ''.join(i for i in self.username if i.isalnum())
    user_data = []
    root_path = Path('users/')

    # start with default user stats
    self.player_rating = 1500
    self.ratings = {}
    self.type_filters = {a: True for a in Type.all_types()}
    self.subregion_setting = Subregion_Setting.Either.value
    self.hint_setting = Subregion_Setting.Either.value
    self.prompt_filter = ''
    self.region_filter = ''

    for user_file in root_path.iterdir():
      if not user_file.is_dir():
        if (user_file.name == self.username):
          with user_file.open(mode='r', encoding='utf-8') as user_data:
            while True:
              line = user_data.readline()
              if len(line) == 0:
                break #end of file
              self.load_user_rating(line)

  def save_user(self):
    user_file = Path('users/' + self.username)
    with user_file.open(mode='w', encoding='utf-8') as user_data:
      user_data.write('^' + f'{self.player_rating:.1f}\n')
      filter_string = '`type_filters'
      for a in self.type_filters.items():
        filter_string += '@' + str(a[0]) + "," + str(a[1])
      user_data.write(filter_string + '\n')
      user_data.write('`subregion_setting@' + str(self.subregion_setting) + '\n')
      user_data.write('`hint_setting@' + str(self.hint_setting) + '\n')
      user_data.write('`prompt_filter@' + self.prompt_filter + '\n')
      user_data.write('`region_filter@' + self.region_filter + '\n')
      for key, value in self.ratings.items():
        user_data.write(key + '@' + str(value) + '\n')
  
  def save_map_locations(self):
    map_location_file = Path('map_locations.txt')
    with map_location_file.open(mode='w', encoding='utf-8') as locations_output:
      locations_output.write('#Do not edit these values directly. If a map location needs to be changed, find the relevant line and delete it, then run "Configure Map" in the app\n')
      for map_location in self.map_locations.items():
        locations_output.write(str(map_location[0]) + ';')
        locations_output.write(str(map_location[1][0]) + ';')
        locations_output.write(str(map_location[1][1]) + '\n')

  def effective_rating(self, card = None, type = None, subregion = None,
      hint = None, new_value = None):
    card = self.current_question.card if card is None else card
    type = self.current_question.type if type is None else type
    subregion = self.current_question.require_subregion if subregion is None else subregion
    hint = self.current_question.give_hint if hint is None else hint
    ck = question_key(card=card, type=type, subregion=subregion, hint=hint)
    if new_value is not None:
      self.ratings[ck] = new_value
    if ck in self.ratings:
      return self.ratings[ck]
    if type == Type.Map.value:
      return card.default_subregion_rating - 100
    elif subregion:
      return card.default_subregion_rating
    else:
      return card.default_rating
  
  def create_question_list(self, cards, type):
    questions = []
    cumulative_weight = 0
    re_prompt = re.compile(self.prompt_filter, re.IGNORECASE) if len(self.prompt_filter) > 0 else None
    re_region = re.compile(self.region_filter, re.IGNORECASE) if len(self.region_filter) > 0 else None

    for index in range(len(cards)):
      card = cards[index]
      if not is_image_type(type) and re_prompt is not None:
        if re_prompt.match(card.prompt) is None:
          continue
      if re_region is not None:
        if re_region.match(card.region) is None:
          continue

      # check this card has a map to be used with it
      if type == Type.Map.value:
        key = card_key(card)
        if key in self.map_locations:
          loc = self.map_locations[key]
          if loc[0] >= 0 and loc[1] >= 1:
            if card.region not in self.maps:
              continue
      for require_subregion in (False, True):
        if require_subregion and type == Type.Map.value:
          continue
        if require_subregion and self.subregion_setting == Subregion_Setting.Never.value:
          continue
        if not require_subregion and self.subregion_setting == Subregion_Setting.Always.value:
          # if the question doesn't have a subregion at all, still want to include it
          if len(card.subregion) > 0 and type != Type.Map.value:
            continue
        if len(card.subregion) == 0 and require_subregion:
          continue
        for give_hint in (False, True):
          if give_hint and self.hint_setting == Hint_Setting.Never.value and not card.hint_required:
            continue
          if len(card.hint) > 0 and self.hint_setting == Hint_Setting.Always.value and not give_hint:
            continue
          if card.hint_required and not give_hint:
            continue
          if len(card.hint) == 0 and give_hint:
            continue
          rating = self.effective_rating(card, type, require_subregion, give_hint)
          weight = logistic.pdf(rating - self.player_rating, 0, 100)
          cumulative_weight += weight
          questions.append(((index, type, require_subregion, give_hint), cumulative_weight))
    return questions, cumulative_weight
  
  def select_question(self):
    available_types = [a for a in Type.all_types() if self.type_filters[a]]
    if len(available_types) == 0:
      return None
    type = random.choice(available_types)
    if type == Type.City.value:
      cards = self.city_cards
    elif type == Type.Flag.value:
      cards = self.flag_cards
    elif type == Type.Bollard.value:
      cards = self.bollard_cards
    elif type == Type.Map.value:
      cards = self.city_cards

    # can cache these variables if it's taking to long to construct each time
    # just need to remember to reset after options are changed
    questions, cumulative_weight = self.create_question_list(cards, type)
    position = uniform(0, cumulative_weight)
    if len(questions) == 0:
      messagebox.showinfo('','Could not find any questions fitting the criteria')
      return None
    for index in range(0, len(questions)):
      if position < questions[index][1]:
        chosen_index = index
        break
    question = questions[chosen_index][0]
    self.current_question = Question(cards[question[0]], question[1], question[2], question[3])
    return self.current_question
  
  def current_correct_answer(self):
    if self.current_question.require_subregion:
      return [self.current_question.card.region, self.current_question.card.subregion]
    else:
      return [self.current_question.card.region]
  
  def is_answer_match(self, answer):
    question = self.current_question
    correct_answer = self.current_correct_answer()
    if question.require_subregion:
      if (answer.count(',') != 1):
        return 'This card requires a region. Please enter the country then the region separated by a comma (,)'
      split_answer = [a.strip() for a in answer.split(',')]
      match1 = (split_answer[0] == correct_answer[0].lower())
      if not match1:
        for region in self.regions:
          if split_answer[0] in region and correct_answer[0].lower() in region:
            match1 = True
      if match1:
        match = (split_answer[1] == correct_answer[1].lower())
        if not match:
          for region in self.regions:
            if split_answer[1] in region and correct_answer[1].lower() in region:
              match = True
      else:
        match = False
    else:
      # do this to make sure players aren't penalised for giving a more precise answer than needed
      given_answer = answer.split(',')[0].strip()
      match = (given_answer == correct_answer[0].lower())
      if not match:
        for region in self.regions:
          if given_answer in region and correct_answer[0].lower() in region:
            match = True
    return match

  def submit_answer(self, given_answer):
    match = self.is_answer_match(given_answer)
    if (isinstance(match, str)):
      return match
    if match is None: #if answer was of invalid form, don't try to go to the next round
      return None
    correct_answer = self.current_correct_answer()
    old_question_rating = self.effective_rating()
    expected_result = 1 / (1 + 10 ** ((old_question_rating - self.player_rating) / 400))
    actual_result = 1 if match else 0
    old_player_rating = self.player_rating
    new_player_rating = self.player_rating + Quiz.player_rating_mult * (actual_result - expected_result)
    new_question_rating = old_question_rating - Quiz.question_rating_mult * (actual_result - expected_result)
    self.player_rating = new_player_rating
    self.effective_rating(new_value=new_question_rating)
    self.save_user()
    output = dict(match=match, correct_answer=correct_answer,
      old_player_rating=old_player_rating, new_player_rating = new_player_rating,
      old_question_rating=old_question_rating, new_question_rating=new_question_rating)
    return output
  
  def select_config_card(self):
    self.config_card = None
    for card in self.city_cards:
      if card_key(card) not in self.map_locations:
        if card.region in self.maps:
          self.config_card = card
          break
    return self.config_card

  def set_config_map_loc(self, coords):
    key = card_key(self.config_card)
    self.map_locations[key] = (coords[0], coords[1])
    self.save_map_locations()
  
  def submit_map_answer(self, coords):
    key = card_key(self.current_question.card)
    x = self.map_locations[key][0]
    y = self.map_locations[key][1]
    distance = math.sqrt((coords[0] - x) ** 2 + (coords[1] - y) ** 2)
    actual_result = 1 - math.sqrt((min(95,max(5,distance))-5)/95)
    old_question_rating = self.effective_rating()
    expected_result = 1 / (1 + 10 ** ((old_question_rating - self.player_rating) / 400))
    old_player_rating = self.player_rating
    new_player_rating = self.player_rating + Quiz.player_rating_mult * (actual_result - expected_result)
    new_question_rating = old_question_rating - Quiz.question_rating_mult * (actual_result - expected_result)
    self.player_rating = new_player_rating
    self.effective_rating(new_value=new_question_rating)
    self.save_user()
    return dict(answer_x=x, answer_y=y, distance=distance, old_player_rating=old_player_rating,
      new_player_rating=new_player_rating, old_question_rating=old_question_rating,
      new_question_rating=new_question_rating)
  
  # Returns a string indicating the problematic item, or None if all are good
  def ambiguity_check(self):
    check_list = [(a.prompt, a.hint, a.hint_required) for a in self.city_cards]
    check_list.sort(key=lambda x: x[0])
    check_index = 0
    while check_index < len(check_list) - 1:
      same_prompts = []
      this_prompt = check_list[check_index][0]
      while check_list[check_index][0] == this_prompt:
        same_prompts.append(check_list[check_index])
        check_index += 1
      if len(same_prompts) < 2:
        continue
      for first_index in range(0, len(same_prompts)):
        if not same_prompts[first_index][2]:
          return 'Questions with prompt: "' + same_prompts[first_index][0] + '" do not have hint marked as required'
      for first_index in range(0, len(same_prompts)-1):
        for second_index in range(first_index + 1, len(same_prompts)):
          if same_prompts[first_index][1] == same_prompts[second_index][1]:
            return 'Questions with prompt "' + same_prompts[first_index][0] + '" do not have different hints'
    return None


  def get_current_question(self):
    return self.current_question

  def get_region_map(self, region_name):
    return self.maps[region_name]
