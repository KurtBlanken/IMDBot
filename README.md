#IMDBot
  IMDBot is a class project for UCSC's CMPS 140/240, a combined graduate/undergraduate course in Artificial Intelligence, with an emphasis on Natural Language Processing.
  The goal is to develop a natural language interface (i.e. chatbot) to the Internet Movie Database (IMDB). The bot should be able to accept user queries and preferences in the form of English sentences (an utterance), and respond with either the requested information or questions required to narrow down the scope of the request.

## Examples
User: I like Nicole Kidman.
IMDBot: Ok.

User: What movies was Gary Oldman last in?
IMDBot: The Book of Eli.

User: Was James Gandolfini in Where the Wild Things Are?
IMDBot: He was.

## Ontology: Classes / Objects
To simplify the knowledge representation, we will attempt to split the world into two very broad categories - classes and objects. This is simply a set representation of the world where every object is an example of something in a class. Finally, classes have related classes. For example, James Gandolfini (JG) is in the class of actors, Where the Wild Things Are is in the class of movies (WTWTA). A query is a filter on everything in a class using objects in a related classes. For example, "movies" have "actors". JG is in the class of actors. Thus, we can find any movies where JG is in the set of actors in that movie. In other words, we are looking at a new class, the class of WTWTA-actors, and seeing if JG is in that class.

# Architecture
See IMDBot.dia and IMDBot.pdf
