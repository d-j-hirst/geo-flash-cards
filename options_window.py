import tkinter as tk
from cards import Type
from quiz import Subregion_Setting, Hint_Setting

#===================
# * OptionsWindow Class *
# Handles the options window (which allows for filtering of future quiz questions)
#===================

class OptionsWindow:
  def __init__(self, parent, quiz, callback):
    self.window = tk.Toplevel(parent)
    self.callback = callback
    self.output = {'filters': quiz.type_filters}

    # create variables associated with widgets
    self.city_filter = tk.IntVar(value = 1 if quiz.type_filters[Type.City.value] else 0)
    self.flag_filter = tk.IntVar(value = 1 if quiz.type_filters[Type.Flag.value] else 0)
    self.map_filter = tk.IntVar(value = 1 if quiz.type_filters[Type.Map.value] else 0)
    self.bollard_filter = tk.IntVar(value = 1 if quiz.type_filters[Type.Bollard.value] else 0)
    self.subregion_setting = tk.IntVar(value=quiz.subregion_setting)
    self.hint_setting = tk.IntVar(value=quiz.hint_setting)
    self.prompt_filter = tk.StringVar(value=quiz.prompt_filter)
    self.region_filter = tk.StringVar(value=quiz.region_filter)

    #create the widgets themselves
    self.city_check = tk.Checkbutton(self.window, text='Cities', variable=self.city_filter)
    self.flag_check = tk.Checkbutton(self.window, text='Flags', variable=self.flag_filter)
    self.map_check = tk.Checkbutton(self.window, text='City Maps', variable=self.map_filter)
    self.bollard_check = tk.Checkbutton(self.window, text='Bollards', variable=self.bollard_filter)
    self.subregion_either = tk.Radiobutton(self.window,
                                           text='Subregions: Either',
                                           variable=self.subregion_setting,
                                           value=Subregion_Setting.Either.value)
    self.subregion_always = tk.Radiobutton(self.window,
                                           text='Subregions: Always if available',
                                           variable=self.subregion_setting,
                                           value=Subregion_Setting.Always.value)
    self.subregion_never = tk.Radiobutton(self.window,
                                          text='Subregions: Never',
                                          variable=self.subregion_setting,
                                          value=Subregion_Setting.Never.value)
    self.hint_either = tk.Radiobutton(self.window,
                                      text='Hints: Either',
                                      variable=self.hint_setting,
                                      value=Hint_Setting.Either.value)
    self.hint_always = tk.Radiobutton(self.window,
                                      text='Hints: Always if available',
                                      variable=self.hint_setting,
                                      value=Hint_Setting.Always.value)
    self.hint_never = tk.Radiobutton(self.window,
                                     text='Hints: Never unless necessary',
                                     variable=self.hint_setting, value=Hint_Setting.Never.value)
    self.prompt_filter_label = tk.Label(self.window, text="Prompt filter:")
    self.prompt_filter_entry = tk.Entry(self.window,
                                        textvariable=self.prompt_filter)
    self.region_filter_label = tk.Label(self.window, text="Region filter:")
    self.region_filter_entry = tk.Entry(self.window,
                                        textvariable=self.region_filter)
    self.ok_button = tk.Button(self.window,
                               text='Save options',
                               command=self.return_options)

    # pack controls so they display
    self.city_check.pack()
    self.flag_check.pack()
    self.map_check.pack()
    self.bollard_check.pack()
    self.subregion_either.pack()
    self.subregion_always.pack()
    self.subregion_never.pack()
    self.hint_either.pack()
    self.hint_always.pack()
    self.hint_never.pack()
    self.prompt_filter_label.pack()
    self.prompt_filter_entry.pack()
    self.region_filter_label.pack()
    self.region_filter_entry.pack()
    self.ok_button.pack()
  
  def return_options(self):
    self.output['filters'][Type.City.value] = (self.city_filter.get() == 1)
    self.output['filters'][Type.Flag.value] = (self.flag_filter.get() == 1)
    self.output['filters'][Type.Map.value] = (self.map_filter.get() == 1)
    self.output['filters'][Type.Bollard.value] = (self.bollard_filter.get() == 1)
    self.output['subregion_setting'] = self.subregion_setting.get()
    self.output['hint_setting'] = self.hint_setting.get()
    self.output['prompt_filter'] = self.prompt_filter.get()
    self.output['region_filter'] = self.region_filter.get()
    self.callback(self.output)
    self.window.destroy()
