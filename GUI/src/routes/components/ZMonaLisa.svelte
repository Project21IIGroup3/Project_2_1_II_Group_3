<!-- Stylized SVG take on Leonardo's Mona Lisa -->
<div class="frame">
	<svg viewBox="0 0 300 420" role="img" aria-label="Stylized Mona Lisa">
		<defs>
			<linearGradient id="ml-sky" x1="0" y1="0" x2="0" y2="1">
				<stop offset="0" stop-color="#aab27f" />
				<stop offset="0.45" stop-color="#6f7a4c" />
				<stop offset="1" stop-color="#3a3520" />
			</linearGradient>
			<radialGradient id="ml-skin" cx="0.45" cy="0.4" r="0.75">
				<stop offset="0" stop-color="#ecc890" />
				<stop offset="0.6" stop-color="#c8955a" />
				<stop offset="1" stop-color="#7a5128" />
			</radialGradient>
			<radialGradient id="ml-vignette" cx="0.5" cy="0.45" r="0.75">
				<stop offset="0.55" stop-color="#000" stop-opacity="0" />
				<stop offset="1" stop-color="#140d04" stop-opacity="0.8" />
			</radialGradient>
		</defs>

		<!-- sky -->
		<rect width="300" height="420" fill="url(#ml-sky)" />

		<!-- hazy distant landscape -->
		<g opacity="0.6">
			<path d="M0 150 L35 118 L70 140 L100 108 L125 132 L125 210 L0 210Z" fill="#7d9788" />
			<path d="M175 128 L210 98 L240 130 L270 112 L300 134 L300 215 L175 215Z" fill="#7d9788" />
			<ellipse cx="45" cy="186" rx="50" ry="8" fill="#c3cba6" />
			<ellipse cx="255" cy="168" rx="45" ry="7" fill="#c3cba6" />
		</g>
		<path d="M0 205 C40 192 80 218 125 206 L125 420 L0 420Z" fill="#5a4a28" />
		<path d="M175 218 C220 202 260 228 300 212 L300 420 L175 420Z" fill="#5a4a28" />
		<path d="M18 262 C60 242 38 222 82 208" stroke="#b08a52" stroke-width="4" fill="none" opacity="0.55" />
		<path d="M222 236 q16 -13 32 0" stroke="#8a6a3a" stroke-width="3" fill="none" />

		<!-- body -->
		<path
			d="M150 205 C105 210 75 235 60 280 C45 330 30 380 25 420 L275 420 C270 380 255 330 240 280 C225 235 195 210 150 205Z"
			fill="#2c2615"
		/>
		<path d="M60 290 C44 340 55 382 112 396 L150 402 L120 350Z" fill="#6b4c22" />
		<path d="M240 290 C256 340 245 380 190 393 L160 399 L186 350Z" fill="#5f431d" />

		<!-- neck & chest -->
		<path d="M132 168 L168 168 L172 218 C160 224 140 224 128 218Z" fill="url(#ml-skin)" />
		<path d="M116 214 C130 210 170 210 184 214 L196 245 C175 263 125 263 104 245Z" fill="url(#ml-skin)" />
		<path
			d="M104 245 C125 263 175 263 196 245"
			stroke="#b08a3e"
			stroke-width="1.5"
			fill="none"
			stroke-dasharray="3 2"
		/>

		<!-- hair (back) -->
		<path
			d="M150 72 C100 72 92 120 100 170 C104 200 98 225 86 246 L112 240 C118 210 118 185 116 160 L184 160 C182 185 182 210 188 240 L214 246 C202 225 196 200 200 170 C208 120 200 72 150 72Z"
			fill="#23160b"
		/>

		<!-- face -->
		<ellipse cx="150" cy="130" rx="35" ry="47" fill="url(#ml-skin)" />

		<!-- hair (front, center part) + veil -->
		<path
			d="M150 80 C125 82 112 100 110 132 C114 110 128 92 150 88 C172 92 186 110 190 132 C188 100 175 82 150 80Z"
			fill="#23160b"
		/>
		<path d="M106 96 C120 76 180 76 194 96" stroke="#140d06" stroke-width="2.5" fill="none" opacity="0.55" />

		<!-- eyes (no brows, famously) -->
		<g fill="#3b2412">
			<ellipse cx="135" cy="125" rx="7" ry="3" />
			<ellipse cx="165" cy="125" rx="7" ry="3" />
		</g>
		<g fill="#120a04">
			<circle cx="136.5" cy="125" r="1.9" />
			<circle cx="163.5" cy="125" r="1.9" />
		</g>
		<g stroke="#6b4322" stroke-width="1" fill="none" opacity="0.7">
			<path d="M127 122 q8 -5 16 0" />
			<path d="M157 122 q8 -5 16 0" />
		</g>

		<!-- nose -->
		<path
			d="M150 128 C148 140 146 146 143 150 C148 154 154 154 157 150"
			stroke="#8a5a2c"
			stroke-width="1.2"
			fill="none"
			opacity="0.7"
		/>

		<!-- the smile -->
		<path d="M138 160 C145 164 155 164 162 159" stroke="#7a3f22" stroke-width="1.6" fill="none" stroke-linecap="round" />
		<path d="M136 157.5 q1.5 2 3 2.3 M161 159 q1.5 -0.5 3 -2.5" stroke="#7a3f22" stroke-width="1" fill="none" opacity="0.6" />

		<!-- hands -->
		<path d="M92 386 C110 370 150 368 176 378 C187 385 181 396 165 397 C140 399 110 399 92 386Z" fill="url(#ml-skin)" />
		<path d="M148 373 C170 360 206 362 216 373 C221 383 206 391 186 389 C170 388 155 383 148 373Z" fill="url(#ml-skin)" />
		<g stroke="#8a5a2c" stroke-width="0.9" fill="none" opacity="0.55">
			<path d="M170 372 q14 -4 26 2" />
			<path d="M172 379 q14 -3 28 3" />
			<path d="M120 388 q20 -6 40 -2" />
		</g>

		<!-- vignette + old-varnish tint -->
		<rect width="300" height="420" fill="url(#ml-vignette)" />
		<rect width="300" height="420" fill="#8a6a20" opacity="0.08" />
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
		height: min(85vh, 100%);
		max-width: 100%;
		border: 10px solid #4a3418;
		box-shadow:
			0 0 0 2px #b08a3e,
			0 8px 16px rgb(0 0 0 / 0.4);
	}
</style>
