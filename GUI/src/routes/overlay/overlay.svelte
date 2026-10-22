<script module lang="ts">
	export interface ParallaxSettings {
		intensity: number;
		depth: number;
		smoothing: number;
	}
</script>

<script lang="ts">
	import "../../styles/overlay.css";
	import { slide } from "svelte/transition";

	interface Props {
		swap: (direction: 1 | -1) => void;
		settings: ParallaxSettings;
	}

	let { swap, settings = $bindable() }: Props = $props();

	let open = $state(true);
</script>

<aside class="overlay" class:collapsed={!open}>
	<header>
		{#if open}<span class="title">Settings</span>{/if}
		<button
			class="icon toggle"
			onclick={() => (open = !open)}
			aria-label={open ? "Collapse" : "Expand"}
			aria-expanded={open}
		>
			<svg viewBox="0 0 24 24"><path d="M6 9l6 6 6-6" /></svg>
		</button>
	</header>

	{#if open}
		<div class="body" transition:slide={{ duration: 150 }}>
			<div class="nav">
				<button class="icon" onclick={() => swap(-1)} aria-label="Previous">
					<svg viewBox="0 0 24 24"><path d="M15 6l-6 6 6 6" /></svg>
				</button>
				<button class="icon" onclick={() => swap(1)} aria-label="Next">
					<svg viewBox="0 0 24 24"><path d="M9 6l6 6-6 6" /></svg>
				</button>
			</div>

			<label>
				<span>Intensity <output>{settings.intensity.toFixed(2)}</output></span>
				<input type="range" min="0" max="1" step="0.01" bind:value={settings.intensity} />
			</label>
			<label>
				<span>Depth <output>{settings.depth}px</output></span>
				<input type="range" min="0" max="100" step="1" bind:value={settings.depth} />
			</label>
			<label>
				<span>Smoothing <output>{settings.smoothing.toFixed(2)}</output></span>
				<input type="range" min="0" max="1" step="0.01" bind:value={settings.smoothing} />
			</label>
		</div>
	{/if}
</aside>
