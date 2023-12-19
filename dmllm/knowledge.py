from typing import Any
from .common import *

from bson import ObjectId as oid

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
        return super().__getattribute__(__name)

    @classmethod
    def new(cls, **kwargs):
        knowledge_type = cls.__name__.lower()
        cid = db[knowledge_type].insert_one(kwargs).inserted_id
        c = cls(cid)
        return c
        
    def current_information(self):
        str_parts = []
        for k,v in self._data.items():
            if k == '_id':
                continue

            if type(v) == list:
                v = ", ".join(v)
            elif type(v) == dict:
                v = json.dumps(v, indent=2)

            str_parts.append(f"{k}: {v}")
        return "\n".join(str_parts)
    
    def set(self, key, value):
        self._data[key] = value
        self.db.update_one({'_id': self._id}, {'$set': {key: value}})

    def query(self, key):
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

        print("Asking:", question)
        response = get_response(my_messages, model=DEFAULT_MODEL)

        try:
            response = json.loads(response)
        except json.decoder.JSONDecodeError:
            pass

        self.set(key, response)
        print("Response:", response)