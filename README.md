# Geo Flash Cards

This is a Python program for practising identifying geographical features useful for Geoguessr. Players are presented with a clue such as a flag, city name, or some other distinctive feature and type in a country or region of a country.

**Disclaimer:** this project is currently under construction, and at any given time may not be stable, well suited to play, or user-friendly in some aspects. Questions may be unbalanced, ambiguous, or occasionally have the wrong answer entirely.

# Installation

- You will need to have Python installed - download the latest version [here](https://www.python.org/downloads/)
- Extract/clone the repository to a new folder
- Open a command prompt in the root folder (the one containing ``app.py``). Run the following commands to set up the Python virtual environment:
    * Create a virtual environment with:  
     ``python3 -m venv env``  
     or if that gives an error,  
     ``python -m venv env``  
    * Then activate the virtual environment:  
     on Windows: ``env\Scripts\activate``  
     on Mac/Linux: ``source tutorial-env/bin/activate``
    * Use pip to install the required dependencies:
     ``pip3 install -r requirements.txt``
- In the command prompt, run the program with:  
  ``python3 app.py``  
  or if that gives an error,  
  ``python app.py``
  If you exit the program, you only need to do this last step to run it again.

# How to use
## User profiles

When opening the program, you will be prompted for your username - if it is your first time playing the game enter whatever you like and it will create a new profile. The profile will only be stored locally on your computer and will keep track of your play so that you get questions of appropriate difficulty. You can have as many profiles as you like, either for different people or for saving different settings (see "Options" below). At the moment the program does not support changing the current profile within the program, quit and restart if you want to use a different profile.

## Answering questions

After loading a profile, the main window will show a form of question for the user to answer. This may be an image such as a flag, or a distinctive terrain feature (bollard, power pole, road sign, etc.), or it may be the name of a city or other feature. The player then has to answer with the country where it is found. Answering is not case sensitive and many common abbreviations and alternative names are accepted (for example, an answer of ``United States of America`` can also be entered as ``US``, ``us``, ``usa``, ``united states``, among others). For the full details look at ``regions.txt``, which you may edit to add additional abbreviations as you wish.

Sometimes the question will require a subregion (state, province, etc.) as well as the country itself. Answer by typing the country and subregion separated by a comma. For example, to answer such a question with the prompt ``Chicago``, answer with, say, ``United States,Illinois``. Once again, common abbreviations are accepted, so ``us,il`` would also be a correct answer here.

Sometimes a hint is provided to a question. The main purpose of a hint is to help ensure that the answer to a question is not ambiguous (although keep in mind that for commonly used names, it is difficult to completely rule out all options; try to select the most notable answer). With default settings, some questions will be provided with a hint even if not necessary, in order to make sure that players do not provide their answers based on the presence of the hint rather than the actual prompt.

For cities and other locations, instead of entering a country by name, the program will present the player with a map on which they should click where they think the locations is within its country.

Once an answer is entered into the given text box, press Enter/Return to submit the answer, and the screen will provide feedback on whether the answer is correct, and what the correct answer was if it is incorrect. Press Enter/Return once more to continue to a new question.

## Ratings

For each profile ratings are kept for both the player and individual questions. Player ratings are used to provide questions of an appropriate level, and question ratings are used to calibrate a player's strengths and weaknesses. When a question is chosen for a player, questions with a rating closer to the player's rating will be much more likely to be chosen, although all questions will still have some chance to be chosen as long as they are eligible under the current settings.

## Question options

The number of questions in the default settings can become quite overwhelming, as there are very many questions that can be asked. Question options can be used to reduce the range of given questions to a manageable number. To view question options, click the menu item ``Commands > Question Options``.

The top checked boxes will enable or disable different types of questions. Below that, the behaviour regarding asking for subregions can be modified - by default ("Either"), the subregion will be asked for 50% of the time when possible; this can be changed so that the subregion is always asked for, or never asked for. Similarly, the frequency of hints can be adjusted between the default "Either" (which gives about a 20% chance for them to appear when not necessary) and "Always if available" or "Never unless necessary".

Finally, more specific control can be provided using the prompt and region filters. [Regular expressions](https://docs.python.org/3/howto/regex.html#regex-howto) can be entered by the user - if so, only questions whose prompts and/or regions match the regular expression will be selected. These filters are case-insensitve. A simple use case is to only ask for questions whose answers lie within a certain country - for example, to see only locations within Japan, simply enter "japan" into the "Region filter" entry box. This is, of course, most useful when wanting questions including subregions or answered on a map, otherwise the answers become trivial.

## User-created questions

Users may add their own questions for use in the program. Questions should be added in plaintext files in subdirectories of the ``\cards`` directory; the structure of these directories and files should mirror those found in the ``\builtin`` directory. Instructions on how to add these questions are presently beyond the scope of this readme, but the files in the ``\builtin`` directory can be used as a guide.