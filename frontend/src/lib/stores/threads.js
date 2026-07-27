import { writable } from 'svelte/store';
import { sendAgentMessage, getMessages, getThreads } from '../api/agent.js';

function createThreadsStore() {
	const store = writable({
		threads: [],
		threadsStatus: 'idle',
		activeThreadId: null,
		messages: [],
		messagesStatus: 'idle',
		sending: false,
		error: null
	});

	let current;
	store.subscribe((v) => (current = v));

	async function loadThreads(userId) {
		store.update((s) => ({ ...s, threadsStatus: 'loading' }));
		try {
			const threads = await getThreads(userId);
			store.update((s) => ({ ...s, threads: threads ?? [], threadsStatus: 'ready' }));
		} catch (err) {
			store.update((s) => ({ ...s, threadsStatus: 'error', error: err.message }));
		}
	}

	async function selectThread(threadId) {
		store.update((s) => ({ ...s, activeThreadId: threadId, messages: [], messagesStatus: 'loading' }));
		try {
			const messages = await getMessages(threadId);
			store.update((s) => ({ ...s, messages: messages ?? [], messagesStatus: 'ready' }));
		} catch (err) {
			store.update((s) => ({ ...s, messagesStatus: 'error', error: err.message }));
		}
	}
	function startNewThread() {
		store.update((s) => ({ ...s, activeThreadId: null, messages: [], messagesStatus: 'ready' }));
	}

	async function send(message, userId) {
		const threadId = current.activeThreadId;

		store.update((s) => ({
			...s,
			sending: true,
			error: null,
			messages: [
				...s.messages,
				{ user_input: message, response: null, created_at: new Date().toISOString(), pending: true }
			]
		}));

		try {
			const res = await sendAgentMessage({ message, thread_id: threadId, user_id: userId });

			store.update((s) => {
				const messages = [...s.messages];
				messages[messages.length - 1] = {
					user_input: message,
					response: res.response,
					created_at: new Date().toISOString()
				};
				return { ...s, messages, sending: false, activeThreadId: res.thread_id };
			});

			if (!threadId) await loadThreads(userId);

			return res;
		} catch (err) {
			store.update((s) => ({
				...s,
				sending: false,
				error: err.message || 'The agent failed to respond.',
				messages: s.messages.slice(0, -1)
			}));
			throw err;
		}
	}

	function reset() {
		store.set({
			threads: [],
			threadsStatus: 'idle',
			activeThreadId: null,
			messages: [],
			messagesStatus: 'idle',
			sending: false,
			error: null
		});
	}

	return { subscribe: store.subscribe, loadThreads, selectThread, startNewThread, send, reset };
}

export const threads = createThreadsStore();
