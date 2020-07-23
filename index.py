from flask import Flask, request, jsonify
import os

from generator.gpt2.gpt2_generator import *
from story import grammars
from story.story_manager import *
from story.utils import *
from play import *

app = Flask(__name__)
generator = None
story_manager = None

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

@app.route('/')
def home():
  return 'Hello, World!'

@app.route('/start')
def start():
  global generator
  generator = GPT2Generator()
  global story_manager
  story_manager = UnconstrainedStoryManager(generator)

  data = None

  with open(YAML_FILE, 'r') as stream:
    data = yaml.safe_load(stream)

  (setting_key, character_key, name, character, setting_description) = random_story(data)

  context, prompt = get_curated_exposition(
                        setting_key, character_key, name, character, setting_description
                    )

  return story_manager.start_new_story(prompt, context=context)

@app.route('/continue')
def continue_story():
  return story_manager.act('')

@app.route('/do', methods = ['POST'])
def do_action():
  action = request.json['action']

  if "you" not in action[:6].lower() and "I" not in action[:6]:
      action = action[0].lower() + action[1:]
      action = "You " + action

  if action[-1] not in [".", "?", "!"]:
      action = action + "."

  action = first_to_second_person(action)

  action = "\n> " + action + "\n"

  return story_manager.act(action)

if __name__ == '__main__':
  app.run()