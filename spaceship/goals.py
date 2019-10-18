

GOALS_BY_CATEGORY = {
  "diet": {
    "icon": None,
    "title": "Plant-Rich Diet",
    "description": "Change your diet, change the world",
    "goals": [
      {
        "name": "Go vegan",
        "icon" : "/static/vegan.png",
        "short_description": "Avoid all animal products",
        "description": "Our diet comes with a steep climate price tag: one-fifth of global emissions. Adopting a vegan diet is the most impactful thing you could do to lower your diet's footprint. A vegan diet eliminates 80% of the average Americans diet related emissions.",
        "links": [
          {
            "url": "https://www.independent.co.uk/life-style/health-and-families/veganism-environmental-impact-planet-reduced-plant-based-diet-humans-study-a8378631.html",
            "title": "Single best way to help fight climate change",
          },
        ],
      },
      {
        "name": "Go vegetarian",
        "icon": "/static/chantal-garnier-910GanwBoew-vegan.jpg",
        "alt" : "Photo by Chantal Garnier on Unsplash",
        "short_description": "Avoid all animal flesh; dairy and eggs are ok",
        "description": "Animal products are bad. Don't eat them.",
      },
      {
        "name": "Avoid beef",
        "icon" : "/static/climate_damage.png",
        "short_description": "Avoid beef",
        "description": "Animal products are bad. Don't eat them.",
      },
    ],
  },
  "transportation": {
    "icon": None,
    "title": "Transportation",
    "description": "Save energy by changing how you travel",
    "goals": [
      {
        "name": "Bike to work/school",
        "icon" : "/static/david-marcu-Op5JMbkOqi0-bike.jpg",
        "alt" : "Photo by David Marcu on Unsplash",
        "short_description": "Ride your bike to work or school",
        "description": "You should be biking more. Good for you and good for the planet.",
      },
       {
        "name": "Take public transit or bike",
        "icon" : "/static/ryan-searle-k1AFA4N8O0g-traffic.jpg",
        "alt": "Photo by Ryan Searle on Unsplash",
        "short_description": "Take public transit or bike",
        "description": "You should be biking more. Good for you and good for the planet.",
      },
      {
        "name": "Plan a local vacation",
        "icon" : "/static/caleb-george-iVXfOilGYHA-vanlife.jpg",
        "alt" : "Photo by Caleb George on Unsplash",
        "short_description": "Take a roadtrip instead of flying",
        "description": "You should be biking more. Good for you and good for the planet.",
      },
    ],
  },
  "education": {
    "icon": None,
    "title": "Education",
    "description": "Learn more about the science and policy of climate change",
    "goals": [
      {
        "name": "Read a book",
        "icon" : "/static/joao-silas-9c_djeQTDyY-book.jpg",
        "alt" : "Photo by João Silas on Unsplash",
        "short_description": "Become educated about climate change",
        "description": "This is your chance. You've always wanted to read.",
      },
      {
        "name": "Have a conversation",
        "icon" : "/static/etienne-boulanger-erCPgyXNlto-chat.jpg",
        "alt" : "Photo by Etienne Boulanger on Unsplash",
        "short_description": "Talk to your friends about climate change",
        "description": "Especially if they don't believe in it",
      },
      {
        "name": "Have a conversation",
        "short_description": "Talk to your friends about climate change",
        "description": "Especially if they don't believe in it",
      },
    ],
  },
}

# let goals know their category
for category, cinfo in GOALS_BY_CATEGORY.items():
  for goal in cinfo['goals']:
    goal['category'] = category
