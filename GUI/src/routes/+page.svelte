<script lang="ts">
    import type { Component } from "svelte";
	import "../styles/landing.css"
	import Overlay, { type ParallaxSettings } from "./overlay/overlay.svelte";
	import { eye, startEyePolling, type EyeEvent } from "./eye";

	const modules = import.meta.glob<{default: Component}>('./components/*.svelte');
	const loaders = Object.values(modules);

	let index = $state(0);
	let current = $derived(loaders[index]());

	let settings = $state<ParallaxSettings>({ intensity: 0.5, depth: 20, smoothing: 0.1 });

	// Live eye offset streamed by the Python bridge (FaceTracking/bridge.py).
	let eyeState = $state<EyeEvent>({ x: 0, y: 0, t: 0, source: "synthetic", connected: false });
	$effect(() => {
		return eye.subscribe((v) => { eyeState = v; });
	});
	$effect(() => {
		const stop = startEyePolling();
		return stop;
	});

	// EMA smoothing (settings.smoothing) and pixel offsets from intensity and
	// depth - the same math as ParallaxMapper in the Python mapping module.
	let smoothed = $state({ x: 0, y: 0 });
	$effect(() => {
		const a = settings.smoothing;
		smoothed.x = a * eyeState.x + (1 - a) * smoothed.x;
		smoothed.y = a * eyeState.y + (1 - a) * smoothed.y;
	});

	let px = $derived(smoothed.x * settings.intensity * settings.depth * 10);
	let py = $derived(smoothed.y * settings.intensity * settings.depth * 10);

	function keyboard_swap(event: KeyboardEvent) {
		switch (event.key) {
			case "ArrowRight":
				console.log("Clicked Arrow Right");
				swap(1);
				break;
			case "ArrowLeft":
				console.log("Clicked Arrow Left");
				swap(-1);
				break;
			default:
				return;
		}
	}

	function swap(direction: 1 | -1) {
		const len = loaders.length;
		index = (index + direction + len) % len;
	}
</script>

<main class="container">
	<div class="scene" style:transform={"translate(" + px + "px, " + py + "px)"}>
		{#await current then mod}
			<mod.default />
		{:catch err}
			<p class="error"> failed to load component {err.message} </p>
		{/await}
	</div>
</main>

<Overlay {swap} bind:settings />
<svelte:window onkeydown={keyboard_swap} />
