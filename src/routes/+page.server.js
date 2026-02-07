import { readFileSync } from 'fs';
import { parse } from 'csv-parse/sync';

function simplifyMedium(raw) {
	if (!raw) return '';
	const m = raw.toLowerCase();
	if (m.includes('watercolour') || m.includes('watercolor')) return 'watercolour';
	if (m.includes('oil')) return 'oil';
	if (m.includes('acrylic')) return 'acrylic';
	if (m.includes('synthetic polymer')) return 'synthetic polymer';
	if (m.includes('natural pigment') || m.includes('earth pigment') || m.includes('ochre')) return 'natural pigments';
	if (m.includes('gouache')) return 'gouache';
	if (m.includes('ink')) return 'ink';
	if (m.includes('mixed media')) return 'mixed media';
	if (m.includes('bronze')) return 'bronze';
	if (m.includes('ceramic') || m.includes('earthenware') || m.includes('stoneware') || m.includes('terracotta') || m.includes('porcelain')) return 'ceramic';
	if (m.includes('marble')) return 'marble';
	if (m.includes('steel') || m.includes('aluminium') || m.includes('copper')) return 'metal';
	if (m.includes('wood') || m.includes('cedar') || m.includes('hardwood')) return 'wood';
	if (m.includes('charcoal') || m.includes('pencil')) return 'works on paper';
	if (m.includes('enamel')) return 'enamel';
	if (m.includes('resin')) return 'resin';
	if (m.includes('concrete')) return 'concrete';
	if (m.includes('neon')) return 'mixed media';
	return '';
}

export function load() {
	const csv = readFileSync('data/wynne_finalists.csv', 'utf-8');
	const records = parse(csv, { columns: true, skip_empty_lines: true });

	const years = {};
	const mediumSet = new Set();

	for (const row of records) {
		const year = row.year;
		if (!years[year]) years[year] = [];

		const filename = row.image_stem + '.webp';
		const medium = simplifyMedium(row.medium);
		if (medium) mediumSet.add(medium);

		years[year].push({
			artist: row.artist,
			title: row.title,
			winner: row.winner === 'True',
			url: row.url,
			imagePath: '/images/' + encodeURIComponent(filename),
			medium
		});
	}

	// Sort each year: winners first
	for (const year of Object.keys(years)) {
		years[year].sort((a, b) => (b.winner ? 1 : 0) - (a.winner ? 1 : 0));
	}

	// Sort year keys descending (most recent first)
	const sortedYears = Object.keys(years).sort((a, b) => Number(b) - Number(a));

	return {
		years: sortedYears.map((y) => ({ year: y, artworks: years[y] })),
		mediums: [...mediumSet].sort()
	};
}
