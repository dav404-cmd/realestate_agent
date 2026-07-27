import { writable } from 'svelte/store';
import { browser } from '$app/environment';

const STORAGE_KEY = 'jpre-theme'; // 'dark' | 'light' | 'system'

function getSystemPref() {
	if (!browser) return 'dark';
	return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
}

function resolve(mode) {
	return mode === 'system' ? getSystemPref() : mode;
}

function createThemeStore() {
	const initialMode = browser ? localStorage.getItem(STORAGE_KEY) || 'system' : 'system';
	const { subscribe, set: _set } = writable(resolve(initialMode));

	let currentMode = initialMode;

	function apply(resolved) {
		if (browser) {
			document.documentElement.setAttribute('data-theme', resolved);
			document.documentElement.style.colorScheme = resolved;
		}
		_set(resolved);
	}

	apply(resolve(initialMode));

	if (browser) {
		window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', () => {
			if (currentMode === 'system') apply(resolve('system'));
		});
	}

	return {
		subscribe,
		/** @param {'dark'|'light'|'system'} mode */
		setMode(mode) {
			currentMode = mode;
			if (browser) localStorage.setItem(STORAGE_KEY, mode);
			apply(resolve(mode));
		},
		toggle() {
			const next = resolve(currentMode) === 'dark' ? 'light' : 'dark';
			this.setMode(next);
		}
	};
}

export const theme = createThemeStore();
