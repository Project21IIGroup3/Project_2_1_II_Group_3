<script lang="ts">
    import type { Component } from "svelte";
	import "../styles/landing.css"
	import Overlay, { type ParallaxSettings } from "./overlay/overlay.svelte";
	import { connectEye } from "./eye";

	const modules = import.meta.glob<{default: Component}>('./components/*.svelte');
	const loaders = Object.values(modules);

	let index = $state(0);
	let current = $derived(loaders[index]());

	let settings = $state<ParallaxSettings>({ intensity: 0.5, depth: 60, smoothing: 0.5 });

	//start the eye bridge on mount, disconnect when the component is removed
	$effect(() => {
		const stop = connectEye();
		return stop;
	});

	function keyboard_swap(event: KeyboardEvent) {
		switch (event.key) {
			case "ArrowRight":
				swap(1);
				break;
			case "ArrowLeft":
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
	<div class="scene">
		{#await current then mod}
			<mod.default {settings} />
		{:catch err}
			<p class="error"> failed to load component {err.message} </p>
		{/await}
	</div>
</main>

<Overlay {swap} bind:settings />
<svelte:window onkeydown={keyboard_swap} />
