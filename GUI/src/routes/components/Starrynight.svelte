<!-- Stylized SVG take on Van Gogh's The Starry Night -->
<div class="frame">
	<svg viewBox="0 0 600 380" role="img" aria-label="Stylized Starry Night">
		<defs>
			<linearGradient id="sn-sky" x1="0" y1="0" x2="0" y2="1">
				<stop offset="0" stop-color="#0b1d47" />
				<stop offset="0.55" stop-color="#1d4a8c" />
				<stop offset="1" stop-color="#3f73b0" />
			</linearGradient>
			<radialGradient id="sn-halo">
				<stop offset="0" stop-color="#fff3a8" stop-opacity="0.9" />
				<stop offset="0.5" stop-color="#e8d25a" stop-opacity="0.35" />
				<stop offset="1" stop-color="#e8d25a" stop-opacity="0" />
			</radialGradient>
			<mask id="sn-crescent">
				<circle cx="530" cy="68" r="22" fill="#fff" />
				<circle cx="520" cy="60" r="19" fill="#000" />
			</mask>
		</defs>

		<rect width="600" height="380" fill="url(#sn-sky)" />

		<!-- wind swirls -->
		<g fill="none" stroke-linecap="round">
			<path
				class="flow"
				d="M-10 95 C80 60 140 125 220 98 S360 40 440 92 S560 112 610 80"
				stroke="#7fa8dc"
				stroke-width="12"
				opacity="0.5"
			/>
			<path
				class="flow"
				d="M-10 95 C80 60 140 125 220 98 S360 40 440 92 S560 112 610 80"
				stroke="#d9e8f8"
				stroke-width="3"
			/>
			<path
				class="flow slow"
				d="M-10 175 C90 150 160 205 260 180 S420 140 610 170"
				stroke="#5f8fcc"
				stroke-width="9"
				opacity="0.5"
			/>
			<!-- the big central spiral -->
			<path
				class="flow"
				d="M250 150 C300 95 400 110 400 160 C400 205 330 215 312 185 C298 162 325 146 345 160"
				stroke="#b4d0f0"
				stroke-width="7"
			/>
			<path
				class="flow slow"
				d="M250 150 C300 95 400 110 400 160 C400 205 330 215 312 185 C298 162 325 146 345 160"
				stroke="#f1f6fc"
				stroke-width="2"
			/>
			<path
				class="flow slow"
				d="M170 150 C150 118 200 104 215 128 C226 146 205 160 192 150"
				stroke="#9fc0e8"
				stroke-width="5"
			/>
		</g>

		<!-- stars -->
		{#each [[90, 60, 0], [190, 45, 1.2], [300, 70, 0.6], [420, 40, 1.8], [470, 150, 0.3], [150, 200, 2.1], [400, 225, 1.4]] as [x, y, d]}
			<g transform="translate({x} {y})">
				<g>
					<circle r="26" fill="url(#sn-halo)" />
					<circle r="16" fill="none" stroke="#fff6c2" stroke-width="2" opacity="0.7" />
					<circle r="8" fill="#f6e27a" />
				</g>
			</g>
		{/each}

		<!-- moon -->
		<g>
			<circle cx="530" cy="68" r="46" fill="url(#sn-halo)" />
			<circle cx="530" cy="68" r="34" fill="none" stroke="#f2c94c" stroke-width="3" opacity="0.6" />
		</g>
		<rect x="500" y="40" width="60" height="60" fill="#f5b83d" mask="url(#sn-crescent)" />

		<!-- hills -->
		<path
			d="M0 285 C80 255 160 275 240 258 S400 246 480 264 S560 252 600 260 L600 380 L0 380Z"
			fill="#2a4a80"
		/>
		<path d="M0 320 C120 300 260 318 380 302 S540 310 600 300 L600 380 L0 380Z" fill="#1b2f55" />

		<!-- village -->
		<g fill="#22355c">
			<rect x="230" y="300" width="28" height="20" />
			<rect x="265" y="296" width="34" height="24" />
			<rect x="340" y="298" width="30" height="22" />
			<rect x="380" y="302" width="36" height="18" />
			<rect x="430" y="300" width="26" height="20" />
			<!-- church -->
			<rect x="305" y="282" width="22" height="38" />
			<path d="M305 282 L316 222 L327 282Z" />
		</g>
		<g fill="#f2d36b">
			<rect x="236" y="306" width="4" height="4" />
			<rect x="274" y="304" width="4" height="4" />
			<rect x="286" y="308" width="4" height="4" />
			<rect x="348" y="306" width="4" height="4" />
			<rect x="392" y="308" width="4" height="4" />
			<rect x="438" y="306" width="4" height="4" />
		</g>

		<!-- cypress -->
		<path
			d="M68 380 C58 300 92 262 80 200 C74 150 102 110 96 36 C118 92 122 142 132 192 C142 252 152 302 146 380Z"
			fill="#161c14"
		/>
		<g stroke="#2e3b22" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.8">
			<path d="M96 60 C104 110 92 160 104 220 C112 270 100 320 108 370" />
			<path d="M88 150 C100 200 86 260 96 330" />
			<path d="M116 140 C124 200 118 260 130 340" />
		</g>
	</svg>
</div>

<style>
	.frame {
		display: grid;
		place-items: center;
		width: 100%;
		height: 100%;
		padding: 2rem;
		box-sizing: border-box;
	}
	svg {
		width: min(90vw, 100%);
		max-height: 85vh;
		border: 10px solid #2b2016;
		box-shadow:
			0 0 0 2px #b08a3e,
			0 8px 16px rgb(0 0 0 / 0.4);
	}
	.flow {
		stroke-dasharray: 22 14;
	}
</style>
