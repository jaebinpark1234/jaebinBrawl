import json

class LogicEventData:
    events = json.loads(open("events.json", 'r').read())

    def encode(byteStream):
        events = json.loads(open("events.json", 'r').read())

        byteStream.writeVInt(24) # Event Slots Amount
        for i in range(24):
            byteStream.writeVInt(i + 1)

        byteStream.writeVInt(len(events)) # Available Events
        for event in events:
            byteStream.writeVInt(0) # Event Index in Teams
            byteStream.writeVInt(event.get("Index", 1)) # Event Index
            byteStream.writeVInt(event.get("NewEventTimer", 0)) # Time until New Event
            byteStream.writeVInt(event.get("Timer", 0)) # Event Timer

            byteStream.writeVInt(event.get("TokenReward", 0)) # Token rewards after "NEW EVENT" is tapped
            byteStream.writeDataReference(15, event.get("LocationID", 0)) # LocationID

            byteStream.writeVInt(event.get("Status", 2)) # Event Status (1 = NEW EVENT, 2 = normal, 3 = Star Token)

            byteStream.writeString(event.get("TextEntry", None))
            byteStream.writeVInt(0)
            byteStream.writeVInt(0)
            byteStream.writeVInt(0)
            byteStream.writeArrayVint(event.get("Modifiers", [])) # Event Modifiers
            byteStream.writeVInt(0) # Special Events Difficulty
            byteStream.writeVInt(event.get("ChallengeType", 0))

        byteStream.writeVInt(0) # Coming Up Events
