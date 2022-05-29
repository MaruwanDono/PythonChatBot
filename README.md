# PythonChatBot
A chatbot made with python from reddit comments data (inspired by sentdex tutorial on youtube).

Data sources : https://files.pushshift.io/reddit/comments/

Scripts:
*py_AI_data_v1_2.py: Extract comments from data sources into pairs question/answer in a .db file
*AI_train.py: Organize pairs into text files and separte training data and testing data.
*training_model.py: Trains the model (options in script starting from line 443).


The chatbot can be launched with the weights I've obtained from training the model. To do this you must first change the
bool "train_model" in training_model.py line 451 to False, then launch the script "training_model.py" with python3.
If "train_model" is True, the script will launch the training.
