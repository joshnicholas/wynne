<script>
	let { data } = $props();

	let yearIndex = $state(0);
	let imageIndex = $state(0);
	let selectedMedium = $state('');

	let touchStartX = $state(0);
	let touchStartY = $state(0);
	let swiping = $state(false);

	const SWIPE_THRESHOLD = 50;

	let currentYear = $derived(data.years[yearIndex]);
	let filteredArtworks = $derived(
		selectedMedium
			? currentYear.artworks.filter((a) => a.medium === selectedMedium)
			: currentYear.artworks
	);
	let currentArtwork = $derived(filteredArtworks[imageIndex]);
	let totalYears = $derived(data.years.length);
	let totalImages = $derived(filteredArtworks.length);

	function changeYear(delta) {
		const next = yearIndex + delta;
		if (next >= 0 && next < totalYears) {
			yearIndex = next;
			imageIndex = 0;
		}
	}

	function changeImage(delta) {
		const next = imageIndex + delta;
		if (next >= 0 && next < totalImages) {
			imageIndex = next;
		}
	}

	let selectEl = $state(null);
	let measureEl = $state(null);

	let selectedLabel = $derived(selectedMedium || 'all mediums');

	$effect(() => {
		if (measureEl && selectEl) {
			// Access selectedLabel to create dependency
			void selectedLabel;
			// Measure after DOM update
			requestAnimationFrame(() => {
				selectEl.style.width = measureEl.offsetWidth + 'px';
			});
		}
	});

	function handleMediumChange(e) {
		selectedMedium = e.target.value;
		imageIndex = 0;
	}

	function handleKeydown(e) {
		switch (e.key) {
			case 'ArrowLeft':
				changeYear(-1);
				break;
			case 'ArrowRight':
				changeYear(1);
				break;
			case 'ArrowUp':
				e.preventDefault();
				changeImage(-1);
				break;
			case 'ArrowDown':
				e.preventDefault();
				changeImage(1);
				break;
		}
	}

	function handleTouchStart(e) {
		const touch = e.touches[0];
		touchStartX = touch.clientX;
		touchStartY = touch.clientY;
		swiping = true;
	}

	function handleTouchEnd(e) {
		if (!swiping) return;
		swiping = false;

		const touch = e.changedTouches[0];
		const dx = touch.clientX - touchStartX;
		const dy = touch.clientY - touchStartY;

		if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > SWIPE_THRESHOLD) {
			changeYear(dx > 0 ? -1 : 1);
		} else if (Math.abs(dy) > Math.abs(dx) && Math.abs(dy) > SWIPE_THRESHOLD) {
			changeImage(dy > 0 ? -1 : 1);
		}
	}
</script>

<svelte:window onkeydown={handleKeydown} />

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
	class="gallery"
	ontouchstart={handleTouchStart}
	ontouchend={handleTouchEnd}
>
	<div class="site-title">Wynne Prize Finalists</div>

	<div class="hint-top">
		<span class="hint-arrow rotate-left">&uarr;</span>
		<span>Swipe to change year</span>
		<span class="hint-arrow rotate-right">&uarr;</span>
	</div>

	<div class="hint-left">
		<!-- <span class="hint-arrow">&darr;</span> -->
				<span class="hint-arrow rotate-left">&uarr;</span>
		<span>Swipe for other finalists</span>
		<!-- <span class="hint-arrow">&uarr;</span> -->
		 		<span class="hint-arrow rotate-right">&uarr;</span>
	</div>

	<div class="year-indicator">
		<span>{currentYear.year}</span>
		<span class="count">{imageIndex + 1}/{totalImages}</span>
	</div>

	<div class="filter-row">
		<span class="filter-wrapper">
			<select bind:this={selectEl} class="medium-filter" value={selectedMedium} onchange={handleMediumChange}>
				<option value="">all mediums</option>
				{#each data.mediums as medium}
					<option value={medium}>{medium}</option>
				{/each}
			</select><span class="filter-caret">&#9662;</span>
			<span bind:this={measureEl} class="filter-measure" aria-hidden="true">{selectedLabel}</span>
		</span>
	</div>

	{#if currentArtwork}
		<div class="image-container">
			<img
				src={currentArtwork.imagePath}
				alt="{currentArtwork.title} by {currentArtwork.artist}"
			/>
		</div>

		<div class="caption">
			{#if currentArtwork.winner}
				<span class="winner">Winner</span>
			{/if}
			<a href={currentArtwork.url} target="_blank" rel="noopener">
				{currentArtwork.artist}
			</a>
			<a href={currentArtwork.url} target="_blank" rel="noopener" class="title">{currentArtwork.title}</a>
		</div>
	{:else}
		<div class="image-container">
			<span class="no-results">No finalists with this medium in {currentYear.year}</span>
		</div>
		<div class="caption"></div>
	{/if}

	<div class="footer">
		<span class="footer-line"><span class="footer-dim">More at the</span> <a href="https://www.artgallery.nsw.gov.au/prizes/wynne/" target="_blank" rel="noopener">Art Gallery of New South Wales</a></span>
		<span class="footer-line"><span class="footer-dim">by <a href="https://joshnicholas.com" target="_blank" rel="me">Josh</a></span></span>
	</div>
</div>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		background: #000;
		color: #fff;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
		overflow: hidden;
		-webkit-user-select: none;
		user-select: none;
	}

	.gallery {
		display: flex;
		flex-direction: column;
		height: 100dvh;
		touch-action: none;
		position: relative;
	}

	.hint-top {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
		padding: 4px 16px;
		font-size: 14px;
		opacity: 0.5;
		flex-shrink: 0;
	}

	.hint-left {
		position: absolute;
		left: 0;
		top: 0;
		bottom: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
		padding: 0 12px;
		font-size: 14px;
		opacity: 0.5;
		writing-mode: vertical-lr;
		transform: rotate(180deg);
	}

	.hint-arrow {
		font-size: 16px;
	}

	.hint-arrow.rotate-right {
		display: inline-block;
		transform: rotate(90deg);
	}

	.hint-arrow.rotate-left {
		display: inline-block;
		transform: rotate(-90deg);
	}

	.site-title {
		padding: 12px 16px 0;
		font-size: 24px;
		font-weight: 600;
		text-align: center;
		flex-shrink: 0;
	}

	.year-indicator {
		padding: 8px 16px 0;
		font-size: 20px;
		font-weight: 600;
		display: flex;
		justify-content: space-between;
		align-items: center;
		flex-shrink: 0;
	}

	.year-indicator .count {
		font-weight: 400;
		opacity: 0.5;
	}

	.filter-row {
		padding: 4px 16px 8px;
		flex-shrink: 0;
	}

	.filter-wrapper {
		position: relative;
		display: inline-flex;
		align-items: baseline;
		cursor: pointer;
	}

	.medium-filter {
		background: none;
		border: none;
		color: #fff;
		font-family: inherit;
		font-size: 20px;
		font-weight: 400;
		opacity: 0.5;
		cursor: pointer;
		padding: 0;
		-webkit-appearance: none;
		appearance: none;
	}

	.filter-caret {
		font-size: 20px;
		opacity: 0.5;
		margin-left: 2px;
		vertical-align: super;
		pointer-events: none;
	}

	.filter-measure {
		position: absolute;
		visibility: hidden;
		white-space: nowrap;
		font-family: inherit;
		font-size: 20px;
		font-weight: 400;
	}

	.medium-filter option {
		background: #000;
		color: #fff;
	}

	.image-container {
		flex: 1;
		min-height: 0;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.image-container img {
		max-width: 100%;
		max-height: 100%;
		object-fit: contain;
	}

	.no-results {
		opacity: 0.5;
		font-size: 16px;
	}

	.caption {
		padding: 8px 16px 0;
		font-size: 20px;
		flex-shrink: 0;
		display: flex;
		gap: 8px;
		align-items: baseline;
		min-height: 32px;
	}

	.caption a {
		color: #fff;
		text-decoration: none;
	}

	.caption a:hover {
		text-decoration: underline;
	}

	.caption .title {
		opacity: 0.5;
	}

	.winner {
		background: #fff;
		color: #000;
		padding: 1px 6px;
		font-size: 11px;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.footer {
		padding: 4px 16px 12px;
		flex-shrink: 0;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 2px;
	}

	.footer-line {
		padding-top: 15px;
		font-size: 16px;
		color: #fff;
	}

	.footer-dim {
		opacity: 0.5;
	}

	.footer-line a {
		color: #fff;
		text-decoration: none;
	}

	.footer-line a:hover {
		text-decoration: underline;
	}
</style>
