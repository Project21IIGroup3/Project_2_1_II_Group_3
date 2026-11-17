import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { calibrate, connectEye, eye, type EyeEvent } from "./eye";

/** Minimal stand-in for the browser WebSocket, driven manually by the tests. */
class FakeWebSocket {
	static instances: FakeWebSocket[] = [];
	static OPEN = 1;

	readyState = 0; //CONNECTING
	sent: string[] = [];
	url: string;
	onopen: (() => void) | null = null;
	onmessage: ((msg: { data: string }) => void) | null = null;
	onclose: (() => void) | null = null;

	constructor(url: string) {
		this.url = url;
		FakeWebSocket.instances.push(this);
	}

	send(data: string) {
		this.sent.push(data);
	}

	close() {
		//the real close handshake is async; tests fire onclose themselves
	}
}

const INITIAL: EyeEvent = {
	x: 0,
	y: 0,
	t: 0,
	source: "synthetic",
	tracking: false,
	connected: false
};

function storeValue(): EyeEvent {
	let value: EyeEvent | undefined;
	const unsubscribe = eye.subscribe((v) => (value = v));
	unsubscribe();
	return value!;
}

function message(payload: unknown): { data: string } {
	return { data: JSON.stringify(payload) };
}

describe("eye.ts websocket client", () => {
	let stops: Array<() => void> = [];

	beforeEach(() => {
		FakeWebSocket.instances = [];
		eye.set(INITIAL);
		vi.stubGlobal("WebSocket", FakeWebSocket);
	});

	afterEach(() => {
		for (const stop of stops) stop();
		stops = [];
		vi.unstubAllGlobals();
		vi.useRealTimers();
	});

	function connect(): FakeWebSocket {
		stops.push(connectEye());
		expect(FakeWebSocket.instances).toHaveLength(1);
		return FakeWebSocket.instances[0]!;
	}

	it("connects to the bridge url and marks the store connected on open", () => {
		const ws = connect();
		expect(ws.url).toBe("ws://127.0.0.1:8765");
		expect(storeValue().connected).toBe(false);
		ws.onopen!();
		expect(storeValue().connected).toBe(true);
	});

	it("updates the store with the fields from a bridge message", () => {
		const ws = connect();
		ws.onopen!();
		ws.onmessage!(message({ x: 0.25, y: -0.5, t: 1234, source: "camera", tracking: true }));
		const value = storeValue();
		expect(value).toMatchObject({
			x: 0.25,
			y: -0.5,
			t: 1234,
			source: "camera",
			tracking: true,
			connected: true
		});
	});

	it("ignores malformed messages", () => {
		const ws = connect();
		ws.onopen!();
		ws.onmessage!(message({ x: 0.1, y: 0.2, t: 1, source: "synthetic", tracking: false }));
		const before = storeValue();
		ws.onmessage!({ data: "not json {" });
		expect(storeValue()).toEqual(before);
	});

	it("reconnects one second after the socket closes", () => {
		const ws = connect();
		ws.onopen!();
		expect(storeValue().connected).toBe(true);

		vi.useFakeTimers();
		ws.onclose!();
		expect(storeValue().connected).toBe(false);
		expect(FakeWebSocket.instances).toHaveLength(1);

		vi.advanceTimersByTime(999);
		expect(FakeWebSocket.instances).toHaveLength(1);
		vi.advanceTimersByTime(1);
		expect(FakeWebSocket.instances).toHaveLength(2);
	});

	it("stop() closes the socket and prevents reconnection", () => {
		const ws = connect();
		ws.onopen!();

		vi.useFakeTimers();
		const stop = stops[0]!;
		stop(); //stop is idempotent, and stops already holds it for cleanup
		ws.onclose!();

		vi.advanceTimersByTime(5000);
		expect(FakeWebSocket.instances).toHaveLength(1); //no retry happened
		expect(storeValue().connected).toBe(false);
	});

	it("calibrate() sends a calibrate message only while the socket is open", () => {
		const ws = connect();
		calibrate(); //still CONNECTING: nothing is sent
		expect(ws.sent).toEqual([]);

		ws.readyState = FakeWebSocket.OPEN;
		calibrate();
		expect(ws.sent).toEqual([JSON.stringify({ type: "calibrate" })]);

		ws.readyState = 0; //closed again
		calibrate();
		expect(ws.sent).toHaveLength(1);
	});
});
