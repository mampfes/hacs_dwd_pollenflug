#!/usr/bin/env python3

# from DWD import Pollenflug
import DWD.Pollenflug

pollen = DWD.Pollenflug.Pollenflug()
pollen.fetch()

print(pollen.last_update)
print(pollen.next_update)
print(pollen.legend)
print(pollen.regions_list)
# print(pollen.regions_with_data)
# print(pollen.pollen_list)
