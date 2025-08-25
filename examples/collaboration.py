import asyncio, json, websockets

async def main():
    uri = "ws://localhost:8765/mcp"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"clientInfo":{"name":"example","version":"0.1"}}}))
        await ws.recv()

        await ws.send(json.dumps({"jsonrpc":"2.0","id":2,"method":"tools/call","params":{
            "name":"orchestrate_collaboration",
            "arguments":{"task":"Draft a product brief","agents":["Claude","GPT-4"]}
        }}))
        print("orchestrate:", await ws.recv())

asyncio.run(main())
