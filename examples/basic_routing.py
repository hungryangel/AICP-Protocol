import asyncio, json, websockets

async def main():
    uri = "ws://localhost:8765/mcp"
    async with websockets.connect(uri, max_size=1<<20) as ws:
        await ws.send(json.dumps({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"clientInfo":{"name":"example","version":"0.1"}}}))
        print("initialize:", await ws.recv())

        await ws.send(json.dumps({"jsonrpc":"2.0","id":2,"method":"tools/call","params":{
            "name":"route_to_agent",
            "arguments":{"message":"Please analyze this dataset.", "target_capabilities":["analysis"]}
        }}))
        print("route_to_agent:", await ws.recv())

asyncio.run(main())
