from .common import *
from .knowledge import Knowledge
from .entity import Entity
from .location import Location

# create a universe?
# create a story
# + the big bad
# + smaller big bads

class World(Knowledge):
    questions = {
        "gods": "What gods are there? What are their domains?",
    }

class SubQuest(Knowledge):
    questions = {
        "NPC_descriptions": "Briefly describe the NPCs in this adventure. This should be a simple JSON list, with each element containing a string description of an interesting character players may encounter.",
        "location_descriptions": "Briefly describe the locations in this adventure. This should be a simple JSON list, with each element containing a string description of an interesting location players may encounter.",
    }

    attribute_prompt = flatten_whitespace(f"""
        Your role in life is to imagine an adventure, in a tabletop RPG.
        This is a smaller bit of a much larger and all-encompassing story, which may take their whole lives to complete.
    """)

    @classmethod
    def new_from_description(cls, description, synchronous=True):
        c = cls.new()
        c.set('description', description)

        for q in cls.questions:
            c.query(q, synchronous=True)

        NPC_ids = []
        if type(c.NPC_descriptions) == list:
            for n in c.NPC_descriptions:
                e = Entity.new_from_description(n, synchronous=synchronous)
                NPC_ids.append(e._id)
            c.set('NPC_ids', NPC_ids)
        
        location_ids = []
        if type(c.location_descriptions) == list:
            for l in c.location_descriptions:
                e = Location.new_from_description(l, synchronous=synchronous, expand=False)
                location_ids.append(e._id)
            c.set('location_ids', location_ids)

        return c

class Quest(Knowledge):
    questions = {
        "big_bad": "Adventurers needs a threat worthy of the heroes' attention. The threat might be a single villain or monster, a villain with lackeys, an assortment of monsters, or an evil organization. Whatever their nature, the antagonists should have goals that the heroes can uncover and thwart. Who is the big bad of this story? Simply describe their personality, appearance, and goals. Do not describe the quest yet.",
        "adventure1": "What is the first adventure in this story? What is the hook? What is the goal?",	
        "adventure2": "What is the second adventure in this story? Perhaps they learn more about the big bad?",
        "adventure3": "What is the third adventure in this story? This is the climax of the story.",
        "start_description": "Briefly describe an interesting starting location for the adventure.",
        "name": "Give a short name for this quest.",
    }
    
    attribute_prompt = flatten_whitespace(f"""
        Your role in life is to imagine a quest, in a tabletop RPG.
        Here are some tips for crafting the adventure:
            Formidable Antagonists: A great adventure story requires a credible threat, appropriate to their level of course. 
                This could be a villain, a group of monsters, or an evil organization. 
                Their motives should be intriguing and challenge the heroes, providing a solid foundation for conflict and engagement.
                Again, these antagonists must be appropriate to their level.
            Familiar Tropes with Innovative Twists: 
                Utilize classic fantasy elements like dragons, orcs, or wizards, but add unique twists. 
                For instance, the mysterious figure seeking help could actually be a king in disguise, or the eccentric wizard could be an illusion masking a deeper secret. This approach respects genre traditions while keeping the story fresh and unpredictable.
            Significant Role of Heroes: Ensure that the heroes' actions and decisions significantly impact the story. Unlike a scripted novel or TV show, an adventure should be open to multiple outcomes, avoiding the feeling of a predetermined path.
            Diverse Appeal for All Players: Address the varied interests of your audience. Incorporate a balance of exploration, social interaction, and combat to cater to different player preferences. Remember to tailor the adventure to your specific audience rather than trying to appeal to every possible player type.
            Element of Surprise: Strategically include surprises to engage and challenge players. This could range from discovering hidden locations to unexpected plot twists. However, maintain a balance to avoid overwhelming the players.
            Structured Adventure Flow: A compelling adventure should have a clear beginning, middle, and end.
                Beginning: Start with an engaging hook that draws players in and sets the stage for the adventure.
                Middle: Develop the story with challenges and discoveries, allowing the heroes to influence the narrative and uncover evolving goals.
                End: Conclude with a climactic encounter where the outcome hinges on the heroes' actions. Leave some story threads open for future adventures.
    """)

    def get_level_description(self, level):
        if 1 <= level <= 4:
            return (f"The characters are around level {level}. Local Heroes: Characters in this tier are still learning the range "
                    "of class features that define them, including their choice of specialization. They might face savage orcs, "
                    "ferocious wolves, giant spiders, evil cultists, bloodthirsty ghouls, and hired thugs. Even a young dragon is "
                    "a significant threat at this stage.")
        elif 5 <= level <= 10:
            return (f"The characters are around level {level}. Heroes of the Realm: Adventurers have mastered the basics of their "
                    "class features. They venture into wilds and ruins, confronting savage giants, ferocious hydras, fearless golems, "
                    "evil yuan-ti, scheming devils, and drow assassins. A young dragon that has established a lair is a challenging "
                    "but manageable foe.")
        elif 11 <= level <= 16:
            return (f"The characters are around level {level}. Masters of the Realm: Characters are paragons of courage and determination. "
                    "They explore uncharted regions and delve into long-forgotten dungeons, facing cunning rakshasas and beholders, "
                    "hungry purple worms, and even powerful adult dragons that have established significant presences.")
        elif 17 <= level <= 20:
            return (f"The characters are around level {level}. Masters of the World: Characters at this level have superheroic capabilities. "
                    "They traverse otherworldly realms and fight savage bator demons, titans, archdevils, lich archmages, and even "
                    "avatars of the gods themselves. The dragons they encounter are ancient and immensely powerful.")
        else:
            return "Invalid level. Please enter a level between 1 and 20."

    @classmethod
    def new_from_description(cls, description=None, player_level=None):
        c = cls.new()

        if description is None:
            description = "A quest."
        c.set('description', description)

        if player_level is not None:
            c.set('player_level', player_level)
            c.set('level_advice', c.get_level_description(player_level))

        # generate textual descriptions
        c.query('adventure1', synchronous=True)
        c.query('name', synchronous=True)
        c.query('big_bad', synchronous=True)
        c.query('start_description', synchronous=True)

        # and make the character, although we don't need them now...
        c.set('big_bad', Entity.new_from_description(c.big_bad, synchronous=False)._id)

        a1 = SubQuest.new_from_description(c.adventure1, synchronous=True)
        c.set('adventure1', a1._id)

        start = Location.new_from_description(
            c.start_description, 
            "The starting location of the adventure", 
            synchronous=True,
            expand=False
        )._id

        c.set('start_location', start)
        a1.set('start_location', start)

        # generate the other adventures asynchronously
        for i in range(2,4):
            c.query(f'adventure{i}', synchronous=False)        

        return c
    
if __name__ == "__main__":
    story = Quest.new_from_description(
        description="I'm interested in doing something cartoony, with fantastical mythical twists and turns, and odd consequences of the universe being in 2d.",
        player_level=3
    )