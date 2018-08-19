# TODO

Things to do next:

1. *The algorithm* to translate user answers into trait scores: each questions
   (for example: _do you like exotic food?_) corresponds to some trait (say,
   openness), we need to convert the the answer to some point scale, so that
   sum of all answers related to openness can be compared with openness trait
   from Genomelink API.

   Consider using Bayesian average:
   https://en.wikipedia.org/wiki/Bayesian_average
   It differs from standard mean in a way that when the sample is small, the
   outcome (average) is pushed towards a pre-selected value, which in our case
   could be 2.5 (or 0, depending on the scale used).

2. *More questions* are needed for other traits

3. *Questionare view*, for asking questions; currently for self-assessment,
   but in the future the same questionare could be used to ask questions about
   other people.

4. *Self-assessment* view to show the results of the self-assessment test.

5. *Friends* (or collegues, or buddies, etc.) - we need to implement adding
   friends in our app; remember - we want to allow both, self-assessment and
   insight from others. Here we have to think how the  questions will be
   formulated; curently our database contains questions like _Do you?_, we
   need to change them into _Does [someone]?_

6. *Name* - our app needs a catchy name!

Optional stuff:

1. Send email to confirm email address upon registration and activate the
   account only when the confirmation link is clicked.

2. Implement _forgotten password_ feature.

3. Social media login, using for example https://pythonhosted.org/Flask-Social/
