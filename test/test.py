import asyncio

async def coroutine1():
    await asyncio.sleep(2)
    return {"id": 1, "content": "result 1"}

async def coroutine2():
    await asyncio.sleep(1)
    return {"id": 2, "content": "result 2"}

async def main():
    tasks = [coroutine1(), coroutine2()]
    completed_count = 0
    results = []

    for coro in asyncio.as_completed(tasks):
        result = await coro
        results.append(result)
        completed_count += 1
        print(f"Coroutine {result['id']} completed ({completed_count}/{len(tasks)}).")

    print("All coroutines completed.")
    print("Results:", sorted(results, key=lambda x: x['id']))

asyncio.run(main())








