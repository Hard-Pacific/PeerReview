import re
from collections import defaultdict

class Requirement:
    @staticmethod
    def check(filename: str, ban: list[str], demand: list[str]):
        with open(filename, "r", encoding="utf-8") as p:
            file = p.readlines()
        ban_dict = defaultdict(list)
        demand_dict = defaultdict(list)
        for line in range(len(file)):
            for command in ban:
                found = bool(re.search(r"\b{}\b".format(command), file[line]))
                if found:
                    ban_dict[line + 1].append(command)
            for command in demand:
                found = bool(re.search(r"\b{}\b".format(command), file[line]))
                if found == True:
                    demand_dict[command].append(line + 1)
        ban_str = Requirement.validate_ban(ban_dict)
        demand_str = Requirement.validate_demand(demand_dict,demand)
        if ban_str == '' and demand_str == '':
            return "Success"
        else:
            return f"{ban_str} \n{demand_str}"
        
    @staticmethod
    def validate_ban(ban_dict: dict) -> str: 
        '''
        Вывод строки,в которой используется command(ban_dict)
        Ничего, если ban_dict пуст
        '''
        #строка для используемых нарушений
        ban_result_str = ''
        ban_items= ban_dict.items()
        if ban_items:
            ban_result_str = f"Used : {', '.join([f'строка {line}:{commands}' for line, commands in ban_items])}"
        return ban_result_str
    
    @staticmethod
    def validate_demand(demand_dict: dict, demand: list[str])-> str:
        '''
        Вывод не использованных command(demand_dict)
        Ничего, если demand_dict пуст
        '''
        #строка для не используемых требований
        demand_result = ''
        demand_list = []
        for command in demand:
            amount = demand_dict[command]
            if len(amount) == 0:
                demand_list.append(command)
        if len(demand_list) != 0:
            demand_result = f"Not used: {', '.join(demand_list)}"
        return demand_result
