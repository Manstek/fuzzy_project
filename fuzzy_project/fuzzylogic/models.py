# fuzzy_logic/models.py
from django.db import models

class Rule(models.Model):
    antecedent1 = models.CharField(max_length=255)
    antecedent2 = models.CharField(max_length=255)
    antecedent3 = models.CharField(max_length=255)
    consequent = models.CharField(max_length=255)

    def __str__(self):
        return f"Если {self.antecedent1}, {self.antecedent2}, {self.antecedent3} -> {self.consequent}"
