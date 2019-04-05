import random

mythology = [
  'Apollo',
  'Artemis',
  'Athena',
  'Persephone',
  'Hermes',
  'Demeter',
  'Poseidon',
  'Gaia',
  'Terra',
]

biome = [
  'Rainforest',
  'Taiga',
  'Tundra',
  'Woodland',
  'Savanna',
  'Grassland',
  'Forest',
  'Wetland',
]

def name_team():
  return ' '.join([random.choice(mythology), random.choice(biome)])