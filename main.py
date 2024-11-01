#!/usr/bin/env python
# coding: utf-8

# In[111]:


import pandas as pd
from collections import defaultdict
import math
from typing import List, Dict


# In[112]:


# Global variables
# currency_codes: Dict[str, CurrencyNode] = defaultdict(CurrencyNode)
currencies : List[str] = list()


# In[113]:


df = pd.read_csv("./dataset/current_price.csv")
# df = pd.read_csv("./dataset/mock.csv")
df.shape


# In[114]:


df.head(3)


# In[115]:


# Pre-process data
column_names = list(df.columns)
pairs = df[column_names[0]].unique()
currency_set = set()
for pair in pairs:
    # create nodes
    numerator, denominator = str(pair).split("/")
    currency_set.add(numerator)
    currency_set.add(denominator)
currencies = list(currency_set)


# In[116]:


# Swap USD (or any chosen base currency) to the first element
currencies.sort()
index = currencies.index('USD')
tmp = currencies[0]
currencies[0] = 'USD'
currencies[index] = tmp

currencies


# In[117]:


# Mapping currency to index
index_mappings : Dict[str, int] = { key: i for i, key in enumerate(currencies) }


# In[118]:


fx_rates = [[0.0 for j in range(len(currencies))]
            for i in range(len(currencies))]

for i in range(len(currencies)):
    fx_rates[i][i] = 1.0

# Analysis on the current price
for index, row in df.iterrows():
    pair = row[column_names[0]]
    numerator, denominator = str(pair).split("/")
    numIndex, denomIndex = index_mappings[numerator], index_mappings[denominator]
    fx_rates[numIndex][denomIndex] = row["Current price"]


for i in range(len(currencies) - 1):
    for j in range(i + 1, len(currencies)):
        if fx_rates[i][j] == 0 and fx_rates[j][i] != 0:
            fx_rates[i][j] = 1 / fx_rates[j][i] 
        elif fx_rates[i][j] != 0 and fx_rates[j][i] == 0:
            fx_rates[j][i] = 1 / fx_rates[i][j] 


# for r in fx_rates:
#     print(r)
# print(fx_rates)


# Step 1: Convert FX rates to negative log weights
# 
# We utilize the logarithm multiplication property to represent the edges.

# In[119]:


vertices = len(fx_rates)
edges = []

for i in range(vertices):
    for j in range(vertices):
        if i != j and fx_rates[i][j] != 0:
            weight = -math.log(fx_rates[i][j])
            edges.append((i, j, weight))


# Helper function to trace the negative cycle path

# In[120]:


def trace_negative_cycle(predecessor, start, vertices):
    cycle = []
    x = start

    # Move x back for a few steps in the cycle to ensure we reach the start of the cycle
    for _ in range(vertices):
        x = predecessor[x]

    # Trace the cycle
    cycle_start = x
    while True:
        cycle.append(x)
        x = predecessor[x]
        if x == cycle_start and len(cycle) > 1:
            cycle.append(x)  # Closing the cycle for clarity
            break

    cycle = list(reversed(cycle))
    cycle_str = [currencies[s] for s in cycle]
    # cycles.add('->'.join(str(x) for x in cycle))
    return '->'.join(cycle_str)


# Step 2: Bellman-Ford function to detect negative cycles

# In[121]:


def bellman_ford(vertices, edges, start):
    distance = [float("inf")] * vertices
    predecessor = [-1] * vertices
    distance[start] = 0

    # Relax edges (V-1) times
    for _ in range(vertices - 1):
        for u, v, weight in edges:
            if distance[u] != float("inf") and weight != 0 and distance[u] + weight < distance[v]:
                distance[v] = distance[u] + weight
                predecessor[v] = u

    # Check for negative cycle and trace it
    has_arbitrage = False
    for u, v, weight in edges:
        if distance[u] != float("inf") and weight != 0 and distance[u] + weight < distance[v]:
            # Trace the negative cycle detected
            has_arbitrage = True
            return has_arbitrage, trace_negative_cycle(predecessor, v, vertices)

    return has_arbitrage, ""


# In[122]:


# Running the Bellman-Ford algorithm from start vertex (0/USD)
has_arbitrage, cycle = bellman_ford(vertices, edges, 0)
if has_arbitrage:
    print("Arbitrage opportunity detected in cycle.")
    amount = 100
    orders = cycle.split("->")
    for i in range(1, len(orders)):
        prev, cur = orders[i-1], orders[i]
        amount *= fx_rates[index_mappings[prev]][index_mappings[cur]]
    print("Cycle:", cycle)
    print("\tAmount:", amount)
    print("Profit: ", round((amount - 100) * 100, 2), "pips")
else:
    print("No arbitrage opportunity detected")

