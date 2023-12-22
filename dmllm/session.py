from .common import *
from .knowledge import Knowledge

class Session(Knowledge):
    def __init__(self, _id):
        super().__init__(_id)

        # get summaries first
        summaries = self.summaries()

        mq = {
            'session_id': self._id,
        }

        if len(summaries):
            # what's the last time we summarized?
            last_summ = max([x['end'] for x in summaries])

            # get all messages after that
            mq['created_at'] = {'$gt': last_summ}

        messages = list(db.messages.find(mq).sort('created_at', 1))

        self.M = [
            *[{"role": "system", "content": "The following are the summaries of the session so far:"}] * (len(summaries) > 0),
            {"role": "system", "content": "\n\n".join([x['summary'] for x in summaries])},
            *[{"role": "system", "content": "The following is the conversation between the DM and the player so far:"}] * (len(messages) > 0),
            *messages,
        ]

        # just in case we have a ton of extra messages...
        self.consolidate_messages()

        from .entity import Entity
        self.player = Entity(self.player_id)

    @property
    def previous(self):
        previous_sessions = db.session.find({'player_id': oid(self.player_id)}).sort('created_at', -1).limit(2)
        previous_sessions = list(previous_sessions)[1:]
        if len(previous_sessions) == 0:
            return None
        else:
            return Session( previous_sessions[0]['_id'] )

    def summarize(self):
        summ_now = self.summaries()
        if not len(summ_now):
            return "Nothing here..."
        
        events = [y for x in summ_now for y in x['events']]
        characters = [y for x in summ_now for y in x['characters']]
        summaries = [x['summary'] for x in summ_now]

        full_s = [
            "Events:\n",
            "\n".join(events),
            "\n\n",
            "Characters:\n",
            "\n".join(characters),
            "\n\n",
            "Summaries:\n",
            "\n".join(summaries),
        ]

        self.db.update_one(
            {'_id': self._id},
            {'$set': {'summary': self._summarize_strings(full_s)}}
        )

        return self._summarize_strings(full_s)

    @classmethod
    def new_with_player(self, player):
        session = Session.new(player_id=oid(player._id))
        return session

    def messages(self, limit=None, q=None):
        if q is None:
            q = {}

        ms = db.messages.find({
            'session_id': self._id,
            **q,
        }).sort('created_at', -1)

        if limit is not None:
            ms = ms.limit(limit)

        return reversed(list(ms))
    
    def summaries(self):
        return list(db.summaries.find({'session_id': self._id}))

    def _summarize_block(self, messages):
        message_text = "\n".join(messages)
        prompt = f"""
        Your goal is to summarize the plotpoints contained in the following conversation between a DM and a player.
        In each plot point, be as specific as possible.
        Keep note of any characters, locations, or items that are mentioned.
        Do not include any information not present in the following messages!

        Messages:
        {message_text}
        """

        messages = [
            {"role": "system", "content": prompt},
        ]

        response = get_response(messages)
        return response

    def _summarize_messages(self, messages=None, char_limit = 4500):
        if messages is None:
            messages = self.M

        parts = [
            f"{m['role']}\n{m['content']}\n"
            for m in messages
        ]
        return self._summarize_strings(parts, char_limit=char_limit)

    def _summarize_strings(self, messages=None, char_limit = 4500):
        # loop, adding messages until doing so would put us over the character limit,
        # summarizing at each step

        print('Saving progress...')
        this_block = []
        summaries = []

        if messages is None:
            messages = self.M

        for m in messages:
            current_len = len("\n".join(this_block))
            if current_len + len(m) + 1 > char_limit:
                summaries.append(self._summarize_block(this_block))
                this_block = []

            this_block.append(m)

        if len(this_block):
            summaries.append(self._summarize_block(this_block))

        #print(summaries)

        if len(summaries) > 1:
            return self._summarize_block(summaries)
        
        return summaries[0]

    def _get_events(self, M=None):
        if M is None:
            M = self.M

        M = [
            *M,
            {"role": "system", "content": "Please give descriptions of the events of the session so far. One event per line."},
        ]

        events = get_response(M)
        events = events.split("\n")
        events = [x.strip() for x in events]
        events = [x for x in events if len(x)]
        return events
    
    def _get_characters(self, M=None):
        if M is None:
            M = self.M

        M = [
            *M,
            {"role": "system", "content": "Please give descriptions of the newly introduced characters from the session so far. One character per line."},
        ]

        characters = get_response(M)
        characters = characters.split("\n")
        characters = [x.strip() for x in characters]
        characters = [x for x in characters if len(x)]
        return characters

    def consolidate_messages(self):
        # let's calculate the total number of tokens we are using
        # and then we can decide whether to consolidate

        # we'll use the following heuristic:
        # if the total number of tokens is at least 3000, consolidate
        # we'll also consolidate if the number of player messages is at least 15
        # one token is roughly 4 characters

        chars = sum([len(x['content']) for x in self.M])
        tokens = chars / 4
        #print('estimating', tokens, 'tokens...')
        from bson.json_util import dumps
        #print(dumps(self.M, indent=2))
        if tokens < 1500 and sum( [x['role'] == 'user' for x in self.M] ) < 15:
            return
        
        summ = self._summarize_messages()
        cs, ev = self._get_characters(), self._get_events()

        start = min([x['created_at'] for x in self.M if 'created_at' in x])
        end = max([x['created_at'] for x in self.M if 'created_at' in x])

        db.summaries.insert_one({
            'session_id': self._id,
            'player_id': self.player_id,
            'characters': cs,
            'events': ev,
            'summary': summ,
            'created_at': dt.datetime.utcnow(),
            'start': start,
            'end': end,
        })

        self.M = [
            {"role": "system", "content": "The following is a summary of the session so far:"},
            {"role": "system", "content": summ},
        ]

    # ------------------
    # SAYING STUFF
    # ------------------

    def humansay(self, content):
        m = {
            'session_id': self._id,
            'player_id': self.player_id,
            'role': 'user',
            'content': content,
            'created_at': dt.datetime.utcnow(),
        }

        self.M.append(m)
        self.consolidate_messages()
        db.messages.insert_one(m)

    def computersay(self, content):
        m = {
            'session_id': self._id,
            'player_id': self.player_id,
            'role': 'assistant',
            'content': content,
            'created_at': dt.datetime.utcnow(),
        }

        self.M.append(m)
        self.consolidate_messages()
        db.messages.insert_one(m)

        print('DM:', content)

    def computersay_self(self, content):
        m = {
            'session_id': self._id,
            'player_id': self.player_id,
            'role': 'system',
            'content': '(thinking to myself...) ' + content,
            'created_at': dt.datetime.utcnow(),
        }

        self.M.append(m)
        db.messages.insert_one(m)
