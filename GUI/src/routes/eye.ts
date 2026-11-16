import { writable } from "svelte/store";

export interface EyeEvent {
	x: number;
	y: number;
	t: number;
	source: "synthetic" | "camera";
	tracking: boolean;  
	connected: boolean;  
}
export const BRIDGE_URL = "ws://127.0.0.1:8765";
const RETRY_MS = 1000;

export const eye = writable<EyeEvent>({
	x: 0,
	y: 0,
	t: 0,
	source: "synthetic",
	tracking: false,
	connected: false
});

let socket: WebSocket | null = null;

export function connectEye(): () => void {
	let stopped = false;
	let retry: ReturnType<typeof setTimeout> | undefined;

	function open() {
		if (stopped) return;
		const ws = new WebSocket(BRIDGE_URL);
		socket = ws;

		ws.onopen = () => eye.update((e) => ({ ...e, connected: true }));

		ws.onmessage = (msg) => {
			try {
				const data = JSON.parse(msg.data);
				eye.set({
					x: data.x,
					y: data.y,
					t: data.t,
					source: data.source,
					tracking: data.tracking,
					connected: true
				});
			} catch {
				// ignore malformed messages
			}
		};

		ws.onclose = () => {
			if (socket === ws) socket = null;
			eye.update((e) => ({ ...e, connected: false }));
			if (!stopped) retry = setTimeout(open, RETRY_MS);
		};
	}

	open();
	return () => {
		stopped = true;
		clearTimeout(retry);
		socket?.close();
		socket = null;
	};
}

export function calibrate() {
	if (socket?.readyState === WebSocket.OPEN) {
		socket.send(JSON.stringify({ type: "calibrate" }));
	}
}