<script lang="ts">
	import { onMount } from "svelte";
	import * as THREE from "three";
	import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
	import type { ParallaxSettings } from "../overlay/overlay.svelte";

	// Settings come from the overlay sliders (passed in by +page.svelte).
	let { settings = { intensity: 0.5, depth: 20, smoothing: 0.1 } }: { settings?: ParallaxSettings } = $props();

	const MODEL_PATH = "/models/porject_test.glb"; // must match the file name in static/models exactly

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

		// The "window": the physical screen, centred at the origin on the z = 0 plane
		let screenH = settings.depth * 0.8;
		let screenW = screenH;

		//  Load the Blender model and fit it just behind the screen 
		new GLTFLoader().load(
			MODEL_PATH,
			(gltf) => {
				const model = gltf.scene;
				const box = new THREE.Box3().setFromObject(model);
				const size = box.getSize(new THREE.Vector3());
				const scale = (screenH * 1.3) / Math.max(size.x, size.y);
				model.scale.setScalar(scale);

				// Re-measure after scaling, then centre in x/y and push the front face to z = 0
				box.setFromObject(model);
				const center = box.getCenter(new THREE.Vector3());
				model.position.x -= center.x + 5;
				model.position.y -= center.y - 1;
				model.position.z -= box.max.z - 22;

				scene.add(model);
			},
			undefined,
			(err) => console.error(`Could not load ${MODEL_PATH}`, err)
		);

		// Eye position 
		// TEMPORARY: the mouse stands in for the viewer's eye.
		// When eye tracking is ready, set target.x / target.y / target.z from it instead.
		const target = new THREE.Vector3(0, 0, settings.depth);
		const eye = target.clone();

		function onMouseMove(e: MouseEvent) {
			const nx = (e.clientX / window.innerWidth) * 2 - 1; // -1 (left) .. 1 (right)
			const ny = 1 - (e.clientY / window.innerHeight) * 2; // -1 (bottom) .. 1 (top)
			target.x = nx * screenW * settings.intensity * 0.2;
			target.y = ny * screenH * settings.intensity * 0.2;
		}
		window.addEventListener("mousemove", onMouseMove);

		// Keep the canvas the size of its container 
		function resize() {
			const w = container.clientWidth;
			const h = container.clientHeight;
			renderer.setSize(w, h);
			screenH = settings.depth * 0.8;
			screenW = screenH * (w / h);
		}
		const observer = new ResizeObserver(resize);
		observer.observe(container);
		resize();

		//Off-axis projection
		const NEAR = 0.1;
		const FAR = 1000;
		let frame = 0;

		function render() {
			target.z = settings.depth;
			eye.lerp(target, settings.smoothing);

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