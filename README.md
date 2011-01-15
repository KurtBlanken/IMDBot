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
## Modules
### imdbot.py
  Receives an id, utterances pair from either stdin (using the special id of "console"), or a pipe. Responsible for passing the id and utterance to the various other modules (information flow).
### Natural Language Understander (NLU.py)
  Responsible for deriving logical meaning from utterance. Must determine whether utterance is a question or a statement (user preference), the objects or classes the utterance refers to, and any relationships between those objects/classes.
### Dialog Manager / Planner (DMP.py)
   Responsible for using logical meaning to craft a database query. Has access to user id, can retrieve user preferences (for a question) or store new user preferences (for a statement). Must either return a response to the query (a statement), or some set of questions to ask to fulfill the query request. Responses are crafted in a similar manner to the input, a set of objects and classes, and the relationships between.
#### OfflineDB
  Accessible by the DMP, the OfflineDB is a read-only data store for knowledge retrieval. The DMP can use the OfflineDB to construct the classes is knows about (i.e. cities, countries, movies, songs, actors, musicians). The OfflineDB can then be queried for objects fitting the given classe(s).
#### OnlineDB
  Accessible by the DMP and NLG, the OnlineDB stores user preferences and information. For example, the users name can be stored to craft more natural responses. User preferences can also be stored here that will persist across queries, if the query type can use the preference.
### Natural Language Generator (NLG.py)
  Responsible for converting from the logical objects and classes used by the DMP back to natural language. Is required to handle both simple statements, like a single object given as a result of a query, and complex queries, like what the user knows about the relationship between several objects and several classes. Can use the user id to personalize the response by, e.g., name or gender.
## Flow
            (utterance) -> NLU -> (question/statement)
                        -> DMP -> (question/statement)
                        -> NLG -> (utterance)
