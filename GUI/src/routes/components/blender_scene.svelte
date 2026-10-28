<script lang="ts">
	import { onMount } from "svelte";
	import * as THREE from "three";
	import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
	import type { ParallaxSettings } from "../overlay/overlay.svelte";

	// Settings come from the overlay sliders (passed in by +page.svelte).
	let { settings = { intensity: 0.5, depth: 60, smoothing: 0.5 } }: { settings?: ParallaxSettings } = $props();

	const MODEL_PATH = "/models/porject_test.glb"; // must match the file name in static/models exactly

	// Units are metres. The forest is ~9.5 model units across with ~2 unit trees,
	// so x6 gives a ~57 m forest with ~12 m trees.
	const MODEL_SCALE = 6;
	// Where the viewer stands, in model units (before scaling): ground there is
	// y = 0.15, so 0.42 puts the eye 1.6 m up, looking towards the rat at the origin.
	// A Blender empty named "Spawn" overrides this.
	const SPAWN = new THREE.Vector3(0, 0.42, 4);
	const SPAWN_YAW = 0; // radians, turns the view around the spawn point

	// The "window" is the physical monitor: ~30 cm tall, centred at the origin on z = 0
	const SCREEN_H = 0.3;
	const HEAD_RANGE = 0.25; // max head offset in metres when the mouse is at the edge

	let container: HTMLDivElement;

	onMount(() => {
		// Renderer
		const renderer = new THREE.WebGLRenderer({ antialias: true });
		renderer.setPixelRatio(window.devicePixelRatio);
		renderer.outputColorSpace = THREE.SRGBColorSpace;
		container.appendChild(renderer.domElement);

		// Scene
		const scene = new THREE.Scene();
		scene.add(new THREE.AmbientLight(0xffffff, 0.6));
		const sun = new THREE.DirectionalLight(0xffffff, 1.5);
		sun.position.set(2, 4, 3);
		scene.add(sun);

		const camera = new THREE.PerspectiveCamera();

		let zoom = 1;
		let aspect = 1;

		//  Load the Blender model and move it so the spawn point sits at the window
		new GLTFLoader().load(
			MODEL_PATH,
			(gltf) => {
				const model = gltf.scene;
				model.scale.setScalar(MODEL_SCALE);

				const world = new THREE.Group(); // shifted so the spawn point is at the origin
				const pivot = new THREE.Group(); // turns the world around the viewer
				world.add(model);
				pivot.add(world);
				scene.add(pivot);

				world.updateMatrixWorld(true);
				const marker = model.getObjectByName("Spawn");
				const spawn = marker
					? marker.getWorldPosition(new THREE.Vector3())
					: model.localToWorld(SPAWN.clone());
				world.position.copy(spawn).negate();
				pivot.rotation.y = SPAWN_YAW;
			},
			undefined,
			(err) => console.error(`Could not load ${MODEL_PATH}`, err)
		);

		// Eye position
		// TEMPORARY: the mouse stands in for the viewer's head.
		// When eye tracking is ready, set head.x / head.y (-1..1) from it instead.
		const head = { x: 0, y: 0 };
		const target = new THREE.Vector3(0, 0, settings.depth / 100);
		const eye = target.clone();

		function onMouseMove(e: MouseEvent) {
			head.x = (e.clientX / window.innerWidth) * 2 - 1; // -1 (left) .. 1 (right)
			head.y = 1 - (e.clientY / window.innerHeight) * 2; // -1 (bottom) .. 1 (top)
		}
		window.addEventListener("mousemove", onMouseMove);

		// Scroll scales the virtual window: smaller window = narrower view = zoom in
		function onWheel(e: WheelEvent) {
			zoom *= Math.exp(-e.deltaY * 0.001);
			zoom = Math.min(Math.max(zoom, 0.3), 3);
		}
		container.addEventListener("wheel", onWheel, { passive: true });

		// Keep the canvas the size of its container
		function resize() {
			const w = container.clientWidth;
			const h = container.clientHeight;
			renderer.setSize(w, h);
			aspect = w / h;
		}
		const observer = new ResizeObserver(resize);
		observer.observe(container);
		resize();

		//Off-axis projection
		const NEAR = 0.01;
		const FAR = 1000;
		let frame = 0;

		function render() {
			const screenH = SCREEN_H / zoom;
			const screenW = screenH * aspect;

			target.x = head.x * HEAD_RANGE * settings.intensity;
			target.y = head.y * HEAD_RANGE * settings.intensity;
			target.z = Math.max(settings.depth, 1) / 100; // slider is in cm

			// smoothing 0 = follow instantly, 1 = very floaty
			eye.lerp(target, Math.pow(0.02, settings.smoothing));

			// Similar triangles: project the screen's edges onto the near plane, as seen from the eye
			const k = NEAR / eye.z;
			const left = (-screenW / 2 - eye.x) * k;
			const right = (screenW / 2 - eye.x) * k;
			const bottom = (-screenH / 2 - eye.y) * k;
			const top = (screenH / 2 - eye.y) * k;

			camera.position.copy(eye);
			camera.rotation.set(0, 0, 0); // always face straight into the screen, never at the eye
			camera.projectionMatrix.makePerspective(left, right, top, bottom, NEAR, FAR);
			camera.projectionMatrixInverse.copy(camera.projectionMatrix).invert();

			renderer.render(scene, camera);
			frame = requestAnimationFrame(render);
		}
		render();

		//  Clean up when the component is removed
		return () => {
			cancelAnimationFrame(frame);
			observer.disconnect();
			window.removeEventListener("mousemove", onMouseMove);
			container.removeEventListener("wheel", onWheel);
			renderer.dispose();
			renderer.domElement.remove();
		};
	});
</script>

<div class="scene" bind:this={container}></div>

<style>
	.scene {
		width: 100vw;
		height: 100vh;
		overflow: hidden;
	}
</style>
