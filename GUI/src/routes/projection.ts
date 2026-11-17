//Pure math for the off-axis parallax projection, extracted from
//blender_scene.svelte so it can be unit tested without a DOM or WebGL.

export const SCREEN_H = 0.3; //physical monitor height in metres
export const HEAD_RANGE = 0.25; //max head offset in metres at the screen edge
export const NEAR = 0.01;
export const FAR = 1000;

export interface Vec2 {
	x: number;
	y: number;
}

export interface Vec3 {
	x: number;
	y: number;
	z: number;
}

export interface ParallaxSettings {
	intensity: number;
	depth: number;
	smoothing: number;
}

// -1 (left/bottom), 1 (right/top)
export function headFromMouse(
	clientX: number,
	clientY: number,
	width: number,
	height: number
): Vec2 {
	return {
		x: (clientX / width) * 2 - 1,
		y: 1 - (clientY / height) * 2
	};
}

export function zoomStep(zoom: number, deltaY: number): number {
	const next = zoom * Math.exp(-deltaY * 0.001);
	return Math.min(Math.max(next, 0.3), 3);
}

export function eyeTarget(head: Vec2, settings: ParallaxSettings): Vec3 {
	return {
		x: head.x * HEAD_RANGE * settings.intensity,
		y: head.y * HEAD_RANGE * settings.intensity,
		z: Math.max(settings.depth, 1) / 100 //slider is in cm
	};
}

export function lerpEye(eye: Vec3, target: Vec3, smoothing: number): Vec3 {
	const a = Math.pow(0.02, smoothing);
	return {
		x: eye.x + (target.x - eye.x) * a,
		y: eye.y + (target.y - eye.y) * a,
		z: eye.z + (target.z - eye.z) * a
	};
}

export function frustumEdges(eye: Vec3, zoom: number, aspect: number) {
	const screenH = SCREEN_H / zoom;
	const screenW = screenH * aspect;
	const k = NEAR / eye.z;
	return {
		left: (-screenW / 2 - eye.x) * k,
		right: (screenW / 2 - eye.x) * k,
		bottom: (-screenH / 2 - eye.y) * k,
		top: (screenH / 2 - eye.y) * k
	};
}
