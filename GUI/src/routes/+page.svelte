<script lang="ts">
    import type { Component } from "svelte";
	import "../styles/landing.css"	
	import Overlay, { type ParallaxSettings } from "./overlay/overlay.svelte";
	const modules = import.meta.glob<{default: Component}>('./components/*.svelte');
	const loaders = Object.values(modules);

	let index = $state(0);
	let current = $derived(loaders[index]());

	let settings = $state<ParallaxSettings>({ intensity: 0.5, depth: 20, smoothing: 0.1 });

	function keyboard_swap(event: KeyboardEvent) {

		switch (event.key) {
			case "ArrowRight":
				console.log("Clicked Arrow Right");
				swap(1);
				break;
			case "ArrowLeft":
				console.log("Clicked Arrow Left");
				swap(-1);
				// index = (index - 1 + len) % len;
				break;
			default:
				return; 
		}
		
	}  

	function swap(direction: 1 | -1) {
		const len = loaders.length;
		index = (index + direction) % len;
	}

</script>

<main class="container">
		
	{#await current then mod}
		<mod.default />
	{:catch err}
		<p class="error"> failed to load component {err.message} </p>
	{/await}
	
</main>

<Overlay {swap} bind:settings />
<svelte:window onkeydown={keyboard_swap} />
