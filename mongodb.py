from common import *
import json
from pymongo import MongoClient
client = MongoClient()

client.lost_mines.story.drop()
client.lost_mines.NPCs.drop()

adventure_name = "alec_first"

#model = "gpt-3.5-turbo"
model = "gpt-4-1106-preview"

storyline = [
    {
        'name': "sandbox",
        'description': "At any stage, the player/character veers away from any plot points. It is okay for them to create their own adventure this way. Play along. Be fun, engaging, but adhere to the rules and lore of the world. Try your best to get them back to the main story line if they begin to stray too far.",
        'next_steps': {
            'create character': "A good first step",
            'determine marching order': "Optional",
            'driving the wagon': "When the journey really begins. Make sure they know some of the plot before beginning."
        }
    },
    {
        'name': "start",
        'description': "Your journey begins on the High Road from Neverwinter, moving southeast. Gundren Rockseeker, a dwarf, hired you in Neverwinter to transport provisions to Phandalin. Gundren, with a secretive demeanor, speaks of a significant discovery he and his brothers made. He promises ten gold pieces for safe delivery to Barthen's Provisions in Phandalin. Accompanied by Sildar Haliwinter, he leaves ahead on horseback. Danger lurks on this path, known for bandits and outlaws.",
        'next_steps': {
            'create character': "A good first step",
            'determine marching order': "Optional",
            'driving the wagon': "When the journey really begins. Make sure they know some of the plot before beginning.",
            'sandbox': "At any stage, the player/character may veer away from the plot points. It is okay for them to create their own adventure this way. Play along. Be fun, engaging, but adhere to the rules and lore of the world. Try your best to get them back to the main story line if they begin to stray too far."
        }
    },
    {
        'name': "create character",
        'description': "The player creates their character. They pick a race first and then a class. If they don't know what their options are, you are to provide brief, succinct descriptions of each race, then class. They may describe their appearance, background, and how they came to know Gundren Rockseeker. Encourage creativity in their backstories, like childhood friendships or past rescues by Gundren.",
        'next_steps': {
            'determine marching order': "Once they're done creating their character, they must determine marching order.",
            'sandbox': "At any stage, the player/character veers away from any plot points. It is okay for them to create their own adventure this way. Play along. Be fun, engaging, but adhere to the rules and lore of the world. Try your best to get them back to the main story line if they begin to stray too far."
        }
    },
    {
        'name': "determine marching order",
        'description': "The party discusses and decides their traveling formation. Who will drive the wagon, scout ahead, or guard the rear? This arrangement is crucial for upcoming encounters and navigating the terrain.",
        'next_steps': {
            'driving the wagon': "Whenever the party is ready.",
            'sandbox': "At any stage, the player/character veers away from any plot points. It is okay for them to create their own adventure this way. Play along. Be fun, engaging, but adhere to the rules and lore of the world. Try your best to get them back to the main story line if they begin to stray too far."
        }
    },
    {
        'name': "driving the wagon",
        'description': "The wagon, pulled by two oxen, contains various mining supplies and food worth 100 gp. The journey is uneventful initially, but the path is known for its dangers. The players must remain alert as they navigate the road.",
        'next_steps': {
            'finding horses': "At some point along the road, probably after some time has passed, the party encounters two dead horses blocking the path.",
            'sandbox': "At any stage, the player/character veers away from any plot points. It is okay for them to create their own adventure this way. Play along. Be fun, engaging, but adhere to the rules and lore of the world. Try your best to get them back to the main story line if they begin to stray too far."
        }
    },
    {
        'name': "finding horses",
        'description': "As the party nears Phandalin, they encounter two dead horses blocking the path, riddled with black-feathered arrows. Unbeknownst to the party, four goblins are hiding in the nearby foliage, waiting for them to approach the horses. When they choose to investigate, before anything else happens, they are ambushed by the four goblins immediately.",
        'next_steps': {
            'combat with goblins': "Approaching and investigating the horses triggers the ambush from four goblins hiding in the thicket.",
            'sandbox': "At any stage, the player/character veers away from any plot points. It is okay for them to create their own adventure this way. Play along. Be fun, engaging, but adhere to the rules and lore of the world. Try your best to get them back to the main story line if they begin to stray too far."
        },
    },
    {
        'name': "combat with goblins",
        'description': "The party must quickly react to the goblin attack. Four goblins, skilled in stealth and ambush tactics, launch their assault. The players must use their wits and combat skills to overcome this threat.",
        'next_steps': {
            'follow goblin trail': "If the party decides to track the goblins, they find a trail leading to the Cragmaw hideout.",
            'sandbox': "At any stage, the player/character veers away from any plot points. It is okay for them to create their own adventure this way. Play along. Be fun, engaging, but adhere to the rules and lore of the world. Try your best to get them back to the main story line if they begin to stray too far."

        }
    },
    {
        'name': "follow goblin trail",
        'description': "The path is treacherous, with potential traps and signs of frequent goblin activity. Stealth and caution are advised.",
        'next_steps': {
            'cave_1': "They eventually alight on the hideout itself.",
            'sandbox': "At any stage, the player/character veers away from any plot points. It is okay for them to create their own adventure this way. Play along. Be fun, engaging, but adhere to the rules and lore of the world. Try your best to get them back to the main story line if they begin to stray too far."
        }
    },
    {
        'name': "cave_1",
        'description': """
            The trail leads to a well-hidden cave, the Cragmaw hideout. 
            "Following the goblins' trail, you come across a large cave in a hillside five miles from the scene of the ambush. A shallow stream flows out of the cave mouth, which is screened by dense briar thickets. A narrow dry path leads into the cave on the right-hand side of the stream."

            The goblins in the dense (completely hidden and impenetrable) thicket on the other side of the river are supposed to be keeping watch on this area, but they are not paying attention. (Goblins can be lazy that way.) 
            However, if the characters make a lot of noise here-for example, loudly arguing about what to do next, setting up a camp, cutting down brush, and so on-the goblins in area 2 notice and attack them through the thicket, which provides the goblins with three-quarters cover (see the rule book for rules on cover).
        """,
        'next_steps': {
            'approach cave': "If the party decides to enter the cave.",
            'trigger goblin attack': "If the party decides to make a lot of noise outside the cave.",
            'sandbox': "At any stage, the player/character veers away from any plot points. It is okay for them to create their own adventure this way. Play along. Be fun, engaging, but adhere to the rules and lore of the world. Try your best to get them back to the main story line if they begin to stray too far."
        }
    },
    {
        'name': "approach cave",
        'description': """
            When the characters cross to the east side of the stream, they can see around the screening thickets to area 2. This is a goblin guard post, though the goblins here are bored and inattentive.
            On the east side of the stream flowing from the cave mouth, a small area in the briar thickets has been hollowed out to form
            a lookout post or blind. Wooden planks flatten out the briars and provide room for guards to lie hidden and watch the area-including a pair of goblins lurking there right now!
            Two goblins are stationed here. If the goblins notice intruders in area 1, they open fire with their bows, shooting through the thickets and probably catching the characters by surprise. If the goblins don't notice the adventurers in area 1, they spot them when they splash across the stream, and neither side is surprised.
            Characters moving carefully or scouting ahead might be able to surprise the goblin lookouts. Have each character who moves ahead make a Dexterity (Stealth) check contested by the goblins' passive Wisdom (Perception)
            Thickets. The thickets around the clearing are difficult terrain, but they aren't dangerous-just annoying. They provide half cover to creatures attacking through them. (See "Difficult Terrain" and "Cover" in the rulebook for more information.)
        """,
        'next_steps': {
            'trigger goblin attack': "If the party alerts the goblins",
            'cave_3': "If the party sneaks by successfully, they enter the cave.",
            'sandbox': "At any stage, the player/character veers away from any plot points. It is okay for them to create their own adventure this way. Play along. Be fun, engaging, but adhere to the rules and lore of the world. Try your best to get them back to the main story line if they begin to stray too far."
        }
    },
    {
        "name": "trigger goblin attack",
        "description": """
        """
    },
    {
        "name": "cave_3",
        "description": """
            The Cragmaws keep a kennel of foul-tempered wolves that they are training for battle.
            Just inside the cave mouth, a few uneven stone steps lead up to a small, dank chamber on the east side of the passage. The cave narrows to a steep fissure at the far end, and is filled with the stench of animals. Savage snarls and the sounds of rattling chains greet your ears where two wolves are chained up just inside the opening. Each wolf's chain leads to an iron rod driven into the base of a stalagmite.
            Three wolves are confined here. They can't reach targets standing on the steps, but all three attack any creature except a goblin that moves into the room (see the "Developments" section). 
            
            Goblins in nearby caves ignore the sounds of fighting wolves, since they constantly snap and snarl at each other.
            
            A character who tries-to calm the animals can attempt a DC 15 Wisdom (Animal Handling) check. 
            On a success, the wolves allow the character to move throughout the room. If the wolves are given food, the DC drops to 10.
            
            Fissure. A narrow opening in the east wall leads to a natural chimney that climbs 30 feet to area 8. 
            At the base of the fissure is rubbish that's been discarded through the opening above. 
            A character attempting to ascend or descend the chimney shaft must make a DC 10 Strength (Athletics) check. 
            If the check succeeds, the character moves at half speed up or down the shaft, as desired. 
            On a check result of 6-9, the character neither gains nor loses ground; 
            on a result of 5 or less, the character falls and takes 1d6 bludgeoning damage per 10 feet fallen, landing prone at the base of the shaft.

            DEVELOPMENTS
            If the wolves are goaded by enemies beyond their reach, they are driven into a frenzy that allows them to yank the iron rod securing their chains out of the floor. Each round that any character remains in sight, the wolves attempt a single DC 15 Strength check. 
            On the first success, they loosen the rod and the DC drops to 10. On a second success, they yank the rod loose, bending it so that their chains are freed.
            A goblin or bugbear can use its action to release one wolf from its chain.
        """,
        "next_steps": {
            "cave_4": "If the party decides to continue into the cave.",
            "cave_1": "If the party decides to leave the cave.",
            'sandbox': "At any stage, the player/character veers away from any plot points. It is okay for them to create their own adventure this way. Play along. Be fun, engaging, but adhere to the rules and lore of the world. Try your best to get them back to the main story line if they begin to stray too far."
        }
    },
    {
        "name": "cave_4",
        "description": """
            From this point on, characters without darkvision will need light to see their surroundings.
            The main passage from the cave mouth climbs steeply upward, the stream plunging and splashing down its west side. 
            In the shadows, a side passage leads west across the other side of the stream.

            Characters using light or darkvision to look farther up the passage spot the bridge at area 5. Add:
            In the shadows of the ceiling to the north, you can just make out the dim shape of a rickety bridge of wood and rope crossing over the passage ahead of you. Another passage intersects this one, twenty feet above the floor.
            Any character who can see the bridge in area 5 might also notice the goblin guarding the bridge. 
            Doing so requires a Wisdom (Perception) check contested by the goblin's Dexterity (Stealth) check result.
            
            The goblin notices the characters if they carry any light or don't use stealth as they approach the bridge. 
            The goblin does not attack. Instead, it attempts to sneak away to the east to inform its companions in area 7 to release a flood. 
            The goblin moves undetected if its Dexterity (Stealth) check exceeds the passive Wisdom (Perception) score of any character who might notice its movements.
            
            Western Passage. 
            This passage is choked with rubble and has steep escarpments. 
            Treat the area as difficult terrain (see "Difficult Terrain" in the rulebook).
            The ledge between the two escarpments is fragile. 
            Any weight in excess of 100 pounds loosens the whole mass and sends it tumbling down to the east. 
            Any creature on the ledge when it falls must make a DC 10 Dexterity saving throw, taking 2d6 bludgeoning damage on a failure, or half as much damage on a success. 
            The creature also falls prone on a failed save (see "Being Prone" in the rulebook).
        """,
        "next_steps": {
            "cave_5": "If the party continues towards the bridge.",
            "cave_6": "If the party successfully makes it to the other side of the ledge.",
            "cave_3": "If the party decides to leave the cave.",
            'sandbox': "At any stage, the player/character veers away from any plot points. It is okay for them to create their own adventure this way. Play along. Be fun, engaging, but adhere to the rules and lore of the world. Try your best to get them back to the main story line if they begin to stray too far."
        }
    },
    {
        "name": "cave_5_lower",
        "description": """
        Where a high tunnel passes through the larger tunnel cavern below, the goblins have set up a bridge guard post.
        The stream passage continues up beyond another set of uneven steps ahead, bending eastward as it goes. 
        A waterfall I sounds out from a larger cavern somewhere ahead of you.
        
        If the characters didn't spot the bridge while navigating area 4, they spot it now. Add:
        A rickety bridge spans the passage, connecting two tunnels that are 20 feet above the stream.
        
        One goblin stands watch on the bridge. 
        It is hiding, and characters can spot it by succeeding on a Wisdom (Perception) check contested by the goblin's Dexterity (Stealth) check. 
        This guard is lazy and inattentive. If no characters are using light sources, each character can attempt a Dexterity (Stealth) check against the goblin's passive Wisdom (Perception) score to creep by without being noticed.
        If the goblin spots the adventurers, it signals the goblins in area 7 to release a flood, then throws javelins down at the characters.

        Bridge. This bridge spans the passage 20 feet above the stream. It's possible to climb up the cavern walls from the lower passage to the bridge. The 20-foot-high walls are rough but slick with spray, requiring a successful DC 15 Strength (Athletics) check to climb.
        The bridge has an Armor Class (AC) of 5 and 10 hit points. If the bridge is reduced to 0 hit points, it collapses. 
        Creatures on the collapsing bridge must succeed on a DC 10 Dexterity saving throw or fall, taking 2d6 bludgeoning damage and landing prone (see "Being Prone" in the rulebook).
        Those who succeed hold onto the bridge and must climb it to safety.

        The players are on the ground.
        """,
        "next_steps": {
            "flood": "if the goblin signals to start the flood.",
            "cave_7": "if the party continues under and beyond the bridge.",
            "cave_7": "if the party is able to get to the top of the bridge, and heads west",
            "cave_6": "if the party is able to get to the top of the bridge, and heads east",
             'sandbox': "At any stage, the player/character veers away from any plot points. It is okay for them to create their own adventure this way. Play along. Be fun, engaging, but adhere to the rules and lore of the world. Try your best to get them back to the main story line if they begin to stray too far."
        }
    },
    {
        "name": "cave_7",
        "description": """
            If the goblins have drained either pool to flood the passage, adjust the following boxed text accordingly.

            This cavern is half filled with two large pools of water. A narrow waterfall high in the eastern wall feeds the pool, which drains out the western end of the chamber to form the stream that flows out of the cave mouth below. Low fieldstone walls serve as dams holding the water in. A wide exit stands to the south, while two smaller passages lead west. The sound of the waterfall echoes through the cavern, making it difficult
            to hear.

            Three goblins guard this cave. If the goblin in area 5 spotted the characters and warned the goblins here, they are ready for trouble. The noise of the waterfall means that the creatures in area 8 can't hear any fighting that takes place here, and vice versa. Therefore, as soon as a fight breaks out here, one goblin flees to area 8 to warn Klarg.
            Rock Dams. The goblins built simple dams to control the flow of water through the heart of the complex. If the goblin sentry in area 5 has called for the goblins here to release a flood, one or both of the pools are mostly empty and the stream is flowing unimpeded.
        """,
        "next_steps": {
            "cave_8": "if the party continues south.",
            "cave_5_upper": "if the party continues east.",
             'sandbox': "At any stage, the player/character veers away from any plot points. It is okay for them to create their own adventure this way. Play along. Be fun, engaging, but adhere to the rules and lore of the world. Try your best to get them back to the main story line if they begin to stray too far."
        }
    },
    {
        "name": "cave_5_upper",
        "description": """
        Where a high tunnel passes through the larger tunnel cavern below, the goblins have set up a bridge guard post.
        The stream passage continues up beyond another set of uneven steps ahead, bending eastward as it goes. 
        A waterfall I sounds out from a larger cavern somewhere ahead of you.
        
        If the characters didn't spot the bridge while navigating area 4, they spot it now. Add:
        A rickety bridge spans the passage, connecting two tunnels that are 20 feet above the stream.
        
        One goblin stands watch on the bridge. 
        It is hiding, and characters can spot it by succeeding on a Wisdom (Perception) check contested by the goblin's Dexterity (Stealth) check. 
        This guard is lazy and inattentive. If no characters are using light sources, each character can attempt a Dexterity (Stealth) check against the goblin's passive Wisdom (Perception) score to creep by without being noticed.
        If the goblin spots the adventurers, it signals the goblins in area 7 to release a flood, then throws javelins down at the characters.

        The players are approaching the bridge from the west tunnel, and can now cross the bridge.
        """,
        "next_steps": {
            "flood": "if the goblin signals to start the flood.",
            "cave_6": "after crossing the bridge, there's a long passageway to the east, which leads to the goblin's den",
             'sandbox': "At any stage, the player/character veers away from any plot points. It is okay for them to create their own adventure this way. Play along. Be fun, engaging, but adhere to the rules and lore of the world. Try your best to get them back to the main story line if they begin to stray too far."
        }
    },
    {
        "name": "cave_6",
        "description": """
            The Cragmaw raiders stationed in the hideout use this area as a common room and barracks.
            This large cave is divided in half by a ten-foot-high
            escarpment. A steep natural staircase leads from the lower portion to the upper ledge. The air is hazy with the smoke of a cooking fire, and pungent from the smell of poorly cured hides and unwashed goblins.
            Six goblins inhabit this den, and one of them is a leader with 12 hit points. The five ordinary goblins tend the cooking fire in the lower (northern) part of the cave near the entrance passage, while the leader rests in the upper (southern) part of the cave.
            Sildar Hallwinter, a human warrior, is held prisoner in this chamber. He is securely bound on the southern ledge of the cavern. The goblins have been beating and tormenting him, so he is weak and at 1 hit point.
            The goblin leader, Yeemik, is second-in-command
            of the whole hideout. If he sees that the characters are getting the upper hand, he grabs Sildar and drags him over to the edge of the upper level. "Truce, or this human dies!" he shouts.
            Yeemik wants to oust Klarg and become the new boss. If the adventurers agree to parley, Y~e.mik tries to(co~vince them to kill Klarg in area 8, prormsing to release Sildar when they bring back the bugbear's head. Sildar groggily warns the characters that they shouldn't trust the goblin, and he's right. If the characters take the deal, Yeemik tries to force them to pay a rich ransom for Sildar even after
            they complete their part of the bargain.
            If the characters refuse to parley, Yeemik shoves Sildar over the edge and continues with the fight. Sildar takes
            Id6 bludgeoning damage from the fall, which is enough to drop him to 0 hit points. Quick-acting characters can try to stabilize him before he dies (see "Damage, Healing, and Dying" in the rulebook).
            
            ROLE PLAYING SILDAR
            Sildar Kinter is a kindhearted human male of nearly fifty years who holds a place of honor in the famous
            griffon cavalry of the great city of Water deep. He is an agent of the Lords' Alliance, a group of allied political powers concerned with mutual security and prosperity. Members of the order ensure the safety of cities and other settlements by proactively eliminating threats by any means, while bringing honor and glory to their leaders
            and homelafds.
            Sildar me\ Gundren Rockseeker in Neverwinter and agreed to accpmpany him back to Phandalin. Sildar wants to investigate the fate of larno Albrek, a human wizard and fellow membe~of the Lords' Alliance who disappeared shortly after arriving in Phandalin. Sildar hopes to learn what happened to larno, assist Gundren in reopening the old mine, and help restore Phandalin to a civilized center of wealth and prosperity.
            
            Sildar provides the characters with four pieces of useful information:
            To The three Rockseeker brothers (Gundren, Tharden, and Nundro) recently located an entrance to the long-lost Wave Echo Cave, site of the mines of the Phandelver's Pact. (Share the information in the first two paragraphs of the "Background" section to the players at this time.) Klarg, the bugbear who leads this goblin band, had orders to waylay Gundren. Sildar heard from the goblins that the Black Spider sent word that the dwarf was to
            be brought to him. Sildar doesn't know who or what the
            Black Spider is.
            o Gundren had a map showing the secret location of Wave
            Echo Cave, but the goblins took it when they captured him. Sildar believes that Klarg sent the map and the dwarf to the chief of the Cragmaws at a place called Cragmaw Castle. Sildar doesn't know where that might be, but he suggests someone in Phandalin might know. (It doesn't occur to Sildar immediately, but a captured goblin might also be persuaded to divulge the castle's location. See the "What the Goblins Know" sidebar on page 8.)
            Sildar's contact in Phandalin is a human wizard named Iarno Albrek. The wizard traveled to the town two months ago to establish order there. After the Lords' Alliance received no word from Iarno, Sildar decided to investigate.
            Sildar tells the characters that he intends to continue on to Phandalin, since it's the nearest settlement. He offers to pay the party 50 gp to provide escort. Although he has no money on him, Sildar can secure a loan to pay the characters within a day after arriving in Phandalin. First, he hopes they'll put a stop to the goblin raids by clearing out the caves.
            
            DEVELOPMENTS
            If he is rescued and healed, Sildar Hallwinter remains with the party but is anxious to reach Phandalin as quickly as possible. He doesn't have any weapons or armor, but
            he can take a shortsword from a defeated goblin or use a weapon loaned to him by a character.
            If Sildar joins the party, see the "NPC Party Members" sidebar for tips on how to run him.

            TREASURE
            Yeemik carries a pouch containing three gold teeth (1 gp each) and 15 sp. Sildar's gear, along with Gundren Rockseeker, was taken to Cragmaw Castle.
            
            NPC PARTY MEMBERS
            An NPC might join the party, if only for a short time. Here are some tips to help you run an NPC party member:
            + Let the characters make the important decisions. They are the protagonists of the adventure. If the characters ask an N PC party member for advice or direction, remember that NPCs make mistakes too.
            + An NPC won't deliberately put himself or herself in harm's
            way unless there's a good reason to do so.
            An NPC won't treat all party members the same way, which can create some fun friction. As an N PC gets to know the characters, think about which characters the NPC likes most and which ones the NPC likes least, and let those likes and dislikes affect how the NPC interacts with the party members. In a combat encounter, keep the NPC's actions simple and straightforward. Also, look for things that the N PC can do besides fighting. For example, an NPC might stabilize a dying character, guard a prisoner, or help barricade a door.
            + If an NPC contributes greatly to the party's success in a
            battle, the NPC should receive an equal share ofthe XP
            earned for the encounter. (The characters receive less XP as a consequence.)
            + NPCs have their own lives and goals. Consequently, an NPC should remain with the party only as long as doing so makes sense for those goals.
            """,
        "next_steps": {
            "cave_1": "if the party decides to leave the cave.",
             'sandbox': "At any stage, the player/character veers away from any plot points. It is okay for them to create their own adventure this way. Play along. Be fun, engaging, but adhere to the rules and lore of the world. Try your best to get them back to the main story line if they begin to stray too far."
        }
    },
    {
        "name": "flood",
        "description": """
        The large pools in area 7 have collapsible walls that can be yanked out of place to release a surge of water down the main passage of the lair. 
        In the round after the goblins in area 7 are signaled by the lookout in area 5, they start knocking away the supports. 
        In the following round on the goblins' initiative count, a water surge pours from area 7 down to area 1.

        The passage is suddenly filled with a mighty roar, as a huge 1surge of rushing water pours down from above!
        The flood threatens all creatures in the tunnel. (Creatures on the bridge at area 5 are out of danger, as are any characters successfully climbing the cavern walls.) 
        Any creature within 10 feet of the disused passage at area 4 or the steps leading up to area 3 can attempt a DC 10 Dexterity saving throw to avoid being swept away. 
        A creature that fails to get out of the way can attempt a DC 15 Strength saving throw to hold on. 
        On a failed save, the character is knocked prone and washed down to area 1, taking 1d6 bludgeoning damage along the way.
        The goblins in area 7 can release a second flood by opening the second pool, but they don't do this unless the goblin on the bridge tells them to. 
        The goblin on the bridge waits to see if the first flood got rid of all the intruders before calling for the second to be released.
        """
    }
]

client.lost_mines.story.count_documents({})

client.lost_mines.NPCs.insert_many([
    {
    "name": "Elmar Barthen",
    "relevance": "Owns a trading post; owes money to the party if you are using the 'Meet Me in  Phandalin' adventure hook",
    "personality traits": "",
    "ideals": "",
    "bonds": "",
    "flaws": "",
    },
    {
    "name": "Toblin Stonehill",
    "relevance": "innkeeper",   
    }
])

client.lost_mines.characters.insert_many([
   {
  "characterName": "",
  "class": "Fighter",
  "level": 1,
  "race": "Human",
  "background": "Noble",
  "alignment": "Lawful Neutral",
  "playerName": "",
  "experiencePoints": 0,
  "attributes": {
    "strength": {"score": 16, "modifier": "+3"},
    "dexterity": {"score": 9, "modifier": "-1"},
    "constitution": {"score": 15, "modifier": "+2"},
    "intelligence": {"score": 11, "modifier": "+0"},
    "wisdom": {"score": 13, "modifier": "+1"},
    "charisma": {"score": 14, "modifier": "+2"}
  },
  "proficiencyBonus": "+2",
  "savingThrows": {
    "strength": {"value": "+5", "proficient": True},
    "dexterity": {"value": "-1", "proficient": False},
    "constitution": {"value": "+4", "proficient": True},
    "intelligence": {"value": "+0", "proficient": False},
    "wisdom": {"value": "+1", "proficient": False},
    "charisma": {"value": "+2", "proficient": False}
  },
  "skills": {
    "acrobatics": {"value": "-1", "proficient": False},
    "animalHandling": {"value": "+1", "proficient": False},
    "arcana": {"value": "+0", "proficient": False},
    "athletics": {"value": "+5", "proficient": True},
    "deception": {"value": "+2", "proficient": False},
    "history": {"value": "+2", "proficient": True},
    "insight": {"value": "+1", "proficient": False},
    "intimidation": {"value": "+2", "proficient": True},
    "investigation": {"value": "+0", "proficient": False},
    "medicine": {"value": "+1", "proficient": False},
    "nature": {"value": "+0", "proficient": False},
    "perception": {"value": "+3", "proficient": True},
    "performance": {"value": "+2", "proficient": False},
    "persuasion": {"value": "+4", "proficient": True},
    "religion": {"value": "+0", "proficient": False},
    "sleightOfHand": {"value": "-1", "proficient": False},
    "stealth": {"value": "-1", "proficient": False},
    "survival": {"value": "+1", "proficient": False}
  },
  "hitPoints": {
    "maximum": 12,
    "current": 12,
    "temporary": 0
  },
  "armorClass": 17,
  "initiative": "-1",
  "speed": "30 feet",
  "equipment": {
    "armor": "Chain mail",
    "weapons": {
      "greataxe": {
        "attackBonus": "+5",
        "damageType": "1d12 + 3 slashing"
      },
      "javelin": {
        "attackBonus": "+5",
        "damageType": "1d6 + 3 piercing",
        "notes": "Can throw a javelin 30 feet or up to 120 feet with disadvantage on the attack roll."
      }
    },
    "other": [
      "Backpack",
      "Blanket",
      "Tinderbox",
      "2 days of rations",
      "Waterskin",
      "Set of fine clothes",
      "Signet ring",
      "Scroll of pedigree"
    ]
  },
  "currency": {
    "gold": 25,
    "silver": 0,
    "copper": 0,
    "electrum": 0,
    "platinum": 0
  },
  "proficienciesLanguages": {
    "proficiencies": "All armor, shields, simple weapons, martial weapons, playing cards",
    "languages": ["Common", "Draconic", "Dwarvish"]
  },
  "backgroundInfo": {
    "humanRaceDescription": "Youngest of common races, innovators, achievers, pioneers, adaptable and ambitious, various cultures and physical characteristics.",
    "fighterClassDescription": "Diverse class, unparalleled mastery with weapons and armor, knowledge of combat skills, well acquainted with death.",
    "nobleBackground": "Family of wealth, power, privilege, affected by Mount Hotenow eruption, goal to civilize Phandalin, lawful neutral alignment, belief in law and order.",
    "personalGoal": "Civilize Phandalin. Meant for more than being a ruler of nothing at all. Rebuilding Corlinn Hill impractical due to the volcano. Phandalin, sacked by orcs five centuries ago, is now being rebuilt and needs a civilizing influence to bring law and order.",
    "alignmentDescription": "Lawful Neutral. Essential to establish law and order, even if it requires an iron fist. Nobility bound by honor and tradition to protect people from threats to stability. An organized society prevents evil and chaos."
  },
  "featuresAndTraits": {
    "secondWind": "Regain hit points equal to 1d10 + fighter level, usable once per short or long rest.",
    "fightingStyle": "Defense, +1 bonus to AC while wearing armor",
    "positionOfPrivilege": "Noble birth, welcome in high society, can secure an audience with a local noble"
  },
   "personality_characteristics": {
    "personalityTraits": "Flattery, dislike for getting dirty, preference for suitable accommodations",
    "ideals": "Protect common people, not bully them",
    "bonds": "Greataxe family heirloom, most precious possession",
    "flaws": "Hard time resisting allure of wealth, especially gold"
  },
  "levelUpInfo": {
    "2ndLevel": {
      "experiencePoints": 300,
      "actionSurge": "Take one additional action on your turn, usable once per short or long rest."
    },
    "3rdLevel": {
      "experiencePoints": 900,
      "improvedCritical": "Weapon attacks score a critical hit on a roll of 19 or 20."
    },
    "4thLevel": {
      "experiencePoints": 2700,
      "abilityScoreImprovement": {
        "strengthIncrease": "Strength increases to 18, resulting in +4 modifier, increased attack bonus, damage for Strength-based attacks, and Athletics."
      }
    },
    "5thLevel": {
      "experiencePoints": 6500,
      "extraAttack": "Make two attacks instead of one when taking the Attack action.",
      "proficiencyBonusIncrease": "Increases to +3, affecting attack bonus, saving throws, skills, and passive Wisdom (Perception)."
    }
  }
}

])

#for parts in storyline:
#    client.lost_mines.story.insert_one(parts)
# DOES SAME AS LINE OF CODE BELOW. KEPT THIS IN FOR STUDYING PURPOSES

client.lost_mines.story.insert_many(storyline)
