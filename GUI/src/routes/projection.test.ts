import { describe, expect, it } from "vitest";
import {
	eyeTarget,
	frustumEdges,
	headFromMouse,
	lerpEye,
	NEAR,
	zoomStep
} from "./projection";

describe("headFromMouse", () => {
	it("maps the window centre to the origin", () => {
		expect(headFromMouse(400, 300, 800, 600)).toEqual({ x: 0, y: 0 });
	});

	it("maps corners to the unit square", () => {
		expect(headFromMouse(0, 0, 800, 600)).toEqual({ x: -1, y: 1 });
		expect(headFromMouse(800, 600, 800, 600)).toEqual({ x: 1, y: -1 });
	});
});

describe("zoomStep", () => {
	it("zooms out on scroll down and in on scroll up", () => {
		expect(zoomStep(1, 100)).toBeLessThan(1);
		expect(zoomStep(1, -100)).toBeGreaterThan(1);
	});

	it("clamps to [0.3, 3]", () => {
		expect(zoomStep(1, 1_000_000)).toBe(0.3);
		expect(zoomStep(1, -1_000_000)).toBe(3);
	});
});

describe("eyeTarget", () => {
	it("scales head offset by intensity and head range", () => {
		const target = eyeTarget({ x: 1, y: 0 }, { intensity: 0.5, depth: 60, smoothing: 0.5 });
		expect(target.x).toBeCloseTo(0.25 * 0.5);
		expect(target.y).toBe(0);
	});

	it("converts the depth slider from cm to m", () => {
		expect(eyeTarget({ x: 0, y: 0 }, { intensity: 1, depth: 60, smoothing: 0 }).z).toBeCloseTo(0.6);
	});

	it("never lets the eye land on z = 0", () => {
		const target = eyeTarget({ x: 0, y: 0 }, { intensity: 1, depth: 0, smoothing: 0 });
		expect(target.z).toBeGreaterThan(0);
	});
});

describe("lerpEye", () => {
	it("follows instantly at smoothing 0", () => {
		const eye = { x: 0, y: 0, z: 1 };
		const target = { x: 0.1, y: 0.2, z: 0.6 };
		expect(lerpEye(eye, target, 0)).toEqual(target);
	});

	it("moves slowly at smoothing 1 and converges over many steps", () => {
		const target = { x: 0.1, y: 0, z: 0.6 };
		let eye = { x: 0, y: 0, z: 0.6 };
		const first = lerpEye(eye, target, 1);
		expect(Math.abs(first.x)).toBeLessThan(0.01); //alpha = 0.02

		for (let i = 0; i < 500; i++) {
			eye = lerpEye(eye, target, 1);
		}
		expect(eye.x).toBeCloseTo(0.1, 5);
	});
});

describe("frustumEdges", () => {
	it("is symmetric when the eye is centred", () => {
		const { left, right, bottom, top } = frustumEdges({ x: 0, y: 0, z: 0.6 }, 1, 16 / 9);
		expect(left).toBeCloseTo(-right);
		expect(bottom).toBeCloseTo(-top);
		//the screen is 0.3 m tall, so the half-height is 0.15 at z = 0.6
		const k = NEAR / 0.6;
		expect(top).toBeCloseTo(0.15 * k);
		expect(right).toBeCloseTo(0.15 * (16 / 9) * k);
	});

	it("shifts with the eye position", () => {
		const eye = { x: 0.1, y: -0.05, z: 0.6 };
		const k = NEAR / 0.6;
		const { left, right, bottom, top } = frustumEdges(eye, 1, 1);
		expect(right - left).toBeCloseTo(0.3 * k); //width is eye-independent
		expect(left).toBeCloseTo((-0.15 - 0.1) * k);
		expect(right).toBeCloseTo((0.15 - 0.1) * k);
		expect(bottom).toBeCloseTo((-0.15 + 0.05) * k);
		expect(top).toBeCloseTo((0.15 + 0.05) * k);
	});

	it("scales the window with zoom", () => {
		const wide = frustumEdges({ x: 0, y: 0, z: 0.6 }, 1, 1);
		const zoomed = frustumEdges({ x: 0, y: 0, z: 0.6 }, 2, 1);
		expect(zoomed.top).toBeCloseTo(wide.top / 2);
	});
});
