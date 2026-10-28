import { writable } from "svelte/store";

export interface EyeEvent {
	x: number; //normalised eye offset, -1..1 (reference-relative)
	y: number;
	t: number; //server timestamp, ms
	source: "synthetic" | "camera";
	connected: boolean;
}

export const BRIDGE_URL = "http://127.0.0.1:8765/eye";

export const eye = writable<EyeEvent>({
	x: 0,
	y: 0,
	t: 0,
	source: "synthetic",
	connected: false
});

export function startEyePolling(intervalMs = 0): () => void {
	let stopped = false;

	async function poll() {
		if (stopped) return;
		try {
			const res = await fetch(BRIDGE_URL, { cache: "no-store" });
			if (!res.ok) throw new Error(res.statusText);
			const data = await res.json();
			eye.set({
				x: data.x,
				y: data.y,
				t: data.t,
				source: data.source,
				connected: true
			});
		} catch {
			eye.update((e) => ({ ...e, connected: false }));
		} finally {
			if (!stopped) setTimeout(poll, intervalMs);
		}
	}

	poll();
	return () => {
		stopped = true;
	};
}
