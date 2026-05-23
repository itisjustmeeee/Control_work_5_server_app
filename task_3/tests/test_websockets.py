from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_connect_to_room():
    with client.websocket_connect(
        '/ws/rooms/python?username=alice'
    ) as websocket:
        data = websocket.receive_json()

        assert data["type"] == "join"
        assert data["username"] == "alice"

def test_send_new_message():
    with client.websocket_connect(
        '/ws/rooms/python?username=alice'
    ) as websocket:
        websocket.receive_json()

        websocket.send_json({
            "type": "message",
            "text": "Hiiiiiiiiii guyessssssssssssss"
        })

        data = websocket.receive_json()

        assert data["type"] == "message"
        assert data["text"] == "Hiiiiiiiiii guyessssssssssssss"
        assert data["username"] == "alice"

def test_two_clients_with_same_message():
    with client.websocket_connect(
        '/ws/rooms/python?username=alice'
    ) as ws1:
        
        with client.websocket_connect(
            '/ws/rooms/python?username=khe'
        ) as ws2:
            
            ws1.receive_json()
            ws1.receive_json()

            ws2.receive_json()

            ws1.send_json({
                "type": "message",
                "text": "hiiiiiiiiii khehehehe"
            })

            data1 = ws1.receive_json()
            data2 = ws2.receive_json()

            assert data1["text"] == "hiiiiiiiiii khehehehe"
            assert data2["text"] == "hiiiiiiiiii khehehehe"

def test_different_rooms_dont_receieve_messages():
    with client.websocket_connect(
        '/ws/rooms/python?username=alice'
    ) as ws_alice:
        
        with client.websocket_connect(
            '/ws/rooms/fastapi?username=khe'
        ) as ws_khe:
            
            ws_alice.receive_json()
            ws_khe.receive_json()

            ws_alice.send_json({
                "type": "message",
                "text": "text lost"
            })

            data = ws_alice.receive_json()

            assert data["text"] == "text lost"

def test_roo_long_message():
    with client.websocket_connect(
        '/ws/rooms/python?username=alice'
    ) as wbs:
        
        wbs.receive_json()

        wbs.send_json({
            "type": "message",
            "text": "uwu" * 102
        })

        data = wbs.receive_json()

        assert data["type"] == "error"
        assert data["detail"] == "Message is too long (you are too long :D)"

def test_user_removal_after_disconnect():
    with client.websocket_connect(
        '/ws/rooms/python?username=alice'
    ) as wbs:
        
        wbs.receive_json()

        response = client.get('/rooms/python/users')

        assert response.json()["users"] == ["alice"]

    response = client.get('/rooms/python/users')

    assert response.json()["users"] == []
