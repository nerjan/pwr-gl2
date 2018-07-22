# TODO

Things to do in the first place:

1. define database models of user, traits, questions and answers (see the file
   `db_declarative.py` for details)
2. make login and logout views plus secure other functions with _authorization
   required_ decorator (in `app.py`)
3. develop an algorithm to translate user answers into trait scores: each
   questions (for example: _do you like exotic food?_) corresponds to some trait
   (say, openness), we need to convert the the answer to some point scale, so
   that sum of all answers related to openness can be compared with openness
   trait from Genomelink API
4. make a list of questions. Perhaps this will be a good start?
   https://ipip.ori.org/New_IPIP-50-item-scale.htm
5. populate questions table with those sample list; perhaps make it automatic
   somehow?
6. write `questionare()` function in `app.py`
7. write `selfassessment()` function in `app.py`
