#!/usr/bin/env python3

"""Check the TurtleBot3 on ROS 2 through 'rosbridge' alone, as a client application reaches it, for 'ci/check-rosbridge.bash'.

The client connects to the WebSocket of 'rosbridge', subscribes to '/clock', '/joint_states', '/tf', '/tf_static',
'/scan', '/odom', and the transient local topic 'robot_description' of 'robot_state_publisher', and waits for a
message of each, with a clock that advances, the joints of both wheels, and a description of the robot.
It then fetches every mesh that the description names through '/file_server/get_file', and the GLB beside it,
named by appending '.glb', which must come back byte for byte when the container holds it, as 'docs/robot-models.md'
of the core describes.
It then advertises '/cmd_vel' and publishes a 'geometry_msgs/msg/TwistStamped' at 20 Hz until '/odom' shows that the
simulated robot moved, then publishes a zero command, so that the robot stops.
It uses the standard library of Python only, and every request id starts with a random prefix of its own.
"""

import argparse
import base64
import hashlib
import json
import os
import socket
import struct
import sys
import time
import xml.etree.ElementTree as ET

WEBSOCKET_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

WHEEL_JOINT_NAMES = ["wheel_left_joint", "wheel_right_joint"]

# Command sent to the simulated robot, a slow forward speed, and the distance that '/odom' must show.
SENT_LINEAR_X = 0.2
EXPECTED_DISTANCE = 0.05


class WebSocketClient(object):
    """Minimal WebSocket client of RFC 6455 for text messages, enough for 'rosbridge'."""

    def __init__(self, host, port, timeout):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.buffer = b""
        key = base64.b64encode(os.urandom(16)).decode()
        request = (
            "GET / HTTP/1.1\r\n"
            "Host: {0}:{1}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Sec-WebSocket-Key: {2}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        ).format(host, port, key)
        self.sock.sendall(request.encode())
        while b"\r\n\r\n" not in self.buffer:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError("rosbridge closed the connection during the handshake")
            self.buffer += chunk
        head, self.buffer = self.buffer.split(b"\r\n\r\n", 1)
        lines = head.decode("latin-1").split("\r\n")
        if " 101 " not in lines[0] + " ":
            raise ConnectionError("rosbridge refused the WebSocket upgrade: " + lines[0])
        accept = base64.b64encode(hashlib.sha1((key + WEBSOCKET_GUID).encode()).digest()).decode()
        headers = {line.split(":", 1)[0].strip().lower(): line.split(":", 1)[1].strip() for line in lines[1:] if ":" in line}
        if headers.get("sec-websocket-accept") != accept:
            raise ConnectionError("rosbridge answered the WebSocket upgrade with a wrong accept key")

    def _send_frame(self, opcode, payload):
        header = bytearray([0x80 | opcode])
        length = len(payload)
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header += struct.pack(">H", length)
        else:
            header.append(0x80 | 127)
            header += struct.pack(">Q", length)
        mask = os.urandom(4)
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        self.sock.sendall(bytes(header) + mask + masked)

    def send(self, message):
        self._send_frame(0x1, json.dumps(message).encode())

    def _parse_frame(self):
        """Return '(fin, opcode, payload)' of the first whole frame of the buffer, or None."""
        if len(self.buffer) < 2:
            return None
        first, second = self.buffer[0], self.buffer[1]
        offset = 2
        length = second & 0x7F
        if length == 126:
            if len(self.buffer) < offset + 2:
                return None
            length = struct.unpack(">H", self.buffer[offset:offset + 2])[0]
            offset += 2
        elif length == 127:
            if len(self.buffer) < offset + 8:
                return None
            length = struct.unpack(">Q", self.buffer[offset:offset + 8])[0]
            offset += 8
        mask = None
        if second & 0x80:
            if len(self.buffer) < offset + 4:
                return None
            mask = self.buffer[offset:offset + 4]
            offset += 4
        if len(self.buffer) < offset + length:
            return None
        payload = self.buffer[offset:offset + length]
        self.buffer = self.buffer[offset + length:]
        if mask:
            payload = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        return bool(first & 0x80), first & 0x0F, payload

    def receive(self, timeout):
        """Return the next JSON message, or None when none arrives within the timeout."""
        deadline = time.monotonic() + timeout
        fragments = b""
        while True:
            frame = self._parse_frame()
            if frame is None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return None
                self.sock.settimeout(remaining)
                try:
                    chunk = self.sock.recv(65536)
                except socket.timeout:
                    return None
                if not chunk:
                    raise ConnectionError("rosbridge closed the connection")
                self.buffer += chunk
                continue
            fin, opcode, payload = frame
            if opcode == 0x8:
                raise ConnectionError("rosbridge closed the connection")
            if opcode == 0x9:
                self._send_frame(0xA, payload)
                continue
            if opcode == 0xA:
                continue
            fragments += payload
            if fin:
                return json.loads(fragments.decode())

    def close(self):
        try:
            self._send_frame(0x8, struct.pack(">H", 1000))
        except OSError:
            pass
        self.sock.close()


def connect(host, port, deadline):
    """Connect to 'rosbridge', retrying until it listens or the deadline passes."""
    last_error = None
    while time.monotonic() < deadline:
        try:
            return WebSocketClient(host, port, timeout=5.0)
        except (OSError, ConnectionError) as error:
            last_error = error
            time.sleep(1.0)
    raise SystemExit("FAIL: no 'rosbridge' answered on {0}:{1}: {2}".format(host, port, last_error))


def stamp_seconds(stamp):
    return stamp.get("sec", 0) + stamp.get("nanosec", 0) * 1e-9


def find_share_dir(package):
    """Return the share folder of a package from the index of 'ament', as the file service resolves it, or None."""
    for prefix in os.environ.get("AMENT_PREFIX_PATH", "").split(os.pathsep):
        if prefix and os.path.exists(os.path.join(prefix, "share", "ament_index", "resource_index", "packages", package)):
            return os.path.join(prefix, "share", package)
    return None


def call_service(client, prefix, count, service, args, timeout):
    """Call a service through 'rosbridge' and return its response, skipping the messages of the subscriptions."""
    call_id = "{0}call-{1}".format(prefix, count)
    client.send({"op": "call_service", "id": call_id, "service": service, "args": args})
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        message = client.receive(timeout=max(0.0, deadline - time.monotonic()))
        if message and message.get("op") == "service_response" and message.get("id") == call_id:
            return message
    raise SystemExit("FAIL: '{0}' gave no answer within {1:.0f} s.".format(service, timeout))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9090)
    parser.add_argument("--timeout", type=float, default=240.0, help="Seconds to wait for the simulation and every topic.")
    arguments = parser.parse_args()

    started = time.monotonic()
    deadline = started + arguments.timeout
    prefix = "ci-" + os.urandom(6).hex() + ":"
    client = connect(arguments.host, arguments.port, deadline)
    print("Connected to 'rosbridge' on {0}:{1} after {2:.0f} s.".format(arguments.host, arguments.port, time.monotonic() - started), flush=True)

    subscriptions = {
        "/clock": "rosgraph_msgs/msg/Clock",
        "/joint_states": "sensor_msgs/msg/JointState",
        "/tf": "tf2_msgs/msg/TFMessage",
        "/tf_static": "tf2_msgs/msg/TFMessage",
        "/scan": "sensor_msgs/msg/LaserScan",
        "/odom": "nav_msgs/msg/Odometry",
        "/robot_description": "std_msgs/msg/String",
    }
    for topic, message_type in subscriptions.items():
        client.send({"op": "subscribe", "id": prefix + "subscribe" + topic, "topic": topic, "type": message_type})

    # Wait for the clock to advance, the joints of both wheels, a transform, a static transform, a scan, an odometry, and the description of the robot.
    clock_stamps = set()
    seen = {topic: 0 for topic in subscriptions}
    wheels_seen = False
    description = None
    odom_start = None
    while time.monotonic() < deadline:
        ready = len(clock_stamps) >= 2 and wheels_seen and description is not None and odom_start is not None and all(seen[topic] for topic in ("/tf", "/tf_static", "/scan"))
        if ready:
            break
        message = client.receive(timeout=1.0)
        if not message or message.get("op") != "publish":
            continue
        topic = message.get("topic")
        body = message.get("msg", {})
        if topic == "/clock":
            clock_stamps.add(stamp_seconds(body.get("clock", {})))
        elif topic == "/joint_states":
            names = body.get("name", [])
            wheels_seen = wheels_seen or all(name in names for name in WHEEL_JOINT_NAMES)
        elif topic in ("/tf", "/tf_static"):
            if body.get("transforms"):
                seen[topic] += 1
        elif topic == "/scan":
            if body.get("ranges"):
                seen[topic] += 1
        elif topic == "/odom":
            odom_start = body["pose"]["pose"]["position"]
        elif topic == "/robot_description":
            if "<robot" in body.get("data", ""):
                description = body["data"]
    else:
        missing = []
        if len(clock_stamps) < 2:
            missing.append("'/clock' advancing")
        if not wheels_seen:
            missing.append("'/joint_states' with the wheel joints")
        for topic in ("/tf", "/tf_static", "/scan"):
            if not seen[topic]:
                missing.append("'{0}' with data".format(topic))
        if odom_start is None:
            missing.append("'/odom'")
        if description is None:
            missing.append("'robot_description' with a description")
        client.close()
        raise SystemExit("FAIL: after {0:.0f} s, 'rosbridge' never delivered {1}.".format(time.monotonic() - started, ", ".join(missing)))
    print("Received '/clock' advancing to {0:.2f} s, '/joint_states' with the wheel joints, '/tf', '/tf_static', '/scan', '/odom', and 'robot_description' of {1} characters after {2:.0f} s.".format(max(clock_stamps), len(description), time.monotonic() - started), flush=True)

    # Fetch every mesh of the description and its GLB through the file service, as a client draws the robot model.
    meshes = sorted({mesh.get("filename") for mesh in ET.fromstring(description).iter("mesh") if mesh.get("filename")})
    if not meshes:
        client.close()
        raise SystemExit("FAIL: the description of the robot names no mesh.")
    count = 0
    glbs = 0
    for uri in meshes:
        count += 1
        response = call_service(client, prefix, count, "/file_server/get_file", {"name": uri}, 60.0)
        if not response.get("result") or not base64.b64decode(response.get("values", {}).get("value", "")):
            client.close()
            raise SystemExit("FAIL: the file service answered no bytes for the mesh '{0}'.".format(uri))
        package, _, path = uri[len("package://"):].partition("/") if uri.startswith("package://") else (None, None, None)
        share_dir = find_share_dir(package) if package else None
        glb_path = os.path.join(share_dir, path + ".glb") if share_dir else None
        if glb_path and os.path.exists(glb_path):
            count += 1
            response = call_service(client, prefix, count, "/file_server/get_file", {"name": uri + ".glb"}, 60.0)
            with open(glb_path, "rb") as glb_file:
                expected = glb_file.read()
            if not response.get("result") or base64.b64decode(response.get("values", {}).get("value", "")) != expected:
                client.close()
                raise SystemExit("FAIL: the file service did not answer the GLB of '{0}' byte for byte.".format(uri))
            glbs += 1
        else:
            print("Warning: the container holds no GLB of '{0}', so a client falls back to the mesh.".format(uri), flush=True)
    print("The file service served the {0} meshes of the description, and {1} GLBs byte for byte.".format(len(meshes), glbs), flush=True)

    # Publish the command at 20 Hz until '/odom' shows that the simulated robot moved.
    client.send({"op": "advertise", "id": prefix + "advertise", "topic": "/cmd_vel", "type": "geometry_msgs/msg/TwistStamped"})
    command = {
        "header": {"frame_id": "base_link"},
        "twist": {"linear": {"x": SENT_LINEAR_X, "y": 0.0, "z": 0.0}, "angular": {"x": 0.0, "y": 0.0, "z": 0.0}},
    }
    stop = {"header": {"frame_id": "base_link"}, "twist": {"linear": {"x": 0.0, "y": 0.0, "z": 0.0}, "angular": {"x": 0.0, "y": 0.0, "z": 0.0}}}
    distance = 0.0
    sent_count = 0
    drive_deadline = min(deadline, time.monotonic() + 60.0)
    next_send = time.monotonic()
    while distance < EXPECTED_DISTANCE and time.monotonic() < drive_deadline:
        if time.monotonic() >= next_send:
            client.send({"op": "publish", "id": prefix + "publish", "topic": "/cmd_vel", "msg": command})
            sent_count += 1
            next_send += 0.05
        message = client.receive(timeout=max(0.0, next_send - time.monotonic()))
        if message and message.get("op") == "publish" and message.get("topic") == "/odom":
            position = message["msg"]["pose"]["pose"]["position"]
            distance = ((position["x"] - odom_start["x"]) ** 2 + (position["y"] - odom_start["y"]) ** 2) ** 0.5

    # Stop the simulated robot, whatever the result.
    for _ in range(10):
        client.send({"op": "publish", "id": prefix + "publish", "topic": "/cmd_vel", "msg": stop})
        time.sleep(0.05)
    client.send({"op": "unadvertise", "id": prefix + "unadvertise", "topic": "/cmd_vel"})
    for topic in subscriptions:
        client.send({"op": "unsubscribe", "id": prefix + "subscribe" + topic, "topic": topic})
    client.close()
    if distance < EXPECTED_DISTANCE:
        raise SystemExit("FAIL: '/odom' showed the robot {0:.3f} m away after {1} commands on '/cmd_vel', short of {2} m.".format(distance, sent_count, EXPECTED_DISTANCE))
    print("'/odom' showed the simulated robot {0:.3f} m away after {1} commands on '/cmd_vel', then a zero command stopped it.".format(distance, sent_count), flush=True)
    print("PASS: the TurtleBot3 on ROS 2 answered over 'rosbridge' alone, with its robot model, in {0:.0f} s.".format(time.monotonic() - started), flush=True)


if __name__ == "__main__":
    sys.exit(main())
