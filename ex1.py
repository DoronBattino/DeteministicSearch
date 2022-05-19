import search
import itertools


class MedicalProblem(search.Problem):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        police_teams = initial["police"]
        medical_teams = initial["medics"]
        state_map = initial["map"]
        police_jobs = self.sick_locations(state_map)
        medical_jobs = self.need_vaccine(state_map)
        time = 0
        time_map = self.new_time_map(state_map)
        initial_list = [police_teams, police_jobs, medical_teams, medical_jobs, time, state_map, time_map]
        initial = tuple(initial_list)
        search.Problem.__init__(self, initial)

    #Sets timer to 'S' and 'Q' on a time map according to ex1 orders
    def new_time_map(self, map):
        time_map = ()
        for row in map:
            time_row = []
            for cell in row:
                if cell == 'S':
                    time_row.append(3)
                elif cell == 'Q':
                    time_row.append(2)
                else:
                    time_row.append(0)
            time_map = time_map + (tuple(time_row),)
        return tuple(time_map)

    #Marks who needs vaccine before it becomes 'S' next turn
    def need_vaccine(self, map):
        current_map = map
        row_index = -1
        col_index = -1
        need_vaccine = ()
        for row in current_map:
            row_index += 1
            for cell in row:
                col_index += 1
                if cell == 'H':
                    if self.is_legal_cell(current_map, row_index + 1, col_index):
                        if map[row_index + 1][col_index] == 'S':
                            need_vaccine = need_vaccine + ((row_index, col_index),)
                            continue
                    if self.is_legal_cell(current_map, row_index - 1, col_index):
                        if map[row_index - 1][col_index] == 'S':
                            need_vaccine = need_vaccine + ((row_index, col_index),)
                            continue
                    if self.is_legal_cell(current_map, row_index, col_index + 1):
                        if map[row_index][col_index + 1] == 'S':
                            need_vaccine = need_vaccine + ((row_index, col_index),)
                            continue
                    if self.is_legal_cell(current_map, row_index, col_index - 1):
                        if map[row_index][col_index - 1] == 'S':
                            need_vaccine = need_vaccine + ((row_index, col_index),)
                            continue
            col_index = -1
        return need_vaccine

    def is_legal_cell(self, current_map, row_index, col_index):
        if row_index < 0 or row_index >= len(current_map) or col_index < 0 or col_index >= len(current_map[0]):
            return False
        return True

    #Marks places with 'S' for police to quarntine
    def sick_locations(self, map):
        current_map = map
        row_index = -1
        col_index = -1
        sick_locations = ()
        for row in current_map:
            row_index += 1
            for cell in row:
                col_index += 1
                if cell == 'S':
                    sick_locations = sick_locations + ((row_index, col_index),)
            col_index = -1
        return sick_locations

    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        polic_teams = state[0]
        police_jobs = state[1]
        medical_teams = state[2]
        medical_jobs = state[3]
        '''All possible police actions'''
        police_actions = []
        for i in range(1, polic_teams + 1):
            police_actions = police_actions + list(itertools.combinations(police_jobs, i))
        police_actions = [ac for ac in police_actions if type(ac) == tuple]

        police_actions1 = []
        for job in police_actions:
            if polic_teams == 0:
                break
            if len(job) <= polic_teams:
                temp_action = ()
                for j in job:
                    temp_action = temp_action + tuple((("quarantine",) + (j,),))
                police_actions1 = police_actions1 + list((temp_action,))
        '''All possible medical actions'''
        medical_actions = []
        for i in range(1, medical_teams + 1):
            medical_actions = medical_actions + list(itertools.combinations(medical_jobs, i))
        medical_actions = [ac for ac in medical_actions if type(ac) == tuple]
        medical_actions1 = []
        for job in medical_actions:
            if medical_teams == 0:
                break
            if len(job) <= medical_teams:
                temp_action = ()
                for j in job:
                    temp_action = temp_action + tuple((("vaccinate",) + (j,),))
                medical_actions1 = medical_actions1 + list((temp_action,))

        if not police_actions1 and not medical_actions1:
            return (),
        if not police_actions1:
            medical_actions1 = medical_actions1 + [(), ]
            return tuple(medical_actions1)
        if not medical_actions1:
            police_actions1 = police_actions1 + [(), ]
            return tuple(police_actions1)

        actions = list(itertools.product(police_actions1, medical_actions1))
        actions = actions + police_actions1
        actions = actions + medical_actions1
        actions = actions + [(), ]

        actions1 = ()
        for ac in actions:
            actions2 = ()
            for ac1 in ac:
                actions2 = actions2 + ac1
            actions1 = actions1 + (actions2,)
        return actions1

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        edit_state = list(state)
        edit_state_map = edit_state[5]
        edit_time_map = edit_state[6]
        if not(state[0] <= 0 and state[2] <= 0):
            if action:
                if type(action[0]) == str:
                    action = (action,)
                for ac in action:
                    to_do = ac[0]
                    x = ac[1][0]
                    y = ac[1][1]
                    temp_state_map, temp_time_map = (), ()
                    row_index, col_index = -1, -1
                    for (row_state, row_time) in zip(edit_state_map, edit_time_map):
                        row_index += 1
                        row_states, row_times = [], []
                        for (state_cell, time_cell) in zip(row_state, row_time):
                            col_index += 1
                            if x == row_index and y == col_index:
                                if to_do == 'vaccinate':
                                    row_states.append('I')
                                    row_times.append(time_cell)
                                elif to_do == 'quarantine':
                                    row_states.append('Q')
                                    row_times.append(3)
                            else:
                                row_states.append(state_cell)
                                row_times.append(time_cell)
                        temp_state_map = temp_state_map + (tuple(row_states),)
                        temp_time_map = temp_time_map + (tuple(row_times),)
                        col_index = -1
                    edit_state_map = temp_state_map
                    edit_time_map = temp_time_map
                new_state_map = edit_state_map
                new_time_map = edit_time_map
                edit_state[5] = new_state_map
                edit_state[6] = new_time_map
        new_state = tuple(edit_state)
        new_state = self.sick_expand(new_state)
        new_state = self.update_map(new_state)
        new_state = self.update_jobs(new_state)
        return new_state

    def update_jobs(self, state):
        update_jobs = list(state)
        police_jobs, medical_jobs = (), ()
        if state[0] > 0:
            police_jobs = self.sick_locations(update_jobs[5])
        if state[2] > 0:
            medical_jobs = self.need_vaccine(update_jobs[5])
        update_jobs[1] = police_jobs
        update_jobs[3] = medical_jobs
        return tuple(update_jobs)

    def sick_expand(self, state):
        update = list(state)
        state_map = state[5]
        time_map = state[6]
        updated_sick, updated_time = (), ()
        row_index, col_index = -1, -1
        for (state_row, time_row) in zip(state_map, time_map):
            row_index += 1
            updated_row_state, updated_row_time = [], []
            for (state_cell, time_cell) in zip(state_row, time_row):
                col_index += 1
                if state_cell == 'H':
                    if self.is_legal_cell(state_map, row_index+1, col_index):
                        if state_map[row_index+1][col_index] == 'S':
                            updated_row_state.append('S')
                            updated_row_time.append(4)
                            continue
                    if self.is_legal_cell(state_map, row_index-1, col_index):
                        if state_map[row_index-1][col_index] == 'S':
                            updated_row_state.append('S')
                            updated_row_time.append(4)
                            continue
                    if self.is_legal_cell(state_map, row_index, col_index+1):
                        if state_map[row_index][col_index+1] == 'S':
                            updated_row_state.append('S')
                            updated_row_time.append(4)
                            continue
                    if self.is_legal_cell(state_map, row_index, col_index-1):
                        if state_map[row_index][col_index-1] == 'S':
                            updated_row_state.append('S')
                            updated_row_time.append(4)
                            continue
                    updated_row_state.append(state_cell)
                    updated_row_time.append(time_cell)
                else:
                    updated_row_state.append(state_cell)
                    updated_row_time.append(time_cell)
            col_index = -1
            updated_sick = updated_sick + (tuple(updated_row_state),)
            updated_time = updated_time + (tuple(updated_row_time),)
        update[5] = updated_sick
        update[6] = updated_time
        return tuple(update)

    def update_map(self, state):
        update = list(state)
        update[4] += 1  #Update time
        updated_time_map, updated_state_map = (), ()
        row_index, col_index = -1, -1
        for (state_row, time_row) in zip(update[5], update[6]):
            row_index += 1
            updated_time_row, updated_state_row = [], []
            for state_cell, time_cell in zip(state_row, time_row):
                col_index += 1
                if time_cell == 4:
                    updated_time_row.append(3)
                    updated_state_row.append(state_cell)
                elif time_cell == 3:
                    updated_time_row.append(2)
                    updated_state_row.append(state_cell)
                elif time_cell == 2:
                    updated_time_row.append(1)
                    updated_state_row.append(state_cell)
                elif time_cell == 1:
                    if state_cell == 'I':
                        updated_time_row.append(0)
                        updated_state_row.append('I')
                    else:
                        updated_time_row.append(0)
                        updated_state_row.append('H')
                elif time_cell == 0:
                    updated_time_row.append(time_cell)
                    updated_state_row.append(state_cell)
            updated_time_map = updated_time_map + (tuple(updated_time_row),)
            updated_state_map = updated_state_map + (tuple(updated_state_row),)
            col_index = -1
        update[5] = updated_state_map
        update[6] = updated_time_map
        return tuple(update)

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        for row in state[5]:
            for cell in row:
                if cell == 'S':
                    return False
        return True

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        immunity = 0
        infection_potential = 0
        i, j = -1, -1
        for i1 in node.state[5]:
            i += 1
            for i2 in i1:
                j += 1
                if i2 == 'I' or i2 == 'Q':
                    immunity += 1
                elif i2 == 'S':
                    infection_potential += self.infectious_level(node.state[5], i, j)
            j = -1
        return len(node.state[3]) + infection_potential - immunity

    def infectious_level(self, map, i, j):
        infectious_level = 0
        if self.is_legal_cell(map, i + 1, j) and map[i + 1][j] == 'H':
            infectious_level += 1
        if self.is_legal_cell(map, i - 1, j) and map[i - 1][j] == 'H':
            infectious_level += 1
        if self.is_legal_cell(map, i, j + 1) and map[i][j + 1] == 'H':
            infectious_level += 1
        if self.is_legal_cell(map, i, j - 1) and map[i][j - 1] == 'H':
            infectious_level += 1
        return infectious_level
    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""


def create_medical_problem(game):
    return MedicalProblem(game)

