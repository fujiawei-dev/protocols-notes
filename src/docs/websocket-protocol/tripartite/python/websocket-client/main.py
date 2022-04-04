"""
Date: 2022.03.12 14:19
Description: https://github.com/websocket-client/websocket-client
LastEditors: Rustle Karl
LastEditTime: 2022.03.12 14:19
"""
import websocket

"""
- [yes] auto reply pong-ping frame
- [yes] close if server not reply pong frame
"""


def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def on_open(ws):
    print("### opened ###")


if __name__ == "__main__":
    websocket.enableTrace(True)

    ws = websocket.WebSocketApp(
        # "ws://localhost:8089",
        "ws://localhost:8787/immigration/ws/server",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    ws.run_forever(
        # ping_interval=83,
        # ping_timeout=81,
        # ping_payload="keep alive",
    )
