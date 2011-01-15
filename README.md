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
