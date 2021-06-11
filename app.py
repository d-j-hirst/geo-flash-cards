import tkinter as tk
from tkinter import messagebox, Menu, simpledialog
from PIL import ImageTk, Image
from quiz import Quiz, Mode
from options_window import OptionsWindow

from cards import Type, is_image_type
#===================
# * App Class *
# Handles the interface of the program
#===================

class App:
  font_size = 16
  rating_font_size = 11
  window_width = 300
  section_height = 300
  middle_section_height = 100
  rating_section_height = 100

  def __init__(self):
    self.window = tk.Tk()

    # set up window grid arrangement
    self.window.geometry(str(App.window_width) + 'x' + str(App.section_height * 2 + App.middle_section_height + App.rating_section_height))
    self.window.columnconfigure(0, weight=1)
    self.window.rowconfigure(0, weight=App.section_height)
    self.window.rowconfigure(1, weight=App.middle_section_height)
    self.window.rowconfigure(2, weight=App.rating_section_height)
    self.window.rowconfigure(3, weight=App.section_height)

    # set up menu bar
    self.menubar = Menu(self.window)
    self.commands_menu = Menu(self.menubar, tearoff=0)
    self.commands_menu.add_command(label="Configure Maps", command=self.begin_map_configuration)
    self.commands_menu.add_command(label="Options", command=self.open_options_window)
    self.commands_menu.add_command(label="Ambiguity check", command=self.ambiguity_check)
    self.commands_menu.add_command(label="Reload Quiz", command=self.reload_quiz)
    self.menubar.add_cascade(label="Commands", menu=self.commands_menu)
    self.window.config(menu=self.menubar)

    # create widgets to be placed within the window
    self.top_frame = tk.Frame(master=self.window, width=App.window_width, height=App.section_height)
    self.middle_frame = tk.Frame(master=self.window, width=App.window_width, height=App.middle_section_height)
    self.rating_frame = tk.Frame(master=self.window, width=App.window_width, height=App.rating_section_height)
    self.bottom_frame = tk.Frame(master=self.window, width=App.window_width, height=App.section_height)
    self.prompt = tk.Label(text='Question prompt', master=self.top_frame, font=('Arial', App.font_size), wraplength=App.window_width)
    self.sub_prompt = tk.Label(text='', master=self.middle_frame, font=('Arial', App.font_size), wraplength=App.window_width)
    self.img_prompt = tk.Label(master=self.top_frame)
    self.rating_prompt = tk.Label(text='', master=self.rating_frame, font=('Arial', App.rating_font_size), wraplength=App.window_width)
    self.answer = tk.Entry(master=self.bottom_frame, width=20, font=('Arial', App.font_size))
    self.map = tk.Canvas(master=self.bottom_frame, width=App.window_width, height=App.section_height)
    
    # place widgets within the grid
    self.top_frame.grid(row=0, column=0)
    self.middle_frame.grid(row=1, column=0)
    self.rating_frame.grid(row=2, column=0)
    self.bottom_frame.grid(row=3, column=0)
    username = simpledialog.askstring("Input", "Enter username (alphanumeric characters only)",
                                      parent=self.window)

    # bind callbacks to 
    self.window.bind('<Return>', key_pressed)
    self.map.bind("<Button-1>", self.click_callback)

    self.quiz = Quiz(username)
  
  def next_cycle(self):
    if self.mode == Mode.Question:
      self.check_answer()
    elif self.mode == Mode.Answer:
      self.load_new_question()
    elif self.mode == Mode.ConfigureMap:
      self.display_next_map_config()

  def load_new_question(self):
    question = self.quiz.select_question()
    if question is None: return
    if question.type == Type.City.value:
      self.prompt.config(text=question.card.prompt, image=None)
      self.prompt.pack()
      self.img_prompt.pack_forget()
    elif question.type == Type.Map.value:
      self.prompt.config(text=question.card.prompt, image=None)
      self.prompt.pack()
      self.img_prompt.pack_forget()
    if is_image_type(question.type):
      self.img = ImageTk.PhotoImage(Image.open(question.card.image_path))
      self.img_prompt.config(image=self.img)
      self.img_prompt.pack()
      self.prompt.pack_forget()
    sub_text = ''
    if question.require_subregion:
      sub_text += 'Include a region (state, province, etc.)\n'
    if question.give_hint:
      sub_text += 'Hint: ' + question.card.hint
    rating_text = 'Rating: ' + f'{self.quiz.effective_rating():.1f}'
    self.sub_prompt.config(text=sub_text)
    self.rating_prompt.config(text=rating_text)
    self.sub_prompt.pack()
    self.rating_prompt.pack()
    if question.type == Type.Map.value:
      map_path = self.quiz.get_region_map(question.card.region)
      self.img = ImageTk.PhotoImage(Image.open(map_path))
      self.map.delete('all')
      self.map.create_image(App.window_width / 2, App.section_height / 2, image=self.img)
      self.map.pack()
    else:
      self.answer.delete(0, 'end')
      self.answer.pack()
      self.answer.focus_set()
      self.map.pack_forget()
    self.mode = Mode.Question

  def check_answer(self):
    question = self.quiz.get_current_question()
    if (question.type == Type.Map.value):
      return
    given_answer = self.answer.get().lower().strip()
    previous_prompt = question.card.prompt if question.type == Type.City.value else ''
    result = self.quiz.submit_answer(given_answer)
    if isinstance(result, str):
      messagebox.showinfo('',result)
      return
    if result is None:
      return

    self.rating_prompt.config(text=f'''Player rating change from {result['old_player_rating']:.1f} to {result['new_player_rating']:.1f}
      Question rating change from {result['old_question_rating']:.1f} to {result['new_question_rating']:.1f}''')
    if result['match']:
      new_text = previous_prompt + '\n\n' + given_answer + ' is correct!' + \
        '\n(Full answer: ' + ', '.join(result['correct_answer']) + ')'
    else:
      new_text = previous_prompt + '\n\n' + given_answer + \
        ' was incorrect. The correct answer was: ' + ', '.join(result['correct_answer'])
    self.prompt.config(img=None, text=new_text)
    self.prompt.pack()
    self.rating_prompt.pack()
    self.answer.pack_forget()
    self.sub_prompt.pack_forget()
    self.mode = Mode.Answer
  
  def display_next_map_config(self):
    config_card = self.quiz.select_config_card()
    if config_card is None:
      messagebox.showinfo('','All maps are already configured, returning to quiz')
      self.load_new_question()
      return
    self.prompt.config(text=config_card.prompt, image=None)
    self.prompt.pack()
    self.img_prompt.pack_forget()
    self.answer.pack_forget()
    sub_text = 'Answer is: ' + config_card.region + ', ' + config_card.subregion
    if len(config_card.hint) > 0:
      sub_text += '\nHint: ' + config_card.hint
    self.sub_prompt.config(text=sub_text)
    self.sub_prompt.pack()
    map_path = self.quiz.maps[config_card.region]
    self.img = ImageTk.PhotoImage(Image.open(map_path))
    self.map.delete('all')
    self.map.create_image(App.window_width / 2, App.section_height / 2, image=self.img)
    self.map.pack()
    
  def begin_map_configuration(self):
    self.mode = Mode.ConfigureMap
    self.display_next_map_config()
  
  def ambiguity_check(self):
    result = self.quiz.ambiguity_check()
    if result is not None:
      messagebox.showinfo('', result)
    else:
      messagebox.showinfo('', 'No ambiguous locations found!')
  
  def reload_quiz(self):
    self.quiz.reload()

  def run(self):
    self.load_new_question()
    self.window.mainloop()

  def click_callback(self, event):
    if self.mode == Mode.ConfigureMap:
      self.quiz.set_config_map_loc((event.x, event.y))
      self.display_next_map_config()
    elif self.mode == Mode.Question:
      result = self.quiz.submit_map_answer((event.x, event.y))
      self.prompt.config(text='You were ' + '{:.1f}'.format(result['distance']) + ' pixels away')
      self.map.create_oval(event.x - 2, event.y - 2, event.x + 2, event.y + 2, fill='red')
      self.map.create_oval(result['answer_x'] - 2, result['answer_y'] - 2, result['answer_x'] + 2, result['answer_y'] + 2, fill='green')
      self.rating_prompt.config(text=f'''Player rating change from {result['old_player_rating']:.1f} to {result['new_player_rating']:.1f}
        Question rating change from {result['old_question_rating']:.1f} to {result['new_question_rating']:.1f}''')
      self.mode = Mode.Answer
    elif self.mode == Mode.Answer:
      self.load_new_question()
  
  def open_options_window(self):
    self.options_window = OptionsWindow(self.window, self.quiz, self.options_window_callback)

  def options_window_callback(self, options):
    self.options_window = None
    self.quiz.type_filters = options['filters']
    self.quiz.subregion_setting = options['subregion_setting']
    self.quiz.hint_setting = options['hint_setting']
    self.quiz.prompt_filter = options['prompt_filter']
    self.quiz.region_filter = options['region_filter']
    self.quiz.save_user()


def key_pressed(event):
  app.next_cycle()


app = App()
app.run()