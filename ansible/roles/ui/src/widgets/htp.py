import random
import string

from rich.align import Align
from rich.console import Group
from rich.rule import Rule
from rich.text import Text

from textual.widgets import Static
from textual.reactive import reactive


class HackThePlanet(Static):

    code = reactive("")
    CHARSET = string.ascii_uppercase + string.digits

    def on_mount(self):
        self.set_interval(0.30, self.mutate_code)
        self.code = self.generate_code()

    def generate_code(self):
        return "".join(
            random.choice(self.CHARSET)
            for _ in range(10)
        )

    def mutate_code(self):
        chars = list(self.code)

        #
        # mutate a few chars at a time
        #

        for pos in random.sample(range(10), random.randint(1, 3)):
            chars[pos] = random.choice(self.CHARSET)

        #
        # rare major mutation
        #

        if random.random() < 0.08:
            for pos in random.sample(range(10), random.randint(4, 8)):
                chars[pos] = random.choice(self.CHARSET)
        self.code = "".join(chars)

    def render(self):
        return Group(
            Rule("H4CK1N6 7H3 P14N37", align="center"),
            Text(""),
            Align.center(
                Text(self.code, style="bold")
            ),
        )