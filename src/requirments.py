import re


class Requirement:
    def __init__(self):
        self.info=None
    
    def validate(self, file_path: str, ban_list: list[str], demand_list: list[str])-> bool:
        with open(f"{file_path}", "r", encoding = "utf-8") as p:
            file = p.readlines()
        ban_list = Requirement.validate_ban(file, ban_list)
        demand_list = Requirement.validate_demand(file, demand_list)
        if len(ban_list) == 0 and len(demand_list) == 0:
            self.info = ["Код отвечает требованиям преподавателя"]
            return True
        else:
            self.info =["Используется:"] + ban_list + ["Не используется: "] + demand_list
            return True
        
    @staticmethod
    def validate_ban(file: list[str], ban: list[str])-> list:
        """
        Получает на вход список банов
        Возвращает список используемых банов
        """
 
        ban_list=[]
        for line in range(len(file)):
            for command in ban:
                found = bool(re.search(r"\b{}\b".format(command), file[line]))
                if found:
                    ban_list.append(f"строка {line+1}: {command}")
        return ban_list
    
    @staticmethod
    def validate_demand(file: list[str], demand: list[str])-> list:   
        """
        Получает на вход список требований
        Возвращает список не используемых требований
        """                  
        for line in range(len(file)):
            for command in demand:
                found = bool(re.search(r"\b{}\b".format(command), file[line]))
                if found:
                    demand.remove(command) 
        return demand                      