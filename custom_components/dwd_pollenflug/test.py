#!/usr/bin/env python3

import asyncio

import aiohttp

# from DWD import Pollenflug
import DWD.Pollenflug


async def main():
    pollen = DWD.Pollenflug.Pollenflug()
    async with aiohttp.ClientSession() as session:
        await pollen.fetch(session)

    print(pollen.last_update)
    print(pollen.next_update)
    print(pollen.legend)
    print(pollen.regions_list)
    # print(pollen.regions_with_data)
    # print(pollen.pollen_list)


asyncio.run(main())
