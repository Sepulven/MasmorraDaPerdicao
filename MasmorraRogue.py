## Aluno: Arthur Sepulven de Aguiar
## Nº: 64726

from searchPlus import *
from typing import ClassVar, Dict, FrozenSet, Iterable, List, Optional, Set, Tuple

# NOTE: Internal structure type aliases.
Position = Tuple[int, int]          # (x, y)
Monster = Tuple[Position, int]      # ((x, y), hp)

# predefinição de uma masmorra inicial simples:
line1: str = "= = = = = = =\n"
line2: str = "= Y . . . . =\n"
line3: str = "= . . . = . =\n"
line4: str = "= . . 1 = . =\n"
line5: str = "= = = . = . =\n"
line6: str = "= @ . . . . =\n"
line7: str = "= = = = = = =\n"
grid: str = line1 + line2 + line3 + line4 + line5 + line6 + line7


class DungeonState:
    """Minimal state: holds only what changes with the actions.
    - hero: (x, y) position of the hero
    - life: hero's remaining life points
    - monsters: frozenset of ((x, y), hp) for the monsters still alive
    """

    def __init__(self, hero: Position, life: int, monsters: Iterable[Monster]) -> None:
        self.hero: Position = hero
        self.life: int = life
        self.monsters: FrozenSet[Monster] = frozenset(monsters)

    def __eq__(self, other: object) -> bool:
        """Definir em que circunstância os dois estados são considerados iguais.
        Necessário para os algoritmos de procura em grafo.
        """
        return (isinstance(other, DungeonState)
                and self.hero == other.hero
                and self.life == other.life
                and self.monsters == other.monsters)

    def __hash__(self) -> int:
        """Necessário para os algoritmos de procura em grafo."""
        return hash((self.hero, self.life, self.monsters))

class MasmorraRogue(Problem):

    # NOTE: defined order of the actions and their (dx, dy) offset
    directions: ClassVar[Dict[str, Position]] = {'B': (0, 1), 'D': (1, 0), 'C': (0, -1), 'E': (-1, 0)}
    order: ClassVar[List[str]] = ['B', 'D', 'C', 'E']

    def __init__(self, mundo: str = grid, vida_inicial: int = 10) -> None:
        rows: List[List[str]] = [r.split() for r in mundo.strip('\n').split('\n')]
        self.N: int = len(rows)        # number of rows
        self.M: int = len(rows[0])     # number of columns
        self.walls: Set[Position] = set()
        self.amulet: Optional[Position] = None
        hero: Optional[Position] = None
        monsters: Set[Monster] = set()

        # NOTE: Build the map and the logic representation
        for y, row in enumerate(rows):
            for x, c in enumerate(row):
                if c == '=':
                    self.walls.add((x, y))
                elif c == 'Y':
                    self.amulet = (x, y)
                elif c == '@':
                    hero = (x, y)
                elif c.isdigit():
                    monsters.add(((x, y), int(c)))
        assert hero is not None # NOTE: Always valid input 
        initial: DungeonState = DungeonState(hero, vida_inicial, monsters)
        super().__init__(initial)

    def actions(self, state: DungeonState) -> List[str]:
        """Return the actions that can be executed in the given
        state. The result would typically be a list, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        if state.life < 1:
            return []
        x, y = state.hero
        valid: List[str] = []
        for a in self.order:
            dx, dy = self.directions[a]
            if (x + dx, y + dy) not in self.walls:
                valid.append(a)
        return valid

    def result(self, state: DungeonState, action: str) -> DungeonState:
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        dx, dy = self.directions[action]
        target: Position = (state.hero[0] + dx, state.hero[1] + dy)
        monsters: Dict[Position, int] = dict(state.monsters)
        hero: Position = state.hero
        if target in monsters:
            # NOTE: During attack the hero stays in place and the monster loses 1 HP
            monsters[target] -= 1
            if monsters[target] == 0:
                del monsters[target]
        else:
            hero = target
        return DungeonState(hero, state.life - 1, monsters.items())

    def goal_test(self, state: DungeonState) -> bool:
        """Return True if the state is a goal. The default method compares the
        state to self.goal or checks for state in self.goal if it is a
        list, as specified in the constructor. Override this method if
        checking against a single self.goal is not enough."""
        return state.hero == self.amulet

    def display(self, state: DungeonState) -> str:
        monsters: Dict[Position, int] = dict(state.monsters)
        out: str = ''
        for y in range(self.N):
            row: List[str] = []
            for x in range(self.M):
                p: Position = (x, y)
                if p == state.hero:
                    row.append('@')
                elif p in self.walls:
                    row.append('=')
                elif p in monsters:
                    row.append(str(monsters[p]))
                elif p == self.amulet:
                    row.append('Y')
                else:
                    row.append('.')
            out += ' '.join(row) + '\n'
        return out

    def executa(self, state: DungeonState, actions_list: List[str],
                verbose: bool = False) -> Tuple[DungeonState, int, bool]:
        """Executa uma sequência de ações a partir do estado, devolvendo o triplo formado pelo estado
        final, o custo acumulado e o booleano que indica se o objectivo foi ou não atingido. Se o
        objectivo for atingido antes da sequência ser toda executada, devolve-se o estado e o custo
        corrente. Há o modo verboso e o não verboso, este último selecionado por defeito."""
        cost: int = 0
        obj: bool = False
        for a in actions_list:
            seg = self.result(state,a)
            cost = self.path_cost(cost,state,a,seg)
            state = seg
            obj = self.goal_test(state)
            if verbose:
                print('Ação:', a)
                print(self.display(state),end='')
                print('Custo Total:',cost)
                print('Atingido o objetivo?', obj)
                print()
            if obj:
                break
        return (state, cost, obj)
