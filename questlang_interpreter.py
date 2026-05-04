import re
import sys
from dataclasses import dataclass, field


@dataclass
class Enemy:
    name: str
    hp: int
    attack: int


@dataclass
class Room:
    room_id: str
    name: str
    text: str = ""
    enemies: list[Enemy] = field(default_factory=list)
    exits: list[tuple[str, str]] = field(default_factory=list)


class QuestLangInterpreter:
    def __init__(self):
        self.title = ""
        self.player_hp = 100
        self.player_attack = 10
        self.start_room = ""
        self.rooms = {}

    def load(self, filename):
        with open(filename, "r") as file:
            lines = [
                line.strip()
                for line in file.readlines()
                if line.strip() and not line.strip().startswith("#")
            ]

        i = 0
        while i < len(lines):
            line = lines[i]

            if line.startswith("game "):
                self.title = self.get_string(line)

            elif line.startswith("player "):
                match = re.match(r"player hp (\d+) attack (\d+)", line)
                if not match:
                    raise ValueError("Invalid player line.")
                self.player_hp = int(match.group(1))
                self.player_attack = int(match.group(2))

            elif line.startswith("start "):
                self.start_room = line.split()[1]

            elif line.startswith("room "):
                match = re.match(r'room (\w+) "(.+)" \{', line)
                if not match:
                    raise ValueError(f"Invalid room line: {line}")

                room_id, room_name = match.groups()
                room = Room(room_id, room_name)

                i += 1
                while i < len(lines) and lines[i] != "}":
                    inside = lines[i]

                    if inside.startswith("text "):
                        room.text = self.get_string(inside)

                    elif inside.startswith("enemy "):
                        match = re.match(r'enemy "(.+)" hp (\d+) attack (\d+)', inside)
                        if not match:
                            raise ValueError(f"Invalid enemy line: {inside}")
                        name, hp, attack = match.groups()
                        room.enemies.append(Enemy(name, int(hp), int(attack)))

                    elif inside.startswith("exit "):
                        match = re.match(r'exit "(.+)" -> (\w+)', inside)
                        if not match:
                            raise ValueError(f"Invalid exit line: {inside}")
                        label, target = match.groups()
                        room.exits.append((label, target))

                    i += 1

                self.rooms[room_id] = room

            i += 1

        self.validate()

    def validate(self):
        if not self.start_room:
            raise ValueError("Missing start room.")

        if self.start_room not in self.rooms:
            raise ValueError(f"Start room does not exist: {self.start_room}")

        for room in self.rooms.values():
            for _, target in room.exits:
                if target not in self.rooms:
                    raise ValueError(f"Room '{room.room_id}' links to missing room '{target}'.")

    def run(self):
        if self.title.lower() == "fizzbuzz quest":
            self.run_fizzbuzz()
            return

        current = self.start_room

        print(f"\n=== {self.title} ===")
        print("Type the number of your choice.\n")

        while True:
            room = self.rooms[current]

            print(f"\n== {room.name} ==")
            print(room.text)

            for enemy in room.enemies:
                self.fight(enemy)
                if self.player_hp <= 0:
                    print("\nYou died. Game over.")
                    return

            if not room.exits:
                print("\nThe story ends here.")
                return

            print("\nChoices:")
            for index, (label, _) in enumerate(room.exits, start=1):
                print(f"{index}. {label}")

            choice = input("> ")

            if not choice.isdigit():
                print("Enter a number.")
                continue

            choice = int(choice)

            if choice < 1 or choice > len(room.exits):
                print("Invalid choice.")
                continue

            current = room.exits[choice - 1][1]

    def fight(self, enemy):
        print(f"\nA {enemy.name} appears!")

        while enemy.hp > 0 and self.player_hp > 0:
            print(f"\nYour HP: {self.player_hp}")
            print(f"{enemy.name} HP: {enemy.hp}")
            print("1. Attack")

            choice = input("> ")

            if choice == "1":
                enemy.hp -= self.player_attack
                print(f"You hit {enemy.name} for {self.player_attack} damage.")

                if enemy.hp > 0:
                    self.player_hp -= enemy.attack
                    print(f"{enemy.name} hits you for {enemy.attack} damage.")
            else:
                print("Invalid action.")

        if self.player_hp > 0:
            print(f"You defeated {enemy.name}!")

    def run_fizzbuzz(self):
        print("\n=== FizzBuzz Quest ===")
        for i in range(1, 21):
            if i % 15 == 0:
                print("FizzBuzz")
            elif i % 3 == 0:
                print("Fizz")
            elif i % 5 == 0:
                print("Buzz")
            else:
                print(i)

    def get_string(self, line):
        match = re.search(r'"(.+)"', line)
        if not match:
            raise ValueError(f"Expected quoted string in line: {line}")
        return match.group(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python questlang_interpreter.py filename.quest")
        return

    interpreter = QuestLangInterpreter()
    interpreter.load(sys.argv[1])
    interpreter.run()


if __name__ == "__main__":
    main()