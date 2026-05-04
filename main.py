import re
from dataclasses import dataclass
from typing import Any


@dataclass
class Node:
    type: str
    fields: dict

    def __repr__(self):
        return f"{self.type}({self.fields})"


class TMLLanguage:
    def __init__(self):
        self.name = ""
        self.tokens = {}
        self.rules = {}
        self.checks = {}


class TMLEngine:
    def __init__(self, definition_text: str):
        self.language = self.load_language(definition_text)
        self.program_text = ""
        self.pos = 0

    def load_language(self, text: str) -> TMLLanguage:
        lang = TMLLanguage()
        lines = text.splitlines()
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            if not line:
                i += 1
                continue

            if line.startswith("language "):
                lang.name = line.split()[1]
                i += 1

            elif line.startswith("token "):
                match = re.match(r"token\s+(\w+)\s*=\s*/(.+)/", line)
                if not match:
                    raise SyntaxError(f"Invalid token line: {line}")
                name, pattern = match.groups()
                lang.tokens[name] = pattern
                i += 1

            elif line.startswith("rule "):
                rule_name = line.split()[1].replace(":", "")
                i += 1
                pattern_lines = []

                while i < len(lines):
                    next_line = lines[i].strip()
                    if next_line.startswith(("rule ", "token ", "check ", "language ")):
                        break
                    if next_line:
                        pattern_lines.append(next_line)
                    i += 1

                lang.rules[rule_name] = " ".join(pattern_lines)

            elif line.startswith("check "):
                rule_name = line.split()[1].replace(":", "")
                i += 1
                check_lines = []

                while i < len(lines):
                    next_line = lines[i].strip()
                    if next_line.startswith(("rule ", "token ", "check ", "language ")):
                        break
                    if next_line:
                        check_lines.append(next_line)
                    i += 1

                lang.checks.setdefault(rule_name, []).extend(check_lines)

            else:
                i += 1

        return lang

    def parse(self, text: str) -> Node:
        self.program_text = text
        self.pos = 0

        start_rule = list(self.language.rules.keys())[0]
        result = self.parse_rule(start_rule)

        self.skip_whitespace()

        if self.pos != len(self.program_text):
            remaining = self.program_text[self.pos:self.pos + 40]
            raise SyntaxError(f"Unexpected text near: {remaining}")

        self.validate(result)
        return result

    def skip_whitespace(self):
        while self.pos < len(self.program_text) and self.program_text[self.pos].isspace():
            self.pos += 1

    def parse_rule(self, rule_name: str) -> Node:
        if rule_name not in self.language.rules:
            raise SyntaxError(f"Unknown rule: {rule_name}")

        pattern = self.language.rules[rule_name]
        alternatives = [alt.strip() for alt in pattern.split("|")]

        for alt in alternatives:
            saved_pos = self.pos

            try:
                fields = self.parse_sequence(alt)
                return Node(rule_name, fields)
            except SyntaxError:
                self.pos = saved_pos

        raise SyntaxError(f"Could not parse rule {rule_name} at position {self.pos}")

    def parse_sequence(self, pattern: str) -> dict:
        parts = self.split_pattern(pattern)
        fields = {}

        for part in parts:
            self.skip_whitespace()

            if part.startswith('"') and part.endswith('"'):
                literal = part[1:-1]
                self.match_literal(literal)

            elif "*=" in part:
                field, rule = part.split("*=")
                values = []

                while True:
                    saved_pos = self.pos

                    try:
                        values.append(self.parse_rule(rule))
                    except SyntaxError:
                        self.pos = saved_pos
                        break

                fields[field] = values

            elif "+=" in part:
                field, rule = part.split("+=")
                values = [self.parse_rule(rule)]

                while True:
                    saved_pos = self.pos

                    try:
                        values.append(self.parse_rule(rule))
                    except SyntaxError:
                        self.pos = saved_pos
                        break

                fields[field] = values

            elif "=" in part:
                field, target = part.split("=")

                if target in self.language.tokens:
                    fields[field] = self.match_token(target)
                elif target in self.language.rules:
                    fields[field] = self.parse_rule(target)
                else:
                    raise SyntaxError(f"Unknown assignment target: {target}")

            elif part in self.language.tokens:
                return {"value": self.match_token(part)}

            elif part in self.language.rules:
                return self.parse_rule(part).fields

            else:
                raise SyntaxError(f"Unknown grammar part: {part}")

        return fields

    def split_pattern(self, pattern: str) -> list[str]:
        return re.findall(r'"[^"]*"|\S+', pattern)

    def match_literal(self, literal: str):
        self.skip_whitespace()

        if self.program_text.startswith(literal, self.pos):
            self.pos += len(literal)
        else:
            raise SyntaxError(f"Expected '{literal}' at position {self.pos}")

    def match_token(self, token_name: str) -> Any:
        self.skip_whitespace()

        pattern = self.language.tokens[token_name]
        regex = re.compile(pattern)
        match = regex.match(self.program_text, self.pos)

        if not match:
            raise SyntaxError(f"Expected token {token_name} at position {self.pos}")

        raw_value = match.group(0)
        self.pos = match.end()

        if token_name == "NUMBER":
            return int(raw_value)

        if token_name == "STRING":
            return raw_value[1:-1]

        if token_name == "BOOL":
            return raw_value == "true"

        return raw_value

    def validate(self, node: Node):
        self.validate_node(node)

    def validate_node(self, node: Node):
        checks = self.language.checks.get(node.type, [])

        for check in checks:
            self.run_check(node, check)

        for value in node.fields.values():
            if isinstance(value, Node):
                self.validate_node(value)

            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, Node):
                        self.validate_node(item)

    def run_check(self, node: Node, check: str):
        if check.startswith("unique("):
            path = check[len("unique("):-1]
            list_name, field_name = path.split(".")

            items = node.fields.get(list_name, [])
            seen = set()

            for item in items:
                value = item.fields.get(field_name)

                if value in seen:
                    raise ValueError(f"Validation error: duplicate {field_name}: {value}")

                seen.add(value)

        elif check.startswith("if key =="):
            key = node.fields.get("key")
            value_node = node.fields.get("value")

            if isinstance(value_node, Node):
                value = value_node.fields.get("value")
            else:
                value = value_node

            if key == "volume":
                if not isinstance(value, int) or not (0 <= value <= 100):
                    raise ValueError("Validation error: volume must be between 0 and 100")


def main():
    with open("appconfig.tml", "r") as file:
        definition = file.read()

    with open("appconfig_program.txt", "r") as file:
        program = file.read()

    engine = TMLEngine(definition)
    model = engine.parse(program)

    print("Language:", engine.language.name)
    print("Parsed Model:")
    print(model)


if __name__ == "__main__":
    main()