import logging
logger = logging.getLogger(__name__)

from typing import Any
from .common import *

def make_pickleable(fn):
    def wrapped():
        return fn
    return wrapped

def _queryset(typ, _id, Ms, k):
    response = get_response(Ms, model=DEFAULT_MODEL)

    st, en = '```json', '```'
    if response.startswith(st) and response.endswith(en):
        print('fixing json!')
        response = response[len(st):-len(en)]

    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        pass

    db[typ].update_one({'_id': _id}, {'$set': {k: response}})
    logging.log(logging.DEBUG, f"Set {k} to {response} for {typ} {_id}")
    return response

class Knowledge:

    def __init__(self, _id):
        if type(_id) == str:
            _id = oid(_id)

        self._id = _id
        self.knowledge_type = self.__class__.__name__.lower()
        self.db = db[self.knowledge_type]

        self._data = self.db.find_one({'_id': _id})
        if self._data is None:
            raise ValueError(f"Knowledge with id {_id} does not exist.")
    
    def __getattribute__(self, __name: str) -> Any:
        # first just check if the attribute exists
        if __name in object.__getattribute__(self, '__dict__'):
            return super().__getattribute__(__name)
        
        try:
            # Try to directly access _data
            _data = object.__getattribute__(self, '_data')
            
            # Check if the attribute is in _data
            if __name in _data:
                return _data[__name]

        except AttributeError:
            # If _data does not exist, just pass and continue
            pass

        # Fallback to normal attribute access
        try:
            return super().__getattribute__(__name)
        except AttributeError:
            # If the attribute does not exist, and there's an instruction, query
            QS = object.__getattribute__(self, 'questions')
            if __name in QS:
                self.query(__name)
                return self.__getattribute__(__name)
            else:
                raise AttributeError(f"Knowledge object does not have attribute {__name}")

    @classmethod
    def new(cls, **kwargs):
        kwargs['created_at'] = dt.datetime.now()
        knowledge_type = cls.__name__.lower()
        cid = db[knowledge_type].insert_one(kwargs).inserted_id
        c = cls(cid)
        return c
        
        
    def current_information(self):
        str_parts = []
        for k,v in self._data.items():
            if k == '_id':
                continue

            if type(v) in {list, dict, set}:
                v = json.dumps(v, indent=2)

            str_parts.append(f"{k}: {v}")
        return "\n".join(str_parts)
    
    def set(self, key, value):
        self._data[key] = value
        self.db.update_one({'_id': self._id}, {'$set': {key: value}})

    def _queryset_async(self, Ms, k):
        from multiprocessing import Process
        p = Process(target=_queryset, args=(self.knowledge_type, self._id, Ms, k))
        p.start()
        return p

    def query(self, key, synchronous=True):
        import asyncio
        question = self.questions[key]

        prompt1 = self.attribute_prompt

        prompt2 = flatten_whitespace(f"""
            The current {self.knowledge_type} description is:
            {indent(self.current_information(), 2)}
        """)

        my_messages = [
            {'role': 'system', 'content': prompt1},
            {'role': 'user', 'content': prompt2},
        ]
        my_messages.append({'role': 'user', 'content': question})

        logger.log(logging.DEBUG, f"Querying {self.knowledge_type} with question {question}")
        if synchronous:
            result = _queryset(self.knowledge_type, self._id, my_messages, key)
            self.set(key, result)
        else:
            self._queryset_async(my_messages, key)